# -*- coding: utf-8 -*-
## @package unittests
# run all unittest in the tests directory
#
# @copyright 2021 University of Leeds, Leeds, UK.
# @author j.h.pickering@leeds.ac.uk and j.leng@leeds.ac.uk
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
"""
# set up linting conditions
# pylint: disable = c-extension-no-member
# pylint: disable = import-error

import unittest
import argparse
import csv

def get_arguments():
    """
    get command line arguments
    """
    parser = argparse.ArgumentParser()

    parser.add_argument("-q",
                        "--quiet",
                        help="if set verbosity is low",
                        action="store_true")

    parser.add_argument("-c",
                        "--csv_file",
                        type=str,
                        required=False,
                        help="if used save list of results to csv file")

    return parser.parse_args()

def print_failures(results, writer):
    """
    print the failures from a results object to csv
        Args:
            results (TextTestResult): the object
            writer (csv.writer): output object
    """
    count = len(results.failures)
    row = ["Assert Failures", str(count)]
    writer.writerow(row)

    for item in results.failures:
        row = ["", item[0]]
        writer.writerow(row)

def print_errors(results, writer):
    """
    print the errors from a results object to csv
        Args:
            results (TextTestResult): the object
            writer (csv.writer): output object
    """
    count = len(results.errors)
    row = ["Errors (unexpected exceptions)", str(count)]
    writer.writerow(row)

    for item in results.errors:
        row = ["", item[0]]
        writer.writerow(row)

def save_results(results, file_name):
    """
    save unittest failures and errors from a results object to CSV file
        Args:
            results (TextTestResult): the object
    """
    with open(file_name, 'w') as out_file:
        print(f"save to {file_name}")
        writer = csv.writer(out_file, delimiter=',', lineterminator='\n')
        if results.wasSuccessful():
            output = ["No failures or errors"]
            writer.writerow(output)
            return

        print_errors(results, writer)
        print_failures(results, writer)

def append_results(results, file_name):
    """
    append integration test results to CSV file
        Args:
            results (TextTestResult): the object
    """
    with open(file_name, 'a') as out_file:
        writer = csv.writer(out_file, delimiter=',', lineterminator='\n')
        row = ["Integration Tests"]
        writer.writerow(row)

        for item in results:
            row = [str(item)]
            writer.writerow(row)

def run_unittests(args):
    """
    run the unit tests
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
    results = runner.run(suite)

    if args.csv_file:
        print("about to save")
        save_results(results, args.csv_file)

if __name__ == '__main__':
    run_unittests(get_arguments())
