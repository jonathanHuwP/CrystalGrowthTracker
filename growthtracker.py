## -*- coding: utf-8 -*-
"""
Created on Sunday 22 Nov 2020

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
import sys
import argparse

from cgt.cgt_app import CGTApp

def get_python_args():
    """
    set up to read project name from command line
        Returns:
            (string) the project name
    """
    parser = argparse.ArgumentParser()

    parser.add_argument("-p",
                        "--project",
                        type=str,
                        required=False,
                        help="project directory path")

    parser.add_argument("-f",
                        "--log_ffmpeg",
                        action='store_true',
                        help="if set write ffmpeg log files to file")

    args = parser.parse_args()
    return args

if __name__ == "__main__":
    application = CGTApp(sys.argv, get_python_args())
