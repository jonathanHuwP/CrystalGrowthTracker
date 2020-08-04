# -*- coding: utf-8 -*-
"""
Created on Tuesday July 21 13:42: 2020

classes for representing points and line segments in pixmap coordinates

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

import numpy as np
from collections import namedtuple

# data-structs for a line segment defined by its end points,
# which must be in pixel coordinages of the underlying image, 
# in order to allow for the math to remain correct while the 
#user zooms in or out on the image

#datastruct for an image point
ImagePointBase = namedtuple("ImagePointBase", ["x", "y"])

class ImagePoint(ImagePointBase):
    """
    class for storing and manipulating a point in the image
    """
    @property
    def floatY(self):
        """
        getter for float value of Y
        """
        return np.float64(self.y)
    
    @property
    def floatX(self):
        """
        getter for float value of X
        """
        return np.float64(self.x)
    
    @property
    def floatCopy(self):
        """
        make a copy with floating point numbers
        """
        return ImagePoint(self.floatX, self.floatY)

    @property
    def vectorLength2(self):
        """
        getter for the square of the length
        """
        x = self.floatX
        y = self.floatY
        
        return x*x + y*y
    
    @property
    def vectorLength(self):
        """
        getter for the length
        """
        return np.sqrt(self.vectorLength2)
    
    def scale(self, zoom):
        """
        make and return a scaled copy
        """
        return ImagePoint(self.x*zoom, self.y*zoom)
    
    def distanceFrom(self, rhs):
        """
        find the distance from self to a point
        
        Parameters
        ----------
        rhs: ImagePoint
            the target point
            
        Returns
        -------
            distance between self and rhs
        """
        tmp = self - rhs
        return tmp.vectorLength
    
    def __add__(self, rhs):
        """
        vector addition
        """
        return ImagePoint(self.floatX + rhs.floatX, self.floatY + rhs.floatY)

    def __sub__(self, rhs):
        """
        vector subtraction
        """
        return ImagePoint(self.floatX - rhs.floatX, self.floatY - rhs.floatY)
    
    def __mul__(self, rhs):
        """ 
        dot product
        """
        return self.floatX*rhs.floatX + self.floatY*rhs.floatY
    
    def __div__(self, rhs):
        """
        divide x and y by factor 

        Parameters
        ----------
        rhs : number
            the factor by which the components are to be devided.

        Returns
        -------
        normalized floating point copy
        """
        return ImagePoint(self.floatX/rhs, self.floatY/rhs)
    
    @property
    def normalize(self):
        """
        return a normalized floating point copy
        """
        l = self.vectorLength
        return ImagePoint(self.floatX/l, self.floatY/l)
    
    def __str__(self):
        """
        make a string representation of the object
        """
        return "Point({}, {})".format(self.x, self.y)
        
# datastruct for a directed line segment displayed on an image
# start the start point
# end the end point
# label the string identifying the line
ImageLineBase = namedtuple("ImageLineBase", ["start", "end", "label"])

class ImageLineSegment(ImageLineBase):
    
    def relabel(self, label):
        """
        return copy with a different label

        Parameters
        ----------
        label : string
            the new label.

        Returns
        -------
        ImageLineSegment
            copy of same line segment with new label.
        """
        return ImageLineSegment(self.start, self.end, label)
    
    def scale(self, zoom, new_label=None):
        """
        make scaled copy

        Parameters
        ----------
        zoom : number
            the scale factor.
        new_label : string, optional
            a new lable. The default is None.

        Returns
        -------
        ImageLineSegment
            scaled copy of line segment.
        """
        x0 = np.uint32(np.round(self.start.x * zoom))
        y0 = np.uint32(np.round(self.start.y * zoom))
        
        x1 = np.uint32(np.round(self.end.x * zoom))
        y1 = np.uint32(np.round(self.end.y * zoom))
        
        start = ImagePoint(x0, y0)
        end   = ImagePoint(x1, y1)
        
        if new_label is None:
            return ImageLineSegment(start, end, self.label)
        else:
            return ImageLineSegment(start, end, new_label)
    
    def shift(self, shift_vector, new_label=None):
        """
        make shifted copy

        Parameters
        ----------
        zoom : ImagePoint
            the shift vector.
        new_label : string, optional
            a new lable. The default is None.

        Returns
        -------
        ImageLineSegment
            shifted copy of line segment.
        """
        x0 = self.start.x + shift_vector.x
        y0 = self.start.y + shift_vector.y
        
        x1 = self.end.x + shift_vector.x
        y1 = self.end.y + shift_vector.y
        
        start = ImagePoint(x0, y0)
        end   = ImagePoint(x1, y1)
        if new_label is None:
            return ImageLineSegment(start, end, self.label)
        else:
            return ImageLineSegment(start, end, new_label)
    
    def newStart(self, new_s, new_label=None):
        """
        make a copy with a new start position

        Parameters
        ----------
        new_s : ImagePoint
            the new start positin.
        new_label : string, optional
            a new lable. The default is None.

        Returns
        -------
        ImageLineSegment
            altered copy of line segment.
        """
        if new_label is None:
            return ImageLineSegment(new_s, self.end, self.label)
        else:
            return ImageLineSegment(new_s, self.end, new_label)
    
    def newEnd(self, new_e, new_label=None):
        """
        make a copy with a new end position

        Parameters
        ----------
        new_e : ImagePoint
            the new end positin.
        new_label : string, optional
            a new lable. The default is None.

        Returns
        -------
        ImageLineSegment
            altered copy of line segment.
        """
        if new_label is None:
            return ImageLineSegment(self.start, new_e, self.label)
        else:
            return ImageLineSegment(self.start, new_e, new_label)
    
    def distancePointToLine(self, point):
        """
        find the distance from a point to the line, 

        Parameters
        ----------
        point : pqqt point
            the centre of the region.
        radius : int
            the region will be a square of size (radius+1)^2.

        Returns
        -------
        numpy.float64
            min distance of point from line in pixels.
        """
        # deal with degenerate case 
        if self.isVertical:
            return abs(self.start.floatX - np.float64(point.x()))
        
        # calculate y - mx -c = 0
        m = np.float64(self.dy)/np.float64(self.dx)
        c = self.start.floatY - m * self.start.floatX
        
        #pt(xp, yp) d = (yp-mxp-c)/sqrt(1^2 + m^2)
        lower = np.sqrt(1.0 + m*m)        
        upper = abs(np.float64(point.y()) - m*np.float64(point.x()) - c)
        
        return upper/lower
    
    @property
    def isVertical(self):
        """
        getter for verticality
        
        Returns
        -------
            True if vertical else false
        """
        if not self.dx:
            return True
        else:
            return False
        
    @property
    def dx(self):
        """
        getter for change in x
        
        Returns
        -------
            change in x between start and end
        """
        return np.int64(self.start.x) - np.int64(self.end.x)
    
    @property
    def dy(self):
        """
        getter for change in x
        
        Returns
        -------
            change in x between start and end
        """    
        return np.int64(self.start.y) - np.int64(self.end.y)
    
    @property
    def normalLine(self):
        """
        find the normal line given by (start, (-dy, dx))

        Returns
        -------
        ImagePoint.
            the normal line
        """
        
        label = "{}-normal".format(self.label)
        end = ImagePoint(-self.dy, self.dx)
        
        return ImageLineSegment(self.start, end, label)
    
    @property
    def vectorDirection(self):
        """
        the dirction of the line as a vector

        Returns
        -------
        ImagePoint
            the line direction.
        """        
        return self.end - self.start
    
    def isClosestPointOnSegment(self, point):
        """
        find the point on the line closest to the target

        Parameters
        ----------
        point : ImagePoint
            the target.

        Returns
        -------
        tuple (bool, ImagePoint)
            the bool is true if the point is on the line segment else false.
        """
        
        vp = point - self.start
        vp = vp.floatCopy
        
        vd = self.vectorDirection.floatCopy
        vdn = vd.normalize

        d = vdn*vp
        offset = vdn.scale(d)
        closest = self.start + offset
        
        flag = True
        if d<=0.0:
            # point is befor start
            flag = False 
        elif offset.vectorLength2 > vd.vectorLength2:
            # point is beyone end
            flag = False
            
        return (flag, closest)
    
    def lineLabelEquals(self, line):
        """
        test equality of line labels
        
        Returns
        -------
            True if lines have the same label else false
        """
        return self.label == line.label

    def labelInSet(self, in_lines):
        """
        Find the first line with a matchin label, if no such return None
        """
        for line in in_lines:
            if self.lineLabelEquals(line):
                return line
            
        return None

    def __str__(self):
        """
        override Python.object user string representation.
        """
        return "Line(Start: {}, End {}, {})".format(
            self.start, self.end, self.label)
    
# base for the line segment differen data structure
DifferenceBase = namedtuple("DifferenceBase", ["start_d", "end_d", "lines_label"])

class ImageLineDifference(DifferenceBase):
    """
    data structure for differenced between two lines the data are:
    
    Contents
    --------
        start_d: float the distance apart of the start points
        end_d: float the distance apart of the end points
        lines_label: the joint label of the two lines
    """
    @property
    def average(self):
        """
        find the average of the start and end differences
        """
        return (self.start_d + self.end_d)/2.0

class ArtifactStore(dict):
    """
    a store for the sets of lines used in the analysis of one crystal in one video
    """
    def __init__(self, name):
        """
        initalize the class
        
        Parameters
        ----------
        name: string
            a name uniquily identifying the video and crystal
        """
        
        self._name = name
        
    @property
    def name(self):
        """
        getter for the name
        """
        return self._name
    
    def differences(self, key0, key1):
        """
        find the differenced between the equivalent lines in two sets, 
        equivalence based on the lines own labels
        
        Parameters
        ----------
        key0: dictionary key
            the key for the first set of lines
        key1: dictionary key
            the key for the second set of lines
            
        Returns
        -------
        
        
        """
        tmp = self.matchPairs(key0, key1)
        
        diffs = []
        for i in tmp:
            sd = i[0].start.distanceFrom(i[1].start)
            ed = i[0].end.distanceFrom(i[1].end)
            diffs.append(ImageLineDifference(sd, ed, i[0].label))
            
        return diffs
    
    def matchPairs(self, key0, key1):
        """
        returns a list of pairs each holding a line from the list at key0,
        and the matching line from the list at key1

        Parameters
        ----------
        key0 : TYPE
            the first time key.
        key1 : TYPE
            the second time key.

        Returns
        -------
        a list of pairs
        """
        
        tmp = []
        for i in self[key0]:
            l = i.labelInSet(self[key1])
            if l is not None:
                tmp.append((i, l))
                
        return tmp

## TESTING
class altQPoint():
    #substitute for qpqtcore QPoint 
    def __init__(self, x, y):
        self._x = x
        self._y = y
        
    def x(self):
        return self._x
    
    def y(self):
        return self._y
    
    def __repr__(self):
        return "({}, {})".format(self._x, self._y)
    
def test():
    st = ImagePoint(100, 200)
    ed = ImagePoint(200, 300)
    
    line = ImageLineSegment(st, ed, "test00")
    
    print(line)
    if line.isVertical:
        print("vertical")
    else:
        print("not vertical")
        
    print(line.dy)
    
    tmp = altQPoint(100, 100)
    
    print("{} -> {}".format(tmp, line.distancePointToLine(tmp)))
        
    
if __name__ == "__main__":
    test()             
