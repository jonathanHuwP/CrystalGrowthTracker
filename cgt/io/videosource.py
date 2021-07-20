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

from cgt.util.qthreadsafequeue import QThreadSafeQueue
from cgt.io.videobuffer import VideoBuffer

class VideoSource(qc.QObject):
    """
    a source of images from a video file, it will run
    a reader in a seperate thread.
    """

    def __init__(self, file_name):
        """
        set up the object
        """
        super().__init__()
        ## the queue of video frames to be displayed
        self._frame_queue = QThreadSafeQueue()

        ## the thread for the VideoBuffer
        self._video_thread = None

        ## a pointer for the video buffered reader
        self._video_reader = None

        ## the viewer currently connected
        self._current_viewer = None

        self.start_player(file_name)

    def start_player(self, file_name):
        """
        start the video player
            Args:
                file_name (string) the video file to be read
        """
        self._video_thread = qc.QThread()
        self._video_reader = VideoBuffer(file_name, self)
        self._length = self._video_reader.get_length()
        self._video_reader.moveToThread(self._video_thread)

        # connections
        self._video_thread.started.connect(self._video_reader.make_frames)
        self._video_thread.finished.connect(self._video_thread.deleteLater)

        # start the thread
        self._video_thread.start()

    def get_buffer(self):
        """
        getter for the video buffer
            Returns:
                (VideoBuffer)
        """
        return self._video_reader

    def get_length(self):
        """
        getter for the lenght
            Returns:
                the number of frams in video (int)
        """
        return self._length

    def get_frame_queue(self):
        """
        getter for the queue of frames to be read
        """
        return self._frame_queue

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
