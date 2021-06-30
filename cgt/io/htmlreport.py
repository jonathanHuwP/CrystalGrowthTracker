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

    with open(html_outfile, "w") as fout:
        write_html_report_start(fout, project)
        write_html_overview(fout, project["results"])
        write_html_regions(fout, project)
        write_html_report_end(fout, report_dir)

    return html_outfile

def make_html_speeds_table(calculator, units):
    """
    make a table of results
    """
    calculator.process_latest_data()
    average_speeds = calculator.get_average_speeds()

    html_table = ["<table border=\"1\" width=\"100%\">"]
    html_table.append("""<caption style=\"caption-side:bottom\"><em>Speeds of the markers.</em></caption>\n""")

    html_table.append(f"<tr><th>ID</th><th>Type</th><th>Speed ({units} s<sup>-1</sup>)</th></tr>")
    for item in average_speeds:
        html_table.append(f"<tr><th>{item.ID}</th><th>{item.m_type.name}</th><th>{item.speed:.2f}</th></tr>")

    html_table.append("</table>")

    return '\n'.join(html_table)

def write_html_report_start(fout, project):
    '''
    Creates the start of a generic html report.
        Args:
            fout (file handler): The file handler allows this function to write out.
            project (CGTProject): The project we are reporting.
    '''
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

    enhanced_path = project['enhanced_video_no_path']
    title = f"Crystal Growth Tracker Report on {enhanced_path}"
    fout.write(f"<title>{title}</title>\n")
    fout.write("</head>\n")
    fout.write("\n<body>\n")
    fout.write(f"<h1 align=\"center\">{title}</h1>")

    timestamp = datetime.now()
    date, time = to_date_and_time(timestamp)
    fout.write(f"<p>Report generated on: {date} at {time}</p>")

    report_info = (r"<p>This project was started at "+project['start_datetime']+r" on machine "
                   +project['host']+r".</p>"
                   +r"<p>The video file, "+str(project['enhanced_video_no_path'])
                   +r" was analysed and has a frame rate of "+str(project['frame_rate'])
                   +" frames per second, and a resolution of " +str(project['resolution'])
                   +str(project['resolution_units'])+" per pixel. Pixels are assumed to be square.</p>"
                   + "<p>Caution: sometimes the frame rate and resolution "
                   +"are changed in the video header when the video is being "
                   +"pre-processed.</p>\n")

    fout.write(report_info)

def write_html_overview(fout, results):
    '''
    Creates the overview section of the html report.
    Args:
        fout (file handler): The file handler allows this function to write out.
        results:              The project results data
    '''
    header2_line = ("<h2 align=\"left\">Overview</h2>\n")
    fout.write(header2_line)

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

def write_html_regions(fout, project):
    """
    write out the results for the regions to file
        Args:
            fout (TextIOWrapper): output file stream
            project (CGTProject): The project data
    """
    results = project["results"]
    fout.write("<h2 align=\"left\">Motion Results</h2>\n")
    fout.write("<p>Results for each region are summerised below.</p>")
    for index in range(len(results.get_regions())):
        write_html_region(fout,
                          results,
                          index,
                          project["frame_rate"],
                          project["resolution"],
                          project["resolution_units"])

def write_html_region(fout, results, index, fps, scale, units):
    '''
    Creates the section for each region in the html report.
        Args:
            fout (TextIOWrapper): output file stream
            results (VideoAnalysisResultsStore): The project results data
            index (int): The index for the crystal that is being reported.
            fps (np.float64): the number of frames per second
            scale (np.float64): the size of a pixel
    '''
    from cgt.util.utils import (get_region)
    fout.write(f"<h3 align=\"left\">Region {index}:</h3>\n")
    region = results.get_regions()[index]
    rect = region.rect()
    position = region.pos()
    top_left = f"({rect.topLeft().x():.1f}, {rect.topLeft().y():.1f})"
    bottom_right = f"({rect.bottomRight().x():.1f}, {rect.bottomRight().x():.1f})"
    pos = f"({position.x()}, { position.y()})"

    fout.write(f"<p>Rectangle: top left {top_left} bottom right {bottom_right}; Position {pos}</p>")

    lines = []
    for marker in results.get_lines():
        if get_region(marker[0]) == index:
            print(f"Region {index} line {marker[0]}")
            lines.append(marker)

    points = []
    for marker in results.get_points():
        if get_region(marker[0]) == index:
            print(f"Region {index} point {marker[0]}")
            points.append(marker)

    calculator = VelocitiesCalculator(lines, points, fps, scale)
    counts = calculator.number_markers()
    if counts[0] > 0 or counts[1] > 0:
        fout.write(make_html_speeds_table(calculator, units))

def write_html_report_end(fout, report_dir):
    '''
    Ends and closes a html report.
        Args:
            fout (file): the output file
            report_dir (pathlib.Path) directory holding the report
    '''
    report_dir = report_dir.joinpath("images/CLONE_whole.jpg")

    fout.write(f"<img src=\"{report_dir}\" alt=\"Missing Image\">")

    fout.write("""<p>Crystal Growht Tracker was developed by
    JH Pickering & J Leng at the University of Leeds, Leeds UK,
    funded by Joanna Leng's EPSRC funded RSE Fellowship (EP/R025819/1).
    The software is freely available from
    <a href=\"https://github.com/jonathanHuwP/CrystalGrowthTracker\">GitHub</a>,
    under the <a href=\"http://www.apache.org/licenses/LICENSE-2.0\">Apache License, Version 2.0</a></p>
    <p>Source code and this report format are copyright University of Leeds, 2020.</p>""")

    fout.write("</font>")
    fout.write("</body>\n")
    fout.write("</html>\n")

def to_date_and_time(timestamp):
    """
    convert a timestamp to date and time fields to
        Args:
            timestame (datetime.datetime) the initial timestamp of
        Returns
            date (string) date in day month year format.
            time (string) time is hour minutes seconds format
    """
    month = timestamp.strftime("%B") # language given by local
    date = f"{timestamp.date().day}-{month}-{timestamp.date().year}"
    time = f"{timestamp.time().hour}:{timestamp.time().minute}:{timestamp.time().second}"
    return date, time
