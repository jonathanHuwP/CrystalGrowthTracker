## -*- coding: utf-8 -*-
"""
Created on Tue 27 Oct 2020

A utility for batch running pyuic to construct the Ui_*.py classes from the *.ui
files produced by Qt Designer.

Licensed under the Apache License, Version 2.0 (the "License"); you may not use
this file except in compliance with the License. You may obtain a copy of the
License at http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed
under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.

This work was funded by Joanna Leng's EPSRC funded RSE Fellowship (EP/R025819/1)

@copyright 2020
@author: j.h.pickering@leeds.ac.uk and j.leng@leeds.ac.uk
"""

import os
import argparse
import pathlib

# a list of the modules that the package requires
ROOT_FILE_NAMES = ["crystaldrawingwidget",
                   "CrystalGrowthTrackerMain",
                   "DrawingLabelTestHarness",
                   "editnotesdialog",
                   "projectpropertieswidget",
                   "projectstartdialog",
                   "regionselectionwidget",
                   "reportviewwidget",
                   "resultstreewidget",
                   "videocontrolwidget",
                   "VideoOverviewWindow",
                   "videoparametersdialog",
                   "video_demonstration"]

# relative path to the Qt .ui files
UI_PATH = "./resources/designer_ui/{}.ui"

# relative path to the python source files
PY_PATH = "./cgt/Ui_{}.py"

def get_args():
    """
    set up and get the command line arguments
        Returns
            namespace of arguments
    """
    text = """
           Automate the construction of Ui_*.py files from Qt Designer's *.ui files.
           If run without command line options it will build all files.
           If run with -f option it will build only one file.
           """
    parser = argparse.ArgumentParser(prog='build_ui', description = text)

    parser.add_argument("-f",
                        "--file_name_root",
                        help="the file name without postfix ",
                        required=False,
                        type=str)

    return parser.parse_args()

def build(file_name_root):
    """
    run pyuic5 on a single file

        Args:
            file_name_root (string) the module name with no decoration or postfix
    """
    ui_file = pathlib.Path(UI_PATH.format(file_name_root))
    py_file = pathlib.Path(PY_PATH.format(file_name_root))

    # in the case of failure CPython will print its own error message
    if os.system(f"pyuic5 {ui_file} -o {py_file}") == 0:
        print(f"made {py_file}")

if __name__ == "__main__":
    args = get_args()

    if args.file_name_root:
        build(args.file_name_root)
    else:
        for file in ROOT_FILE_NAMES:
            build(file)
