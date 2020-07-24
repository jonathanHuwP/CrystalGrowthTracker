# DrawingLabel

This is a brief description of the DrawingLabel class its support classes and test harness

## Objective and Overview

The objective is to provide a graphical user interface allowing the user to draw lines about a growing feature in a still frame from a video, then load a frame from a different time (assuming no motion of the feature or the camera) and adjust the lines to the resize feature. Finally, the displacement of the lines, in pixel coordinates has to be calculated.

The software has to provide a means of:
1. displaying an image
2. allowing the user to draw straight lines on the image
3. allowing the user to modify the lines by shifting the whole line or the endpoints.
4. allowing the user to produce an ordered list of sets of lines in which each new set is produced by altering all (or some) of the lines in the previous set.
5. for any two sets in a list the relative motion between the pairs of lines must be calculated
6. the original lines must be uniquely labelled to allow identification
7. the lines must be able to be displayed with or without the labels. 
8. if required multiple sets of lines must be displayed in the same image
9. the user must be able to produce a picture (PNG, JPEG) of the image with the lines included

The software is to form part of a package written in PyQt5 so subclassing a QWidgets, which allows for user interaction by Qt signalling was the preferred option.

Finally, in calculating in pixel coordinates we have assumed that the pixels are square, so that ten pixels horizontally is the same as ten pixels vertically. In general this will not be true so we have to allow for a future upgrade in which the pixel calculations will use a two by two matrix to correct the stigmatism.

## Software Design

The top-level class was a subclass of QLabel called `DrawingLabel`, it was supported by several classes in the module `image_artifacts` that supplied functions for calculations on pixels

### `image_artifacts`

The lowest level of the software is the module `image_artifacts`, which provides classes representing: an image point; a line segment defined by two image points; and a container for ordered sets of line segments. These classes implement the mathematics required to provide for: 

1. picking by the user when selecting or adjusting lines
2. calculate the displacement between a pair of lines 

An important consideration is the conversion from integer coordinates of raw image points to floating point number required in the calculations.

In general, the classes are derived from Python `namedtuple` objects, available in the `collections` module. The named tuples hold the data and are subclassed to provide the required functions.

`ImagePoint` stores a pair of numbers as the (x, y) coordinates of a point on the image. It also provides overloaded mathematic operators (*+-/), vector length (origin to point), and a `distanceFrom` function that determines the distance from the point to another point.

`ImageLineSegment` stores a line segment as a pair of `ImagePoints` (start, end) and a label. It provides functions for the it provides functions that allow the generation of a new modified line (shift, shift start, shift end). It also provides a function that determines if an image point is withing a given distance of the line segment. The function implements the following algorithm, which returns (True, the closest point on the line) if satisfied and (False None) otherwise.

    test(point, epsilon)
        if self.start.distanceFrom(point) <= epsilon
            return (True, self.start)
            
        if self.end.distanceFrom(point) <= epsilon
            return (True, self.end)
            
        if self.distanceToPoint(point) > epsilon
            return (False, None)
            
        closest = self.closestPoint(point)
        
        if self.isInLineSegment(closest)
            return (True, closest)
        else
            return (False, None)
            
            
`ArtifactStore` provides storage for sets of lines and a function to compare any two sets, the result is a list of type `ImageLineDifference` a simple data type that stores the distance the start and end points have moved, and an average function. `ArtifactStore` itself is implemented as a subclass of the Python dictionary class (dict is subclassable since 2.2, you don't need to use `collections.UserDict` anymore). This allows each set of lines to be given an identifier, which can be related to the frame number of the video, also `ArtifactStore` has a name which allows the user to name features on the image and separate results for each feature. 

If the image pixels are not square and a correction is required, the matrix can be added t `ArtifactStore` and passed into the `distanceFrom` function of `ImagePoint` which is used to calculate the displacements. 

### `DrawingLabel`

`DrawingLabel` is a subclass of QLabel its basic function is to store the orignal image as a constant pixmap, which is redisplayed with or without lines as the user requires. The mouse down, up and moved callback functions have been overridden, which allows for handling user input. Internally newly created lines are stored in a list called `_linedBase`, when they are moved the modified copies are stored in a list `_linesNew`. 

`DrawingLabel's` behaviour is governed by state variables, defined using Python `enum.IntEnum`. These relate to how the user's inputs are handled and how the lines are stored. In creating mode, the user is allowed to draw lines; in adjusting the user can select existing lines and move them (whole line or just end points); in copying mode existing lines can be adjusted and are then copied to new set.

### TestHarness

The test harness provides a QDialog, showing the image at the top and a table of line separation distances at the bottom. A check box allows the user to select whether or not to view the line's labels. Radio buttons allow the user to select the states: drawing or adjusting lines; and creating or copying. Note when copying the drawing/adjusting is set to adjusting and disabled as drawing new lines in copying mode is not allowed.

To save an image click the "Save" button, this will output the image to a file called `my_image.png`

To fully test view the image draw some lines, then select the "Copying" state and adjust the lines. You now have the old lines in solid and the new lines in dashed. Click the "Calculate" button and the differences will populate the table in the lower part of the dialog.

The pixmap used is one of the scikit image module's data, if you prefer to use your own image comment out the code and add the following `self._drawing.setPixmap(qg.QPixmap("whatever.jpg"))`

## Running

To run you must first build the user interface class by running 

    pyuic5 .\DrawingLabelTestHarness.ui -o .\Ui_DrawingLabelTestHarness.py
    
Then run the main class

    python .\DrawingLabelTestHarness.py

## Known Bugs or Other Issues

1. it is possible for the user to move the mouse outside the image.
2. In copying mode the user can only make one adjustment to a line before having to accept or reject it. This prevents multiple adjustments, and is likely to infuriate users.
3. the Drawing/Adjusting and Creating/copying states should be combined.