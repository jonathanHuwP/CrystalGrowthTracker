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
import os
import csv
import numpy as np
from pathlib import Path
from itertools import groupby

from cgt.model.videoanalysisresultsstore import VideoAnalysisResultsStore
from cgt.model.line import Line
from cgt.model.region import Region
from cgt.model.imagepoint import ImagePoint
from cgt.model.imagelinesegment import ImageLineSegment

def read_csv_project(results_dir, new_project):
    '''Coordinates the reading of a selection of csv reports.
    Args:
        results_dir (str): name of results directory
        new_project (CGTProject):  An empty project data structure.
    Returns:
        None
    Throws:
        IOException if error reading files
    '''
    files = []
    dirpath = ""
    for (dirpath, _, filenames) in os.walk(results_dir):
        files.extend(filenames)
        break

    line_seg_data = []
    line_data = []
    region_data = []

    segments_flag = False
    info_flag = False
    lines_flag = False
    region_flag = False

    for file in files:
        if file.endswith('.csv'):
            if "project_line_segments" in file:
                line_seg_data = readcsv2listofdicts(file, dirpath)
                segments_flag = True
            elif "project_info" in file:
                readcsvinfo2dict(new_project, file, dirpath)
                info_flag = True
            elif "project_lines" in file:
                line_data = readcsv2listofdicts(file, dirpath)
                lines_flag = True
            elif "project_regions" in file:
                region_data = readcsv2listofdicts(file, dirpath)
                region_flag = True

    if not segments_flag:
        raise IOError(f"no project_line_segments file found in {dirpath}")
    if not region_flag:
        raise IOError(f"no project_regions file found in {dirpath}")
    if not lines_flag:
        raise IOError(f"no project_lines file found in {dirpath}")
    if not info_flag:
        raise IOError(f"no project_info file found in {dirpath}")

    store = VideoAnalysisResultsStore()
    store_regions(store, region_data, dirpath)
    store_lines(store, line_data, line_seg_data)
    new_project["results"] = store
    new_project.ensure_numeric()

def readcsv2listofdicts(file, dirpath):
    '''Reads regions, crystals and lines csv reports created by the Crystal Growth Tracker
       as a list of dictionaries.
       This means varaibles are read with the header as a pair so can be for searched
       by its semantic meaning.
            Args:
                file (str) directory name in which results are to be saved
            Returns:
                data (list(dictionary)) list each item of which is a one field dictionary
            Throws:
                IOError, OSError, EOFError if reaing error
    '''
    dir_in = Path(dirpath)
    file_to_open = dir_in / file

    data = []

    with open(file_to_open, 'r') as file_in:
        reader = csv.DictReader(file_in)
        for row in reader:
            data.append(row)

    return data

def readcsvinfo2dict(new_project, file, dirpath):
    '''
    Read a csv file holding project info as a dictionary, so varibles are
    read with the header as a pair so can be searched by its semantic meaning.
        Args:
            new_project (CGTProject):  An empty project data structure.
            file (str):                file name
            dirpath (str):             directory holding file
        Returns:
            None
        Throws
            IOError is problem reading file
    '''
    dir_in = Path(dirpath)
    file_to_open = dir_in / file

    with open(file_to_open, 'r') as file_in:
        reader = csv.reader(file_in)
        for row in reader:
            if len(row) == 2:
                key = row[0]
                value = row[1]
                new_project[key] = value

def store_regions(store, regions_data, dirpath):
    '''
    convert string lists to regions and adds them to a
    Crystal Growth Tracker to a results object.
        Args:
            store:    A results class object.
            regions_data ([dict]): list of dictionarys read in from csv
            dirpath (string) path to directory holding images directory
        Returns:
            None
    '''
    for i, region in enumerate(regions_data):
        top = int(region["Top"])
        left = int(region["Left"])
        bottom = int(region["Bottom"])
        right = int(region["Right"])
        start_frame = int(region["Start frame"])
        end_frame = int(region["End frame"])

        tmp_region = Region(top, left, bottom, right, start_frame, end_frame)
        start_end = read_argb_numpy_images(dirpath, i)

        store.add_region(tmp_region, start_end)

def read_argb_numpy_images(dirpath, i):
    """
    read the start end numpy images for region number i from directory.
        Args:
            dirpath (string) the full path to the directory.
            i (int) the array index of the region.
        Returns:
            a pair of numpy.images in ARGB (uint8) format
        Throws:
            FileNotFound
    """
    name = f"Region_{i}.npz"
    path = Path(dirpath)
    path = path.joinpath("images", name)

    tmp = np.load(path)
    start_end = (tmp["start"], tmp["end"])

    return start_end

def store_lines(store, lines, segments):
    """
    combine the lines and segments and store the
        Args:
            store (VideoAnalysisResultsStore) the results object to be filled
            lines ([[string]]) the data rows of the lines csv file
            segments ([[string]]) the data rows of the lines_segments csv file
    """
    for row in lines:
        note = row["Note"]
        region_index = int(row["Region Index"])

        line = Line(note)
        store.add_line(region_index, line)

    for row in segments:
        frame = int(row["Frame"])
        start_x = int(row["Start x"])
        start_y = int(row["Start y"])
        end_x = int(row["End x"])
        end_y = int(row["End y"])
        line_segment = ImageLineSegment(ImagePoint(start_x, start_y),
                                        ImagePoint(end_x, end_y))
        line_index = int(row["Line Index"])
        store.lines[line_index].add_line_segment(frame, line_segment)