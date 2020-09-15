# -*- coding: utf-8 -*-
"""
Created on Tuesday August 18 2020

module results provides storage classes for CGT results.
IO and analysis are provided seperatly.

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
# pylint: disable = E0401

from cgt.linesetsandframesstore import LineSetsAndFramesStore

class Crystal:
    """
    storage for the crystals identifed in the video, the class is a container
    for sets of lines, each set is indexed by the number of the video frame
    from which it was derived.
    """
    def __init__(self, notes=None, faces=None):
        """
        initalization function

            Args:
                region (Region) the video region holding the crystal

                faces (image_artifacts.ArtifactStore) the lines defining the faces
        """
        ## any notes associated with the crystal
        self._notes = notes

        ## ArtifactStore for the lines forming the faces indexed by frame number
        self._faces = LineSetsAndFramesStore()

        if faces is not None:
            self._faces = faces

    def add_faces(self, faces, frame_number):
        """
        add a list of faces and the frame number to the crystal

            Args:
                faces ([image_artifacts.ImageLineSegment]) list of lines

                frame_number (int) the frame number associate with the list
        """
        self._faces[frame_number] = faces

    @property
    def number_of_frames_held(self):
        """
        getter for the number of frames held

            Returns:
                number of frames (int)
        """
        return len(self._faces)

    @property
    def notes(self):
        """
        getter for any notes

            Returns:
                the notes or None
        """
        return self._notes

    @property
    def list_of_frame_numbers(self):
        """
        getter for the frames held

            Returns:
                the frames (dict_keys)
        """
        return self._faces.keys()

    def faces_in_frame(self, frame_number):
        """
        getter for the lines in a given frame

            Args:
                frame_number (int) the number of the frame

            Returns:
                the list of lines representing the faces in the frame
        """
        return self._faces[frame_number]

    def face_movement_distances(self, first_frame, second_frame):
        """
        getter for the distances the face have moved, in pixels, between the two frames

            Args:
                first_frame (int) number of the first frame, must be in store

                second_frame (int) number of the second frame, must be in store

            Returns
                a list of image_artifacts.ImageLineDifference objects holding the differences

        TODO implement this
        """
        return 0
