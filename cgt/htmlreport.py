'''
htmlreport.py

This python module contains functions that create reports in csv or html
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
from cgt import utils
#from cgt.utils import find_hostname_and_ip
from cgt.results_print_demo import make_test_result


def save_html_report(results_dir, info):
    '''Creates the html report file sop that it can manage the report writing
    and pass the file handle to the functions that write the relevant parts.

    Args:
        results_dir (str): The directory name the user has selected to save the
                           results in.
        filename_in (str): The name of the video file that is being analysed.

    Returns:
       Nothing is returned.
    '''
    print("hi from save_html_report")
    print(results_dir)

    #path = os.path.dirname(os.path.abspath(results_dir))
    path = os.path.abspath(os.path.realpath(results_dir))


    start = info["start"]
    filename_in = info['in_file_no_path']
    prog = info["prog"]
 
    results_dir_final = (path+r"/CGT_"+info['in_file_no_extension']+r"_"+start)
    info['results_dir'] = results_dir_final
 
    try:
        os.makedirs(results_dir_final)
    except OSError:
        print("Unexpected error:", sys.exc_info()[0])
        sys.exit("Could not create directory for the results.")
 
    html_outfile_name = (results_dir_final+r"/"+filename_in
                         +r"_"+prog+r"_report.html")
 
    try:
        fout = open(html_outfile_name, "w")
    except  OSError:
        print("Could not open html report file, with error message: ", sys.exc_info()[0])
        sys.exit("Could not create html report.")

    results = make_test_result()

    info['no_of_cystals'] = len(results.crystals)
    info['no_of_regions'] = len(results.regions)
# 
#     print("crystals_array: ", crystals_array)
# 
    fout = write_html_report_start(fout, info,)

    fout = write_html_overview(fout, info, results)

    fout = write_html_crystals(fout, info, results)

    write_html_report_end(fout)



def save_html_report1(info, time_stamp):
    '''Creates the html report file sop that it can manage the report writing
    and pass the file handle to the functions that write the relevant parts.

    Args:
        results_dir (str): The directory name the user has selected to save the
                           results in.
        filename_in (str): The name of the video file that is being analysed.

    Returns:
       Nothing is returned.
    '''
    print("hi from save_html_report1")

    results_dir = (info["proj_full_path"]+r"/"+time_stamp)

    print(results_dir)

    path = os.path.abspath(os.path.realpath(results_dir))

    prog = info["prog"]

#  
    try:
        os.makedirs(results_dir)
    except OSError:
        print("Unexpected error:", sys.exc_info()[0])
        sys.exit("Could not create directory for the results.")

    html_outfile_name = (results_dir+r"/"+prog+r"_report.html")

    try:
        fout = open(html_outfile_name, "w")
    except  OSError:
        print("Could not open html report file, with error message: ", sys.exc_info()[0])
        sys.exit("Could not create html report.")


    fout = write_html_report_start1(fout, info,)
# 
#     write_html_report_end(fout)

    return results_dir




def write_html_report_start1(fout, info):
    '''Creates the start of an html report which is generic for the PERPL
    scripts.

    Args:
        fout (file handler): The file handler allows this function to write out.
        info (dict): A python dictionary containing a collection of useful parameters
            such as the filenames and paths.

    Returns:
       fout (file handler): The file handler is passed back so that other parts of
                            the report can be written by different functions.
    '''
    prog = info['prog']

    print("Hi from write_html_report_start1")

    fout.write("<!DOCTYPE html>\n")

    fout.write("<html>\n")
    fout.write("<head>\n")
    fout.write("<meta charset=\"UTF-8\">\n")
    fout.write("<style>\n")
    fout.write("table, th, td {\n")
    fout.write("    border: 1px solid black;\n")
    fout.write("    border-collapse: collapse;\n")
    fout.write("}\n")
    fout.write("th, td {\n")
    fout.write("    padding: 15px;\n")
    fout.write("}\n")
    fout.write("</style>\n")

    title_line1 = ("<title>Report on *** Produced by the Crystal Growth Tracker (+++) "
                   "Software</title>\n")
    title = title_line1.replace("***", info['source_no_path'])
    title = title.replace("+++", info['prog'])
    fout.write(title)

    fout.write("</head>\n")
    fout.write("\n<body>\n")
    title_line2 = ("<h1 align=\"center\">Report on *** Produced by the "
                   "Crystal Growth Tracker (+++) Software</h1>\n")
    title2 = title_line2.replace("***", info['source_no_path'])
    title2 = title2.replace("+++", prog)
    fout.write(title2)

    program_info = '<p><i>%s</i>: %s</p>\n' % (info['prog'], info['description'])
    fout.write(program_info)


    report_info = (r"<p>This project was started at "+info['start']+r" on the "
                    +info['host']+r" host system with the "+info['operating_system']
                    +" operating system. The video file, "+info['source_no_path']
                    +r" was analysed and has a frame rate of "+str(info['frame_rate'])
                    +" and resolution of " +str(info['resolution'])
                    +" "+str(info['resolution_units'])+" per pixel. A note of caution "
                    +"is needed here because sometimes the frame rate and resolution "
                    +"are changed in the video header when the video is being "
                    +"pre-processed so in this report we always give results in pixels "
                    +"and frames as well as SI units where possible. This report provides "
                    +"images and information on experimental X-ray videos created at "
                    +"Diamond Light Source.</p>\n")

    fout.write(report_info)

    return fout


def write_html_report_start(fout, info):
    '''Creates the start of an html report which is generic for the PERPL
    scripts.

    Args:
        fout (file handler): The file handler allows this function to write out.
        info (dict): A python dictionary containing a collection of useful parameters
            such as the filenames and paths.

    Returns:
       fout (file handler): The file handler is passed back so that other parts of
                            the report can be written by different functions.
    '''
    prog = info['prog']
    #results_dir = info['results_dir']
    #in_file_no_extension = info['in_file_no_extension']
    #in_file_no_path = info['in_file_no_path']
    #html_outfile_name = (results_dir+r"/"+in_file_no_extension+r"_"+prog+r"_report.html")

    #print("Hi from write_html_report_start")

    fout.write("<!DOCTYPE html>\n")

    fout.write("<html>\n")
    fout.write("<head>\n")
    fout.write("<meta charset=\"UTF-8\">\n")
    fout.write("<style>\n")
    fout.write("table, th, td {\n")
    fout.write("    border: 1px solid black;\n")
    fout.write("    border-collapse: collapse;\n")
    fout.write("}\n")
    fout.write("th, td {\n")
    fout.write("    padding: 15px;\n")
    fout.write("}\n")
    fout.write("</style>\n")

    title_line1 = ("<title>Report on *** Produced by the Crystal Growth Tracker (+++) "
                   "Software</title>\n")
    title = title_line1.replace("***", info['in_file_no_path'])
    title = title.replace("+++", info['prog'])
    fout.write(title)

    fout.write("</head>\n")
    fout.write("\n<body>\n")
    title_line2 = ("<h1 align=\"center\">Report on *** Produced by the "
                   "Crystal Growth Tracker (+++) Software</h1>\n")
    title2 = title_line2.replace("***", info['in_file_no_path'])
    title2 = title2.replace("+++", prog)
    fout.write(title2)

    program_info = '<p><i>%s</i>: %s</p>\n' % (info['prog'], info['description'])
    fout.write(program_info)


    report_info = (r"<p>This program ran at "+info['start']+r" on the "
                    +info['host']+r" host system with the "+info['operating_system']
                    +" operating system. The video file, "+info['in_file_no_path']
                    +r" was analysed and has a frame rate of "+str(info['frame_rate'])
                    +" and resolution of " +str(info['resolution'])
                    +" "+str(info['resolution_units'])+" per pixel. A note of caution "
                    +"is needed here because sometimes the frame rate and resolution "
                    +"are changed in the video header when the video is being "
                    +"pre-processed so in this report we always give results in pixels "
                    +"and frames as well as SI units where possible. This report provides "
                    +"images and information on experimental X-ray videos created at "
                    +"Diamond Light Source.</p>\n")

    fout.write(report_info)

    return fout


def write_html_overview(fout, info, results):
    '''Creates the overview section of the html report.

    Args:
        fout (file handler): The file handler allows this function to write out.
        info (dict): A python dictionary containing a collection of useful parameters
            such as the filenames and paths.

    Returns:
       fout (file handler): The file handler is passed back so that other parts of
                            the report can be written by different functions.
    '''

    header2_line = ("<h2 align=\"left\">Overview</h2>\n")
    fout.write(header2_line)

    line = ("<p>The number of crystals analyzed:  *** </p>\n")
    line = line.replace("***", str(len(results.crystals)))
    fout.write(line)

    line = ("<p>The number of crystals that formed closed polygons:  *** </p>\n")
    line = line.replace("***", str("TO BE ADDED!"))
    fout.write(line)

    fout.write("<p align=\"center\"> An image will go here the caption is below</p>")

    fout.write("<p align=\"center\"><i>The final frame of the video showing the regions"
               " in which crystals were analyzed as highlighted boxes.</i></p>")

    header3_line = ("<h3 align=\"left\">Image Statistics from the Raw Video</h3>\n")
    fout.write(header3_line)

    fout.write("<p>This section details some image statistics that show the evolution"
               " of the individual frames of the raw video.</p>")

    fout.write("<p align=\"center\">A plot of the mean grayscale value for each frame"
               " over time will go here the caption is below</p>")

    fout.write("<p align=\"center\"><i>The mean grayscale value of each frame plotted"
               " against the frame number. The gray boxed areas represent the time limits"
               " of each region containing a crystal.</i></p>")

    return fout



def write_html_crystals(fout, info, results):
    '''Creates the section for each crystal in the html report.

    Args:
        fout (file handler): The file handler allows this function to write out.
        crystal_number (int): The index for the crystal that is being reported.
        info (dict): A python dictionary containing a collection of useful parameters
            such as the filenames and paths.

    Returns:
       fout (file handler): The file handler is passed back so that other parts of
                            the report can be written by different functions.
    '''
    print("Hello from write_html_crystal")


    for i, crystal in enumerate(results.crystals):
        print("i: ", i)
        print("crystal: ", crystal)
        header2_line = ("<h2 align=\"left\">Crystal: *** </h2>\n")
        header2_line = header2_line.replace("***", str(i))
        fout.write(header2_line)

        fout = write_html_region(fout, results, i)

        line = ("<p><b>Number of recorded faces</b>:  *** </p>\n")
        line = line.replace("***", str("Should be in table"))
        fout.write(line)

        line = ("<p><b>Closed Polygon formed</b>:  *** </p>\n")
        line = line.replace("***", str("TO BE ADDED!"))
        fout.write(line)

        line = ("<p><b>Number of times measured</b>:  *** </p>\n")
        line = line.replace("***", str(crystal.number_of_frames_held))
        fout.write(line)

        line = ("<p><b>Frame Rate</b>:  *** </p>\n")
        line = line.replace("***", str(results.video.frame_rate))
        fout.write(line)

        write_frame_table(fout, results, i, crystal)

        

    return fout




def write_html_region(fout, results, i):

    region, r_index = results.get_region(i)
    #print(results.get_region(i))
    header3_line = ("<h3 align=\"left\">Region ***:</h3>\n")
    header3_line = header3_line.replace("***", str(r_index))
    fout.write(header3_line)

    line = ("<p>Top:  *** </p>\n")
    line = line.replace("***", str(region.top))
    fout.write(line)

    line = ("<p>Left:  *** </p>\n")
    line = line.replace("***", str(region.left))
    fout.write(line)

    line = ("<p>Bottom:  *** </p>\n")
    line = line.replace("***", str(region.bottom))
    fout.write(line)

    line = ("<p>Right:  *** </p>\n")
    line = line.replace("***", str(region.right))
    fout.write(line)

    line = ("<p>Start Frame:  *** </p>\n")
    line = line.replace("***", str(region.start_frame))
    fout.write(line)

    line = ("<p>End Frame:  *** </p>\n")
    line = line.replace("***", str(region.end_frame))
    fout.write(line)

    return fout


def write_frame_table(fout, results, i, crystal):


    fout.write("<table>\n")
    fout.write("<caption style=\"caption-side:bottom\"><em>The frame numbers, "
               "number of faces recorded and elapsed times of the frames in "
               "which measurements were made</em></caption>\n")
    fout.write("   <tr>\n")
    fout.write("     <th>Frame Number</th>\n")
    fout.write("     <th>Number of Recorded Faces</th>\n")
    fout.write("     <th>Elapsed Time (s)</th>\n")
    fout.write("     <th>Time Difference Previous (s)</th>\n")
    fout.write("   </tr>\n")

    last_frame_number = 0
    for frame in crystal.list_of_frame_numbers:
        print("last_frame_number: ",last_frame_number)
        faces = crystal.faces_in_frame(frame)
        print("faces:", len(faces))
#         video = results.video
#         print("video: ", video)
        elapsed_time = frame / results.video.frame_rate
        print("elapsed_time: ", elapsed_time)
        time_difference = (frame - last_frame_number) / results.video.frame_rate
        print("time_difference: ", time_difference)
        last_frame_number = frame
        fout.write('   <tr> <td> %d </td> <td> %d </td> <td> %.2f </td> <td> %.2f </td> </tr>\n'
                   %(frame, len(faces), elapsed_time, time_difference))
#                   '</td> </tr> \n' %(frame, faces, elapsed_time, time_difference))

    fout.write("</table>\n")
    fout.write("<p></p>\n")

    return fout




def write_html_report_end(fout):
    '''Ends and closes an html report.
    '''
    fout.write("</body>\n")
    fout.write("</html>\n")

    fout.close()
