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

import enum
import socket
import datetime

from sys import platform as _platform
import array as arr
import PyQt5.QtGui as qg
import PyQt5.QtCore as qc

import cv2
import numpy as np

class MarkerTypes(enum.IntEnum):
    """
    define the types of marker used in images
    """
    ## mark a line
    LINE = 1

    ## mark a point
    POINT = 2

    ## a region
    REGION=4

    ## not in any other.
    DECORATOR = 8

class ItemDataTypes(enum.IntEnum):
    """
    define the indices for storing data in QGraphicsItem
    """
    ## store for the type of data item
    ITEM_TYPE = 0

    ## store for parent hash code
    PARENT_HASH = 1

    ## store for the number of the frame in which the artifact was defined
    FRAME_NUMBER = 2

    ## the index number of the region in which the mark is defined
    REGION_INDEX = 3

    ## for a cross the centre point
    CROSS_CENTRE = 4

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

def make_positive_rect(corner, opposite_corner):
    """
    draw a rectangle with positive size (x, y) from two points
        Args:
            corner (QPointF) scene coordinates of a corner
            opposite_corner (QPointF) scene coordinates of the opposing corner
    """
    # get the width and height (strictly positive)
    width = abs(opposite_corner.x()-corner.x())
    height = abs(opposite_corner.y()-corner.y())

    # find the top left of the new adjusted rectangle
    top_left_x = min(opposite_corner.x(), corner.x())
    top_left_y = min(opposite_corner.y(), corner.y())

    return qc.QRectF(top_left_x, top_left_y, width, height)

def length_squared(point):
    """
    square of length from origin of a point
        Args:
            point (QPointF) the point
        Returns
            square of length
    """
    return point.x()*point.x() + point.y()*point.y()

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

def hash_marker(marker):
    """
    find hash code for marker
        Args:
            marker (QGraphicsItem) the item to hash
        Returns:
            hash code or None if not appropriate type
    """
    m_type = get_marker_type(marker)

    if m_type == MarkerTypes.LINE:
        return hash_graphics_line(marker)

    if m_type == MarkerTypes.POINT:
        return hash_graphics_point(marker)

    return None

def hash_graphics_line(line):
    """
    a hash function for QGraphicsLineItem,
        Args:
            line (QGraphicsLineItem) the line
        Returns:
            hash of tuple (line hash, position hash, frame)
    """
    hashes = (hash_qlinef(line.line()),
                          hash_qpointf(line.pos()),
                          hash(line.data(ItemDataTypes.FRAME_NUMBER)))

    return hash(hashes)

def hash_graphics_point(point):
    """
    a hash function for QGraphicsPathItem,
        Args:
            line (QGraphicsPathItem) the line
        Returns:
            hash of tuple (centre hash, position hash, frame number)
    """
    hashes = (hash_qpointf(point.data(ItemDataTypes.CROSS_CENTRE)),
              hash_qpointf(point.pos()),
              hash(point.data(ItemDataTypes.FRAME_NUMBER)))

    return hash(hashes)

def hash_qlinef(line):
    """
    a hash function for QLineF,
        Args:
            line (QLineF) the line
        Returns:
            hash of tuple formed from end point coordinates (x1, x2, y1, y2)
    """
    coords = (line.x1(), line.x2(), line.y1(), line.y2())
    return hash(coords)

def hash_qpointf(point):
    """
    a hash function for QPontF,
        Args:
            point (QpointF) the point
        Returns:
            hash of tuple formed from end point coordinates (x, y)
    """
    coords = (point.x(), point.y())
    return hash(coords)

def get_marker_type(item):
    """
    get the type enum of the item
        Args:
            item (QGraphicsItem)
        Returns:
            the type enum or None
    """
    return item.data(ItemDataTypes.ITEM_TYPE)

def get_parent_hash(item):
    """
    get the parent hash code of the item
        Args:
            item (QGraphicsItem)
        Returns:
            the parent hash code (int): 'p' if progenitor, or None
    """
    return item.data(ItemDataTypes.PARENT_HASH)

def get_frame(item):
    """
    get the frame number of the item
        Args:
            item (QGraphicsItem)
        Returns:
            the frame number (int), or None
    """
    return item.data(ItemDataTypes.FRAME_NUMBER)

def get_region(item):
    """
    get the index of the region in which the item is defined
        Args:
            item (QGraphicsItem)
        Returns:
            the region index (int), or None
    """
    return item.data(ItemDataTypes.REGION_INDEX)

def get_point_of_point(item):
    """
    get the centre point of a cross
        Args:
            item (QGraphicsItem)
        Returns:
            the centre point (QPontF), or None
    """
    return item.data(ItemDataTypes.CROSS_CENTRE)

def make_cross_path(point):
    """
    make the path object corresponding to a cross centred at a scene point
        Args:
            point (QPointF) location in scene coordinates
        Returns:
            the path (QPainterPath) for the cross
    """
    path = qg.QPainterPath()

    up_right = qc.QPointF(10.0, 10.0)
    up_left = qc.QPointF(-10.0, 10.0)

    path.moveTo(point)
    path.lineTo(point+up_right)
    path.moveTo(point)
    path.lineTo(point+up_left)
    path.moveTo(point)
    path.lineTo(point-up_right)
    path.moveTo(point)
    path.lineTo(point-up_left)

    return path

def cgt_intersection(centred_normal, clone):
    """
    find intersection of centred_normal and clone
        Args:
            centred_normal (QLineF) the normal vector
            clone (QLineF) the clone
        Returns:
            intersection (QPointF) the intersection point
            extensiong (QLineF) the extension to clone if needed, else None
    """
    ## based on Graphics Gems III's "Faster Line Segment Intersection"
    a = centred_normal.p2() - centred_normal.p1()
    b = clone.p1() - clone.p2()
    c = centred_normal.p1() - clone.p1()

    # test if parallel
    denominator = a.y() * b.x() - a.x() * b.y()
    if denominator == 0 or not math.isfinite(denominator):
        raise ArithmeticError("Clone line is parallel to parent")

    # find the intersection
    reciprocal = 1.0 / denominator
    na = (b.y() * c.x() - b.x() * c.y()) * reciprocal
    intersection = centred_normal.p1() + (a * na)

    # test if outside clone segmet and assign extension as required
    nb = (a.x() * c.y() - a.y() * c.x()) * reciprocal
    extension = None
    if nb < 0.0:
        extension = qc.QLineF(clone.p1(), intersection)
    elif nb > 1.0:
        extension = qc.QLineF(clone.p2(), intersection)

    return intersection, extension

def make_arrow_head(line, length_cutoff=10):
    """
    if line.length() > length_cutoff add a small triangle to the end
        Args:
            line (QLineF) the line
            length_cutoff (float) the minimum length for a head to be added
        Returns:
            QPolygon the triangle
    """
    if line.length() < length_cutoff:
        return None

    # make normal based at p2
    delta_t = (line.length()-10.0)/line.length()
    normal = line.normalVector()
    offset = line.pointAt(delta_t)-line.p1()
    offset_normal = qc.QLineF(normal.p1()+offset, normal.p2()+offset)

    opposit_normal = qc.QLineF(offset_normal.p1(), offset_normal.pointAt(-1.0))

    offset_normal.setLength(5.0)
    opposit_normal.setLength(5.0)

    return qg.QPolygonF([line.p2(), offset_normal.p2(), opposit_normal.p2()])

def make_arrow(line, clone):
    """
    make the arrow line between a line and a parallel clone
        Args:
            line (QLineF) the parent line
            clone (QLineF) the parallel clone line
        Returns:
            arrow_line (QLineF) the arrow line (p1, p2) as parent to clone
            extension (QLineF) the extension to clone, None if not needed
    """
    # make normal based at centre of parent line
    normal = line.normalVector()
    centre = line.center()
    offset = centre-line.p1()
    centred_normal = qc.QLineF(normal.p1()+offset, normal.p2()+offset)

    intersection, extension = cgt_intersection(centred_normal, clone)
    arrow = qc.QLineF(centre, intersection)

    return arrow, extension
