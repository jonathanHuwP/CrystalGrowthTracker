# -*- coding: utf-8 -*-
"""
Created on Mon Jul  6 13:08:59 2020

a class representing a line segement in both rectanglualr and polar formats, 
in pixmap coordinates, together with a storage class for such lines

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
import math

from collections import namedtuple

# datastruct for line in both (theta, r)  and (m, c) formats
BaseLine = namedtuple("BaseLine", 
                       ["start", "end", "theta", "r", "m", "c", "length"])

class PolarLine(BaseLine):
    """
    representation of a line in polar coordinates and gradient intercept coordinates
    
    Contents
    --------
    theta: float
        the angle the line makes with x axis
        
    r: float
        the shortes distance from the origin to the line
    """
        
    def equals(self, l2, e_theta=0.05, e_r=5.0):
        """
        equalitiy function for lines
    
        Parameters
        ----------
        self : PolarLine
            the first line.
        l2 : TYPE
            the second line.
        e_theta : float
            the epsilon value for the angle
        e_r : float
            the epsilon value for the distance to origin
    
        Returns
        -------
        True if the lines are equal within the epsilon values
        """
        e_theta = abs(e_theta)
        e_r = abs(e_r)
        
        t = False
        if abs(self.theta - l2.theta) <= e_theta:
            t = True
            
        r = False
        if abs(self.r - l2.r) <= e_r:
            r = True
     
        return t and r
    
    def point_to_line(self, p):
        """
        find the shortes distanc from p to the line
        """
        x = p[1]
        y = p[0]
        
        return abs(self.m*x - y + self.c)/math.sqrt(self.m*self.m + 1)
    
    def y_polar(self, x):
        """
        find the y value for an x value
        """
        y = self.r - x*math.cos(self.theta)
        y /= math.sin(self.theta)
        
        return y
        
    def y_linear(self, x):
        return self.m*x + self.c
    
    def x_polar(self, y):
        x = self.r - y*math.sin(self.theta)
        x /= math.cos(self.theta)
        
        return x
    
    def x_linear(self, y):
        return (y-self.c)/self.m
        
    
class PolarLineList(list):
    """
    Storage for lines in polar form
    """
    def __init__(self, e_theta=0.05, e_r=5.0):
        """
        initalize the list

        Parameters
        ----------
        e_theta : float, optional
            the epsilon value for the theta comparison. The default is 0.05.
        e_r : float, optional
            the epsilon value for the r compaison. The default is 5.0.
        Returns
        -------
        None.
        """
        self._e_theta = e_theta
        self._e_r = e_r

    @property
    def epsilon_theta(self):
        
        return self._e_theta
    
    @property
    def epsilon_r(self):
        return self._e_r
    
    def append(self, o):
        """
        Overridden method will eliminate duplicates storing the longest

        Parameters
        ----------
        o : PolarLine
            the ploar line to be stored.
        Throws
        ------
        exception if not PolarLine object

        Returns
        -------
        None.
        """
        if not isinstance(o, PolarLine):
            s = "Attempt to stort type {}, in PolarLineList".format(
                type(o))
            raise TypeError(s)
            
        if not len(self):
            super().append(o)
            
        match = self.find_match(o)
        
        if match is None:
            super().append(o)
        elif o.length > match.length:
            self.remove(match)
            super().append(o)
            
    def find_match(self, o):
        """
        find the first PolarLine that matches

        Parameters
        ----------
        o : PolarLine
            the target for which a match is sought.

        Returns
        -------
        the match if one is found, else None.
        """
        
        for line in self:
            if line.equals(o):
                return line
        
        return None
        
        

    
def line_length(start, end):
    """
    find length of line
    """
    dx = start[1] - end[1]
    dy = start[0] - end[0]
    
    return math.sqrt((dx*dx) + (dy*dy))

def gradient(start, end):
    import sys
    """
    Find the gradient of a line segment 

    Parameters
    ----------
    start : tuple
        start point
    end : tuple
        end point

    Returns
    -------
    Float
        the gradient
    """
 
    dx = start[1] - end[1]
    dy = start[0] - end[0]
    
    if dx == 0:
        return sys.float_info.max
    else:
        return float(dy)/float(dx)
        
def y_intercept(point, grad):
    """
    find the y intercept of a line (y - m*x)

    Parameters
    ----------
    point : tuple
        a point on the line.
    grad : float
        the gradient.

    Returns
    -------
    float
        the y intercept.
    """
    import sys
    if grad == sys.float_info.max:
        return sys.float_info.max
    else:
        return float(point[0]) - grad*float(point[1])

def line_to_theta_r(start, end):
    """
    convert a line from (start, end) to (theta, r) parameters, where
    r it the shortes distance from the line to the orgin
    theta is the anti-clockwise angle from the x-axis to the shortes distane line
    Parameters
    ----------
    start : tuple
        start point
    end : tuple
        end point

    Returns
    -------
    float: theta, float r
    """

    
    grad = gradient(start, end)
    theta = math.atan(grad)
    
    y_inter = y_intercept(start, grad)
    r = abs(y_inter)/math.sqrt(grad*grad + 1.0)
    
    return PolarLine(
        start, end, theta, r, grad, y_inter, line_length(start, end))

## TESTING FUNCTIONS
####################

def make_lines():
    classifications = ["A1", "B1", "A1", "B2", "A2", 
                       "A1", "B1", "A2", "A2",  "A2"]
    
    lines = []
    lines.append(
        PolarLine((80,194), (41,125), 
                  0.514451313, 25.8140807, 
                  0.5652, 52.4615, 79.25906888))
    lines.append(
        PolarLine((90,208), (138,122), 
                  -0.509070888, 179.9599543, 
                  -0.5581, -369.2500, 98.48857802))
    lines.append(
        PolarLine((47,135), (35,113), 
                  0.499346722, 23.38394571, 
                  0.5455, 48.8333, 25.059928))
    lines.append(
        PolarLine((35,112), (87,19), 
                  -0.509833229, 85.20845626, 
                  -0.5591, -174.5962, 106.5504575))
    lines.append(
        PolarLine((133,95), (112,56), 
                  0.493941369, 72.0631731, 
                  0.5385, 152.0000, 44.29446918))
    lines.append(
        PolarLine((86,206), (69,175), 
                  0.501604054, 23.64565076, 
                  0.5484, 49.1765, 35.35533906))
    lines.append(
        PolarLine((117,161), (143,114), 
                  -0.505290188, 180.312866, 
                  -0.5532, -372.5000, 53.71219601))
    lines.append(
        PolarLine((114,61), (98,32), 
                  0.504165961, 70.34813806, 
                  0.5517, 145.6250, 33.12099032))
    lines.append(
        PolarLine((104,42), (91,19), 
                  0.514451313, 69.87213045, 
                  0.5652, 142.0000, 26.41968963))
    lines.append(
        PolarLine((143,112), (130,88), 
                  0.496422753, 72.39503858, 
                  1.8342, -82.4555, 27.29468813))

    return lines, classifications

def test():
    lines, classifications = make_lines()
    
    p_lines = PolarLineList()
    
    type_flag = False
    try:
        #pass
        p_lines.append(7)
    except TypeError as te:
        type_flag = True
        print("Type Error caught: ", str(te))
        
    if not type_flag:
        print("Error type error not caught")
    
    print("RAW LINES")
    for i in range(len(lines)):
        p_lines.append(lines[i])
        print("{} => {}".format(lines[i], classifications[i]))
        
    print("\nPROCESSED LINES")
    for line in p_lines:
        print(line)

if __name__ == "__main__":
    test()