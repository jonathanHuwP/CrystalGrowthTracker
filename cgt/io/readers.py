'''
readers.py

This python module contains functions that read images, animations or other
files useful to the CrystalGrowthTracker application.

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

import sys
import os
from timeit import default_timer as timer
from datetime import timedelta
from imageio import get_reader
from cgt.util import overviewplots



def read_video_frame(frame_number, filename, outpath):
    '''
    Opens an avi input file and parses it to get a frame.
    '''
    start = timer()

    print("hi read_video_frame")
    file_name = filename
    print(file_name)
    print("frame_number: ", frame_number)

    try:
        video = get_reader(file_name, 'ffmpeg')
    except:
        print("Unexpected error:", sys.exc_info()[0])
        raise

    try:
        if not os.path.exists(outpath):
            os.makedirs(outpath)
    except OSError:
        sys.exit('Fatal: output directory ' + outpath +
                ' does not exist and cannot be created')

    num = 0
    img = None
    for img in video.iter_data():
        if num == int(frame_number):
            filename_frame = overviewplots.save_grayscale_frame(outpath,
                                                               img,
                                                               frame_number)
            filename_histogram = overviewplots.plot_histogram(outpath,
                                                             img,
                                                             num,
                                                             img.mean(),
                                                             img.std())
            break

        num = num+1

    #number = r"{0:05d}".format(frame_number)
    #filename_frame = str(outpath)+r'/GrayscaleFrame'+number+'.png'
    #filename_histogram = str(outpath)+'/HistogramFrame'+number+'.png'
    end = timer()
    time = str(timedelta(seconds=(end-start)))
    print("The time to read and process the video was: ", time) # Time in seconds

    return filename_frame, filename_histogram
