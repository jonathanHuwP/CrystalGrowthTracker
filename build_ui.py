# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
"""
Created on Wednesday Sept 30 2020

module results provides storage classes for CGT results.
IO and analysis are provided seperatly.

Licensed under the Apache License, Version 2.0 (the "License"); you may not use
this file except in compliance with the License. You may obtain a copy of the
License at
http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed
under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.

@copyright 2020
@author: j.h.pickering@leeds.ac.uk
"""
import os
import argparse
import pathlib

def get_args():
    """
    set up and get the command line arguments

        Returns
            namespace of arguments
    """
    parser = argparse.ArgumentParser(
        prog='build_ui',
        epilog="""Script for automating the compilation of Qt 
        user interfaces created with QDesigner""")

    parser.add_argument(
        "-d",
        "--directory",
        help="Source directory",
        required=True, type=str)
    parser.add_argument(
        "-c",
        "--clean",
        help="Remove existing Ui files",
        action='store_true')

    return parser.parse_args()

def compile_user_interface(ui_file, py_file):
    """
    convert a qdesigner ui file to a python file

        Args:
            ui_file (pathlib.Path) the full path to the ui file
            py_file (pathlib.Path) the full path to the python file

        Returns:
            None
    """
    command = "pyuic5 {} -o {}"
    os.system(command.format(ui_file, py_file))

def list_ui_files(directory):
    """
    list all ui files in a directory

        Args:
            directory (string) the directory

        Returns:
            list of files in directory ending in .ui
    """
    files = os.listdir(directory)
    return [f for f in files if f.endswith(".ui")]

def list_compiled_ui_files(directory):
    """
    list all compiled ui files (Ui_*) in a directory

        Args:
            directory (string) the directory

        Returns:
            list of files in directory starting with Ui_
    """
    files = os.listdir(directory)
    return [f for f in files if f.startswith("Ui_")]

def main():
    """
    the top level function
    """
    args = get_args()

    path = pathlib.Path(args.directory)
    if not path.is_dir():
        print("Error {} is not a directory".format(path))
        return
    print("Path: {}".format(path))

    if args.clean:
        files = list_compiled_ui_files(path)
        print("{} files to be removed".format(len(files)))
        for file in files:
            target = path.joinpath(file)
            print("\t{}".format(target))
            target.unlink()

    files = list_ui_files(path)
    print("{} files to be compiled:".format(len(files)))
    for file in files:
        source = path.joinpath(file)
        file = file.rsplit('.', 1)[0]
        file += ".py"
        file = "Ui_" + file
        target = path.joinpath(file)
        print("\t{} => {}".format(source, target))
        compile_user_interface(source, target)

if __name__ == "__main__":
    main()
