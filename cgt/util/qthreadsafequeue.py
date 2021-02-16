## -*- coding: utf-8 -*-
"""
Created on  Mon 04 Jan 2021

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
import PyQt5.QtCore as qc

class QThreadSafeQueue(qc.QObject):
    """
    a list with Qt mutex protected accessor
    functions designed to operate as a queue
    """

    def __init__(self, parent=None):
        """
        set up list and QMutex
            Args:
                parent (QObject) the parent object
        """
        super().__init__(parent)
        self._mutex = qc.QMutex()
        self._list = []

    def push(self, item):
        """
        add item to end of queue
            Args:
                item (object) the item to add
        """
        self._mutex.lock()
        self._list.append(item)
        self._mutex.unlock()

    def pop(self):
        """
        remove item from head of queue
            Returns:
                (object) the head of the queue
        """
        item = None
        self._mutex.lock()
        if len(self._list) > 0:
            item = self._list.pop(0)
        self._mutex.unlock()
        return item

    def clear(self):
        """
        clear the queue
        """
        self._mutex.lock()
        self._list.clear()
        self._mutex.unlock()

    def is_empty(self):
        """
        find is queue has any items
            Returns:
                True if queue has no items else False
        """
        flag = True
        self._mutex.lock()
        flag = len(self._list) < 1
        self._mutex.unlock()
        return flag
