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
  - name: Gunjan Das
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

X-ray synchrotron radiation allows the investigation of many physical processes in unprecedented ways. One application, important to the fine chemicals industry, is charaterizing the early stages of crystallization.  To aid chemical engineers working in this area we developed the CrystalGrowthTracker package.  It allows crystals to be found in videos and their growth rates measured.  We hope that this work can provide the basis for fully automated and 3D systems.

# Statement of Need

Much of the output of global fine chemicals industries consists of crystalline powders produced by precipitation from solution.  Since the geometry of a crystal is the result of differential growth rates on different crystal planes, there is great commercial interest in studying the growth rates of crystal faces in the early stages of crystallization.  One approach is to use the X-rays of synchrotron radiation [@Baruchel2013] to produce 2D shadowgraphs of crystals precipitating onto a substrate.

Videos of the shadow graphs first need enhancement using packages such as Euler’s Magnifier [@Wu12Eulerian] and some statistical analysis of the raw video is desirable to find regions of interest.  **CrystalGrowthTracker** has been developed to assist in the analysis of videos of the raw and enhanced videos.  The package was developed by Leng and Pickering, with specifications provided by Schroeder, and beta tested by Das, who prsented on the project [@das:bca21],[@das:isic21]. Details of the data collection can be found in [@10.1117/12.2530698].

# Design

Although the obvious approach would be to use image analysis and machine learning, the relatively noisy data, the limited number of data sets and the need for verifiable results lead to a manual approach.  User analysis of video required the package to have a graphical user interface (GUI).  Finally the users needed to be able to download and run the package on any machine, so the package was developed using Python and PyQt5, from Riverbank Computing Limited [@web:riverbank], within the conda package management system.  The use of Qt naturally leads to an object orientated architecture.

The package allows the user to load two videos, raw and enhanced, and provides the following functionality:

1.  Easy install and uninstall plus availablity of a translation package.
2.  Analyse and display intensity statistics of the raw video, to assist selection of times of interest.
3.  Play enhanced video and allow the selection of regions of interest.
4.  In regions of interest allow features to be marked up on a given frame.  The markers being, lines for crystal faces, or points for other features.
5.  Change the frame of a region of interest and move the markers to follow the underlying feature.
6.  Use time and space calibration data to calculate the true speed of the marker motions.
7.  Store the above data in an open human readable format and present a report in HTML.

# Functionality

Videos documenting the [install](@installVid), [uninstall](@uninstallVid) and [operation](@operateVid) of the package are available on YouTube.  Sample video data is available via [Zenodo](@zenodoSample).

A model-view-controller (MVC) software architecture [@mvc88krasne] was used, in which the view and the controller were merged into the main widget.  The video was accessed via a VideoSource object, which was held by the main window, together with project data, and results objects. These objects constitute a MVC architecture and were made available to the widgets carrying out user functions by getter methods.  These widgets were themselves held by the main window in a tab widget.

The VideoSource object accessed the video via the ffmpeg package [@web:ffmpeg], which was encapsulated in a subprocess. The frame access had to be in terms of time rather than frame number as when accessing a specified frame number ffmpeg scans the entire video to count frames from the start.  The widgets requiring video stored their current video-play-time and when playing called for the frame at the next time-step.  No effort was made to play at the correct number of frames per second.

Project data and results were saved in comma-separated value (CSV) files handled by an input-output module using the Python csv module.  The results of a project can be saved in a HTML report, which can be viewed using the report tab widget. The HTML was written by a report writer module using offscreen rendering for the associated graphics.

The video was displayed using a QGraphicsView with an associated QGraphicsScene, which together provide a scene-graph and view. Video was displayed as a QPixmap at depth zero in the scene, and the user crystal-face-markers are QGrapicsItems at a depth with a positive value, above the pixmap. A zoom feature is provided by scaling the view matrix in the QGraphicsView.

The user was able to add a marker to an image feature in a single key-frame of the video, then advance to a new key-frame and drag a clone of the marker to the feature's new locations.  The markers were graphics items augmented to hold their frame numbers and the identity of their parent.  Calculating the speeds of motion consisted of ordering the chains of cloned graphics items by frame number, finding the displacements in pixel coordinates, converting the pixel distances to real distances using the scaling factor.  The pixels are assumed to be square as individual x-ray sensors in the array were square. Frame number intervals are converted to times and speeds calculated.

# Testing, Documentation and Linting

A test suite is provided, that utilizes the Python unittest module.  Because the Python unittest module cannot run the ffmpeg subprocess a separate test was developed for these interactions.  The Qt QTest object is used to simulate IO events, and the capture the resultant signals.  The tests can be executed by adding the '-t' flag to the main cgt command line. The Python script run_test executes all tests and saves the results to a CSV file.

Doxygen was used to generate documentation from source code comments.  The code was developed using the Pylint static code analysis tool, for which a runner script was developed. The script runs Pylint on all files, with the output displayed in the shell tool window or saved to CSV file.

# Availability
The software can be obtained from [GitHub](https://github.com/jonathanHuwP/CrystalGrowthTracker) under an Apache License.

# Acknowledgement
The authors acknowledge I13-2 beamline at DLS for the beamtime (MT20984-1) and Research Complex at Harwell for generating the test data.  Funding was provided by: the Future Continuous Manufacturing and Advanced Crystallization (CMAC) Hub (EPSRC Grant EP/P006965/1); G. Das's PhD studentship from the University of Leeds; and Joanna Leng's EPSRC funded RSE Fellowship (EP/R025819/1).

# References
