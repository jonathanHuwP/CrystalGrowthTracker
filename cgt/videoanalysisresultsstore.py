# -*- coding: utf-8 -*-
"""
Created on Tuesday August 18 2020

Licensed under the Apache License, Version 2.0 (the "License"); you may not use
this file except in compliance with the License. You may obtain a copy of the
License at
http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed
under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.

@copyright 2020
@author: j.h.pickering@leeds.ac.uk
"""

# set up linting conditions
# pylint: disable = too-many-public-methods
# pylint: disable = c-extension-no-member## define a date user pair for the history

from collections import namedtuple
import os
import datetime as dt

##
## Args:
##
## date the date on which a results were added
##
## user_name the login of the user who added the results
DateUser = namedtuple("DateUser", ["date", "user_name"])

## a tuple for the video on which the analysis is based
##
## Args:
##
## name the video file name or path
##
## frame_rate number of frames per second
##
## length the numer of frames in the video
##
## width the horizontal size of the video in pixels
##
## height the vertical size of the video in pixels
VideoSource = namedtuple("VideoSource", ["name", "frame_rate", "length", "width", "height"])

class VideoAnalysisResultsStore:
    """
    a storage class that records the results and history of a video analysis
    """
    def __init__(self, video, history=None, crystals=None):
        """
        initalize an object

            Args:
                video (video_source) description of the original video sequence

                history ([date_user]) a list of (date, unser name) recording changes

                crystals ([Crystal]) the crystal objects holding faces, times and region
        """

        ## a record of the date and user for all saves
        self._history = []

        if history is not None:
            self._history = history
        else:
            self._history.append(DateUser(str(dt.date.today()), os.getlogin()))

        ## the source video on which the analyais is based
        self._video = video

        ## storage for the crystals identified by the user dict(name, crystal)
        self._crystals = {}

        if crystals is not None:
            self._crystals = crystals

    @property
    def video(self):
        """
        getter for the description of the video

            Returns:
                the description of the video source
        """
        return self._video

    @property
    def history(self):
        """
        getter for the history

            Returns:
                the list of (date, user name) pairs
        """
        return self._history

    def add_crystal(self, crystal):
        """
        add a crystal to the results

            Args:
                crystal (Crystal) the crystal to be added
        """
        self._crystals[crystal.name] = crystal

    @property
    def crystal_names(self):
        """
        getter for a list of the names of the crystals

            Returns:
                list of crystal names
        """
        return [i.name for i in self._crystals]

    def get_crystal(self, name):
        """
        getter for an individual crystal

            Args:
                name the name or id of the crystal

            Returns:
                the chosen crystel crystal

            Throws:
                KeyError if unknow name
        """
        return self._crystals[name]
