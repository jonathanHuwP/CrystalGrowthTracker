'''
writecsvreports.py

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
import sys
import cgt.videoanalysisresultsstore as vas
from cgt.crystal import Crystal
from cgt.region import Region
from cgt.results_print_demo import make_test_result
import csv



def save_csv_reports(results_dir, info):
    
    
    print("save_csv_reports")
    save_csv_regions(results_dir, info)
    #save_csv_crystals(results_dir, info)
    #save_csv_lines(results_dir, info)
    save_csv_info(results_dir, info)

def save_csv_crystals(results_dir, info):
    '''Creates the csv report file for crystals.

    Args:
        results_dir (str): The directory name the user has selected to save the
                           results in.
        info (dict): A python dictionary containing a collection of useful parameters
            such as the filenames and paths.

    Returns:
       Nothing is returned.
    '''    
    print("Hello from save_csv_cystals")
    print(results_dir)

    path = os.path.abspath(os.path.realpath(results_dir))

    print(path)

    start = info["start"]
    prog = info["prog"]
    in_file_no_extension = info["in_file_no_extension"]

    results_dir_final = (path+r"/CGT_"+info['in_file_no_extension']+r"_"+start)
    info['results_dir'] = results_dir_final
    print(results_dir_final)

    csv_outfile_name = (results_dir_final+r"/"+in_file_no_extension
                         +r"_"+prog+r"_crystals.csv")
    print("csv_outfile_name: ", csv_outfile_name)

    try:
        fout = open(csv_outfile_name, "w")
    except OSError:
        print("Could not open csv crystals report file, with error message: ", sys.exc_info()[0])
        sys.exit("Could not create csv crystals report.")

    header = ("Region number,",
              "Top left horizontal","Top left vertical",
              "Bottom right horizontal","Bottom right vertical",
              "Start frame","End frame")

    #regions = [[1, 2, 3, 4, 5, 6], 
    #           [700, 800, 9, 10, 65, 29], 
    #           [10, 11, 12, 20 ,20 ,20]]
    results = make_test_result()
    
    regions_array = []
    index = 0
    for region in results.regions:
        regions_array.append([index,
                              region.top,
                              region.left,
                              region.bottom,
                              region.right,
                              region.start_frame,
                              region.end_frame])
        index = index + 1

    with fout:
        writer = csv.writer(fout, delimiter=',', lineterminator = '\n')
        writer.writerow(header)
        for row in regions_array:
            writer.writerow(row)

    fout.close()




def save_csv_regions(results_dir, info):
    '''Creates the csv report file for regions.

    Args:
        results_dir (str): The directory name the user has selected to save the
                           results in.
        info (dict): A python dictionary containing a collection of useful parameters
            such as the filenames and paths.

    Returns:
       Nothing is returned.
    '''    
    
    print("Hello from save_csv_regions")
    print(results_dir)

    path = os.path.abspath(os.path.realpath(results_dir))

    print(path)

    start = info["start"]
    prog = info["prog"]
    in_file_no_extension = info["in_file_no_extension"]

    results_dir_final = (path+r"/CGT_"+info['in_file_no_extension']+r"_"+start)
    info['results_dir'] = results_dir_final
    print(results_dir_final)

    csv_outfile_name = (results_dir_final+r"/"+in_file_no_extension
                         +r"_"+prog+r"_regions.csv")
    print("csv_outfile_name: ", csv_outfile_name)

    try:
        fout = open(csv_outfile_name, "w")
    except OSError:
        print("Could not open csv regions report file, with error message: ", sys.exc_info()[0])
        sys.exit("Could not create csv regions report.")

    header = ("Crystal number", "Region number,",
              "Top left horizontal","Top left vertical",
              "Bottom right horizontal","Bottom right vertical",
              "Start frame","End frame")

    results = make_test_result()
    
    regions_array = []
    index = 0
    for region in results.regions:
        regions_array.append([index, index,
                              region.top,
                              region.left,
                              region.bottom,
                              region.right,
                              region.start_frame,
                              region.end_frame])
        index = index + 1

    with fout:
        writer = csv.writer(fout, delimiter=',', lineterminator = '\n')
        writer.writerow(header)
        for row in regions_array:
            writer.writerow(row)

    fout.close()



def save_csv_lines(results_dir, info):
    
    print("save_csv_lines")
    
def save_csv_info(results_dir, info):
    '''Creates the csv report file for info.

    Args:
        results_dir (str): The directory name the user has selected to save the
                           results in.
        info (dict): A python dictionary containing a collection of useful parameters
            such as the filenames and paths.

    Returns:
       Nothing is returned.
    '''    
    
    print("Hello from save_csv_info")
    print(results_dir)

    path = os.path.abspath(os.path.realpath(results_dir))

    print(path)

    start = info["start"]
    prog = info["prog"]
    in_file_no_extension = info["in_file_no_extension"]

    results_dir_final = (path+r"/CGT_"+info['in_file_no_extension']+r"_"+start)
    info['results_dir'] = results_dir_final
    print(results_dir_final)

    csv_outfile_name = (results_dir_final+r"/"+in_file_no_extension
                         +r"_"+prog+r"_info.csv")
    print("csv_outfile_name: ", csv_outfile_name)

    try:
        fout = open(csv_outfile_name, "w")
    except OSError:
        print("Could not open csv info report file, with error message: ", sys.exc_info()[0])
        sys.exit("Could not create csv info report.")



    writer = csv.writer(fout, delimiter=',', lineterminator = '\n')
    for key, value in info.items():
        print("key: ", key)
        print("value: ", value)
        writer.writerow([key, value])

    fout.close()


