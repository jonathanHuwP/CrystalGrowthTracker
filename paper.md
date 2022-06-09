---
title: 'CrystalGrowthTracker: A Python package to analyse crystal face advancement rates from time lapse synchrotron radiography'
tags:
  - Python
  - video processing
  - crystal growth
  - synchrotron radiation
authors:
  - name: Joanna Leng^[co-first author]
    orcid: 0000-0001-9790-162X
    affiliation: "1,3"
  - name: Jonathan H. Pickering^[co-first author]
    affiliation: "2,3"
    orcid: 0000-0001-5283-8065
  - name: Sven L. M. Schroeder
    affiliation: "4,5,6,7"
  - name: Gunjen Das
    affiliation: "4,5,6,7"
affiliations:
 - name: EPSRC Research Fellow in Software Engineering
   index: 1
 - name: Research Fellow in Software Engineering
   index: 2
 - name: School of Computer Science, University of Leeds, Leeds, LS2 9JT, UK
   index: 3
 - name: School of Chemical and Process Engineering, University of Leeds, LS2 9JT, UK
   index: 4
 - name: Diamond Light Source Ltd, Oxfordshire, OX11 0DE, UK
   index: 5
 - name: Research Complex at Harwell, Oxfordshire, OX11 0FA, Uk
   index: 6
 - name: EPSRC Centre for Innovative Manufacturing in Continuous Manufacturing and Advanced Crystallisation, University of Strathclyde, G1 1RD, UK
   index: 7
date: 15 October 2021
bibliography: paper.bib
---

# Summary

X-ray synchrotron radiation allows the investigation of many physical processes in unprecedented ways. One application, important to the fine chemicals industry, is charaterizing the early stages of crystallization.  To aid chemical engineers working in this area we developed the CrystalGrowthTracker package.  It allows crystals to be found in videos and their growth rates measured.  We hope that this work can provide the basis for further fully automated systems.

# Statement of Need

Much of the output of global fine chemicals industries consists of crystalline powders produced by precipitation from solution.  Since the geometry of a crystal is the result of differential growth rates on different crystal planes, there is great commercial interest in studying the growth rates of crystal faces in the early stages of crystallization.  One approach is to use the X-rays of synchrotron radiation [@Baruchel2013] to produce shadowgraphs of crystals precipitating onto a substrate.  Videos of the shadow graphs first need enhancement using the packages such as Euler’s Magnifier [@Wu12Eulerian] and some statistical analysis of the raw video is desirable to find regions of interest.  **CrystalGrowthTracker** has been developed to assist in the analysis of videos of the raw and enhanced videos.

# Design

Although the obvious approach would be to use image analysis and machine learning, the relatively noisy data, the limited number of data sets and the need for verifiable results lead to a manual approach.  User analysis of video required the package to be based on a graphical user interface (GUI).  Finally the users would need to be able to download and run the package on any machine, so the package was developed using Python and PyQt5, from Riverbank Computing Limited (https://riverbankcomputing.com/about), within the conda package management system.  The use of Qt naturally leads to an object orientated architecture.

The package must allow the user to load two videos, the raw and the enhanced, and must provide the following functions.

1.  Analyse and display intensity statistics of the raw video, to assist selection of times of interest.
2.  Play enhanced video and allow the selection of regions of interest.
3.  In regions of interest allow features to be marked up on a given frame.  The markers being, lines for crystal faces, or points for other features.
4.  Change the frame of a region of interest and move the markers to follow the underlying feature.
5.  Use time and space calibration data to calculate the true speed of the marker motions.
6.  Store the above data in an open human readable format and present a report in HTML.

# Functionalities

A model-view-controller (MVC) software architecture [@mvc88krasne] was used, in which the view and the controller were merged into the main widget.  The video was accessed via a VideoSource object, which was held by the main window, together with project data, and results objects. These objects constitute the MVC architecture model and were made available to the widgets carrying out user functions by getter methods.  These widgets were themselves held by the main window in a tab widget.

The VideoSource object accessed the video via the ffmpeg package (https://www.ffmpeg.org/), which was encapsulated in a using the subprocess module. The frame access had to be in terms of time rather than frame number as when accessing a specified frame number ffmpeg scans the entire video to count frames from the start.  The widgets requiring video stored their own time in the video and when playing called for the frame at the next time step.  No effort was made to play at the correct number of frames per second.

Project data and results are saved in comma-separated value (CSV) files handled by an input-output module using the Python csv module.  The results of a project can be saved in a HTML report, which can be viewed using the report tab widget. The HTML was written by a report writer module using offscreen rendering for the associated graphics.

The video is displayed using a QGraphicsView with an associated QGraphicsScene, which together provide a scene-graph and view. Video is displayed as a QPixmap at depth zero in the scene, and the user markings are QGrapicsItems at depth one (above the pixmap). A zoom feature is provided by scaling the view matrix in the QGraphicsView.

The user was able to add markers to image features in a single frame of the video, then advance to a new frame and drag clones of the markers to the features new locations.  The markers were graphics items augmented to hold their frame numbers and the identity of their parent.  Calculating the speeds of motion consisted of ordering the chains of cloned graphics items by frame number, finding the displacements in pixel coordinates, converting the pixel distances to real distances using the scaling factor. The pixels are assumed to be square as individual x-ray sensors in the array were square. Frame number intervals are converted to times and speeds calculated.

# Testing, Documentation and Linting

A test suite is provided, that utilizes the Python unittest module. The Qt QTest object is used to simulate IO events, and the capture the resultant signals. The tests can be run using unittest from the command line or all tests can execute using the run_test tool, which can also save the results to a CSV file.  A separate test was developed for the VidoeSource, as unittest itself can only test the call and responce to a subprocess call by mocking the subprocess.

Doxygen was used to generate documentation from source code comments.  The code was developed using the Pylint static code analysis tool, for which a runner script was developed. The script runs Pylint on all files, with the output displayed in the shell tool window or saved to CSV file.

# Availability
The software can be obtained from [GitHub](https://github.com/jonathanHuwP/CrystalGrowthTracker) under an Apache License.

# Acknowledgement
This work was funded by Joanna Leng's EPSRC funded RSE Fellowship (EP/R025819/1).
