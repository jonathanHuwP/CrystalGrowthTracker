## -*- coding: utf-8 -*-
"""
Created on Tue 27 Oct 2020

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
# pylint: disable = c-extension-no-member

import os
import tempfile
import pickle

class CGTAutoSave():
    """
    construct and use a binary autosave file
    """
    ## file type identification code
    _MAGIC_CODE = "cgt-01"

    def __init__(self, project=None):
        """
        set-up the object

            Args:
                project (CGTProject) the project data
        """
        ## store for the file path
        self._file_path = None

        if project is not None:
            self.new_project(project)

    def new_project(self, project):
        # get file, close file, save file path
        descriptor, file_path = tempfile.mkstemp(suffix='.cgtback',
                                                 prefix='.',
                                                 dir=project["proj_full_path"],
                                                 text=False)
        os.close(descriptor)

        # store the file path
        self._file_path = file_path

    def set_file_path(self, file_path):
        """
        setter for the file path

            Args:
                file_path (string)
        """
        self._file_path = file_path

    def get_file_path(self):
        """
        getter for the file path

            Returns:
                backup file path (string)
        """
        return self._file_path

    def save_data(self, project):
        """
        write data to the binary file

            Args:
                projcet (CGTProject) the data to be output
        """
        with open(self._file_path, 'w+b') as file:
            # delete existing contents
            file.truncate(0)

            # make tuple of project name and output
            data = (self._MAGIC_CODE,
                    project["proj_name"],
                    project)

            # save binary
            pickle.dump(data, file)

    def erase_data(self):
        """
        remove data from file but leave it in existance

            Returns:
                None
        """
        with open(self._file_path, 'w+b') as file:
            # delete existing contents
            file.truncate(0)

    def clean_up(self):
        """
        delete the file

            Returns:
                None
        """
        os.remove(self._file_path)

    @staticmethod
    def list_backups(dir_path):
        """
        make a list of all backup files, and project names

            Args:
                dir_path (string) full path to search directory

            Returns:
                list of tuples, each of which is (backup file, project name)
        """
        files = []
        output = []

        raw = os.listdir(dir_path)

        for item in raw:
            item = os.path.join(dir_path, item)
            if os.path.isfile(item) and item.endswith(".cgtback"):
                files.append(os.path.join(dir_path, item))

        for file in files:
            data = None

            # ignore empty or corrupt files
            try:
                data = pickle.load(open(file, 'rb'))
            except EOFError:
                pass

            if data is not None and len(data) > 1 and data[0] == CGTAutoSave._MAGIC_CODE:
                output.append((file, data[1]))

        return output

    @staticmethod
    def get_backup_project(file_path):
        """
        gets the contents of a backup file23

            Args:
                file_path (string) the file path including name

            Returns:
                (CGTProject) the project data
        """
        print("Autosave get_backup_project")
        try:
            tmp = pickle.load(open(file_path, 'rb'))
        except EOFError:
            return None

        if tmp[0] == CGTAutoSave._MAGIC_CODE:
            return tmp[2]

        return None
        
    @staticmethod
    def make_autosave_from_file(file_path):
        """
        make an autosave object with only a file name and path
        
            Args:
                file_path (string) the file path
                
            Returns:
                CGTAutosave object
        """
        tmp = CGTAutoSave()
        tmp.set_file_path(file_path)
        return tmp
        
    @staticmethod
    def make_autosave_from_project(project):
        """
        make an empty autosave object in a project directory
        
            Args:
                project (CGTProject) the project object
                
            Returns:
                CGTAutosave object
        """
        return CGTAutoSave(project)

    @staticmethod
    def make_autosave_and_save_from_project(project):
        """
        make an autosave object in the project directory and save
        the project to the file
        
            Args:
                project (CGTProject) the project object
                
            Returns:
                CGTAutosave object
        """
        tmp = CGTAutoSave(project)
        tmp.save_data(project)
        return tmp