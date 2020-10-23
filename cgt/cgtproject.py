## -*- coding: utf-8 -*-
"""
Created on Mon Feb 24 15:45:07 2020

This module contains the top level graphical user interface for measuring the
growth rates of crystals observed in videos taken using an X-ray synchrotron source

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

import getpass

from cgt import utils

class CGTProject(dict):
    """
    a store for a the project data and results

    Contents:
        prog: (string) name of program
        description: (string) description of the program
        start_datetime: (string) timestamp of start of project
        host: (string) name of computer
        ip_address: (string) ip address of computer
        operating_system: (string) operating system of computer
        enhanced_video_path: (pathlib.Path) the full path of the image enhanced video
        enhanced_video_no_path: the name of the enhanced video file
        enhanced_video_no_extension: name of the enhanced video file without extension
        raw_video: (pathlib.Path) the full path and name of the original video
        raw_video_no_path: (string) the name of the original video file
        raw_video_no_extension: (string) the name of the original video file without extension
        proj_name: (string) the name of the projcect
        notes: (string) notes input by user
        frame_rate: (int) the frame rate
        resolution: (float) the real world size of a pixel
        resolution_units: (string) the units of size of a pixel
        results: (VideoAnalysisResultsStore) the results
    """
    def __init__(self):
        """
        initalize the class

            Returns:
                None
        """
        super().__init__()

        ## a flag to indicate the dictionary has been changed. can be unset after a save
        self._changed = False

        # program name
        self["prog"] = None

        # program description
        self["description"] = None

        # a time stamp for the start of the project
        self["start_datetime"] = None

        # name of computer on which we are running
        self['host'] = None

        # ip address of computer on which the project started
        self['ip_address'] = None

        # operating system on we which the project started
        self['operating_system'] = None

        # the video on which the program will operate
        self["enhanced_video"] = None

        # the original video before image enhancment, may be null
        self["raw_video"] = None

        # the name of the project
        self["proj_name"] = None

        # the full path to the project
        self["proj_full_path"] = None

        # the users notes
        self["notes"] = None

        # the video frame rate
        self["frame_rate"] = None

        # the results
        self["results"] = None

        # the path to the enhanced_video
        self["enhanced_video_path"] = None

        # the plain file name of the enhanced_video
        self['enhanced_video_no_path'] = None

        # the file name of the enhanced_video without postfix
        self['enhanced_video_no_extension'] = None

        # the path to the raw_video video file
        self['raw_video_path'] = None

        # the plain file name of the raw_video video file
        self['raw_video_no_path'] = None

        # the file extension of the raw_video video file
        self['raw_video_no_extension'] = None

        # the user who stated the project
        self['start_user'] = None

        # the video frame rate
        self['frame_rate'] = None

        # the real world distance represented by the edge length of a pixel
        self['resolution'] = None

        # the units of the resolution
        self['resolution_units'] = None

        # path to latest saved report
        self["latest_report"] = None

    def init_new_project(self):
        """
        fill in the data for a new project
        """
        prog = 'CGT'
        description = 'Semi-automatically tracks the growth of crystals from X-ray videos.'

        self["prog"] = prog
        self["description"] = description
        self["start_datetime"] = utils.timestamp()
        self['host'], self['ip_address'], self['operating_system'] = utils.find_hostname_and_ip()
        self["start_user"] = getpass.getuser()

    def __setitem__(self, item, value):
        """
        override setitem to allow changs flag to be set on any data change

            Returns:
                None
        """
        super(CGTProject, self).__setitem__(item, value)
        self._changed = True

    def reset_changed(self):
        """
        make the changed status false

            Returns:
                None
        """
        self._changed = False

        if self["results"] is not None:
            self["results"].reset_changed()

    def has_been_changed(self):
        """
        getter for the current changed status

            Return:
                true if the dictionary contains new data else false
        """
        if self["results"] is None:
            return self._changed

        return self._changed or self["results"].has_been_changed()
