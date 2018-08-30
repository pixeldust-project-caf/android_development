# python3

"""Entry point for Keystone META monitor.

Defines the entry point for the META monitor service. Provides a platform
dependent customization wrapper around the meta_monitor library. Useful for
encapsulating dependencies (ex: google.cloud.logging) that shouldn't
necessarily live in the meta_monitor library itself.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse
import asyncio
import google.cloud.logging

import meta_monitor

def main():
  # Parse command line flags.
  parser = argparse.ArgumentParser()
  parser.add_argument(
      '--meta_poll_interval',
      type=int,
      default=7200,
      help='Time between META poll attempts in seconds.')
  args = parser.parse_args()

  # Route logs to StackDriver. The Google Cloud logging library enables logs
  # for INFO level by default.
  # Taken from the "Setting up StackDriver Logging for Python" page at
  # https://cloud.google.com/logging/docs/setup/python
  client = google.cloud.logging.Client()
  client.setup_logging()

  # Create a top level working folder for clone and archive operations.
  work_dir = tempfile.mkdtemp()
  logging.info('Working folder is %s', work_dir)

  # Use actual subprocess commands in production.
  commands = meta_monitor.MetaMonitorCommands()

  # Create a polling loop coroutine for each Qualcomm SoC.
  loop = asyncio.get_event_loop()
  targets = [
      meta_monitor.target_meta_loop(
          commands, target, args.meta_poll_interval, work_dir, loop)
      for target in meta_monitor.META_TARGETS]

  # Use asyncio.gather() to submit all coroutines to the event loop as
  # recommended by @gvanrossum in the GitHub issue comments at
  # https://github.com/python/asyncio/issues/477#issuecomment-269038238
  loop.run_until_complete(asyncio.gather(*targets))


if __name__ == '__main__':
  main()
