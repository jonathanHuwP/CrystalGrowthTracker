# -*- coding: utf-8 -*-
"""
Created on Fri 25 June 2021

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
import subprocess
import pathlib
import json
import argparse
from collections import namedtuple

## data type for results
PylintIssues = namedtuple("PylintIssues", ["error",
                                           "warning",
                                           "refactor",
                                           "convention"])

def total_issues(issues):
    """
    count total numbe of issues in a PylintIssues container
    """
    return len(issues.error) + len(issues.warning) + len(issues.refactor) + len(issues.convention)

def get_args():
    """
    get command line arguments
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-d",
                        "--directory",
                        type=str,
                        required=False,
                        help="directory to be searched")

    parser.add_argument("-f",
                        "--file",
                        type=str,
                        required=False,
                        help="target file")

    parser.add_argument("-t",
                        "--type",
                        type=str,
                        choices = ["error", "warning", "refactor", "convention"],
                        required=False,
                        help="Report only type: error, warning, refactor, convention")


    return parser.parse_args()

def pylint_files(file_list):
    """
    run pylint on the files in the list
        Args:
            file_list ([pathlib.Path])
        Returns:
            dictionary of outputs with file names as keys
    """
    linting = {}

    for file in file_list:
        print(f"linting {str(file)}")
        linting[file] = pylint_file(str(file))

    print("\n\n")
    return linting

def pylint_file(file_name):
    """
    run pylint on a single file
        Args:
            file_name (string)
        Returns:
            linting output ([string])
    """
    result = subprocess.run(['pylint', '-f', 'json', file_name],
                            stdout=subprocess.PIPE,
                            check=False)

    output = str(result.stdout.decode('utf-8'))
    return json.loads(output)

def analyse_output(file, results):
    """
    analyse the lint output
        Args:
            file (pathlib.Path) the file
            results ([dict]) results in JSON format
        Returns:
            PylintIssues: holding arrays of (line, description) pairs
    """
    num_issues = len(results)

    if num_issues == 0:
        print(f"File {file} no problems")
        return None

    return process_pylint_results(results)

def process_pylint_results(results):
    """
    process the results of pylint run on a file
        Args:
            results [dict]: list of the json results
        Returns:
            PylintIssues: holding arrays of (line, description) pairs
    """
    error = []
    warning = []
    refactor = []
    convention = []

    for issue in results:
        if issue["type"] == "convention":
            convention.append((issue['line'], issue['message']))
        elif issue["type"] == "refactor":
            refactor.append((issue['line'], issue['message']))
        elif issue["type"] == "warning":
            warning.append((issue['line'], issue['message']))
        elif issue["type"] == "error":
            error.append((issue['line'], issue['message']))

    return PylintIssues(error, warning, refactor, convention)

def print_issues(issue_files):
    """
    print a lint of all the file and issues
        Args:
            issue_files ([(file, PylintIssues)])
    """
    if issue_files:
        for (file, issues) in issue_files:
            print(f"File {file}: {total_issues(issues)} issues")

            print(f"    {len(issues.error)} Error")
            for (line, description) in issues.error:
                print(f"        Line {line}: {description}")

            print(f"    {len(issues.warning)} Warning")
            for (line, description) in issues.warning:
                print(f"        Line {line}: {description}")

            print(f"    {len(issues.refactor)} Refactor")
            for (line, description) in issues.refactor:
                print(f"        Line {line}: {description}")

            print(f"    {len(issues.convention)} Convention")
            for (line, description) in issues.convention:
                print(f"        Line {line}: {description}")

def display_all(linting_list):
    """
    print all issues found in files in
        Args:
            linting_list ([(pathlib.Path, PylintIssues)])
    """
    issue_files = []
    for file, results in linting_list.items():
        issues = analyse_output(file, results)
        if issues  is not None:
            issue_files.append((file, issues))
        print_issues(issue_files)

def filter_output(issue_type, results):
    """
    filter issues of a give type
    """
    if not results:
        return None

    issues = []
    for issue in results:
        if issue["type"] == issue_type:
            issues.append((issue['line'], issue['message']))

    return issues

def print_issues_type(issue_type, issue_files):
    """
    print issues of given type
        Args:
            issue_type (string): the type
            issue_files ([(file, PylintIssues)])
    """
    if issue_files:
        for (file, issues) in issue_files:
            if issues is not None and issues:
                print(f"File {file}: {len(issues)} of type {issue_type}")
                for (line, description) in issues:
                    print(f"    Line {line}: {description}")

def display_type(issue_type, linting_list):
    """
    display issues of specific type
        Args:
            issue_type (string): the issue type class
            linting_list ([(pathlib.Path, PylintIssues)])
    """
    issue_files = []
    for file, results in linting_list.items():
        issues = filter_output(issue_type, results)
        issue_files.append((file, issues))

    print_issues_type(issue_type, issue_files)

def main():
    """
    The main function
    """
    args = get_args()

    files = None
    if args.file is not None:
        path = pathlib.Path(args.file)
        files = [path]
    elif args.directory is not None:
        path = pathlib.Path(args.directory)
        files =[x for x in path.glob("**/*.py") if not x.name.startswith("Ui_")]
    else:
        path =  pathlib.Path('.')
        files =[x for x in path.glob("**/*.py") if not x.name.startswith("Ui_")]

    linting_list = pylint_files(files)

    if args.type is not None:
        display_type(args.type, linting_list)
    else:
        display_all(linting_list)

if __name__ == "__main__":
    main()
