'''
readcsvreports.py

This python module contains functions that create reports in csv
format for the CrystalGrowthTracker application.

Joanna Leng (an EPSRC funded Research Software Engineering Fellow (EP/R025819/1))
Jonathan Pickering (also funded on this fellowship)
University of Leeds
June 2020

Copyright 2020

Licensed under the Apache License, Version 2.0 (the "License"); you may not use
this file except in compliance with the License. You may obtain a copy of the
License at
http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed
under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
'''
import os
from pathlib import Path
import csv
from cgt.videoanalysisresultsstore import VideoAnalysisResultsStore
#import cgt.videoanalysisresultsstore as vas
from cgt.crystal import Crystal
from cgt.region import Region
from cgt.imagepoint import ImagePoint
from cgt.imagelinesegment import ImageLineSegment
from cgt.results_print_demo import make_test_result


def read_csv_project(dir, info):
    '''Coordinates the reading of a selection of csv reports.

    Args:
        results_dir (str): The directory name the user has selected to save the
                           results in.

    Returns:
        error_code (int):  An error code is returned a 0 (zero) values means all
                           file were read while a 1 (one) value means 1 or more
                           files were not read.
    '''
    print("hello from read_csv_reports")
    error_code = 0


    files = []
    dirpath = ""
    for (dirpath, dirnames, filenames) in os.walk(dir):
        files.extend(filenames)
        break


    error_crystal = 0
    error_line = 0
    error_region = 0
    print(files)
    crystal_data = []
    line_data = []
    region_data = []
    for file in files:
        if file[-4:] == '.csv':
            print(file)
            if "project_crystals" in file:
                print("Crystals!")
                crystal_data, error_crystal = readcsv2listofdicts(file, dirpath)
            if "project_info" in file:
                print("Info!")
                info_data, error_info = readcsvinfo2dict(file, dirpath)
            if "project_lines" in file:
                print("Lines!")
                line_data, error_line = readcsv2listofdicts(file, dirpath)
            if "project_regions" in file:
                print("Regions!")
                region_data, error_region = readcsv2listofdicts(file, dirpath)

    print("crystal_data: ", crystal_data)
    print("line_data: ", line_data)
    print("region_data: ", region_data)
    print("info_data: ", info_data)

    if error_crystal or error_line or error_region or error_info == 1:
        error_code = 1

    if error_code == 0:
        store = VideoAnalysisResultsStore()
        storeregions(store, region_data)
        storecrystals(crystal_data, line_data)


    return info_data, error_code



def read_csv_reports(results_dir):
    '''Coordinates the reading of a selection of csv reports.

    Args:
        results_dir (str): The directory name the user has selected to save the
                           results in.

    Returns:
        error_code (int):  An error code is returned a 0 (zero) values means all
                           file were read while a 1 (one) value means 1 or more
                           files were not read.
    '''
    print("hello from read_csv_reports")
    error_code = 0


    files = []
    dirpath = ""
    for (dirpath, dirnames, filenames) in os.walk(results_dir):
        files.extend(filenames)
        break


    error_crystal = 0
    error_line = 0
    error_region = 0
    print(files)
    crystal_data = []
    line_data = []
    region_data = []
    for file in files:
        if file[-4:] == '.csv':
            print(file)
            if "CGT_crystals" in file:
                print("Crystals!")
                crystal_data, error_crystal = readcsv2listofdicts(file, dirpath)
            if "CGT_info" in file:
                print("Info!")
            if "CGT_lines" in file:
                print("Lines!")
                line_data, error_line = readcsv2listofdicts(file, dirpath)
            if "CGT_regions" in file:
                print("Regions!")
                region_data, error_region = readcsv2listofdicts(file, dirpath)

    print("crystal_data: ", crystal_data)
    print("line_data: ", line_data)
    print("region_data: ", region_data)


    if error_crystal or error_line or error_region == 1:
        error_code = 1

    if error_code == 0:
        source = vas.VideoSource("ladkj.mp4", 8, 700, 800, 600)
        store = vas.VideoAnalysisResultsStore(source)
        store.append_history()
        storeregions(store, region_data)
        storecrystals(crystal_data, line_data)

    return error_code



def readcsv2listofdicts(file, dirpath):
    '''Reads csv reports created by the Crystal Growth Tracker as a list of dictionaries.
       This allows means varaibles are read with the header as a pair so can be searched 
       by its semantic meaning.

    Args:
        results_dir (str): The directory name the user has selected to save the
                           results in.

    Returns:
        data (list of doctionaries): A list of dictionaries where each item in the list is a row
                                     from the file read.
        error_code (int):  An error code is returned a 0 (zero) values means all file were read 
                           while a 1 (one) value means 1 or more files were not read.
    '''
    error_code = 0
    dir_in = Path(dirpath)
    file_to_open = dir_in / file
    print(file_to_open)

    data = []

    if not os.path.exists(file_to_open):
        print("ERROR; The input file does not exist.")
        return
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
    except:
        print("Reading failed for file ", file)
        error_code = 1
    finally:
        print("Read file: ", file)


    return (data, error_code)


def readcsvinfo2dict(file, dirpath):
    '''Reads csv reports created by the Crystal Growth Tracker as a list of dictionaries.
       This allows means varaibles are read with the header as a pair so can be searched 
       by its semantic meaning.

    Args:
        results_dir (str): The directory name the user has selected to save the
                           results in.

    Returns:
        data (list of doctionaries): A list of dictionaries where each item in the list is a row
                                     from the file read.
        error_code (int):  An error code is returned a 0 (zero) values means all file were read
                           while a 1 (one) value means 1 or more files were not read.
    '''
    error_code = 0
    dir_in = Path(dirpath)
    file_to_open = dir_in / file
    print(file_to_open)

    data = {}

    if not os.path.exists(file_to_open):
        print("ERROR; The input file does not exist.")
        return
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
                    data[key] = value
    except (IOError, OSError, EOFError) as exception:
        print(exception)
        error_code = 1
    except:
        print("Reading failed for file ", file)
        error_code = 1
    finally:
        print("Read file: ", file)

    print("data: ", data)

    return (data, error_code)



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



def storecrystals(crystal_data, line_data):
    ''' Writes the crystal_data list/array which is read in from a csv file created by the
        Crystal Growth Tracker to a results object. To do this is must also use the line_data
        which is again a list/array which is read in from a csv file created by the
        Crystal Growth Tracker.
    Args:
        crystal_data (list of doctionaries): A list of dictionaries where each item in the list
                                            is a row from the file read.
        line_data (list of doctionaries): A list of dictionaries where each item in the list
                                            is a row from the file read.

    Returns:
        Nothing
    '''


    for crystal in crystal_data:
        #print("crystal: ", crystal)
        crystal_index = int(crystal["Crystal index"])
        print("crystal_index: ", crystal_index)
        #region_index = int(crystal["Region index"])
        note = str(crystal["Note"])
        #number_of_frames = int(crystal["Number of frames"])
        frame_number = int(crystal["Frame number"])

        if note:
            temp_crystal = Crystal(notes=note)
        else:
            temp_crystal = Crystal()

        line_list = []
        for line in line_data:
            crystal_index_from_line = int(line["Crystal index"])
            print("crystal_index_from_line: ", crystal_index_from_line)
            if crystal_index == crystal_index_from_line:
                print("line: ", line)
                x0 = int(line["x0"])
                y0 = int(line["y0"])
                x1 = int(line["x1"])
                y1 = int(line["y1"])
                line_number = line["Line number"]
                line = ImageLineSegment(ImagePoint(x0, y0),
                                         ImagePoint(x1, y1),
                                         line_number)
                line_list.append(line)
        temp_crystal.add_faces(line_list, frame_number)



