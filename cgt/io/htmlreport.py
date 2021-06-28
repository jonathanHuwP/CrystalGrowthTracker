'''
htmlreport.py

This python module contains functions that create reports in csv or html
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
from datetime import datetime

from cgt.model.velocitiescalculator import VelocitiesCalculator

def save_html_report(project):
    '''
    Creates and co-ordinates the html report file creation and on the file handle to
    other functions that write/create the relevant sections.
        Args:
            project (CGTProject): The project we are reporting.
        Returns:
            error_code (int):      An error code is returned a 0 (zero) values means all
                                   file were read while a 1 (one) value means 1 or more
                                   files were not read.
        Throws:
            Error if the report directory cannot be made, or file cannot be opened
    '''
    report_dir = pathlib.Path(project["proj_full_path"]).joinpath("report")

    if not report_dir.exists():
        report_dir.mkdir()

    html_outfile = report_dir.joinpath("report.html")
    calculator = VelocitiesCalculator(project["results"])
    html_table = make_html_speeds_table(calculator)

    try:
        with open(html_outfile, "w") as fout:
            write_html_report_start(fout)

            fout.write(html_table)
            write_html_report_end(fout)
    except (IOError, OSError, EOFError) as exception:
        print(exception)
    finally:
        print(f"Read file: {html_outfile}")

    return html_outfile

def make_html_speeds_table(calculator):
    """
    make a table of results
    """
    calculator.process_latest_data()
    average_speeds = calculator.get_average_speeds()

    html_table = ["<table border=\"1\" width=\"100%\">"]
    html_table.append("""<caption style=\"caption-side:bottom\"><em>Speeds of the markers.</em></caption>\n""")

    html_table.append("<tr><th>ID</th><th>Type</th><th>Speed</th></tr>")
    for item in average_speeds:
        id_item = str(item.ID)
        type_item = item.m_type.name
        speed_item = str(item.speed)
        html_table.append(f"<tr><th>{id_item}</th><th>{type_item}</th><th>{speed_item}</th></tr>")

    html_table.append("</table>")

    return '\n'.join(html_table)

def write_html_report_start1(fout, project):
    '''
    Creates the start of a generic html report.
        Args:
            fout (file handler): The file handler allows this function to write out.
            project (CGTProject): The project we are reporting.
        Returns:
            fout (file handler): The file handler is passed back so that other parts of
                                 the report can be written by different functions.
    '''

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

    title = "<title>Report on {} Produced by the Crystal Growth Tracker ({}) Software</title>\n"
    title = title.format(project['enhanced_video_path'], project['prog'])

    fout.write(title)

    fout.write("</head>\n")
    fout.write("\n<body>\n")

    title2 = ("<h1 align=\"center\">Report on {} Produced by the"
              " Crystal Growth Tracker ({}) Software</h1>\n")
    title2 = title2.format(project['enhanced_video'], project['prog'])
    fout.write(title2)

    program_info = '<p><i>{}</i>: {}</p>\n'.format(project['prog'], project['description'])
    fout.write(program_info)

    report_info = (r"<p>This project was started at "+project['start_datetime']+r" on the "
                   +project['host']+r" host system with the "+project['operating_system']
                   +" operating system. The video file, "+str(project['enhanced_video_no_path'])
                   +r" was analysed and has a frame rate of "+str(project['frame_rate'])
                   +" and resolution of " +str(project['resolution'])
                   +" "+str(project['resolution_units'])+" per pixel. A note of caution "
                   +"is needed here because sometimes the frame rate and resolution "
                   +"are changed in the video header when the video is being "
                   +"pre-processed so in this report we always give results in pixels "
                   +"and frames as well as SI units where possible. This report provides "
                   +"images and information on experimental X-ray videos created at "
                   +"Diamond Light Source.</p>\n")

    fout.write(report_info)

    return fout




def write_html_overview(fout, results):
    '''Creates the overview section of the html report.
    Args:
        fout (file handler): The file handler allows this function to write out.
        results:              The project results data
    Returns:
       fout (file handler): The file handler is passed back so that other parts of
                            the report can be written by different functions.
    '''

    header2_line = ("<h2 align=\"left\">Overview</h2>\n")
    fout.write(header2_line)

    # removed to fix report JPH
    # line = ("<p>The number of crystals analyzed:  *** </p>\n")
    # line = line.replace("***", str(len(results.crystals)))
    # fout.write(line)

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



def write_html_crystals(fout, project, results):
    '''Creates the section for each crystal in the html report.
    Args:
        fout (file handler): The file handler allows this function to write out.
        project (CGTProject): The project we are reporting.
        results:              The project results data
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
        line = line.replace("***", str(project['frame_rate']))
        fout.write(line)

       # write_frame_table(fout, results, crystal)
        #write_table(fout, results, crystal)



    return fout




def write_html_region(fout, results, i):
    '''Creates the section for each region in the html report.

    Args:
        fout (file handler): The file handler allows this function to write out.
        results:              The project results data
        i (int):             The index for the crystal that is being reported.


    Returns:
       fout (file handler): The file handler is passed back so that other parts of
                            the report can be written by different functions.
    '''

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


def write_frame_table(fout, results, crystal):
    '''Creates a table for each time the faces are recorded for a region/crytal.
    Args:
        fout (file handler): The file handler allows this function to write out.
        results:              The project results data
        crystal (cgt.model.crystal.Crystal): The crystal data structure.

    Returns:
       fout (file handler): The file handler is passed back so that other parts of
                            the report can be written by different functions.
    '''

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
        print("last_frame_number: ", last_frame_number)
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
                   %(50, len(faces), elapsed_time, time_difference))
                   #%(frame, len(faces), elapsed_time, time_difference))
#                   '</td> </tr> \n' %(frame, faces, elapsed_time, time_difference))

    fout.write("</table>\n")
    fout.write("<p></p>\n")

    return fout



def write_table(fout, results, crystal):
    '''Creates a table for demonstration purposes.
    Args:
        fout (file handler): The file handler allows this function to write out.
        results:              The project results data
        crystal (cgt.model.crystal.Crystal): The crystal data structure.

    Returns:
       fout (file handler): The file handler is passed back so that other parts of
                            the report can be written by different functions.
    '''

    fout.write("<table>\n")
    fout.write("<caption style=\"caption-side:bottom\"><em>The Table "
               "demonstrates it is possible to table data, perhaps of a moving "
               "face</em></caption>\n")
    fout.write("   <tr>\n")
    fout.write("     <th>Frame Number</th>\n")
    fout.write("     <th>Number of Recorded Faces</th>\n")
    fout.write("     <th>Elapsed Time (s)</th>\n")
    fout.write("     <th>Time Difference Previous (s)</th>\n")
    fout.write("   </tr>\n")

    last_frame_number = 0
    data = [[250, 3, 31.2567, 0.00000], [[320, 4, 40.267398, 4.621]]]
    for frame in data:
        fout.write('   <tr> <td> %d </td> <td> %d </td> <td> %.2f </td> <td> %.2f </td> </tr>\n'
                   %(frame[0], frame[1], frame[2], frame[3]))


    fout.write("</table>\n")
    fout.write("<p></p>\n")

    return fout

def write_html_report_start(fout):
    '''
    start a html report.
        Args:
            fout (file): the output file
    '''
    fout.write("<body>\n")
    fout.write("<html>\n")
    timestamp = datetime.now()
    month = timestamp.strftime("%B") # language given by local
    date = f"{timestamp.date().day}-{month}-{timestamp.date().year}"
    time = f"{timestamp.time().hour}:{timestamp.time().minute}:{timestamp.time().second}"

    fout.write(f"<p>Report generated on: {date} at {time}</p>")

def write_html_report_end(fout):
    '''
    Ends and closes a html report.
        Args:
            fout (file): the output file
    '''
    fout.write("</font>")
    fout.write("</body>\n")
    fout.write("</html>\n")
