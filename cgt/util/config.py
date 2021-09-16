## -*- coding: utf-8 -*-
"""
Created on Wed Sept 56 2021

This module contains the top level graphical user interface for measuring the
growth rates of crystals observed in videos taken using an X-ray synchrotron source

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
import pathlib

## use logging for debug purposes
use_logs = False

## save ffmpeg logs to file
use_ffmpeg_log = False

## a global log file
_log_file = None

def stop_logging():
    global _log_file
    if _log_file is not None:
        _log_file.close()
        _log_file = None

def start_logging():
    global _log_file
    path = pathlib.Path("cgt_log.txt")
    if path.exists():
        path.unlink()
    _log_file = open(str(path), 'a')

def log(text):
    global _log_file
    if _log_file is not None:
        _log_file.write(text+'\n')
