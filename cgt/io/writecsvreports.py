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

    regions_array = []

    for index, region in enumerate(results.regions):
        regions_array.append([index,
                              region.top,
                              region.left,
                              region.bottom,
                              region.right,
                              region.start_frame,
                              region.end_frame])

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
    header = ("Region index", "Top", "Left", "Bottom", "Right", "Start frame", "End frame")
    save_array_cvs(project, title, header, regions_array)

    title = r"_project_lines.csv"
    header = ("Index", "Note", "Region Index")
    save_array_cvs(project, title, header, lines_array)

    title = r"_project_line_segments.csv"
    header = ["Frame", "Start x", "Start y", "End x", "End y", "Line Index"]
    save_array_cvs(project, title, header, line_segments_array)

    save_region_images(project)

def save_region_images(project):
    """
    save the images of the start and end frames of each region.

        Args:
            project (CGTProject): the project holding the results, must not be None
        Returns:
            None
        Throws:
            Error if a file cannot be opened
    """
    results = project["results"]

    if results is None or len(results.region_images) < 1:
        return

    path = pathlib.Path(project["proj_full_path"])
    path = path.joinpath("images")
    path.mkdir(parents=True, exist_ok=True)

    regions = results.regions
    images = results.region_images

    for i, start_end in enumerate(images):
        name_root = f"Region_{str(i)}"
        np.savez_compressed(path.joinpath(name_root), start=start_end[0], end=start_end[1])

        name = name_root + "_" + str(regions[i].start_frame) + ".png"
        image = nparray_to_qimage(start_end[0])
        image.save(str(path.joinpath(name)))

        name = name_root + "_" + str(regions[i].end_frame) + ".png"
        image = nparray_to_qimage(start_end[1])
        image.save(str(path.joinpath(name+".png")))

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
