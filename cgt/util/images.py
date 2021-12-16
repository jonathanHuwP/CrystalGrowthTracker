# -*- coding: utf-8 -*-
## @package images
# functions for converting images between different storage formats
#
# @copyright 2021 University of Leeds, Leeds, UK.
# @author j.h.pickering@leeds.ac.uk and j.leng@leeds.ac.uk
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
'''
# set up linting conditions
# pylint: disable = c-extension-no-member
import array as arr
import numpy as np

import PyQt5.QtGui as qg

def memview_3b_to_qpixmap(pixels, width, height):
    """
    convert a CPython array pixels (RGB unsingned char) to QPixmap

        Args:
            pixels (CPython array) the imput pixel array
            width (int) the width of the image in pixels
            height (int) the height of the image in pixels

        Returns:
            a QPixmap of the image
    """
    tmp = arr.array('B', pixels.reshape(pixels.size))

    im_format = qg.QImage.Format_RGB888

    image = qg.QImage(
        tmp,
        width,
        height,
        3*width,
        im_format)

    return qg.QPixmap.fromImage(image)

def nparray_to_qimage(array):
    """
    convert an image in numpy array format to a QImage (Qt editing type)
        Args:
            array (np.array uint=8) the numpy array
            brg (bool) if True is blue/red/green format, else RGB
        Returns:
            a QImage Qt image manipulation format
    """
    # set for Red/Green/Blue 8 bits each
    image_format = qg.QImage.Format_RGB888

    if array.shape[2] == 4:
        # Alpha/Red/Green/Blue 8 bits each
        image_format = qg.QImage.Format_ARGB32

    image = qg.QImage(
        array,
        array.shape[1],
        array.shape[0],
        array.shape[2]*array.shape[1],
        image_format)

    return image

def qimage_to_nparray(image):
    """
    convert a QImage (Qt editing type) to an np array
        Args:
            image (QImage) the image, assumed to be RGB
        Returns:
            np array (uint8) the array
    """
    if image.format() != qg.QImage.Format_RGB32:
        message = f"QImage not in Format_RGB32, actual {image.format()}"
        raise ValueError(message)
        #image = image.convertToFormat(qg.QImage.Format.Format_RGB32)

    if image.depth() != 32:
        raise ValueError(f"Image depth not 32, actual: {image.depth()}")

    size = image.size()
    width = size.width()
    height = size.height()

    # get pointer to pixels and set size in bits
    bits = image.bits()
    bits.setsize(width*height*image.depth())

    # this array will actually point to the data in image
    array = np.ndarray(shape=(height, width, image.depth()//8),
                       dtype=np.uint8,
                       buffer=bits)

    # make a deep copy so the array will survive when image deleted
    return array.copy()
