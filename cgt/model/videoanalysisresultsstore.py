# -*- coding: utf-8 -*-
"""
Created on Tuesday August 18 2020

Licensed under the Apache License, Version 2.0 (the "License"); you may not use
this file except in compliance with the License. You may obtain a copy of the
License at http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed
under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.

This work was funded by Joanna Leng's EPSRC funded RSE Fellowship (EP/R025819/1)

@copyright 2020
@author: j.h.pickering@leeds.ac.uk and j.leng@leeds.ac.uk
"""

# set up linting conditions
# pylint: disable = too-many-public-methods
# pylint: disable = too-many-arguments

class VideoAnalysisResultsStore:
    """
    a storage class that records the results of a video analysis
    """
    def __init__(self, regions=None):
        """
        initalize an object

            Args:
                video (video_source) description of the original video sequence

                regions ([Region]) the region objects
        """
        ## storage for the regions
        self._regions = []

        flag = False
        if regions is not None:
            self._regions = regions
            flag = True

        ## flag to indicate store has been changed
        self._changed = True

    def has_been_changed(self):
        """
        getter for the changed status

            Returns:
                the changed flag
        """
        return self._changed

    def reset_changed(self):
        """
        make the changed status false

            Returns:
                None
        """
        self._changed = False

    def set_changed(self):
        """
        set the changed status to true

            Returns:
                None
        """
        self._changed = True

    @property
    def regions(self):
        """
        getter for the regions array

            Returns:
                regions array
        """
        return self._regions

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
        self.set_changed()

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
        self.set_changed()

        return index

    @property
    def number_of_regions(self):
        """
        getter for the number of regions in the store

            Returns:
                the number of regions
        """
        return len(self._regions)

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
