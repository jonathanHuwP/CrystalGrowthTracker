## -*- coding: utf-8 -*-
"""
Created on Sat June 19 2021

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
# set up linting conditions
# pylint: disable = c-extension-no-member

import pathlib

import PyQt5.QtWidgets as qw
import PyQt5.QtCore as qc
import PyQt5.QtGui as qg

from cgt.util.utils import make_report_file_names

class OffScreenRender():
    """
    an off-screen renderer for images
    """

    def __init__(self, project):
        """
        set up the object
            Args:
                project (CGTProject): the project data
        """
        ## the view
        self._view = qw.QGraphicsView()
        self._view.setScene(qw.QGraphicsScene())

        ## the current project
        self._project = project

    def list_pixmaps(self):
        """
        get a list of all the pixmaps
        """
        rpt_dir, _, _ = make_report_file_names(self._project["proj_full_path"])
        image_dir = rpt_dir.joinpath("images")
        images = [i for i in image_dir.iterdir() if i.suffix == ".ppm"]
        return images

    def render_region_images(self):
        """
        render the images defined in the project results
            Args:
                project (CGTProject): the project
        """
        images = self.list_pixmaps()
        region_images = [i for i in images if i.name.startswith("regions_")]

        names = []
        for file_path in region_images:
            names.append(self.make_image_with_regions(file_path, self._project["results"].get_regions()))

        return names

    def make_image_with_regions(self, file_path, regions):
        """
        make a image with the regions marked as
            Args:
                file_path (pathlib.Path): file path
                regions ([QGrapicsRectItem]): the regions of
        """
        self._view.scene().clear()

        file_name = str(file_path)
        pixmap = qg.QPixmap()
        if not pixmap.load(file_name):
            raise IOError(f"unable to read {file_name}")

        pixmap_item = self._view.scene().addPixmap(pixmap)
        pixmap_item.setZValue(-1.0)
        rect = pixmap_item.boundingRect()
        self._view.scene().setSceneRect(rect)

        for region in regions:
            self._view.scene().addRect(region.rect(), region.pen(), region.brush())

        image = self.make_image()
        head, _, tail = file_name.rpartition(".ppm")
        out_name = head + ".png" + tail
        image.save(out_name)

        return pathlib.Path(out_name)

    def make_image(self):
        """
        get an image of a whole scene
            Returns:
                QImage of everything within the scene-graph's bounding rectangle
        """
        bound_rect = self._view.scene().itemsBoundingRect()

        image =  qg.QImage(bound_rect.size().toSize(),
                           qg.QImage.Format_ARGB32)

        top_left = self._view.mapFromScene(bound_rect.toAlignedRect().topLeft())
        bottom_right = self._view.mapFromScene(bound_rect.toAlignedRect().bottomRight())

        image.fill(qc.Qt.white)
        painter = qg.QPainter(image)
        self._view.render(painter, source=qc.QRect(top_left, bottom_right))

        return image
