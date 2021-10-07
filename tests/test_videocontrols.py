'''
Created on Tue December 08 2020

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
'''
import unittest

import PyQt5.QtWidgets as qw
import PyQt5.Qt as qt
from PyQt5.QtTest import QTest, QSignalSpy

from cgt.gui.cgtvideocontrols import CGTVideoControls

class TestVideoControls(unittest.TestCase):
    """
    test the video control widget
    """

    def setUp(self):
        """
        build a full test class
        """
        ## the QApplication
        self.app = qw.QApplication([])

        ## the widget
        self._controller = CGTVideoControls()

    def tearDown(self):
        """
        remove
        """
        del self._controller

    def test_one_frame_forward(self):
        """
        test the controller emitts the step froward signal
        """
        spy = QSignalSpy(self._controller.one_frame_forward)
        QTest.mouseClick(self._controller._stepUpButton, qt.Qt.LeftButton)

        message = "the wrong number of signals emitted"
        self.assertEqual(len(spy), 1, message)

    def test_one_frame_backward(self):
        """
        test the controller emitts the the step back signal
        """
        spy = QSignalSpy(self._controller.one_frame_backward)
        QTest.mouseClick(self._controller._stepDownButton, qt.Qt.LeftButton)

        message = "the wrong number of signals emitted"
        self.assertEqual(len(spy), 1, message)

    def test_goto_end(self):
        """
        test the jump to last frame
        """
        spy = QSignalSpy(self._controller.start_end)
        QTest.mouseClick(self._controller._lastFrameButton, qt.Qt.LeftButton)

        message = "the wrong number of signals emitted"
        self.assertEqual(len(spy), 1, message)
        message = "signal argument is False (backward)"
        self.assertTrue(spy[0][0], message)

    def test_goto_start(self):
        """
        test the jump to first frame
        """
        spy = QSignalSpy(self._controller.start_end)
        QTest.mouseClick(self._controller._firstFrameButton, qt.Qt.LeftButton)

        message = "the wrong number of signals emitted"
        self.assertEqual(len(spy), 1, message)
        message = "signal argument is True (forward)"
        self.assertFalse(spy[0][0], message)
