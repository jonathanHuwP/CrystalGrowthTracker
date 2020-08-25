# -*- coding: utf-8 -*-
"""
Created on Tuesday August 18 2020

the functins are a demonstration of how to print out a results store

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

import cgt.videoanalysisresultsstore as vas
from cgt.crystal import Crystal
from cgt.region import Region
from imagepoint import ImagePoint
from imagelinesegment import ImageLineSegment

import sys
sys.path.insert(0, '..\\CrystalGrowthTracker')

def make_test_result():
    """
    factory function to procduce a Results object
    """
    source = vas.VideoSource("ladkj.mp4", 8, 500, 800, 600)
    regions = [make_region1(), make_region2()]

    return vas.VideoAnalysisResultsStore(source, regions=regions)

def make_region1():
    """
    factory function to produce a test crystal
    """

    line1 = ImageLineSegment(ImagePoint(50, 150),
                             ImagePoint(150, 50),
                             "01")

    line2 = ImageLineSegment(ImagePoint(50, 50),
                             ImagePoint(150, 150),
                             "02")


    tmp_crystal = Crystal(name="01")

    tmp_crystal.add_faces([line1, line2], 250)

    return Region(450, 200, 675, 500, 250, 500, [tmp_crystal])

def make_region2():
    """
    factory function to produce a test crystal
    """

    line1 = ImageLineSegment(ImagePoint(100, 200),
                             ImagePoint(250, 200),
                             "01")

    line2 = ImageLineSegment(ImagePoint(200, 150),
                             ImagePoint(200, 300),
                             "02")

    line1a = ImageLineSegment(ImagePoint(100, 225),
                              ImagePoint(250, 225),
                              "01")

    line2a = ImageLineSegment(ImagePoint(175, 150),
                              ImagePoint(175, 300),
                              "02")

    tmp_crystal = Crystal(name="02")

    tmp_crystal.add_faces([line1, line2], 250)
    tmp_crystal.add_faces([line1a, line2a], 500)

    return Region(350, 100, 575, 400, 150, 400, [tmp_crystal])

if __name__ == "__main__":
    results = make_test_result()

    for record in results.history:
        print(record)

    video = results.video
    print(video.name, video.frame_rate, video.length, video.width, video.height)

    for region in results.regions:
        print("Region")
        print(region.top_left_horizontal,
              region.top_left_vertical,
              region.bottom_right_horizontal,
              region.bottom_right_vertical,
              region.start_frame,
              region.end_frame)

        for crystal in region.crystals:
            print("Crystal {} has {} frames".format(crystal.name, crystal.number_of_frames_held))

            for frame in crystal.list_of_frame_numbers:
                print("\tframe number {}".format(frame))

                faces = crystal.faces_in_frame(frame)

                for face in faces:
                    print("\t\t{} ({} {}), ({}, {})".format(
                        face.label, face.start.x, face.start.y, face.end.x, face.end.y))
