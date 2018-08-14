# python3

"""Tests for meta_monitor."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import asyncio
import unittest

import meta_monitor


class _MockProcess():

  def __init__(self, returncode, stdout, stderr):
    self.returncode = returncode
    self.stdout = stdout
    self.stderr = stderr

  async def wait(self):
    return self.returncode

  async def communicate(self):
    return self.stdout, self.stderr


def _MakeMockCommand(returncode, stdout, stderr):
  """Construct a coroutine to return a MockProcess.

  Args:
    returncode: Value to return from the wait() function.
    stdout: Byte array to return for stdout from the communicate() function.
    stderr: Byte array to return for stderr from the communicate() function.
  Returns:
    A coroutine that creates a MockProcess instance.
  """
  async def _GetMockProcess(*args, cwd):
    return _MockProcess(returncode, stdout, stderr)
  return _GetMockProcess


class MetaMonitorTest(unittest.TestCase):

  def testFetchGitTagsSuccess(self):
    git_tags = (
        'f5f1746d5d872753920bf4056d50566b3d348f50\trefs/tags/r1.0.1_00001.0\n'
        '1777e58a70490ab5b572316c8dc777f37e280b89\trefs/tags/r1.0.1_00002.0\n'
        'f06fe78f489b70ba93087709a5ea9a0a51771006\trefs/tags/r1.0.1_00003.0\n'
        '647ea03b0ab84d01118499af59c7dc1e4507d2b8\trefs/tags/r1.0.1_00003.0.1\n'
        '55e123518f8c13bd4e90674f610f86c796ee6518\trefs/tags/r1.0.1_00004.0\n')

    expected_tags = [
        'r1.0.1_00001.0',
        'r1.0.1_00002.0',
        'r1.0.1_00003.0',
        'r1.0.1_00003.0.1',
        'r1.0.1_00004.0']

    tags = asyncio.get_event_loop().run_until_complete(
        meta_monitor.fetch_target_meta_tags(
            'snapdragon-high-mid-2018-spf-1-0-1',
            git_cmd=_MakeMockCommand(0, git_tags.encode(), ''.encode())))
    self.assertEqual(tags, expected_tags)

if __name__ == '__main__':
  unittest.main()
