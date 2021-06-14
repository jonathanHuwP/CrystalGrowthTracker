'''
writecsvreports.py

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
import pathlib
import csv
import numpy as np

from cgt.util.utils import nparray_to_qimage

def save_csv_project(project):
    """
    save a project as a selection of csv reports.
        Args:
            project (CGTProject) the project to be saved
        Returns:
            None
        Throws:
            Error if a file cannot be opened
    """
    if project is None:
        return

    save_csv_results(project)
    save_csv_info(project)

def save_csv_results(project):
    '''
    Save the results, if any, from a project.
        Args:
            project (CGTProject): the project holding the results, must not be None
        Returns:
            None
        Throws:
            Error if a file cannot be opened
    '''
    results = project["results"]

    if results is None:
        return

    if results.video_statistics is not None:
        save_csv_video_statistics(project, results.video_statistics)

    save_csv_growth_rates(project, results)

def save_csv_video_statistics(project, stats):
    """
    save the video statistics
        Args:
            project (CGTProject)
            stats (VideoIntensityStats)
    """
    path = pathlib.Path(project["proj_full_path"])
    csv_outfile_name = project["prog"] + r"_" + project["proj_name"] + r"_video_statistics.csv"

    with open(path.joinpath(csv_outfile_name), "w") as fout:
        writer = csv.writer(fout, delimiter=',', lineterminator='\n')
        writer.writerow(stats.bins)
        for item in stats.frames:
            array = []
            array.append(item.mean)
            array.append(item.std_deviation)
            array.extend(item.bin_counts)
            writer.writerow(array)

def save_csv_growth_rates(project, results):
    """
    save everything except the video statistics
        Args:
            results (VideoAnalysisResultsStore)
    """
    regions_array = []

    for index, region_graph_item in enumerate(results.regions):
        region = region_graph_item.rect()
        regions_array.append([index,
                              region.top(),
                              region.left(),
                              region.bottom(),
                              region.right()])

    lines_array = []
    line_segments_array = []
    line_to_region = results.region_lines_association

    for index, line in enumerate(results.lines):
        region_index = line_to_region.get_region(index)
        lines_array.append([index, line.note, region_index])
        keys = line.frame_numbers
        for key in keys:
            segment = line[key]
            line_segments_array.append([key,
                                        int(segment.start.x),
                                        int(segment.start.y),
                                        int(segment.end.x),
                                        int(segment.end.y),
                                        index])

    title = r"_project_regions.csv"
    header = ("Region index", "Top", "Left", "Bottom", "Right")
    save_array_cvs(project, title, header, regions_array)

    title = r"_project_lines.csv"
    header = ("Index", "Note", "Region Index")
    save_array_cvs(project, title, header, lines_array)

    title = r"_project_line_segments.csv"
    header = ["Frame", "Start x", "Start y", "End x", "End y", "Line Index"]
    save_array_cvs(project, title, header, line_segments_array)

def save_array_cvs(info, title, header, data_array):
    """
    writes an array into a commer seperated values files
        Args:
            info (CGTProject) the project object holding the paths
            title (string) the end of the file name
            header (array(string)) array of column headers
            data_array (array) the array to be written
    """
    path = pathlib.Path(info["proj_full_path"])
    csv_outfile_name = info["prog"] + r"_" + info["proj_name"] + title

    with open(path.joinpath(csv_outfile_name), "w") as fout:
        writer = csv.writer(fout, delimiter=',', lineterminator='\n')
        writer.writerow(header)
        for row in data_array:
            writer.writerow(row)

def save_csv_info(info):
    '''Creates the csv report file for info.

        Args:
            info (CGTProject) the project to be saved, must not be None

        Returns:
            None

        Throws:
            Error if file cannot be opened
    '''
    path = pathlib.Path(info["proj_full_path"])
    csv_outfile_name = info["prog"] + r"_" + info["proj_name"] + r"_project_info.csv"

    with open(path.joinpath(csv_outfile_name), "w") as fout:
        writer = csv.writer(fout, delimiter=',', lineterminator='\n')
        for key, value in info.items():
            writer.writerow([key, value])
