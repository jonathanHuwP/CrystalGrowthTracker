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
# pylint: disable = too-many-arguments

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
## frame_count the numer of frames in the video
##
## width the horizontal size of the video in pixels
##
## height the vertical size of the video in pixels
VideoSource = namedtuple("VideoSource", ["name", "frame_rate", "frame_count", "width", "height"])

class VideoAnalysisResultsStore:
    """
    a storage class that records the results and history of a video analysis
    """
    def __init__(self, video, history=None, regions=None, crystals=None, region_crystal=None):
        """
        initalize an object

            Args:
                video (video_source) description of the original video sequence

                history ([date_user]) a list of (date, unser name) recording changes

                regions ([Region]) the region objects

                crystals ([Crystal]) the crystal object

                region_crystal ([(int, int)] a mapping (<region index>, <crystal index>)
        """

        ## a record of the date and user for all saves
        self._history = []

        if history is not None:
            self._history = history

        ## the source video on which the analysis is based
        self._video = video

        ## storage for the regions
        self._regions = []

        if regions is not None:
            self._regions = regions

        ## storage for the crystals
        self._crystals = []

        if crystals is not None:
            self._crystals = crystals

        ## a bi-dirctional mapping of regions and crystals to each other
        self._region_crystal = []

        if region_crystal is not None:
            self._region_crystal = region_crystal

    def append_history(self):
        """
        add an item to the history
        """
        self._history.append(DateUser(str(dt.date.today()), os.getlogin()))

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
        """
        getter for the regions array

            Returns:
                regions array
        """
        return self._regions

    @property
    def crystals(self):
        """
        getter for the crystals array

            Returns:
                crystals array
        """
        return self._crystals

    @property
    def region_crystal(self):
        """
        getter for the regions crystals mapping array

            Returns:
                regions crystals mapping array
        """
        return self._region_crystal

    def reserve_regions(self, size):
        """
        set the size of the regions array, will overwrite all existing enteries

            Args:
                size (int) the desired size

            Returns:
                None
        """
        self._regions.extend(['']*size)

    def insert_region(self, region, index):
        """
        insert a region at a specified index in the regions array, will overwrite existing

            Args:
                region (Region) the region to be added
                index (int) the index at which the region is to be located

            Returns:
                None

            Throws:
                IndexError if index out of range
        """
        self._regions[index] = region

    def add_region(self, region):
        """
        add a crystal to the results

            Args:
                region (Region) the region to be added

            Reterns:
                index of the new region
        """
        index = len(self._regions)
        self._regions.append(region)
        return index

    def reserve_crystals(self, size):
        """
        set the size of the crystals array, will overwrite all existing enteries

            Args:
                size (int) the desired size

            Returns:
                None
        """
        self._crystals.extend(['']*size)

    def insert_crystal(self, crystal, index):
        """
        insert a crystal at a specified index in the regions array, will overwrite existing

            Args:
                crystal (Crystal) the crystal to be added
                index (int) the index at which the crystal is to be located

            Returns:
                None

            Throws:
                IndexError if index out of range
        """
        self._crystals[index] = crystal

    def add_crystal(self, crystal, region_index):
        """
        add a crystal and the index of its associated region to the store,

            Args:
                crystal (Crystal) the crystal object to be added
                region_index (int) the array index of the associated region
        """
        c_index = len(self._crystals)
        self._crystals.append(crystal)
        self._region_crystal.append((region_index, c_index))

    @property
    def number_of_regions(self):
        """
        getter for the number of regions in the store

            Returns:
                the number of regions
        """
        return len(self._regions)

    @property
    def number_of_crystals(self):
        """
        getter for a list crystals

            Returns:
                list crystals
        """
        return len(self._crystals)

    def get_crystals(self, region_index):
        """
        getter for crystals in a region

            Args:
                region_index the array index of the region

            Returns:
                a list of the crystal belonging to the region

            Throws:
                IndexError: if out of range
        """
        lst = []

        for i in self._region_crystal:
            if i[0] == region_index:
                lst.append(self.crystals[i[1]])

        return lst

    def get_region(self, crystal_index):
        """
        getter for the region holding a crystal, and its array index

            Args:
                crystal_index (int) the array index of the crystal

            Returns:
                the region holding the crystal, the array index of the region
        """
        for i in self._region_crystal:
            if i[1] == crystal_index:
                return self._regions[i[0]], i[0]

        return None, None
