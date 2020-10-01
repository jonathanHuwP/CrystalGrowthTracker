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
import csv
import cgt.videoanalysisresultsstore as vas
from cgt.crystal import Crystal
from cgt.region import Region
from cgt.results_print_demo import make_test_result



def save_csv_project(info):
    '''Coordinates the creation of a selection of csv reports.

    Args:
        results_dir (str): The directory name the user has selected to save the
                           results in.
        info (dict): A python dictionary containing a collection of useful parameters
            such as the filenames and paths.

    Returns:
       Nothing is returned.
    '''

    print("save_csv_project")
    
    print("info: ", info)

    #results = make_test_result()

    #print("results: ", results)

#     regions_array = []
# 
#     for index, region in enumerate(results.regions):
#         print("Region: ", index)
#         regions_array.append([index,
#             region.top,
#             region.left,
#             region.bottom,
#             region.right,
#             region.start_frame,
#             region.end_frame])
# 
#     crystals_array = []
#     lines_array = []
#     for index, crystal in enumerate(results.crystals):
# 
#         region, region_index = results.get_region(index)
# 
#         print("Crystal {} is in region {}".format(index, region_index))
#         print("The number of times measured is {}".format(crystal.number_of_frames_held))
# 
# 
#         note = ""
#         if crystal.notes is not None:
#             note = crystal.notes
# 
#         for frame in crystal.list_of_frame_numbers:
#             print("\tframe number {}".format(frame))
# 
#             faces = crystal.faces_in_frame(frame)
# 
# 
#             crystals_array.append([index,
#                 region_index,
#                 note,
#                 crystal.number_of_frames_held,
#                 frame])
#  
#             for face in faces:
#                 lines_array.append([index,
#                                     region_index,
#                                     frame,
#                                     face.label,
#                                     face.start.x,
#                                     face.start.y,
#                                     face.end.x,
#                                     face.end.y])


    #save_csv_regions(results_dir, info, regions_array)
    #save_csv_crystals(results_dir, info, crystals_array)
    #save_csv_lines(results_dir, info, lines_array)
    save_csv_info1(info)



def save_csv_reports(results_dir, info):
    '''Coordinates the creation of a selection of csv reports.

    Args:
        results_dir (str): The directory name the user has selected to save the
                           results in.
        info (dict): A python dictionary containing a collection of useful parameters
            such as the filenames and paths.

    Returns:
       Nothing is returned.
    '''

    print("save_csv_reports")

    results = make_test_result()

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

        region, region_index = results.get_region(index)

        print("Crystal {} is in region {}".format(index, region_index))
        print("The number of times measured is {}".format(crystal.number_of_frames_held))


        note = ""
        if crystal.notes is not None:
            note = crystal.notes

        for frame in crystal.list_of_frame_numbers:
            print("\tframe number {}".format(frame))

            faces = crystal.faces_in_frame(frame)


            crystals_array.append([index,
                region_index,
                note,
                crystal.number_of_frames_held,
                frame])
 
            for face in faces:
                lines_array.append([index,
                                    region_index,
                                    frame,
                                    face.label,
                                    face.start.x,
                                    face.start.y,
                                    face.end.x,
                                    face.end.y])
#                print("\t\t{} ({} {}), ({}, {})".format(
#                     face.label, face.start.x, face.start.y, face.end.x, face.end.y))



#     lines_array = []
#     index = 0
#     for region in results.regions:
#         print("Region: ", index)
#         regions_array.append([index,
#                               region.top_left_horizontal,
#                               region.top_left_vertical,
#                               region.bottom_right_horizontal,
#                               region.bottom_right_vertical,
#                               region.start_frame,
#                               region.end_frame])
#         for crystal in region.crystals:
#             print("Crystal {} has {} frames".format(crystal.name, crystal.number_of_frames_held))
# 
#             for frame in crystal.list_of_frame_numbers:
#                 print("\tframe number {}".format(frame))
# 
#                 faces = crystal.faces_in_frame(frame)
#                 crystals_array.append([index,
#                     crystal.name,
#                     crystal.number_of_frames_held,
#                     frame])
# 
#                 #print("faces: ", faces)
#                 for face in faces:
#                     print("\t\t{} ({} {}), ({}, {})".format(
#                         face.label, face.start.x, face.start.y, face.end.x, face.end.y))
#                     lines_array.append([crystal.name,
#                                         face.label,
#                                         face.start.x,
#                                         face.start.y,
#                                         face.end.x,
#                                         face.end.y])
#         index = index + 1

    #print("crystals_array: ", crystals_array)
    #print("lines_array: ", lines_array)

    save_csv_regions(results_dir, info, regions_array)
    save_csv_crystals(results_dir, info, crystals_array)
    save_csv_lines(results_dir, info, lines_array)
    save_csv_info(results_dir, info)




def save_csv_regions(results_dir, info, regions_array):
    '''Creates the csv report file for regions.

    Args:
        results_dir (str): The directory name the user has selected to save the
                           results in.
        info (dict): A python dictionary containing a collection of useful parameters
            such as the filenames and paths.
        regions_array (array): Regions data in a format that is easy to write into a csv file.

    Returns:
       Nothing is returned.
    '''

    print("Hello from save_csv_regions")

    path = os.path.abspath(os.path.realpath(results_dir))

    start = info["start"]
    prog = info["prog"]
    in_file_no_extension = info["in_file_no_extension"]

    results_dir_final = (path+r"/CGT_"+info['in_file_no_extension']+r"_"+start)
    info['results_dir'] = results_dir_final

    csv_outfile_name = (results_dir_final+r"/"+in_file_no_extension
                         +r"_"+prog+r"_regions.csv")

    try:
        fout = open(csv_outfile_name, "w")
    except OSError:
        print("Could not open csv regions report file, with error message: ", sys.exc_info()[0])
        sys.exit("Could not create csv regions report.")

    header = ("Region index",
              "Top","Left",
              "Bottom","Right",
              "Start frame","End frame")

    with fout:
        writer = csv.writer(fout, delimiter=',', lineterminator = '\n')
        writer.writerow(header)
        for row in regions_array:
            writer.writerow(row)

    fout.close()





def save_csv_crystals(results_dir, info, crystals_array):
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

    path = os.path.abspath(os.path.realpath(results_dir))


    start = info["start"]
    prog = info["prog"]
    in_file_no_extension = info["in_file_no_extension"]

    results_dir_final = (path+r"/CGT_"+info['in_file_no_extension']+r"_"+start)
    info['results_dir'] = results_dir_final

    csv_outfile_name = (results_dir_final+r"/"+in_file_no_extension
                         +r"_"+prog+r"_crystals.csv")

    try:
        fout = open(csv_outfile_name, "w")
    except OSError:
        print("Could not open csv crystals report file, with error message: ", sys.exc_info()[0])
        sys.exit("Could not create csv crystals report.")


    header = ("Crystal index", "Region index", "Note",
              "Number of frames","Frame number")

#    header = ("Region number,",
#              "Top left horizontal","Top left vertical",
#              "Bottom right horizontal","Bottom right vertical",
#              "Start frame","End frame")

    #regions = [[1, 2, 3, 4, 5, 6], 
    #           [700, 800, 9, 10, 65, 29], 
    #           [10, 11, 12, 20 ,20 ,20]]
#    results = make_test_result()
    
#    regions_array = []
#    index = 0
#    for region in results.regions:
#        regions_array.append([index,
#                              region.top,
#                              region.left,
#                              region.bottom,
#                              region.right,
#                              region.start_frame,
#                              region.end_frame])
#        index = index + 1

    with fout:
        writer = csv.writer(fout, delimiter=',', lineterminator = '\n')
        writer.writerow(header)
        for row in crystals_array:
            writer.writerow(row)

    fout.close()








def save_csv_lines(results_dir, info, lines_array):
    '''Creates the csv report file for lines.

    Args:
        results_dir (str): The directory name the user has selected to save the
                           results in.
        info (dict): A python dictionary containing a collection of useful parameters
            such as the filenames and paths.
        regions_array (array): Regions data in a format that is easy to write into a csv file.

    Returns:
       Nothing is returned.
    '''

    print("Hello from save_csv_lines")

    path = os.path.abspath(os.path.realpath(results_dir))

    start = info["start"]
    prog = info["prog"]
    in_file_no_extension = info["in_file_no_extension"]

    results_dir_final = (path+r"/CGT_"+info['in_file_no_extension']+r"_"+start)
    info['results_dir'] = results_dir_final

    csv_outfile_name = (results_dir_final+r"/"+in_file_no_extension
                         +r"_"+prog+r"_lines.csv")

    try:
        fout = open(csv_outfile_name, "w")
    except OSError:
        print("Could not open csv lines report file, with error message: ", sys.exc_info()[0])
        sys.exit("Could not create csv lines report.")


    header = ("Crystal index", "Region index",
              "Frame number", "Line number",
              "x0","y0",
              "x1","y1",)

#    results = make_test_result()
#    
#    regions_array = []
#    index = 0
#    for region in results.regions:
#        regions_array.append([index, index,
#                              region.top,
#                              region.left,
#                              region.bottom,
#                              region.right,
#                              region.start_frame,
#                              region.end_frame])
#        index = index + 1


    with fout:
        writer = csv.writer(fout, delimiter=',', lineterminator = '\n')
        writer.writerow(header)
        for row in lines_array:
            writer.writerow(row)

    fout.close()


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

    path = os.path.abspath(os.path.realpath(results_dir))


    start = info["start"]
    prog = info["prog"]
    in_file_no_extension = info["in_file_no_extension"]

    results_dir_final = (path+r"/CGT_"+info['in_file_no_extension']+r"_"+start)
    info['results_dir'] = results_dir_final

    csv_outfile_name = (results_dir_final+r"/"+in_file_no_extension
                         +r"_"+prog+r"_info.csv")

    try:
        fout = open(csv_outfile_name, "w")
    except OSError:
        print("Could not open csv info report file, with error message: ", sys.exc_info()[0])
        sys.exit("Could not create csv info report.")

    writer = csv.writer(fout, delimiter=',', lineterminator = '\n')
    for key, value in info.items():
        #print("key: ", key)
        #print("value: ", value)
        writer.writerow([key, value])

    fout.close()


def save_csv_info1(info):
    '''Creates the csv report file for info.

    Args:
        results_dir (str): The directory name the user has selected to save the
                           results in.
        info (dict): A python dictionary containing a collection of useful parameters
            such as the filenames and paths.

    Returns:
       Nothing is returned.
    '''

    print("Hello from save_csv_info1")
    
    #print("results_dir: ", results_dir)
    #print("info: ", info)

#     path = os.path.abspath(os.path.realpath(results_dir))
# 
# 
#     start = info["start"]
#     prog = info["prog"]
#     in_file_no_extension = info["in_file_no_extension"]
# 
#     results_dir_final = (path+r"/CGT_"+info['in_file_no_extension']+r"_"+start)
#     info['results_dir'] = results_dir_final
# 
#     csv_outfile_name = (results_dir_final+r"/"+in_file_no_extension
#                          +r"_"+prog+r"_info.csv")
# 
#     try:
#         fout = open(csv_outfile_name, "w")
#     except OSError:
#         print("Could not open csv info report file, with error message: ", sys.exc_info()[0])
#         sys.exit("Could not create csv info report.")
# 
#     writer = csv.writer(fout, delimiter=',', lineterminator = '\n')
#     for key, value in info.items():
#         #print("key: ", key)
#         #print("value: ", value)
#         writer.writerow([key, value])
# 
#     fout.close()


