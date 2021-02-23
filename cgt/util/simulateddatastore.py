# -*- coding: utf-8 -*-
"""
Created on Feb 2021

provides a class, derived from QLabel, that allows the user to select a
retcangular region of a pixmap in pixmap coordinates

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

class SimulatedDataStore():
    """
    store used to simulate the results in CGTMain
    """
    def __init__(self):
        """
        provide an empty list
        """
        self._data = []

    def get_region(self, index):
        """
        getter for a region
            Args:
                index (int) the list index
            Returns:
                the region
            Throws:
                IndexError: list index out of range
        """
        return self._data[index]

    def append(self, datum):
        """
        add item to list
            Args:
                datum (object) tht item to be added
            Returns:
                the new length of the list
        """
        self._data.append(datum)
        return len(self._data)

    def remove(self, index):
        """
        remove an item
            Args:
                index (int) the index of the item to be removed
            Throws:
                IndexError: pop index out of range
        """
        self._data.pop(index)

    def replace_region(self, rectangle, index):
        """
        replace an existing region
            Args:
                rectangle (QRect) the new region
                index (int) the list index
            Throws:
                IndexError: pop index out of range
        """
        self._data[index] = rectangle

    @property
    def length(self):
        """
        getter for the lenght of the list
            Returns:
                (int) the length of the list
        """
        return len(self._data)
