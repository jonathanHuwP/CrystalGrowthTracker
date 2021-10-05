## -*- coding: utf-8 -*-
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
# set up linting conditions
# pylint: disable = c-extension-no-member
import socket
import datetime
import pathlib

from sys import platform as _platform
import array as arr
from math import (sqrt, isfinite)

import PyQt5.QtGui as qg
import PyQt5.QtCore as qc
import PyQt5.QtWidgets as qw

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

def find_hostname_and_ip():
    """
    Finds the hostname and IP address to go in the log file.
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
    '''
    Gets the date and time from the operating system and turns it into
    a string used as a time stamp. This function allows consistency in the
    format of the time stamp string.
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
    if denominator == 0 or not isfinite(denominator):
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

def perpendicular_dist_to_position(gline, scale):
    """
    find the distance to the position of a QGraphicsLine
        Args:
            gline (QGraphicsLine): the line
            scale (float): the pixel scale
    """
    unit_normal = gline.line().normalVector().unitVector()
    del_x = gline.pos().x()*unit_normal.dx()*scale
    del_y = gline.pos().y()*unit_normal.dy()*scale

    return sqrt(del_x*del_x + del_y*del_y)

def rect_to_tuple(rect):
    """
    convert a qrectangl to a tuple
        Args:
            rect (QRect)
        Returns:
            ((left, top, width, height))
    """
    array = []

    array.append(rect.left())
    array.append(rect.top())
    array.append(rect.width())
    array.append(rect.height())

    return array

def g_point_to_tuple(point):
    """
    convert the data in a QGraphicsPathItem reprsenting a point to a tuple
        Args:
            point (QGraphicsPathItem) the point for conversion
        Returns:
            list [x1, y1, px, py, frame]
    """
    array = []
    centre = point.data(ItemDataTypes.CROSS_CENTRE)
    position = point.pos()
    array.append(centre.x())
    array.append(centre.y())
    array.append(position.x())
    array.append(position.y())
    array.append(point.data(ItemDataTypes.FRAME_NUMBER))
    array.append(point.data(ItemDataTypes.REGION_INDEX))

    return array

def g_line_to_tuple(line):
    """
    convert the data in a QGraphicsLineItem to a tuple
        Args:
            line (QGraphicsLineItem) the line
        Returns:
            list [x1, y1, x2, y2, px, py, frame]
    """
    array = []
    array.append(line.line().x1())
    array.append(line.line().y1())
    array.append(line.line().x2())
    array.append(line.line().y2())
    array.append(line.pos().x())
    array.append(line.pos().y())
    array.append(line.data(ItemDataTypes.FRAME_NUMBER))
    array.append(line.data(ItemDataTypes.REGION_INDEX))

    return array

def list_to_g_point(point, pen):
    """
    convert the data in a list to a graphics point
        Args:
            point (list [ID, x, y, pos_x, pos_y, frame, region]) the point as list
            pen (QPen) the drawing pen
        Returns:
            QGraphicsPathItem
    """
    centre_x = float(point[1])
    centre_y = float(point[2])
    position_x = float(point[3])
    position_y = float(point[4])
    frame = int(point[5])
    region = int(point[6])

    centre = qc.QPointF(centre_x, centre_y)
    position = qc.QPointF(position_x, position_y)

    path = make_cross_path(centre)
    item = qw.QGraphicsPathItem(path)
    item.setPos(position)
    item.setData(ItemDataTypes.ITEM_TYPE, MarkerTypes.POINT)
    item.setData(ItemDataTypes.FRAME_NUMBER, frame)
    item.setData(ItemDataTypes.REGION_INDEX, region)
    item.setData(ItemDataTypes.CROSS_CENTRE, centre)
    item.setPen(pen)
    item.setZValue(1.0)

    return item

def list_to_g_line(line, pen):
    """
    convert the data in a list to a graphics line
        Args:
            line (list [ID, x1, y1, x2, y2, pos_x, pos_y, frame, region]) the line as list
            pen (QPen) the drawing pen
        Returns:
            QGraphicsLineItem
    """
    x1 = float(line[1])
    y1 = float(line[2])
    x2 = float(line[3])
    y2 = float(line[4])
    position_x = float(line[5])
    position_y = float(line[6])
    frame = int(line[7])
    region = int(line[8])

    position = qc.QPointF(position_x, position_y)

    item = qw.QGraphicsLineItem(x1, y1, x2, y2)
    item.setPos(position)
    item.setData(ItemDataTypes.ITEM_TYPE, MarkerTypes.LINE)
    item.setData(ItemDataTypes.FRAME_NUMBER, frame)
    item.setData(ItemDataTypes.REGION_INDEX, region)
    item.setPen(pen)
    item.setZValue(1.0)

    return item

def make_report_file_names(proj_full_path):
    """
    make the directory and file names for a report
        Args:
            proj_full_path (string): the path of the results directory
        Returns:
            report_dir (pathlib.Path)
            html_outfile (pathlib.Path)
            hash_file (pathlib.Path)
    """
    report_dir = pathlib.Path(proj_full_path).joinpath("report")
    html_outfile = report_dir.joinpath("report.html")
    hash_file = report_dir.joinpath("results_hash.json")

    return (report_dir, html_outfile, hash_file)

def get_rect_even_dimensions(rect_item, even_dimensions=True):
    """
    get the the graphics rectangle of the item, moved to position, with sides of even length
        Args:
            rect_item (QGraphicsRectItem)
            even_dimensions (bool): if False even dimensions are not enforced
        Returns
            (QRect): with even length sides
    """
    rect = rect_item.rect().toAlignedRect()
    pos = rect_item.pos().toPoint()
    rect.translate(pos)
    width = rect.width()
    height = rect.height()

    if not even_dimensions:
        return rect

    if width%2 == 1:
        rect.setWidth(width+1)

    if height%2 == 1:
        rect.setHeight(height+1)

    return rect
