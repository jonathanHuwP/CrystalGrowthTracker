# -*- coding: utf-8 -*-
## @package mpl
# <PACKAGE DESCRIPTION>
#
# @copyright Jonathan Pickering and Joanna Leng, University of Leeds, Leeds, UK.
"""
Created on Friday 17 Sept 2021

Licensed under the Apache License, Version 2.0 (the "License"); you may not use
this file except in compliance with the License. You may obtain a copy of the
License at http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed
under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.

This work was funded by Joanna Leng's EPSRC funded RSE Fellowship (EP/R025819/1)

@copyright 2021
@author: j.h.pickering@leeds.ac.uk and j.leng@leeds.ac.uk
"""
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure

class MplCanvas(FigureCanvasQTAgg):
    """
    matplotlib drawing area for use with qt
    """
    def __init__(self, width=5, height=4, dpi=100):
        """
        initalize object
            Args:
                width (float): width in inches
                height (float); height in inches
                dpi (float): dots per inch
        """
        fig = Figure(figsize=(width, height), dpi=dpi)

        ## pointer the AxesSubplot
        self.axes = fig.add_subplot(111)

        super().__init__(fig)

class OffScreenRender(FigureCanvasAgg):
    """
    matplotlib drawing area for use with offscreen rendering
    """
    def __init__(self, width=5, height=4, dpi=100):
        """
        initalize object
            Args:
                width (float): width in inches
                height (float); height in inches
                dpi (float): dots per inch
        """
        fig = Figure(figsize=(width, height), dpi=dpi)

        ## pointer the AxesSubplot
        self.axes = fig.add_subplot(111)

        super().__init__(fig)

def make_mplcanvas(width=5, height=4, dpi=100, toolbar_flag=True):
    """
    make a QT canvas and, if chosen, a toolbar is
        Args:
            width (float): width in inches
            height (float); height in inches
            dpi (float): dots per inch
            toolbar_flag (bool): if true make a toolbar
        Returns:
            (MplCanvas, NavigationToolbar2QT): second term None if toolbar_flag is False
    """
    canvas = MplCanvas(width, height, dpi)
    toolbar = None

    if toolbar_flag:
        toolbar = NavigationToolbar(canvas, None)

    return canvas, toolbar

def render_graph(frames, canvas, frame=None):
    """
    render the graph of intesities against time
        Args:
            frames ([FrameStats]): the frame statistics
            canvas (mapplotlib.FigureCanvas): the canvas
            frame (int): the frame number, if valid provided frame line will be added
        Returns:
            pointer to frame line or None
    """
    means = [x.mean for x in frames]
    std_dev = [x.std_deviation for x in frames]

    upper = [means[a]+x for a, x in enumerate(std_dev)]
    lower = [means[a]-x for a, x in enumerate(std_dev)]
    x_vals = range(0, len(means))

    canvas.axes.plot(x_vals, means, label=r'$\mu$')
    canvas.axes.plot(x_vals, lower, label=r"-$\sigma$")
    canvas.axes.plot(x_vals, upper, label=r"$\sigma$")
    canvas.axes.fill_between(x_vals, lower, upper, alpha=0.2)

    frame_line = None
    if frame is not None and not frame < 0 and not frame >= len(frames):
        line_x = [frame, frame]
        line_y = [5, 250]
        frame_line = canvas.axes.plot(line_x, line_y)

    canvas.axes.set_xlabel('Frame')
    canvas.axes.set_ylabel('Pixel Intensity')
    canvas.axes.set_title('Mean Intensitites')
    canvas.axes.set_ylim(0, 256)

    canvas.axes.legend()

    canvas.draw()

    return frame_line

def render_prob_density(stats, canvas, frame):
    """
    plot the prob density
        Args:
            stats (VideoIntensityStats): the video statistics
            canvas (FigureCanvas): the drawing Canvas
            frame (int): the frame number
        Returns:
            pointer to line

    """
    frames = stats.get_frames()
    curve = canvas.axes.plot(stats.get_bins()[1:32],
                             frames[frame].bin_counts)

    canvas.axes.set_xlabel('Pixel Intensity')
    canvas.axes.set_ylabel('Proportion')
    canvas.axes.set_title(f'Pixel Intensities Frame {frame}')
    canvas.axes.set_xlim(0, 256)
    canvas.axes.set_ylim(0)
    canvas.axes.grid(True)

    canvas.draw()

    return curve

def update_density(plot, density_curve, stats, frame):
    """
    change the frame displayed in the density function plot
        Args:
            plot (MplCanvas): the canvas
            density_curve (matplotlib.lines.Line2D): the line
            stats (VideoIntensityStats): container for the statistics data
            frame (int): the frame number
    """
    if density_curve is None:
        return

    frames = stats.get_frames()
    density_curve[0].set_data(stats.get_bins()[1:32],
                              frames[frame].bin_counts)

    plot.draw()

def update_graph(plot, frame_line, frame):
    """
    update the frame line in the graph
        Args:
            plot (MplCanvas): the canvas
            frame_line (matplotlib.lines.Line2D): the line
            frame (int): the frame number
    """
    line_x = [frame, frame]
    line_y = [5, 250]
    frame_line[0].set_data(line_x, line_y)
    plot.draw()

def draw_displacements(canvas, lines, points, region):
    """
    draw the time displacement graphs
        Args:
            canvas (MplCanvas): the drawing canvas
            lines (): array of graphics line
            points (): array of grahics point
            region (int): the region
    """
    canvas.axes.cla()
    canvas.axes.set_title(f'Marker Displacements Frame {region}')
    canvas.axes.set_ylabel("Displacement (micron)")
    canvas.axes.set_xlabel("Frame (number)")

    for i, marker in enumerate(lines):
        displacements = [0.0]
        frames = [0]
        for dis in marker:
            new_dis = displacements[-1] + dis.get_length()
            displacements.append(new_dis)
            frames.append(dis.get_end())

        canvas.axes.plot(frames, displacements, label=f"Line {i}")

    for i, marker in enumerate(points):
        displacements = [0.0]
        frames = [0]
        for dis in marker:
            new_dis = displacements[-1] + dis.get_length()
            displacements.append(new_dis)
            frames.append(dis.get_end())

        canvas.axes.plot(frames, displacements, label=f"Point {i}")

    if len(lines) or len(points):
        canvas.axes.legend()

    canvas.draw()
