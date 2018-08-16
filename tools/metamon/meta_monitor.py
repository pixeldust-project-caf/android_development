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
import re

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


def git(*args, cwd):
  """Execute a git command.

  Args:
    *args: A list of strings containing everything after the 'git' command.
    cwd: A string path where the command will be executed.
  Returns:
    A coroutine that returns a Process instance.
  """
  logging.info('Running "git %s"', ' '.join(args))
  return asyncio.create_subprocess_exec(
      'git', *args, stdout=asyncio.subprocess.PIPE, cwd=cwd)


def gcloud(*args, cwd):
  """Execute a gcloud command.

  Args:
    *args: Command and arguments to pass to the 'gcloud' command.
    cwd: A string path where the command will be executed.
  Returns:
    A coroutine that returns a Process instance.
  """
  logging.info('Running "gcloud %s"', ' '.join(args))
  return asyncio.create_subprocess_exec(
      'gcloud', *args, stdout=asyncio.subprocess.PIPE, cwd=cwd)


async def fetch_target_meta_tags(target, git_cmd=git):
  """Fetch META tags for a Qualcomm SoC target.

  Args:
    target: Name of a target Qualcomm SoC
    git_cmd: Function to create a asyncio.subprocess.Process object that will
      run a git command.
  Returns:
    A list of META tags in the repo for the given Qualcomm SoC target. Returns
    an empty list when the undelying git command fails.
  """
  git_subproc = await git_cmd(
      'ls-remote', '--refs', '--tags', META_URL_TEMPLATE % target, cwd=None)
  returncode = await git_subproc.wait()
  if returncode:
    logging.warning('git ls-remote for %s returned %d', target, returncode)
    return []

  stdout, _ = await git_subproc.communicate()
  raw_tags = stdout.decode('utf-8', 'ignore')
  logging.debug('Raw META tags for %s', raw_tags)
  meta_tags = re.findall(META_TAG_REGEX, raw_tags)

  logging.info('META tags for %s', target)
  logging.info(' '.join(meta_tags))
  return meta_tags


async def target_meta_loop(target, interval, loop):
  """Main loop to fetch META tags for a Qualcomm SoC target.

  Args:
    target: Name of a target Qualcomm SoC.
    interval: Time in seconds to wait between poll attempts.
    loop: A reference to the asyncio event loop in use.
  Returns:
    Nothing. Loops forever.
  """
  next_wakeup_time = loop.time() + interval

  # TODO(brianorr): Fetch META tags from CloudSQL.
  current_meta_tags = await fetch_target_meta_tags(target)

  while True:
    sleep_time = max(0, next_wakeup_time - loop.time())
    next_wakeup_time += interval

    logging.info('%s sleeping for %f', target, sleep_time)
    await asyncio.sleep(sleep_time)

    new_meta_tags = await fetch_target_meta_tags(target)
    meta_tags_delta = set(new_meta_tags) - set(current_meta_tags)

    # TODO(brianorr): Kick off META build for each new tag.
    if meta_tags_delta:
      logging.info('Found new META tags: %s', ' '.join(meta_tags_delta))

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

  # Create a polling loop coroutine for each Qualcomm SoC.
  targets = [
      target_meta_loop(target, args.meta_poll_interval, loop)
      for target in META_TARGETS]

  # Use asyncio.gather() to submit all coroutines to the event loop as
  # recommended by @gvanrossum in the GitHub issue comments at
  # https://github.com/python/asyncio/issues/477#issuecomment-269038238
  loop.run_until_complete(asyncio.gather(*targets))


if __name__ == '__main__':
  main()

