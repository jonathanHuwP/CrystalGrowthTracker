## -*- coding: utf-8 -*-
'''
writecsvreports.py

This python module contains functions that create reports in comma seperated values
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

from cgt.util.utils import (rect_to_tuple,
                            g_point_to_tuple,
                            g_line_to_tuple)

def save_csv_project(project):
    """
    save a project as a selection of csv reports.
        Args:
            project (CGTProject) the project to be saved
        Returns:
            None
        Throws:
            IOException if a file cannot be opened
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
            IOException if a file cannot be opened
    '''
    results = project["results"]

    if results is None:
        return

    if results.get_video_statistics() is not None:
        save_csv_video_statistics(project, results.get_video_statistics())

    save_csv_growth_rates(project)

def save_csv_video_statistics(project, stats):
    """
    save the video statistics
        Args:
            project (CGTProject)
            stats (VideoIntensityStats)
        Throws:
            IOException if file cannot be opened
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

def save_csv_growth_rates(project):
    """
    save everything except the video statistics
        Args:
            project (CGTProject) the project object
        Throws:
            IOException if file cannot be opened
    """
    save_csv_regions(project)
    save_csv_lines(project)
    save_csv_points(project)

def save_csv_info(info):
    '''Creates the csv report file for info.
        Args:
            info (CGTProject) the project to be saved, must not be None
        Throws:
            IOException if file cannot be opened
    '''
    path = pathlib.Path(info["proj_full_path"])
    csv_outfile_name = info["prog"] + r"_" + info["proj_name"] + r"_project_info.csv"

    with open(path.joinpath(csv_outfile_name), "w") as fout:
        writer = csv.writer(fout, delimiter=',', lineterminator='\n')
        for key, value in info.items():
            writer.writerow([key, value])

def save_csv_regions(project):
    """
    print regions to csv
        Args:
            project (CGTProject) the project object
        Throws:
            IOException if file cannot be opened
    """
    path = pathlib.Path(project["proj_full_path"])
    csv_outfile_name = project["prog"] + r"_" + project["proj_name"] + r"_regions.csv"
    results = project["results"]

    headers = ["ID", "Left", "Top", "Width", "Height"]
    with open(path.joinpath(csv_outfile_name), 'w') as fout:
        writer = csv.writer(fout, delimiter=',', lineterminator='\n')
        writer.writerow(headers)

        for i, region in enumerate(results.get_regions()):
            region_data = rect_to_tuple(region.rect())
            region_data = [i] + region_data
            writer.writerow(region_data)

def save_csv_points(project):
    """
    print out points to csv file
        Args:
            project (CGTProject) the project object
        Throws:
            IOException if file cannot be opened
    """
    path = pathlib.Path(project["proj_full_path"])
    csv_outfile_name = project["prog"] + r"_" + project["proj_name"] + r"_points.csv"
    results = project["results"]

    headers = ["ID", "x", "y", "pos_x", "pos_y", "frame", "region"]
    with open(path.joinpath(csv_outfile_name), 'w') as fout:
        writer = csv.writer(fout, delimiter=',', lineterminator='\n')
        writer.writerow(headers)

        for i, points_array in enumerate(results.get_points()):
            for point in points_array:
                point_data = g_point_to_tuple(point)
                point_data = [i] + point_data

                writer.writerow(point_data)

def save_csv_lines(project):
    """
    print out the lines to csv file
        Args:
            project (CGTProject) the project object
        Throws:
            IOException if file cannot be opened
    """
    path = pathlib.Path(project["proj_full_path"])
    csv_outfile_name = project["prog"] + r"_" + project["proj_name"] + r"_lines.csv"
    results = project["results"]

    headers = ["ID", "x1", "y1", "x2", "y2", "pos_x", "pos_y", "frame", "region"]
    with open(path.joinpath(csv_outfile_name), 'w') as fout:
        writer = csv.writer(fout, delimiter=',', lineterminator='\n')
        writer.writerow(headers)

        for i, line_array in enumerate(results.get_lines()):
            for line in line_array:
                line_data = g_line_to_tuple(line)
                line_data = [i] + line_data

                writer.writerow(line_data)
