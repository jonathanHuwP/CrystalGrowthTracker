"""
Created on Thursday 09 June 2022

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
from pathlib import Path
from setuptools import setup

def read(fname):
    """
    read and return contents of file:
        Args:
            fname (str): the file name
        Returns:
            (str) the contents of the file
    """
    return (Path(__file__).parent.joinpath(fname)).open(encoding='UTF-8').read()

setup(
    name='CrystalGrowthTracker',
    version='1.0.0',
    packages=['cgt',
             ],
    license='Apache 2.0, January 2004',
    description ='Measure crystal growth rates in x-ray shadowgraphs.',
    platforms="Windows10, Linux",
    long_description=read('README.md'),
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'cgt=cgt.main:main',
        ]
    }
    )
