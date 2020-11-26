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
from pathlib import Path
import csv
from itertools import groupby

from cgt.model.videoanalysisresultsstore import VideoAnalysisResultsStore
from cgt.model.crystal import Crystal
from cgt.model.region import Region
from cgt.model.imagepoint import ImagePoint
from cgt.model.imagelinesegment import ImageLineSegment

def read_csv_project(results_dir, new_project):
    '''Coordinates the reading of a selection of csv reports.
    Args:
        results_dir (str): The directory name the user has selected to save the
                           results in i.e., the project directory.
        new_project:       An empty project data structure.
    Returns:
        error_code (int):  An error code is returned a 0 (zero) values means all
                           file were read while a 1 (one) value means 1 or more
                           files were not read.
    '''
    print("hello from read_csv_project")
    error_code = 0

    files = []
    dirpath = ""
    for (dirpath, _, filenames) in os.walk(results_dir):
        files.extend(filenames)
        break

    # check there is a project_info file
    if not any("project_info" in s for s in files):
        return 1

    error_crystal = 0
    error_line = 0
    error_region = 0
    error_info = 0

    #print("Files: {}".format(files))

    crystal_data = []
    line_data = []
    region_data = []

    for file in files:
        if file[-4:] == '.csv':
            if "project_crystals" in file:
                crystal_data, error_crystal = readcsv2listofdicts(file, dirpath)
            if "project_info" in file:
                error_info = readcsvinfo2dict(new_project, file, dirpath)
            if "project_lines" in file:
                line_data, error_line = readcsv2listofdicts(file, dirpath)
            if "project_regions" in file:
                region_data, error_region = readcsv2listofdicts(file, dirpath)

    if error_crystal or error_line or error_region or error_info == 1:
        error_code = 1

    if error_code == 0:
        store = VideoAnalysisResultsStore()
        storeregions(store, region_data)
        storecrystals(store, crystal_data, line_data)
        new_project["results"] = store
        print("new_project[results]: ", new_project["results"])

    return error_code




def readcsv2listofdicts(file, dirpath):
    '''Reads regions, crystals and lines csv reports created by the Crystal Growth Tracker
       as a list of dictionaries.
       This means varaibles are read with the header as a pair so can be for searched
       by its semantic meaning.
    Args:
        file (str):                  The directory name the user has selected to save the
                                     results in.
    Returns:
        data (list of dictionaries): A list of dictionaries where each item in the list is a row
                                     from the file read.
        error_code (int):            An error code is returned a 0 (zero) values means all file
                                     were read while a 1 (one) value means 1 or more files were
                                     not read.
    '''
    print("hello from readcsv2listofdicts")
    error_code = 0
    dir_in = Path(dirpath)
    file_to_open = dir_in / file
    print("Open file: ", file_to_open)

    data = []

    if not os.path.exists(file_to_open):
        print("ERROR; The input file does not exist.")
        return (1, None)
    print("file exists")

    try:
        with open(file_to_open, 'r') as file_in:
            reader = csv.DictReader(file_in)
            #column_names = reader.fieldnames
            #print(column_names)
            for row in reader:
                #print(row)
                #print(row['Crystal index'])
                data.append(row)
    except (IOError, OSError, EOFError) as exception:
        print(exception)
        error_code = 1
    finally:
        print("Read file: ", file)
        print("data: ", data)


    return (data, error_code)




def readcsvinfo2dict(new_project, file, dirpath):
    '''Reads the csv project info report created by the Crystal Growth Tracker as a list
       of dictionaries.
       This means varibles are read with the header as a pair so can be searched
       by its semantic meaning.
    Args:
        new_project ():        An empty project data structure.
        file (str):            The file name is given to reflect the contents of the file.
        dirpath (str):         The directory name the user has selected to save the
                               project in.
    Returns:
        data (list of dictionaries): A list of dictionaries where each item in the list is a row
                                     from the file read.
        error_code (int):  An error code is returned a 0 (zero) values means all file were read
                           while a 1 (one) value means 1 or more files were not read.
    '''
    print("hello from readcsvinfo2dict")
    error_code = 0
    dir_in = Path(dirpath)
    file_to_open = dir_in / file
    print("Open file: ", file_to_open)


    if not os.path.exists(file_to_open):
        print("ERROR; The input file does not exist.")
        return (1, None)
    print("file exists")

    try:
        with open(file_to_open, 'r') as file_in:
            reader = csv.reader(file_in)
            #column_names = reader.fieldnames
            #print(column_names)
            for row in reader:
                #print(row)
                #print(row['Crystal index'])
                if len(row) == 2:
                    key = row[0]
                    value = row[1]
                    new_project[key] = value
    except (IOError, OSError, EOFError) as exception:
        print(exception)
        error_code = 1
    finally:
        print("Read file: ", file)

    print("new_project: ", new_project)

    return error_code



def storeregions(store, regions_data):
    ''' Writes the regions_data list/array which is read in from a csv file created by the
        Crystal Growth Tracker to a results object.
    Args:
        store:    A results class object.
        regions_data (list of doctionaries): A list of dictionaries where each item in the list
                                            is a row from the file read.

    Returns:
        Nothing
    '''

    print("Hello from storeregions")

    for region in regions_data:
        #print("region: ", region)
        top = int(region["Top"])
        #print("top: ", top)
        #print("type(top): ", type(top))
        left = int(region["Left"])
        bottom = int(region["Bottom"])
        right = int(region["Right"])
        start_frame = int(region["Start frame"])
        end_frame = int(region["End frame"])
        store.add_region(Region(top, left, bottom, right, start_frame, end_frame))



def storecrystals(store, crystal_data, line_data):
    '''
        Writes the crystal_data and line_data dictionaries to a results object.
        Args:
            store (VideoAnalysisResultsStore) the results object to be filled
            crystal_data (list of doctionaries): A list of dictionaries where each item in the list
                                            is a row from the file read.
            line_data (list of doctionaries): A list of dictionaries where each item in the list
                                            is a row from the file read.

        Returns:
            None
    '''
    print("Hello from storecrystals")
    for crystal in crystal_data:
        crystal_index = int(crystal["Crystal index"])
        region_index = int(crystal["Region index"])

        temp_crystal = None
        if crystal["Note"] is not None and crystal["Note"] != "":
            temp_crystal = Crystal(notes=crystal["Note"])
        else:
            temp_crystal = Crystal()

        line_list = []
        frame_numbers = []
        for line in line_data:
            crystal_index_from_line = int(line["Crystal index"])
            if crystal_index == crystal_index_from_line:
                x0 = int(line["x0"])
                y0 = int(line["y0"])
                x1 = int(line["x1"])
                y1 = int(line["y1"])
                frame_number = int(line["Frame number"])
                line_number = line["Line number"]
                line = ImageLineSegment(ImagePoint(x0, y0),
                                        ImagePoint(x1, y1),
                                        line_number)
                line_list.append((line, frame_number))
                frame_numbers.append(frame_number)

        unique_frame_numbers = [i for i, j in groupby(frame_numbers)]

        for frame_number in unique_frame_numbers:
            lines = [item[0] for item in line_list if item[1]==frame_number]
            temp_crystal.add_faces(lines, frame_number)

        store.add_crystal(temp_crystal, region_index)
