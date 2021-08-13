## -*- coding: utf-8 -*-
"""
Created on Thur Mar 04 2021

This module contains the top level graphical user interface for measuring the
growth rates of crystals observed in videos taken using an X-ray synchrotron source

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
# set up linting conditions
# pylint: disable = too-many-public-methods
# pylint: disable = too-many-instance-attributes
# pylint: disable = c-extension-no-member
# pylint: disable = import-error

import PyQt5.QtCore as qc
import ffmpeg

from cgt.io.videodata import make_video_data

class VideoSource(qc.QObject):
    """
    a source of images from a video file, it will run
    a reader in a seperate thread.
    """

    ## the pixel format and number of bytes
    PIX_FMT = ('rgb24', 3)

    def __init__(self, file_name):
        """
        set up the object
        """
        super().__init__()

        ## file name
        self._file_name = file_name

        ## video data
        self._video_data = {}

        ## the queue of video frames to be displayed
        self._frame_queue = []

        ## the viewer currently connected
        self._current_viewer = None

        self.probe_video(file_name)

    def probe_video(self, file_path):
        """
        load a video file
            Args:
                file_path (string) the file
        """
        self._video_data = None
        try:
            probe = ffmpeg.probe(file_path)
            video_info = next(s for s in probe['streams'] if s['codec_type'] == 'video')

            print("Video Data\n========")
            for key in video_info.keys():
                print(f"\t{key} => {video_info[key]} {type(video_info[key])}")
            print("\n")

            self._video_data = make_video_data(file_path,
                                              video_info["width"],
                                              video_info["height"],
                                              video_info["duration_ts"],
                                              video_info["duration"],
                                              VideoSource.PIX_FMT[1])
        except ffmpeg.Error as error:
            self.display_error(f"File {file_path} cannot be probed: {error}")
            return False
        except StopIteration:
            self.display_error(f"File {file_path} does not appear to contain video information")
            self._video_data = None
            return False
        except KeyError as exception:
            self.display_error(f"Probe video data error: unknown key {exception}")
            return False

        return True

    def connect_viewer(self, viewer):
        """
        connect the VideoBuffer's 'display_image' signal and the
        viewers 'request_frame' and 'clear_queue' signals, any
        previous connections are disconnected.
            Args:
                viewer (QObject) if None the source is disconnected from any previous connections
        """
        self.disconnect_viewer()
        if viewer is None:
            return

        viewer.play_pause()
        self._video_reader.display_image.connect(viewer.display_image)
        viewer.request_frame.connect(self.request_frame)
        viewer.clear_queue.connect(self.clear)
        self.clear()

        self._current_viewer = viewer

    def simple_connect_viewer(self, viewer):
        """
        connect the VideoBuffer's 'display_image' signal and the
        viewers 'request_frame', any
        previous connections are disconnected. No pause i
            Args:
                viewer (QObject) if None the source is disconnected from any previous connections
        """
        self.disconnect_viewer()
        if viewer is None:
            return

        self._video_reader.display_image.connect(viewer.display_image)
        viewer.request_frame.connect(self.request_frame)
        viewer.clear_queue.connect(self.clear)
        self.clear()

        self._current_viewer = viewer

    def disconnect_viewer(self):
        """
        disconnect the VideoBuffer's 'display_image' signal
        from the viewer object's 'display_image' slot
        """
        if self._current_viewer is not None:
            self._video_reader.display_image.disconnect(self._current_viewer.display_image)
            self._current_viewer.request_frame.disconnect(self.request_frame)
            self._current_viewer.clear_queue.disconnect(self.clear)

    @qc.pyqtSlot(int)
    def request_frame(self, frame_number):
        """
        request a frame from the video
            Args:
                frame_number (int) the frame to be read
        """
        self._frame_queue.push(frame_number)

    def request_frames(self, frames):
        """
        request a list of frames
            Args:
                frames ([int]) list of fame number
        """
        self._frame_queue.add(frames)


    @qc.pyqtSlot()
    def clear(self):
        """
        clear the frame queue
        """
        self._frame_queue.clear()

    def stop(self):
        """
        stop the thread
        """
        self._video_reader.stop()
        self._video_thread.quit()
        self._video_thread.wait()
