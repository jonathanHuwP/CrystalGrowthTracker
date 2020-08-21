# -*- coding: utf-8 -*-
"""
Created on Tuesday July 21 13:42: 2020

this module hold low level classes representing artifacts that can
be drawn on an image

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

from imagelinesegment import ImageLineDifference

class LineSetsAndFramesStore(dict):
    """
    a store for the sets of lines used in the analysis of one crystal in one video
    """
    def __init__(self):
        """
        initalize the class

            Returns:
                None
        """
        super().__init__()

    def differences(self, key0, key1):
        """
        find the differenced between the equivalent lines in two sets,
        equivalence based on the lines own labels

            Args:
            key0 (dictionary key) the key for the first set of lines
            key1 (dictionary key) the key for the second set of lines

            Returns:
                a list of differences (list(ImageLineDifference))

        """
        tmp = self.match_pairs(key0, key1)

        diffs = []
        for i in tmp:
            start_distance = i[0].start.distance_from(i[1].start)
            end_distance = i[0].end.distance_from(i[1].end)
            diffs.append(ImageLineDifference(start_distance, end_distance, i[0].label))

        return diffs

    def match_pairs(self, key0, key1):
        """
        returns a list of pairs each holding a line from the list at key0,
        and the matching line from the list at key1

            Args:
                key0 : (time key) the first time key.
                key1 : (time key) the second time key.

            Returns:
                a list of pairs each having the key0 line first
                (list(tuple(ImageLineSegment, ImageLineSegment)))
        """

        tmp = []
        for line in self[key0]:
            line_match = line.label_in_set(self[key1])
            if line_match is not None:
                tmp.append((line, line_match))

        return tmp