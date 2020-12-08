'''
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
from cgt.model.cgtproject import CGTProject
from cgt.io.readcsvreports import read_csv_project

def test_io(path):
    """
    TODO turn this into a proper io unit test
    """
    proj = CGTProject()

    read_csv_project(path, proj)

    results = proj["results"]
    print("Regions\n=======")
    for region in results.regions:
        print(region)
    print("\nLines\n======")
    for line in results.lines:
        print(line)
        for key in line.keys():
            print(f"\tFrame {key} => {line[key]}")

if __name__ == "__main__":
    test_io(r"C:\Users\jhp11\tmp\ns_02")