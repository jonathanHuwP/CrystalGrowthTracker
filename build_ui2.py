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
from os import remove
from os.path import join, isfile
import argparse
import pathlib
from pathlib import Path 
from PyQt5 import uic
from PyQt5.uic import compileUiDir

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

#     parser.add_argument(
#         "-d",
#         "--directory",
#         help="Source directory",
#         required=True, type=str)
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

    # to make the pyuic5 command create relative path for the import functions it creates in the
    # compiled *_ui.py files it needs to be executed in the form source directory and in the form
    # pyuic5 some_file_view.ui -o ..\views\some_file_view_ui.py
    # The source and target can be strings as the command is executed as a string.
    command = "pyuic5 {} -o {}"
    print(command)
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
    list all compiled ui files (*_ui.py) in a directory

        Args:
            directory (string) the directory

        Returns:
            list of files in directory starting with Ui_
    """
    files = os.listdir(directory)
    return [f for f in files if f.endswith("_ui.py")]

def py_name(py_dir, py_file):
    """
    Local function to create the Python source file name for the compiled
    .ui file.
    
    @param py_dir suggested name of the directory (string)
    @param py_file suggested name for the compile source file (string)
    @return tuple of directory name (string) and source file name (string)
    """
    return py_dir, "Ui_{0}".format(py_file)

def main():
    """
    the top level function
    """
    args = get_args()


    cwd_start = os.getcwd()
    print("cwd_start: ", cwd_start)
    print("type(cwd_start: ", type(cwd_start))

    path = pathlib.Path(cwd_start)
    if not path.is_dir():
        print("Error {} is not a directory".format(path))
        return
    print("Path: {}".format(path))
    print("type(path): ", type(path))



    path_in = path.joinpath("cgt/resources")
    if not path_in.is_dir():
        print("Error {} is not a directory".format(path_in))
        return
    print("Resources Path: {}".format(path_in))
    print("type(path_in): ", type(path_in))


    path_out = path.joinpath("cgt/views")
    if not path_out.is_dir():
        print("Error {} is not a directory".format(path_out))
        return
    print("Views Path: {}".format(path_out))
    print("type(path_out): ", type(path_out))

    os.chdir("cgt/resources")
    #cwd_resources = os.getcwd()
    #print("cwd_resources: ", cwd_resources)
#     os.chdir(cwd_start)
#     os.chdir("cgt/views")
#     cwd_views = os.getcwd()
#     print("cwd_views: ", cwd_views)
# 
    if args.clean:
        files_to_remove = list_compiled_ui_files(path_in)
        print("{} files to be removed".format(len(files_to_remove)))
        #files_to_process = list_compiled_ui_files(cwd_resources)
        #print("{} files to be processed".format(len(files_to_process)))
        for file in files_to_remove:
            target = path_out.joinpath(file)
            print("\t{}".format(target))
            target.unlink()

    target_dir = "cgt/views"
    init_fname = "__init__.py"
    files_to_process = list_ui_files(path_in)
    print("{} files to be compiled:".format(len(files_to_process)))
    view_relative_path = "../views"
    for file in files_to_process:
        print("file: ", file)
        print("type(file) ", type(file))
        if file != init_fname and isfile(join(target_dir, file)):
            remove(join(target_dir, file))

    #compileUiDir(path_in, map=lambda dir, fname: (path_in, fname), from_imports=True)
    #compileUiDir(path_in, recurse=True, py_name(path_in, "ui_{0}".format(py_file))
    compileUiDir(path_in, recurse=True)

#         target_file = file.rsplit('.', 1)[0]
#         target_file += "_ui.py" 
#         target = view_relative_path+'\\'+target_file
#         print("target: ", target)
# 
#         command = r"pyuic5 -d --resource-suffix=cgt.views "+file+r" -o ..\views\\"+target_file
#         print("command: ", command)
#         os.system(command)

if __name__ == "__main__":
    main()
