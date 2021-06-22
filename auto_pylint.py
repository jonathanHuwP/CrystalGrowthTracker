import subprocess
import pathlib
import json
from collections import namedtuple

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
    import sys
    result = subprocess.run(['pylint', '-f', 'json', file_name], stdout=subprocess.PIPE)
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


if __name__ == "__main__":
    p = pathlib.Path('.')
    files =[x for x in p.glob("**/*.py") if not x.name.startswith("Ui_")]
    linting = pylint_files(files)

    for file, results in linting.items():
        analyse_output(file, results)
