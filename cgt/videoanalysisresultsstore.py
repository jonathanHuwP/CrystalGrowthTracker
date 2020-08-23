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
# pylint: disable = c-extension-no-member

from collections import namedtuple
import os
import datetime as dt

## define a date user pair for the history
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
    def __init__(self, video, history=None, regions=None):
        """
        initalize an object

            Args:
                video (video_source) description of the original video sequence

                history ([date_user]) a list of (date, unser name) recording changes

                regions ([Region]) the region objects holding crystals
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
        self._regions = {}

        if regions is not None:
            self._regions = regions

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
        
    @property
    def regions(self):
        return self._regions

    def add_region(self, region):
        """
        add a crystal to the results

            Args:
                region (Region) the region to be added
        """
        self._regions[region.name] = region

    @property
    def number_of_regions(self):
        """
        getter for the number of regions in the store

            Returns:
                the number of regions
        """
        return len(self._regions)

    @property
    def region_and_crystal_ids(self):
        """
        getter for a list of lists of crystal names,
        each item in top level list is one region

            Returns:
                list of lists of crystal names, each sub-list represents one region
        """
        lst = []
        for region in self._regions:
            lst.append(region.crystal_names)

        return lst

    def get_crystal(self, region_id, crystal_name):
        """
        getter for an individual crystal

            Args:
                region_id the array index of the region
                crystal_name the name or id of the crystal

            Returns:
                the chosen crystel crystal

            Throws:
                KeyError if unknow name
        """
        return self._regions[region_id][crystal_name]

    def get_region(self, region_id):
        """
        getter for a region

            Args:
                region_id (int) the array index of the region

            Returns:
                the region indexed by region_id
        """
        return self._regions[region_id]
