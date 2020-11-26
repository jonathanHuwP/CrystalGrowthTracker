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
import os
import csv


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
    print("hello form save_csv_project")
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
    print("hello from save_csv_results")

    results = project["results"]

    print("results: ", results)

    if results is None:
        return

    regions_array = []

    for index, region in enumerate(results.regions):
        print("Region: ", index)
        regions_array.append([index,
                              region.top,
                              region.left,
                              region.bottom,
                              region.right,
                              region.start_frame,
                              region.end_frame])

    crystals_array = []
    lines_array = []
    for index, crystal in enumerate(results.crystals):

        _, region_index = results.get_region(index)

        print("Crystal {} is in region {}".format(index, region_index))
        print("The number of times measured is {}".format(crystal.number_of_frames_held))

        note = ""
        if crystal.notes is not None:
            note = crystal.notes

        crystals_array.append([index, region_index, note])

        for frame in crystal.list_of_frame_numbers:
            print("\tframe number {}".format(frame))

            faces = crystal.faces_in_frame(frame)

            for face in faces:
                lines_array.append([index,
                                    frame,
                                    face.label,
                                    face.start.x,
                                    face.start.y,
                                    face.end.x,
                                    face.end.y])

    save_csv_regions(project, regions_array)
    save_csv_crystals(project, crystals_array)
    save_csv_lines(project, lines_array)




def save_csv_regions(info, regions_array):
    '''Creates the csv report file for regions.

        Args:
            info (dict): A python dictionary containing a collection of useful parameters
                         such as the filenames and paths.
            regions_array (array): Regions data in a format that is easy to write into a csv file.

        Returns:
            None

        Throws:
            Error if file cannot be opened
    '''

    print("hello from save_csv_regions")

    results_dir = info["proj_full_path"]
    path = os.path.abspath(os.path.realpath(results_dir))


    csv_outfile_name = (path+r"/"+info["prog"]
                        +r"_"+info["proj_name"]+r"_project_regions.csv")

    header = ("Region index",
              "Top", "Left",
              "Bottom", "Right",
              "Start frame", "End frame")

    with open(csv_outfile_name, "w") as fout:
        writer = csv.writer(fout, delimiter=',', lineterminator='\n')
        writer.writerow(header)
        for row in regions_array:
            writer.writerow(row)




def save_csv_crystals(info, crystals_array):
    '''Creates the csv report file for crystals.

        Args:
            info (dict): A python dictionary containing a collection of useful parameters
                         such as the filenames and paths.
            crystals_array (list) a list of lists of output data

        Returns:
            None

        Throws:
            Error if file cannot be opened
    '''
    print("hello from save_csv_cystals")

    results_dir = info["proj_full_path"]

    path = os.path.abspath(os.path.realpath(results_dir))

    csv_outfile_name = (path+r"/"+info["prog"]
                        +r"_"+info["proj_name"]+r"_project_crystals.csv")

    header = ("Crystal index",
              "Region index",
              "Note")

    with open(csv_outfile_name, "w") as fout:
        writer = csv.writer(fout, delimiter=',', lineterminator='\n')
        writer.writerow(header)
        for row in crystals_array:
            print(row)
            writer.writerow(row)




def save_csv_lines(info, lines_array):
    '''Creates the csv report file for lines.

        Args:
            info (dict): A python dictionary containing a collection of useful parameters
                        such as the filenames and paths.
            lines_array (array): lines data as array of arrays of output data.

        Returns:
            None

        Throws:
            Error if file cannot be opened
    '''
    print("hello from save_csv_lines")

    results_dir = info["proj_full_path"]

    path = os.path.abspath(os.path.realpath(results_dir))

    csv_outfile_name = (path+r"/"+info["prog"]
                        +r"_"+info["proj_name"]+r"_project_lines.csv")

    header = ("Crystal index",
              "Frame number",
              "Line number",
              "x0",
              "y0",
              "x1",
              "y1")

    with open(csv_outfile_name, "w") as fout:
        writer = csv.writer(fout, delimiter=',', lineterminator='\n')
        writer.writerow(header)
        for row in lines_array:
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
    print("hello from save_csv_info")

    results_dir = info["proj_full_path"]

    path = os.path.abspath(os.path.realpath(results_dir))

    csv_outfile_name = (path+r"/"+info["prog"]
                        +r"_"+info["proj_name"]+r"_project_info.csv")

    with open(csv_outfile_name, "w") as fout:
        writer = csv.writer(fout, delimiter=',', lineterminator='\n')
        for key, value in info.items():
            writer.writerow([key, value])
