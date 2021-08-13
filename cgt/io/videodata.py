## -*- coding: utf-8 -*-
"""
Created on  Sunday 01 Aug 2021

Licensed under the Apache License, Version 2.0 (the "License"); you may not use
this file except in compliance with the License. You may obtain a copy of the
License at http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed
under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.

This work was funded by Joanna Leng's EPSRC funded RSE Fellowship (EP/R025819/1)

@copyright 2021
@author: j.h.pickering@leeds.ac.uk and j.leng@leeds.ac.uk
"""
from collections import namedtuple

## data structure for video data
VideoData = namedtuple("VideoData",
                       ["file_name", 
                        "width", 
                        "height", 
                        "frame_count",
                        "frame_rate",
                        "length", 
                        "frame_size"])
    
def current_length_seconds(data, frame_interval):
    """
    calculate the length of video at current frame rate
        Args:
            data (VideoData): the data struct holding the length 
            frame_interval (float): time between frames
        Returns:
            (float) length of video in seconds 
    """
    return frame_interval*data.frame_count
    
def convert_to_film_time(data, time, frame_interval):
    """
    convert time to film time
        data (VideoData)
        time (float): time in player
        frame_interval (float): time between frames in player 
    """
    play_length = frame_interval*data.frame_count
    ratio = play_length/data.length
    return time*ratio

def make_video_data(file_name, 
                    width, height, 
                    frame_count, 
                    length, 
                    avg_frame_rate,
                    bytes_per_pixel=3):
    """
    factory function for VideoData objects
        Args:
            file_name (string)
            width (int)
            height (int)
            frame_count (int)
            length (string): length of video in seconds
            avg_frame_rate (string)/ average frame rate n/m (n frames in m seconds)
            bytes_per_pixel (int)
        Returns:
            VideoData object
    """
    frame_size = width * height * bytes_per_pixel
    length_fp = float(length)
    parts = avg_frame_rate.split('/')
    frames = float(parts[0])
    seconds = float(parts[1])
    
    return VideoData(file_name, 
                     width, 
                     height, 
                     frame_count, 
                     (frames/seconds), 
                     length_fp, 
                     frame_size)
