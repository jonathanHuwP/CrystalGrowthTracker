# -*- coding: utf-8 -*-
"""
Created on Sun 03 Oct 2021

Licensed under the Apache License, Version 2.0 (the "License"); you may not use
this file except in compliance with the License. You may obtain a copy of the
License at http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed
under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.

This work was funded by Joanna Leng's EPSRC funded RSE Fellowship (EP/R025819/1)

@copyright 2021
@author: j.h.pickering@leeds.ac.uk and j.leng@leeds.ac.uk
"""
# set up linting conditions
# pylint: disable = c-extension-no-member
# pylint: disable = import-error

import unittest
import argparse

def get_arguments():
    """
    get command line arguments
    """
    parser = argparse.ArgumentParser()

    parser.add_argument("-q",
                        "--quiet",
                        help="if set verbosity is low",
                        action="store_true")

    return parser.parse_args()

def run_tests(args):
    """
    run the tests
        Args:
            args (argparse.namespace): command line
    """
    loader = unittest.TestLoader()
    test_dir = './tests'
    suite = loader.discover(test_dir)

    verbosity = 2
    if args.quiet:
        verbosity = 1

    runner = unittest.TextTestRunner(verbosity=verbosity)
    runner.run(suite)

if __name__ == '__main__':
    run_tests(get_arguments())