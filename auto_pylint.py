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
                            check=True)
    output = str(result.stdout.decode('utf-8'))#.splitlines()
    return json.loads(output)

def analyse_output(file, results):
    """
    analyse the lint output
        Args:
            file (pathlib.Path) the file
            results ([dict]) results in JSON format
        Returns:
            (LintResult)
    """
    num_issues = len(results)

    if num_issues == 0:
        print(f"File {file} no problems")
        return

    print(f"File: {file}\n========")
    for issue in results:
        print(f"\t{issue['line']} => {issue['message']}")

def main():
    """The main function"""
    path = pathlib.Path('.')
    files =[x for x in path.glob("**/*.py") if not x.name.startswith("Ui_")]
    linting_list = pylint_files(files)

    for file, results in linting_list.items():
        analyse_output(file, results)

if __name__ == "__main__":
    main()
