'''
utils.py

This python module contains useful functions that are needed for the
 CrystalGrowthTracker application.

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
# set up linting conditions
# pylint: disable = c-extension-no-member

import socket
import datetime

from sys import platform as _platform
import array as arr
import PyQt5.QtGui as qg

import cv2
import numpy as np

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

def nparray_to_qimage(array, brg=False):
    """
    convert an image in numpy array format to a QImage (Qt editing type)

        Args:
            array (np.array uint=8) the numpy array
            brg (bool) if True is blue/red/green format, else RGB

        Returns:
            a QImage Qt image manipulation format
    """
    if brg:
        array = cv2.cvtColor(array, cv2.COLOR_BGR2RGB)

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
    if image.format() != qg.QImage.Format.Format_RGB32:
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

def find_hostname_and_ip():
    """Finds the hostname and IP address to go in the log file.

    Args:
       No arguments

    Returns:
       host (str): Name of the host machine executing the script.
       ip_address (str): IP adress of the machine that runs the script.
       operating_system (str): Operating system of the machine that runs the script.

    """
    host = 'undetermined'
    ip_address = 'undetermined'
    operating_system = 'undetermined'

    try:
        host = socket.gethostbyaddr(socket.gethostname())[0]
    except socket.herror:
        host = "undetermined"

    my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        # doesn't even have to be reachable
        my_socket.connect(('10.255.255.255', 1))
        ip_address = my_socket.getsockname()[0]
    except socket.error:
        ip_address = '127.0.0.1'
    finally:
        my_socket.close()

    if _platform in ("linux", "linux2"):
        # linux
        operating_system = 'Linux'
    elif _platform == "darwin":
        # MAC OS X
        operating_system = 'Mac OSX'
    elif _platform == "win32":
        # Windows
        operating_system = 'Windows'
    elif _platform == "win64":
    # Windows 64-bit
        operating_system = 'Windows'

    return host, ip_address, operating_system

def timestamp():
    ''' Gets the date and time from the operating system and turns it into
        a string used as a time stamp. This function allows consistency in the
        format of the time stamp string.
        Args:
            NONE
        Returns:
            timestamp (str):  In the format of year_month_day_hour_minute_second.
    '''
    return datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

def difference_to_distance(difference, scale):
    """
    convert a difference object to distance to

        Args:
            difference (ImageLineDifference) the difference
            scale (float) the pixel size

        Returns:
            the average seperation as a distance
    """
    return difference.average * scale

def difference_list_to_velocities(diff_list, scale, fps):
    """
    converts a list of (frame interval, difference) tuples to a list of velocities

        Args:
            diff_list (tuple(int, ImageLineDifference)) the list of inputs
            scale (float) the size of a pixel
            fps (int) the number of frames per second

        Returns:
            a list of velocities
    """
    velocities = []
    for frames, diff in diff_list:
        distance = difference_to_distance(diff, scale)
        time = frames/fps
        velocity = distance/time

        if velocity < 0.0:
            velocities.append(-velocity)
        else:
            velocities.append(velocity)

    return velocities

def rectangle_properties(rectangle):
    """
    find the top left, bottom right and centre of a rectangle
        Args:
            rectangle (QRect) the rectangle
        Returns:
            top left, top right, bottom left, bottom right, centre (QPoint)
    """
    top_left = rectangle.topLeft()
    top_right = rectangle.topRight()
    bottom_left = rectangle.bottomLeft()
    bottom_right = rectangle.bottomRight()
    ctr = top_left + bottom_right
    ctr /= 2

    return top_left, top_right, bottom_left, bottom_right, ctr

def qpoint_sepertation_squared(point_a, point_b):
    """
    find the square of the distance apart of two points
        Args:
            point_a (QPoint) first point
            point_b (QPoint) second point
        Returns:
            the square of the distance from a to b
    """
    difference = point_a - point_b
    return difference.x()*difference.x() + difference.y()*difference.y()

# For debugging
################

def qtransform_to_string(trans):
    """
    print out matrix
    """
    row1 = f"|{trans.m11():+.2f} {trans.m12():+.2f} {trans.m13():+.2f}|\n"
    row2 = f"|{trans.m21():+.2f} {trans.m22():+.2f} {trans.m23():+.2f}|\n"
    row3 = f"|{trans.m31():+.2f} {trans.m32():+.2f} {trans.m33():+.2f}|"
    return row1 + row2 + row3

def rectangle_to_string(rect):
    """
    print out rect
    """
    top_left = rect.topLeft()
    size = rect.size()
    return f"QRect({top_left.x()}, {top_left.y()}) ({size.width()}, {size.height()})"
