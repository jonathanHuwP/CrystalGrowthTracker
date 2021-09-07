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
import json
from datetime import datetime
import pathlib

import PyQt5.QtGui as qg

from cgt.model.velocitiescalculator import VelocitiesCalculator
from cgt.util.utils import get_rect_even_dimensions

from cgt.util.utils import (hash_results,
                            make_report_file_names,
                            get_region)

def save_html_report(data_source):
    '''
    Creates and co-ordinates the html report file creation and on the file handle to
    other functions that write/create the relevant sections.
        Args:
            data_source (crystalgrowthtrackermain): holder for all the data and video.
        Returns:
            the report file (pathlib.Path)
        Throws:
            Error if the report directory cannot be made, or file cannot be opened
    '''
    project = data_source.get_project()
    report_dir, html_outfile, hash_file = make_report_file_names(project["proj_full_path"])

    if not report_dir.exists():
        report_dir.mkdir()

    with open(html_outfile, "w") as fout:
        write_html_report_start(fout, project)
        image_files = save_region_location_images(report_dir, data_source)
        write_html_overview(fout, image_files)
        write_html_stats(fout, report_dir)
        write_html_regions(fout, project)
        write_html_report_end(fout, report_dir)

    with open(hash_file, 'w') as fout:
        hash_code = hash_results(project["results"])
        data = {"results_hash": hash_code}
        json.dump(data, fout)

    project["latest_report"] = str(html_outfile)
    return html_outfile

def write_html_stats(fout, report_dir):
    """
    write the statistics section
        Args:
            fout (file): the open output file
            report_dir (string): path to report dir
    """
    fout.write("<h2>Image Statistics</h2>\n")
    path = pathlib.Path(report_dir).joinpath("images")
    path = path.joinpath("stats_graph.png")
    if not path.exists():
        fout.write("<p>Not available</p>")
    else:
        fout.write(f"<img src=\"{path}\" width=\"80%\">\n")
        fout.write("<p>Graph of image intensit statistics against frame number.</p>")

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

def write_html_overview(fout, image_files):
    '''
    Creates the overview section of the html report.
    Args:
        fout (file handler): The file handler allows this function to write out.
        image_files (libpath.Path): the locations of the files holding region location images
    '''
    fout.write("<h2 align=\"left\">Overview</h2>\n")

    fout.write("<figure><br>")

    for name in image_files:
        fout.write(f"<img src=\"{name}\" width=\"30%\">\n")

    fout.write("<br><figcaption><i>First, middel and last frames showing the regions.</i></figcaption>")
    fout.write("</figure>")

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

    html_table = ["<table border=\"1\" width=\"100%\">"]
    html_table.append("""<caption style=\"caption-side:bottom\"><em>Summary of the regions.</em></caption>\n""")

    html_table.append(f"<tr><th>ID</th><th>Top Left(pixels)</th><th>Bottom Right (pixels)</th></tr>")
    for i, region in enumerate(results.get_regions()):
        rect = region.rect()
        position = region.pos()
        top_left = f"({rect.topLeft().x()+position.x():.1f}, {rect.topLeft().y()+position.y():.1f})"
        bottom_right = f"({rect.bottomRight().x()+position.x():.1f}, {rect.bottomRight().y()+position.y():.1f})"
        html_table.append(f"<tr><th>{i}</th><th>{top_left}</th><th>{bottom_right}</th></tr>")

    html_table.append("</table>")

    fout.write('\n'.join(html_table))

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
    fout.write(f"<h3 align=\"left\">Region {index}:</h3>\n")

    lines = []
    for marker in results.get_lines():
        if get_region(marker[0]) == index:
            lines.append(marker)

    points = []
    for marker in results.get_points():
        if get_region(marker[0]) == index:
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

def save_region_location_images(report_dir, data_source):
    """
    save start, middle and final frames of video with the regions marked
        Args:
            report_dir (libpath.Path): the directory to hold images
            data_source (CrystlGrowthTrackerMain): the holder of the data
    """
    images_dir = report_dir.joinpath("images")
    start_file = images_dir.joinpath("regions_start.png")
    middle_file = images_dir.joinpath("regions_middle.png")
    last_file = images_dir.joinpath("regions_end.png")

    last = data_source.get_enhanced_reader().get_video_data().get_frame_count()-1
    middle = int(last/2)
    first = 0

    if not images_dir.exists():
        images_dir.mkdir()

    save_image_with_regions(first, start_file, data_source)
    save_image_with_regions(middle, middle_file, data_source)
    save_image_with_regions(middle, last_file, data_source)

    return [start_file, middle_file, last_file]

def save_image_with_regions(frame, out_file, data_source):
    """
    save frame to file
        Args:
            frame (int): frame number
            out_file (pathlib.Path):
            data_source (CrystalGrowthTrackeMain): holder of the data
    """
    pixmap = data_source.get_enhanced_reader().get_pixmap(frame)

    painter = qg.QPainter(pixmap)
    painter.setPen(data_source.get_pens().get_display_pen())
    results = data_source.get_results()
    for region in results.get_regions():
        rect = get_rect_even_dimensions(region, False)
        painter.drawRect(rect)

    painter.end()

    pixmap.save(str(out_file))
