#!/usr/bin/env python
# Copyright (c) 2012 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

'''Unit tests for the 'grit build' tool.
'''

import codecs
import os
import sys
import tempfile
if __name__ == '__main__':
  sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

import unittest

from grit import util
from grit.tool import build


class BuildUnittest(unittest.TestCase):

  def testFindTranslationsWithSubstitutions(self):
    # This is a regression test; we had a bug where GRIT would fail to find
    # messages with substitutions e.g. "Hello [IDS_USER]" where IDS_USER is
    # another <message>.
    output_dir = tempfile.mkdtemp()
    builder = build.RcBuilder()
    class DummyOpts(object):
      def __init__(self):
        self.input = util.PathFromRoot('grit/testdata/substitute.grd')
        self.verbose = False
        self.extra_verbose = False
    builder.Run(DummyOpts(), ['-o', output_dir])

  def testGenerateDepFile(self):
    output_dir = tempfile.mkdtemp()
    builder = build.RcBuilder()
    class DummyOpts(object):
      def __init__(self):
        self.input = util.PathFromRoot('grit/testdata/substitute.grd')
        self.verbose = False
        self.extra_verbose = False
    expected_dep_file = os.path.join(output_dir, 'substitute.grd.d')
    builder.Run(DummyOpts(), ['-o', output_dir,
                              '--depdir', output_dir,
                              '--depfile', expected_dep_file])

    self.failUnless(os.path.isfile(expected_dep_file))
    with open(expected_dep_file) as f:
      line = f.readline()
      (dep_output_file, deps_string) = line.split(': ')
      deps = deps_string.split(' ')

      self.failUnlessEqual("resource.h", dep_output_file)
      self.failUnlessEqual(1, len(deps))
      self.failUnlessEqual(deps[0],
          util.PathFromRoot('grit/testdata/substitute.xmb'))

  def testAssertOutputs(self):
    output_dir = tempfile.mkdtemp()
    class DummyOpts(object):
      def __init__(self):
        self.input = util.PathFromRoot('grit/testdata/substitute.grd')
        self.verbose = False
        self.extra_verbose = False

    # Incomplete output file list should fail.
    builder_fail = build.RcBuilder()
    self.failUnlessEqual(2,
        builder_fail.Run(DummyOpts(), [
            '-o', output_dir,
            '-a', os.path.abspath(
                os.path.join(output_dir, 'en_generated_resources.rc'))]))

    # Complete output file list should succeed.
    builder_ok = build.RcBuilder()
    self.failUnlessEqual(0,
        builder_ok.Run(DummyOpts(), [
            '-o', output_dir,
            '-a', os.path.abspath(
                os.path.join(output_dir, 'en_generated_resources.rc')),
            '-a', os.path.abspath(
                os.path.join(output_dir, 'sv_generated_resources.rc')),
            '-a', os.path.abspath(
                os.path.join(output_dir, 'resource.h'))]))

  def _verifyWhitelistedOutput(self,
                               filename,
                               whitelisted_ids,
                               non_whitelisted_ids,
                               encoding='utf8'):
    self.failUnless(os.path.exists(filename))
    whitelisted_ids_found = []
    non_whitelisted_ids_found = []
    with codecs.open(filename, encoding=encoding) as f:
      for line in f.readlines():
        for whitelisted_id in whitelisted_ids:
          if whitelisted_id in line:
            whitelisted_ids_found.append(whitelisted_id)
        for non_whitelisted_id in non_whitelisted_ids:
          if non_whitelisted_id in line:
            non_whitelisted_ids_found.append(non_whitelisted_id)
    self.longMessage = True
    self.assertEqual(whitelisted_ids,
                     whitelisted_ids_found,
                     '\nin file {}'.format(os.path.basename(filename)))
    non_whitelisted_msg = ('Non-Whitelisted IDs {} found in {}'
        .format(non_whitelisted_ids_found, os.path.basename(filename)))
    self.assertFalse(non_whitelisted_ids_found, non_whitelisted_msg)

  def testWhitelistStrings(self):
    output_dir = tempfile.mkdtemp()
    builder = build.RcBuilder()
    class DummyOpts(object):
      def __init__(self):
        self.input = util.PathFromRoot('grit/testdata/whitelist_strings.grd')
        self.verbose = False
        self.extra_verbose = False
    whitelist_file = util.PathFromRoot('grit/testdata/whitelist.txt')
    builder.Run(DummyOpts(), ['-o', output_dir,
                              '-w', whitelist_file])
    header = os.path.join(output_dir, 'whitelist_test_resources.h')
    rc = os.path.join(output_dir, 'en_whitelist_test_strings.rc')

    whitelisted_ids = ['IDS_MESSAGE_WHITELISTED']
    non_whitelisted_ids = ['IDS_MESSAGE_NOT_WHITELISTED']
    self._verifyWhitelistedOutput(
      header,
      whitelisted_ids,
      non_whitelisted_ids,
    )
    self._verifyWhitelistedOutput(
      rc,
      whitelisted_ids,
      non_whitelisted_ids,
      encoding='utf16'
    )

  def testWhitelistResources(self):
    output_dir = tempfile.mkdtemp()
    builder = build.RcBuilder()
    class DummyOpts(object):
      def __init__(self):
        self.input = util.PathFromRoot('grit/testdata/whitelist_resources.grd')
        self.verbose = False
        self.extra_verbose = False
    whitelist_file = util.PathFromRoot('grit/testdata/whitelist.txt')
    builder.Run(DummyOpts(), ['-o', output_dir,
                              '-w', whitelist_file])
    header = os.path.join(output_dir, 'whitelist_test_resources.h')
    map_cc = os.path.join(output_dir, 'whitelist_test_resources_map.cc')
    map_h = os.path.join(output_dir, 'whitelist_test_resources_map.h')
    pak = os.path.join(output_dir, 'whitelist_test_resources.pak')

    # Ensure the resource map header and .pak files exist, but don't verify
    # their content.
    self.failUnless(os.path.exists(map_h))
    self.failUnless(os.path.exists(pak))

    whitelisted_ids = [
        'IDR_STRUCTURE_WHITELISTED',
        'IDR_STRUCTURE_IN_TRUE_IF_WHITELISTED',
        'IDR_INCLUDE_WHITELISTED',
    ]
    non_whitelisted_ids = [
        'IDR_STRUCTURE_NOT_WHITELISTED',
        'IDR_STRUCTURE_IN_TRUE_IF_NOT_WHITELISTED',
        'IDR_STRUCTURE_IN_FALSE_IF_WHITELISTED',
        'IDR_STRUCTURE_IN_FALSE_IF_NOT_WHITELISTED',
        'IDR_INCLUDE_NOT_WHITELISTED',
    ]
    for output_file in (header, map_cc):
      self._verifyWhitelistedOutput(
        output_file,
        whitelisted_ids,
        non_whitelisted_ids,
      )

  def testOutputAllResourceDefinesTrue(self):
    output_dir = tempfile.mkdtemp()
    builder = build.RcBuilder()
    class DummyOpts(object):
      def __init__(self):
        self.input = util.PathFromRoot('grit/testdata/whitelist_resources.grd')
        self.verbose = False
        self.extra_verbose = False
    whitelist_file = util.PathFromRoot('grit/testdata/whitelist.txt')
    builder.Run(DummyOpts(), ['-o', output_dir,
                              '-w', whitelist_file,
                              '--output-all-resource-defines',])
    header = os.path.join(output_dir, 'whitelist_test_resources.h')
    map_cc = os.path.join(output_dir, 'whitelist_test_resources_map.cc')

    whitelisted_ids = [
        'IDR_STRUCTURE_WHITELISTED',
        'IDR_STRUCTURE_NOT_WHITELISTED',
        'IDR_STRUCTURE_IN_TRUE_IF_WHITELISTED',
        'IDR_STRUCTURE_IN_TRUE_IF_NOT_WHITELISTED',
        'IDR_STRUCTURE_IN_FALSE_IF_WHITELISTED',
        'IDR_STRUCTURE_IN_FALSE_IF_NOT_WHITELISTED',
        'IDR_INCLUDE_WHITELISTED',
        'IDR_INCLUDE_NOT_WHITELISTED',
    ]
    non_whitelisted_ids = []
    for output_file in (header, map_cc):
      self._verifyWhitelistedOutput(
        output_file,
        whitelisted_ids,
        non_whitelisted_ids,
      )

  def testOutputAllResourceDefinesFalse(self):
    output_dir = tempfile.mkdtemp()
    builder = build.RcBuilder()
    class DummyOpts(object):
      def __init__(self):
        self.input = util.PathFromRoot('grit/testdata/whitelist_resources.grd')
        self.verbose = False
        self.extra_verbose = False
    whitelist_file = util.PathFromRoot('grit/testdata/whitelist.txt')
    builder.Run(DummyOpts(), ['-o', output_dir,
                              '-w', whitelist_file,
                              '--no-output-all-resource-defines',])
    header = os.path.join(output_dir, 'whitelist_test_resources.h')
    map_cc = os.path.join(output_dir, 'whitelist_test_resources_map.cc')

    whitelisted_ids = [
        'IDR_STRUCTURE_WHITELISTED',
        'IDR_STRUCTURE_IN_TRUE_IF_WHITELISTED',
        'IDR_INCLUDE_WHITELISTED',
    ]
    non_whitelisted_ids = [
        'IDR_STRUCTURE_NOT_WHITELISTED',
        'IDR_STRUCTURE_IN_TRUE_IF_NOT_WHITELISTED',
        'IDR_STRUCTURE_IN_FALSE_IF_WHITELISTED',
        'IDR_STRUCTURE_IN_FALSE_IF_NOT_WHITELISTED',
        'IDR_INCLUDE_NOT_WHITELISTED',
    ]
    for output_file in (header, map_cc):
      self._verifyWhitelistedOutput(
        output_file,
        whitelisted_ids,
        non_whitelisted_ids,
      )


if __name__ == '__main__':
  unittest.main()
