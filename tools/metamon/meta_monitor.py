# python3

"""Monitors META repos and META Cloud Builds.

Periodically polls META repos to detect new META releases and kick off new META
integration builds. Also monitors META integration builds and pushes build state
to a Cloud SQL database.

Usage:
  $ python3 metamon.py
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse
import asyncio
import logging
import os
import random
import re
import tempfile

# URL template of Qualcomm META repo for each SoC target platform.
META_URL_TEMPLATE = 'https://chipmaster2.qti.qualcomm.com/home2/git/google-inc/%s_test_device.git'

# Extract just the git tag from the output of 'git ls-remote --refs --tags'.
META_TAG_REGEX = r'refs/tags/(r[a-z0-9_\.]+)'

# List of supported SoC target platforms.
META_TARGETS = [
    # SDM845
    'sdm845-la-2-0',
    # SDM660
    'snapdragon-high-mid-2017-spf-3-0',
    # MSM8917
    'snapdragon-high-mid-2018-spf-1-0-1'
]


def make_subprocess_cmd(cmd):
  """Creates a function that returns an async subprocess.

  Args:
    cmd: Command to run in the subprocess. Arguments should be provided when
      calling the returned function.
  Returns:
    A function that creates an asyncio.subprocess.Process instance.
  """
  def subprocess_cmd(*args, cwd):
    logging.info('Running "%s %s"', cmd, ' '.join(args))
    return asyncio.create_subprocess_exec(
        cmd, *args, stdout=asyncio.subprocess.PIPE, cwd=cwd)
  return subprocess_cmd


class MetaMonitorCommands:

  def __init__(self):
    self.git = make_subprocess_cmd('git')
    self.tar = make_subprocess_cmd('tar')
    self.gcloud = make_subprocess_cmd('gcloud')
    self.gsutil = make_subprocess_cmd('gsutil')
    self.rm = make_subprocess_cmd('rm')


async def fetch_target_git_tags(commands, url):
  """Fetch META tags for a Qualcomm SoC target.

  Args:
    commands: Subprocess creation object.
    url: URL of git repo to retrieve tags from.
  Returns:
    A list of META tags in the repo for the given Qualcomm SoC target. Returns
    an empty list when the undelying git command fails.
  """
  git_subproc = await commands.git(
      'ls-remote', '--refs', '--tags', url, cwd=None)
  returncode = await git_subproc.wait()
  if returncode:
    logging.warning('git ls-remote returned %d', returncode)
    return []

  stdout, _ = await git_subproc.communicate()
  raw_tags = stdout.decode('utf-8', 'ignore')
  meta_tags = re.findall(META_TAG_REGEX, raw_tags)
  return meta_tags


async def clone_target_meta(commands, url, target_work_dir):
  """Clone META repo for a Qualcomm SoC target.

  Args:
    commands: Subprocess creation object.
    url: URL of git repo to clone.
    target_work_dir: Path to destination folder for the cloned repo.
  Returns:
    The META tag that is returned by running 'git describe' in the cloned repo.
    Returns the empty string when the underlying commands fail.
  """
  rm_subproc = await commands.rm('-rf', target_work_dir, cwd=None)
  returncode = await rm_subproc.wait()
  if returncode:
    logging.warning('%s: rm returned %d', target, returncode)
    return ''

  git_clone_subproc = await commands.git(
      'clone', '--depth=1', '--quiet', url, target_work_dir, cwd=None)
  returncode = await git_clone_subproc.wait()
  if returncode:
    logging.warning('git clone returned %d', returncode)
    return ''

  git_describe_subproc = await commands.git('describe', cwd=target_work_dir)
  returncode = await git_describe_subproc.wait()
  if returncode:
    logging.warning('git describe returned %d', returncode)
    return ''

  stdout, _ = await git_describe_subproc.communicate()
  meta_tag = stdout.decode('utf-8', 'ignore').strip()
  return meta_tag


async def archive_target_meta(
    commands, target, work_dir, target_work_dir, target_meta_tag):
  """Zip and upload the META source repo to Cloud Storage

  Args:
    commands: Subprocess creation object.
    target: Name of a target Qualcomm SoC.
    work_dir: Top level working folder.
    target_work_dir: Path to the cloned target repository.
    target_meta_tag: META tag at target repository HEAD.
  Returns:
    True for success. False for failure.
  """
  meta_archive_name = 'meta-source-%s.tar.gz' % target
  tar_subproc = await commands.tar(
      '-C', target_work_dir, '-cf', meta_archive_name,
      '--use-compress-program=pigz', '.', cwd=work_dir)
  returncode = await tar_subproc.wait()
  if returncode:
    logging.warning('%s: tar returned %d', target, returncode)
    return False

  gsutil_subproc = await commands.gsutil(
      'cp', meta_archive_name,
      'gs://meta-source/%s/%s/meta-source.tar.gz' % (target, target_meta_tag),
      cwd=work_dir)
  returncode = await gsutil_subproc.wait()
  if returncode:
    logging.warning('%s: gsutil returned %d', target, returncode)
    return False

  return True


async def target_meta_loop(commands, target, interval, work_dir, loop):
  """Main loop to fetch META tags for a Qualcomm SoC target.

  Args:
    commands: Subprocess creation object.
    target: Name of a target Qualcomm SoC.
    interval: Time in seconds to wait between poll attempts.
    loop: A reference to the asyncio event loop in use.
  Returns:
    Nothing. Loops forever.
  """
  target_work_dir = os.path.join(work_dir, target)

  # Stagger the wakeup time of the target loops to avoid hammering the remote
  # server with requests all at once.
  next_wakeup_time = loop.time() + random.randrange(0, interval)

  # TODO(brianorr): Fetch META tags from CloudSQL.
  git_target_url = META_URL_TEMPLATE % target
  current_meta_tags = await fetch_target_git_tags(commands, git_target_url)
  current_meta_tags = current_meta_tags[:-1]

  while True:
    # Calculate the polling loop's next wake-up time. To stay on schedule we
    # keep incrementing next_wakeup_time by the polling inteval until we
    # arrive at a time in the future.
    while next_wakeup_time < loop.time():
      next_wakeup_time += interval
    sleep_time = max(0, next_wakeup_time - loop.time())
    logging.info('%s: sleeping for %f', target, sleep_time)
    await asyncio.sleep(sleep_time)

    # Retrieve current tags from the remote repo.
    new_meta_tags = await fetch_target_git_tags(commands, git_target_url)
    if not new_meta_tags:
      continue
    logging.info('%s: META tags: %s', target, ' '.join(new_meta_tags))

    # See if new META tags were added since the last check.
    meta_tags_delta = set(new_meta_tags) - set(current_meta_tags)
    if not meta_tags_delta:
      logging.info('%s: no new META tags', target)
      continue
    logging.info('%s: new META tags: %s', target, ' '.join(meta_tags_delta))

    # Clone the repo and verify that HEAD points to a new tag.
    target_meta_tag = await clone_target_meta(commands, target, target_work_dir)
    if target_meta_tag not in new_meta_tags:
      logging.warning(
          '%s: Expected new tags but HEAD points to %s', target,
          target_meta_tag)
      continue

    # Zip and archive the cloned repo to Cloud Storage.
    archive_success = await archive_target_meta(
        commands, target, work_dir, target_work_dir, target_meta_tag)
    if not archive_success:
      continue

    # TODO(brianorr): Kick off META build for the new tag.
    current_meta_tags = new_meta_tags


def main():
  # Parse command line flags.
  parser = argparse.ArgumentParser()
  parser.add_argument(
      '--meta_poll_interval',
      type=int,
      default=3600,
      help='Time between META poll attempts in seconds.')
  parser.add_argument(
      '--log',
      default='WARN',
      help='Set the Python logging level.')
  args = parser.parse_args()

  # Set the runtime log level or raise an exception if the user provided an
  # invalid log enum.
  numeric_level = getattr(logging, args.log.upper(), None)
  if not isinstance(numeric_level, int):
    raise ValueError('Invalid log level: %s' % args.log)
  logging.basicConfig(level=numeric_level)

  loop = asyncio.get_event_loop()

  # Create a top level working folder for clone and archive operations.
  work_dir = tempfile.mkdtemp()
  logging.info('Working folder is %s', work_dir)

  # Use actual subprocess commands in production.
  commands = MetaMonitorCommands()

  # Create a polling loop coroutine for each Qualcomm SoC.
  targets = [
      target_meta_loop(
          commands, target, args.meta_poll_interval, work_dir, loop)
      for target in META_TARGETS]

  # Use asyncio.gather() to submit all coroutines to the event loop as
  # recommended by @gvanrossum in the GitHub issue comments at
  # https://github.com/python/asyncio/issues/477#issuecomment-269038238
  loop.run_until_complete(asyncio.gather(*targets))


if __name__ == '__main__':
  main()
