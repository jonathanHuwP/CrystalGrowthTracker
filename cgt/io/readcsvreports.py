## -*- coding: utf-8 -*-
'''
readcsvreports.py

This python module contains functions that create reports in csv
format for the CrystalGrowthTracker application.

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
'''
# pylint: disable = no-name-in-module
# pylint: disable = too-many-locals
# pylint: disable = too-many-branches
# pylint: disable = c-extension-no-member

import csv
import pathlib
import numpy as np

import PyQt5.QtCore as qc
import PyQt5.QtWidgets as qw

from cgt.model.videoanalysisresultsstore import VideoAnalysisResultsStore
from cgt.util.framestats import FrameStats, VideoIntensityStats

def read_csv_project(results_dir, new_project):
    '''Coordinates the reading of a selection of csv reports.
    Args:
        results_dir (str): name of results directory
        new_project (CGTProject):  An empty project data structure.
    Throws:
        IOException if error reading files
    '''
    results_path = pathlib.Path(results_dir)
    files = [x for x in results_path.iterdir() if x.is_file()]
    if len(files) < 1:
        raise IOError(f"Directory {results_path} contains no files.")

    read_csv_info(new_project, files, results_path)

    new_project["results"] = VideoAnalysisResultsStore()
    read_csv_video_statistics(new_project, files, results_path)

    new_project.ensure_numeric()

def read_csv_info(new_project, files, path):
    """
    read the project information file.
        Args:
            new_project (CGTProject): the project object
            files ([pathlib.Path]): list of files in directory
            path (pathlib.Path): the working directory
        Throws:
            IOException if error reading file
    """
    tmp = [x for x in files if str(x).endswith("project_info.csv")]

    if len(tmp) < 1:
        raise FileNotFoundError(f"Directory {path} has no project_info.csv file.")

    if len(tmp) > 1:
        raise IOError(f"Directory {path} has more than one project_info.csv file.")

    with tmp[0].open('r') as file_in:
        reader = csv.reader(file_in)
        for row in reader:
            if len(row) == 2:
                key = row[0]
                value = row[1]
                if value == "":
                    new_project[key] = None
                else:
                    new_project[key] = value

def read_csv_video_statistics(new_project, files, path):
    """
    read the video statistics, if it exists
        Args:
            new_project (CGTProject): the project object
            files ([pathlib.Path]): list of files in directory
            path (pathlib.Path): the working directory
        Throws:
            IOException if error reading file
    """
    tmp = [x for x in files if str(x).endswith("video_statistics.csv")]

    if len(tmp) < 1:
        return

    if len(tmp) > 1:
        raise IOError(f"Directory {path} has more than one video_statistics.csv file.")

    with tmp[0].open('r') as file_in:
        reader = csv.reader(file_in)
        row = next(reader)
        bins = []
        for item in row:
            if bin is not None:
                bins.append(np.float64(item))

        stats = VideoIntensityStats(bins)

        for row in reader:
            mean = np.float64(row.pop(0))
            std_dev = np.float64(row.pop(0))
            bin_counts = [np.float64(i) for i in row]
            stats.append_frame(FrameStats(mean, std_dev, bin_counts))

    new_project["results"].set_video_statistics(stats)
