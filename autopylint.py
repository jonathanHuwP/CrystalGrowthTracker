# -*- coding: utf-8 -*-
## @package autopylint
# <PACKAGE DESCRIPTION>
#
# @copyright Jonathan Pickering and Joanna Leng, University of Leeds, Leeds, UK.
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
import csv
import stat
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

    parser.add_argument("-o",
                        "--out_file",
                        type=str,
                        required=False,
                        help="output csv file")

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

def analyse_output(results):
    """
    analyse the lint output
        Args:
            results ([dict]) results in JSON format
        Returns:
            PylintIssues: holding arrays of (line, description) pairs
    """
    num_issues = len(results)

    if num_issues == 0:
        return PylintIssues([], [], [], [])

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
        issues = analyse_output(results)
        if total_issues(issues) == 0:
            print(f"File {file} no issues.")
        else:
            issue_files.append((file, issues))
    if len(issue_files) > 0:
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

def check_file(file_name):
    """
    test if file: exists and is writable or can be created
        Args:
            file_name (str): the file name
        Returns:
            (pathlib.Path): the path or None if problems
    """
    if not file_name:
        return None

    path = pathlib.Path(file_name)

    # if file exists test if writable
    if path.exists() and path.is_file():
        handle = None
        try:
            handle = open(path, 'w')
        except PermissionError:
            return None
        finally:
            if handle:
                handle.close()

    # crate file with write permissions
    try:
        path.touch(stat.S_IWUSR)
    except PermissionError:
        return None

    return path

def write_results(out_file, linting_list, issue_type):
    """
    write the results to file
    """
    headers = ["File", "Issue Type", "Issue Count", "Line", "Message"]
    with out_file.open('w') as fout:
        writer = csv.writer(fout, delimiter=',', lineterminator='\n')
        writer.writerow(headers)
        for file, results in linting_list.items():
            array = [file]
            issues = analyse_output(results)
            writer.writerow(array)
            write_issues(writer, issues, issue_type)

def write_issues(writer, issues, issue_type=None):
    """
    write issues to csv file
        Args:
            wrirter (csv.writer): the output file writer
            issues (PylintIssues): container for the issues
            issue_type (str): if provided the only output this type
    """
    if issue_type == "error":
        write_errors(writer, issues)
    elif issue_type == "warning":
        write_warnings(writer, issues)
    elif issue_type == "refactor":
        write_refactoring(writer, issues)
    elif issue_type == "convention":
        write_conventions(writer, issues)
    else:
        write_errors(writer, issues)
        write_warnings(writer, issues)
        write_refactoring(writer, issues)
        write_conventions(writer, issues)

def write_errors(writer, issues):
    """
    write errors to csv file
        Args:
            wrirter (csv.writer): the output file writer
            issues (PylintIssues): container for the issues
    """
    array = ["", "Errors", f"{len(issues.error)}"]
    writer.writerow(array)
    for line, message in issues.error:
        array = ["", "", "", line, message]
        writer.writerow(array)

def write_warnings(writer, issues):
    """
    write warnings to csv file
        Args:
            wrirter (csv.writer): the output file writer
            issues (PylintIssues): container for the issues
    """
    array = ["", "Warnings", f"{len(issues.warning)}"]
    writer.writerow(array)
    for line, message in issues.warning:
        array = ["", "", "", line, message]
        writer.writerow(array)

def write_refactoring(writer, issues):
    """
    write refactoring to csv file
        Args:
            wrirter (csv.writer): the output file writer
            issues (PylintIssues): container for the issues
    """
    array = ["", "Refactoring", f"{len(issues.refactor)}"]
    writer.writerow(array)
    for line, message in issues.refactor:
        array = ["", "", "", line, message]
        writer.writerow(array)

def write_conventions(writer, issues):
    """
    write conventions to csv file
        Args:
            wrirter (csv.writer): the output file writer
            issues (PylintIssues): container for the issues
    """
    array = ["", "Convention", f"{len(issues.convention)}"]
    writer.writerow(array)
    for line, message in issues.convention:
        array = ["", "", "", line, message]
        writer.writerow(array)

def display_results(linting_list, issue_type):
    """
    display the results
    """
    if issue_type is not None:
        display_type(issue_type, linting_list)
    else:
        display_all(linting_list)

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

    out_file = None
    if args.out_file:
        out_file = check_file(args.out_file)
        if not out_file:
            print(f"File {args.out_file} cannot: be created, or opened for writing")
            return

    linting_list = pylint_files(files)

    if out_file:
        write_results(out_file, linting_list, args.type)
    else:
        display_results(linting_list, args.type)

if __name__ == "__main__":
    main()
