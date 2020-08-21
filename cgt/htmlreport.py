'''
reports.py

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
import datetime
from cgt import utils
from cgt.utils import find_hostname_and_ip


def save_html_report(results_dir, filename_in):
    '''Creates the html report file sop that it can manage the report writing
    and pass the file handle to the functions that write the relevant parts.
    '''
    prog = 'CGT'
    description = 'Semi-automatically racks the growth of crystals from X-ray videos.'

    info = {'prog':prog,
            'description':description}
    print(results_dir)

    info['in_file_no_path'] = filename_in
    info['in_file_no_extension'] = os.path.splitext("filename_in")[0]
    info['frame_rate'] = 20
    info['resolution'] = 10
    info['resolution_units'] = "nm"

    path = os.path.dirname(os.path.abspath(results_dir))

    print(path)

    start = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    info['start'] = start
    print(start)

    info['host'], info['ip_address'], info['operating_system'] = utils.find_hostname_and_ip()
    print(find_hostname_and_ip())

    results_dir_final = (path+r"/CGT_"+filename_in+r"_"+start)
    info['results_dir'] = results_dir_final
    print(results_dir_final)

    try:
        os.makedirs(results_dir_final)
    except OSError:
        print("Unexpected error:", sys.exc_info()[0])
        sys.exit("Could not create directory for the results.")

    html_outfile_name = (results_dir_final+r"/"+filename_in
                         +r"_"+prog+r"_report.html")

    fout = open(html_outfile_name, "w")

    fout = write_html_report_start(fout, info)



    write_html_report_end(fout)


def write_html_report_start(fout, info):
    '''Creates the start of an html report which is generic for the PERPL
    scripts.
    '''
    prog = info['prog']
    results_dir = info['results_dir']
    in_file_no_extension = info['in_file_no_extension']
    in_file_no_path = info['in_file_no_path']
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




def write_html_report_end(fout):
    '''Ends and closes an html report which is generic for the PERPL
    scripts.
    '''
    fout.write("</body>\n")
    fout.write("</html>\n")

    fout.close()
