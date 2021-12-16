# -*- coding: utf-8 -*-
## @package testproject
# <PACKAGE DESCRIPTION>
#
# @copyright Jonathan Pickering and Joanna Leng, University of Leeds, Leeds, UK.
'''
Created on 05 Oct 2021

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
import unittest
import getpass

from cgt.util.utils import find_hostname_and_ip
from cgt.model.cgtproject import CGTProject

class TestProject(unittest.TestCase):
    """
    advanced tests of IO units
    """

    def setUp(self):
        """
        build a full test class
        """
        self._project = CGTProject()
        self._project.init_new_project()

    def tearDown(self):
        """
        delete widget
        """
        del self._project

    def test_create_project(self):
        """
        test if a new project is created correctly
        """
        host, ip_address, operating_system = find_hostname_and_ip()

        message = "wrong host name"
        self.assertEqual(self._project['host'], host, message)
        message = "wrong ip address"
        self.assertEqual(self._project['ip_address'], ip_address, message)
        message = "wrong operating system"
        self.assertEqual(self._project['operating_system'], operating_system, message)
        message = "wrong user name"
        self.assertEqual(self._project["start_user"], getpass.getuser(), message)

    def test_add_data(self):
        """
        ensure numeric data are not string
        """
        self._project["resolution"] = "8.1"
        self._project["frame_rate"] = "22"
        self._project.ensure_numeric()
        message = "error in resolution"
        self.assertEqual(self._project["resolution"], 8.1, message)
        message = "error in frame rate"
        self.assertEqual(self._project["frame_rate"], 22.0, message)
        message = "project not in changed state after new data"
        self.assertTrue(self._project.has_been_changed(), message)
        self._project.reset_changed()
        message = "project not in unchanged state after reset"
        self.assertFalse(self._project.has_been_changed(), message)

if __name__ == "__main__":
    unittest.main()
