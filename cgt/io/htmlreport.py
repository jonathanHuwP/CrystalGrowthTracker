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
import itertools

import PyQt5.QtGui as qg
import PyQt5.QtCore as qc

from cgt.model.velocitiescalculator import VelocitiesCalculator
from cgt.io.mpl import OffScreenRender, render_graph
from cgt.util.utils import (get_rect_even_dimensions,
                            hash_results,
                            make_report_file_names,
                            get_region)

class ReportMaker(qc.QObject):
    """
    provide ability to signal in Qt
    """

    ## the progress signal
    stage_completed = qc.pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)

    def save_html_report(self, data_source):
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

        stage = itertools.count(1)
        with open(html_outfile, "w") as fout:
            write_html_report_start(fout, project)
            self.stage_completed.emit(next(stage))
            image_files = save_region_location_images(report_dir, data_source)
            self.stage_completed.emit(next(stage))
            region_files = save_region_start_images(report_dir, data_source)
            self.stage_completed.emit(next(stage))
            key_frame_files = save_region_keyframe_images(report_dir, data_source)
            self.stage_completed.emit(next(stage))
            save_time_evolution_video_statistics(report_dir, data_source)
            self.stage_completed.emit(next(stage))
            #write_html_overview(fout, image_files)
            write_html_stats(fout, report_dir)
            self.stage_completed.emit(next(stage))
            write_html_regions(fout, project, image_files, region_files, key_frame_files)
            self.stage_completed.emit(next(stage))
            write_html_report_end(fout, report_dir)
            self.stage_completed.emit(next(stage))

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
    fout.write("<h1>Image Statistics</h1>\n")
    fout.write("<p>This section details some image statistics that show the evolution"
               " of the individual frames of the raw video.</p>")

    fout.write("<p align=\"center\">A plot of the mean grayscale value for each frame"
               " over time will go here the caption is below</p>")

    fout.write("<p align=\"center\"><i>The mean grayscale value of each frame plotted"
               " against the frame number. The gray boxed areas represent the time limits"
               " of each region containing a crystal.</i></p>")

    path = pathlib.Path(report_dir).joinpath("images")
    path = path.joinpath("video_statistics.png")
    print(path)
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

    html_table = ["<table style=\"margin-bottom:5mm;\" class=\"hg-pdf\">"]
    html_table.append("""<caption>Speeds of the markers.</caption>\n""")

    html_table.append(f"<tr><th>ID</th><th>Type</th><th>Speed ({units} s<sup>-1</sup>)</th></tr>")
    for item in average_speeds:
        html_table.append(f"<tr><td>{item.ID}</td><td>{item.m_type.name}</td><td>{item.speed:.2f}</td></tr>")

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
    fout.write("    border: 2px solid black;\n")
    fout.write("    border-collapse: collapse;\n")
    fout.write("    font-size: 20px\n")
    fout.write("}\n")
    fout.write("th, td {\n")
    fout.write("    padding: 15px;\n")
    fout.write("}\n")
    fout.write("tr {")
    fout.write("    page-break-inside:avoid;")
    fout.write("    page-break-after:auto")
    fout.write("}")
    fout.write("h1 {\n")
    fout.write("    font-size: 40px;\n")
    fout.write("}\n")
    fout.write("h1 {\n")
    fout.write("    font-size: 30px;\n")
    fout.write("}\n")
    fout.write("h2 {\n")
    fout.write("    font-size: 25px;\n")
    fout.write("}\n")
    fout.write("h3 {\n")
    fout.write("    font-size: 20px;\n")
    fout.write("}\n")
    fout.write("p {\n")
    fout.write("    font-size: 20px;\n")
    fout.write("}\n")
    fout.write("caption {\n\tfont-style: italic;\n\tfont-size: 20px;\n\tpadding: 2px;\n\ttext-align: left;\n}")
    fout.write("figcaption {\n\tfont-style: italic;\n\tfont-size: 20px;\n\tpadding: 2px;\n\ttext-align: left;\n}")
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

def write_html_regions(fout, project, image_files, region_image_files, frame_image_files):
    """
    write out the results for the regions to file
        Args:
            fout (TextIOWrapper): output file stream
            project (CGTProject): The project data
            region_image_files ([pathlib.Path]): paths to images of each region
            frame_image_files ([pathlib.Path]): paths to images of each region at key frames
    """
    results = project["results"]
    fout.write("<h1 align=\"left\">Regions</h2>\n")
    fout.write("<p>The regions chosen for analysis are described.</p>")
    fout.write("<figure><br>")
    for name in image_files:
        fout.write(f"<img src=\"{name}\" width=\"30%\">\n")
    fout.write("<br><figcaption><i>First, middel and last frames showing the regions.</i></figcaption>")
    fout.write("</figure>")

    html_table = ["<table style=\"margin-bottom:5mm;\">"]
    html_table.append("""<caption>Summary of the regions.</caption>\n""")

    html_table.append(f"<tr><th>ID</th><th>Top Left(pixels)</th><th>Bottom Right (pixels)</th></tr>")
    for i, region in enumerate(results.get_regions()):
        rect = get_rect_even_dimensions(region, False)
        top_left = f"({rect.topLeft().x():.1f}, {rect.topLeft().y():.1f})"
        bottom_right = f"({rect.bottomRight().x():.1f}, {rect.bottomRight().y():.1f})"
        html_table.append(f"<tr><td>{i}</td><td>{top_left}</td><td>{bottom_right}</td></tr>")

    html_table.append("</table>")

    fout.write('\n'.join(html_table))
    fout.write("<figure><br>")
    for image in region_image_files:
        fout.write(f"<img src=\"{image}\" width=\"10%\">\n")
    fout.write("<br><figcaption><i>First frame of each region.</i></figcaption>")
    fout.write("</figure>")

    for index in range(len(results.get_regions())):
        write_html_region(fout,
                          results,
                          index,
                          frame_image_files[index],
                          project["frame_rate"],
                          project["resolution"],
                          project["resolution_units"])

def write_html_region(fout, results, index, images, fps, scale, units):
    '''
    Creates the section for each region in the html report.
        Args:
            fout (TextIOWrapper): output file stream
            results (VideoAnalysisResultsStore): The project results data
            index (int): The index for the crystal that is being reported.
            images ([pathlib.Path]): paths to images of region at each key frame
            fps (np.float64): the number of frames per second
            scale (np.float64): the size of a pixel
    '''
    fout.write(f"<h2 align=\"left\">Region {index}:</h3>\n")

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

    fout.write("<figure>")
    for image in images:
        fout.write(f"<img src=\"{image}\" width=\"10%\">\n")
    fout.write("<br><figcaption><i>The region at each key frame.</i></figcaption>")
    fout.write("</figure>")

def write_html_report_end(fout, report_dir):
    '''
    Ends and closes a html report.
        Args:
            fout (file): the output file
            report_dir (pathlib.Path) directory holding the report
    '''
    fout.write("""<hr>\n<em><p>Crystal Growht Tracker was developed by
    JH Pickering & J Leng at the University of Leeds, Leeds UK,
    funded by Joanna Leng's EPSRC funded RSE Fellowship (EP/R025819/1).
    The software is freely available from
    <a href=\"https://github.com/jonathanHuwP/CrystalGrowthTracker\">GitHub</a>,
    under the <a href=\"http://www.apache.org/licenses/LICENSE-2.0\">Apache License, Version 2.0</a></p>
    <p><em>Source code and this report format are copyright University of Leeds, 2020.</p>""")

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

def save_time_evolution_video_statistics(report_dir, data_source):
    """
    save image of time evolution of mean pixel intensity
        Args:
            report_dir (libpath.Path): the directory to hold images
            data_source (CrystlGrowthTrackerMain): the holder of the data
    """
    statistics = data_source.get_results().get_video_statistics()
    if statistics is None:
        return None

    images_dir = report_dir.joinpath("images")
    file_name = images_dir.joinpath("video_statistics.png")

    canvas = OffScreenRender()
    render_graph(statistics.get_frames(), canvas)
    canvas.print_png(str(file_name))

    return file_name

def save_region_start_images(report_dir, data_source):
    """
    save image of each region
        Args:
            report_dir (libpath.Path): the directory to hold images
            data_source (CrystlGrowthTrackerMain): the holder of the data
    """
    images_dir = report_dir.joinpath("images")
    raw_image = data_source.get_enhanced_reader().get_pixmap(0)
    files = []

    results = data_source.get_results()
    for i, region in enumerate(results.get_regions()):
        rect = get_rect_even_dimensions(region)
        pixmap = raw_image.copy(rect)
        out_file = images_dir.joinpath(f"region_{i}.png")
        pixmap.save(str(out_file))
        files.append(out_file)

    return files

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

def save_region_keyframe_images(report_dir, data_source):
    """
    save image of each region
        Args:
            report_dir (libpath.Path): the directory to hold images
            data_source (CrystlGrowthTrackerMain): the holder of the data
    """
    images_dir = report_dir.joinpath("images")
    files = []

    results = data_source.get_results()
    for index in range(len(results.get_regions())):
        files.append(save_keyframe_images(images_dir,
                                          data_source,
                                          index))

    return files

def save_keyframe_images(images_dir, data_source, region_index):
    """
    save image of the region at each key frame
        Args:
            images_dir,
            data_source, region_index
    """
    results = data_source.get_results()
    region = results.get_regions()[region_index]
    key_frames = results.get_key_frames(region_index)
    rect = get_rect_even_dimensions(region)
    files = []

    if key_frames is None:
        return files

    for frame in key_frames:
        raw_image = data_source.get_enhanced_reader().get_pixmap(frame)
        pixmap = raw_image.copy(rect)
        out_file = images_dir.joinpath(f"region_{region_index}_frame_{frame}.png")
        pixmap.save(str(out_file))
        files.append(out_file)

    return files