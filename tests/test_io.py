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
import tempfile
import pathlib

from cgt.io.writecsvreports import save_csv_project
from cgt.model.cgtproject import CGTProject
from tests.makeresults import make_results_object

class TestIO(unittest.TestCase):
    """
    tests of IO
    """

    def setUp(self):
        """
        build a full test class
        """
        self._project = CGTProject()
        self._project.init_new_project()
        self._project["results"] = make_results_object()

    def tearDown(self):
        """
        clean up
        """
        if isinstance(self._tmp_dir, tempfile.TemporaryDirectory):
            self._tmp_dir.cleanup()

    def test_write_read(self):
        """
        test output
        """
        # save to tmp file
        # read results
        # compare with existing
        self._tmp_dir = tempfile.TemporaryDirectory()
        self._project["proj_full_path"] = self._tmp_dir.name
        self._project["proj_name"] = "testing"

        save_csv_project(self._project)

        self.assert_file_names(pathlib.Path(self._tmp_dir.name))



    def assert_file_names(self, dir_path):
        """
        assert the correct number and names of output files
            Args:
                dir_path (pathlib.Path): the directory holding the output files
        """
        files = ["CGT_testing_lines.csv",
                 "CGT_testing_points.csv",
                 "CGT_testing_project_info.csv",
                 "CGT_testing_regions.csv"]

        contents = [x.name for x in dir_path.iterdir()]

        self.assertEqual(len(contents), 4, "wrong number of csv files")

        for file in files:
            self.assertIn(file, contents, "unknown file in csv directory")



if __name__ == "__main__":
    unittest.main(verbosity=2)
