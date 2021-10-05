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
import operator
import itertools
import numpy as np

import PyQt5.QtCore as qc
import PyQt5.QtWidgets as qw

from cgt.util.framestats import FrameStats, VideoIntensityStats
from cgt.util.markers import(get_region,
                             get_frame)
from cgt.util.scenegraphitems import (list_to_g_point,
                                      list_to_g_line)

def read_csv_project(results_dir, new_project, pens):
    '''Coordinates the reading of a selection of csv reports.
    Args:
        results_dir (str): name of results directory
        new_project (CGTProject):  An empty project data structure.
        pens (PenStore): the current set of pens
    Throws:
        IOException if error reading files
    '''
    results_path = pathlib.Path(results_dir)
    files = [x for x in results_path.iterdir() if x.is_file()]

    if len(files) < 1:
        raise IOError(f"Directory {results_path} contains no files.")

    read_csv_info(new_project, files, results_path)

    old_signal_state = new_project["results"].blockSignals(True)
    read_csv_video_statistics(new_project, files, results_path)

    if read_csv_regions(new_project, files, results_path):
        read_csv_points(new_project, files, results_path, pens)
        read_csv_lines(new_project, files, results_path, pens)
        extract_key_frames(new_project["results"])
    new_project["results"].blockSignals(old_signal_state)

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

    if new_project["stats_from_enhanced"] == "True":
        new_project["stats_from_enhanced"] = True
    else:
        new_project["stats_from_enhanced"] = False


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
        for item in [0] + row[2:]:
            if bin is not None:
                bins.append(np.float64(item))

        stats = VideoIntensityStats(bins)

        for row in reader:
            mean = np.float64(row.pop(0))
            std_dev = np.float64(row.pop(0))
            bin_counts = [np.float64(i) for i in row]
            stats.append_frame(FrameStats(mean, std_dev, bin_counts))

    tmp = new_project["results"]
    new_project["results"].set_video_statistics(stats)

def read_csv_regions(new_project, files, path):
    """
    read the video regions, if it exists
        Args:
            new_project (CGTProject): the project object
            files ([pathlib.Path]): list of files in directory
            path (pathlib.Path): the working directory
        Returns:
            True if regions found and read
        Throws:
            IOException if error reading file
    """
    tmp = [x for x in files if str(x).endswith("regions.csv")]
    flag = False

    if len(tmp) < 1:
        return flag

    if len(tmp) > 1:
        raise IOError(f"Directory {path} has more than one regions.csv file.")

    with tmp[0].open('r') as file_in:
        reader = csv.reader(file_in)
        next(reader) # remove headers
        for row in reader:
            tmp = [float(x) for x in row]
            rect = qc.QRectF(tmp[1], tmp[2], tmp[3], tmp[4])
            new_project["results"].add_region(qw.QGraphicsRectItem(rect))
            if not flag:
                flag = True

    return flag

def read_csv_points(new_project, files, path, pens):
    """
    read the points file, if it exists
        Args:
            new_project (CGTProject): the project object
            files ([pathlib.Path]): list of files in directory
            path (pathlib.Path): the working directory
        Throws:
            IOException if error reading file
    """
    tmp = [x for x in files if str(x).endswith("points.csv")]

    if len(tmp) < 1:
        return

    if len(tmp) > 1:
        raise IOError(f"Directory {path} has more than one points.csv file.")

    rows = []
    with tmp[0].open('r') as file_in:
        reader = csv.reader(file_in)
        next(reader) # remove headers
        for row in reader:
            tmp = [int(row[0])]
            tmp += [float(x) for x in row[1:5]]
            tmp += [int(x) for x in row[5:]]
            rows.append(tmp)

    rows.sort(key=operator.itemgetter(6))

    for _, region_iterator in itertools.groupby(rows, operator.itemgetter(6)):
        region_group = [x for x in region_iterator]
        region_group.sort(key=operator.itemgetter(0))
        for _, point_iterator in itertools.groupby(region_group, operator.itemgetter(0)):
            point_group = [x for x in point_iterator]
            point_group.sort(key=operator.itemgetter(5))
            g_marker = []
            for row in point_group:
                g_marker.append(list_to_g_point(row, pens.get_display_pen()))

            new_project["results"].insert_point_marker(g_marker)

def read_csv_lines(new_project, files, path, pens):
    """
    read the lines file, if it exists
        Args:
            new_project (CGTProject): the project object
            files ([pathlib.Path]): list of files in directory
            path (pathlib.Path): the working directory
            pens (PenStore): the current pens set
        Throws:
            IOException if error reading file
    """
    tmp = [x for x in files if str(x).endswith("lines.csv")]

    if len(tmp) < 1:
        return

    if len(tmp) > 1:
        raise IOError(f"Directory {path} has more than one regions.csv file.")

    with tmp[0].open('r') as file_in:
        reader = csv.reader(file_in)
        next(reader) # remove headers
        rows = []
        for row in reader:
            tmp = [int(row[0])]
            tmp += [float(x) for x in row[1:7]]
            tmp += [int(x) for x in row[7:]]
            rows.append(tmp)

    rows.sort(key=operator.itemgetter(8))

    for _, region_iterator in itertools.groupby(rows, operator.itemgetter(8)):
        region_group = [x for x in region_iterator]
        region_group.sort(key=operator.itemgetter(0))
        for _, line_iterator in itertools.groupby(region_group, operator.itemgetter(0)):
            line_group = [x for x in line_iterator]
            line_group.sort(key=operator.itemgetter(7))
            g_marker = []
            for row in line_group:
                g_marker.append(list_to_g_line(row, pens.get_display_pen()))

            new_project["results"].insert_line_marker(g_marker)

def extract_key_frames(results):
    """
    fill the region to key-frame map from the lines
        Args:
            results (VideoAnalysisResultsStore) the results object
    """

    frames = []

    for line_set in results.get_lines():
        for line in line_set:
            frames.append((get_region(line), get_frame(line)))

    for point_set in results.get_points():
        for point in point_set:
            frames.append((get_region(point), get_frame(point)))

    frames.sort(key=operator.itemgetter(0))

    for region, group in itertools.groupby(frames, operator.itemgetter(0)):
        tmp = list(group)
        tmp.sort(key=operator.itemgetter(1))
        for key_frame, _ in itertools.groupby(tmp, operator.itemgetter(1)):
            results.add_key_frame(region, key_frame)
