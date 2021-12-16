# -*- coding: utf-8 -*-
## @package testvideocontrols
# <PACKAGE DESCRIPTION>
#
# @copyright Jonathan Pickering and Joanna Leng, University of Leeds, Leeds, UK.
'''
Created on Oct 2020

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
'''
# set up linting condition
# pylint: disable = protected-access
# pylint: disable = c-extension-no-member
# pylint: disable = no-name-in-module
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

    def test_initial_state(self):
        """
        test initialized ok
        """
        minimum, maximum = self._controller.get_range()
        self.assertEqual(minimum, 0, "minimum not zero")
        self.assertEqual(maximum, 99, "maximum not 99")

    def test_one_frame_forward(self):
        """
        test the controller emitts the step forward signal
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

    def test_goto_frame_button(self):
        """
        test goto button works
        """
        number = 27
        spy = QSignalSpy(self._controller.frame_changed)
        QTest.keyClicks(self._controller._gotoSpinBox, str(number))
        QTest.mouseClick(self._controller._goToButton, qt.Qt.LeftButton)

        message = "the wrong number of signals emitted"
        self.assertEqual(len(spy), 1, message)
        message = "signal argument is wrong"
        self.assertEqual(spy[0][0], number, message)

    def test_goto_frame_box(self):
        """
        test goto spinbox works
        """
        number = 27
        spy = QSignalSpy(self._controller.frame_changed)
        QTest.keyClicks(self._controller._gotoSpinBox, str(number))
        QTest.keyClick(self._controller._gotoSpinBox, qt.Qt.Key_Return)

        message = "the wrong number of signals emitted"
        self.assertEqual(len(spy), 1, message)
        message = "signal argument is wrong"
        self.assertEqual(spy[0][0], number, message)

    def test_play_pause(self):
        """
        test pause button works
        """
        spy = QSignalSpy(self._controller.pause)
        QTest.mouseClick(self._controller._pauseButton, qt.Qt.LeftButton)

        message = "the wrong number of signals emitted"
        self.assertEqual(len(spy), 1, message)

    def test_play_forwards(self):
        """
        test forwards button works
        """
        spy = QSignalSpy(self._controller.forwards)
        QTest.mouseClick(self._controller._forwardButton, qt.Qt.LeftButton)

        message = "the wrong number of signals emitted"
        self.assertEqual(len(spy), 1, message)

    def test_play_backwards(self):
        """
        test backwards button works
        """
        spy = QSignalSpy(self._controller.backwards)
        QTest.mouseClick(self._controller._backwardButton, qt.Qt.LeftButton)

        message = "the wrong number of signals emitted"
        self.assertEqual(len(spy), 1, message)

    def test_zoom_box(self):
        """
        test zoom spinbox works
        """
        number = 2.0
        spy = QSignalSpy(self._controller.zoom_value)
        self._controller._zoomSpinBox.clear()
        QTest.keyClicks(self._controller._zoomSpinBox, str(number))

        message = "the wrong number of signals emitted"
        self.assertEqual(len(spy), 1, message)
        message = "signal argument is wrong"
        self.assertEqual(spy[0][0], number, message)

    def test_slider(self):
        """
        test slider works
        """
        number = 44

        spy = QSignalSpy(self._controller.frame_changed)
        self._controller._frameSlider.setValue(number)
        QTest.mouseClick(self._controller._frameSlider, qt.Qt.LeftButton)

        message = "the wrong number of signals emitted"
        self.assertEqual(len(spy), 1, message)
        message = "signal argument is wrong"
        self.assertEqual(spy[0][0], number, message)

if __name__ == '__main__':
    unittest.main(verbosity=2)
