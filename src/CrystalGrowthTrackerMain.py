# -*- coding: utf-8 -*-
"""
Created on Mon Feb 24 15:45:07 2020

This code is made available by the University of Leeds under the Apache License,
see associated licence documents, all rights are reserved.

@author: j.h.pickering@leeds.ac.uk
"""

import sys
import lazylogger

import PyQt5.QtWidgets as qw
import PyQt5.QtGui as qg
import PyQt5.QtCore as qc

import numpy as np

# data struct for a use selected rectangle in numpy unsigned int format.
from collections import namedtuple
BaseRect = namedtuple("BaseRect", "top, bottom, left, right")

class DrawRect(BaseRect):
    """
       extends the BaseRect structure with a scale function, the intention
       is to define a rectangle within a grayscale image defined as a numpy 
       array, and allow for rescaling of the image.
    """
    
    def scale(self, factor):
        """
        make a new rectangle that is a scaled copy of the existing rectangle 

        Parameters
        ----------
        factor : real or integer number
            the scaling factor for the rectangle.

        Returns
        -------
        DrawRect
            the scaled rectangle.
        """
        t = np.uint32(np.round(self.top*factor))
        b = np.uint32(np.round(self.bottom*factor))
        l = np.uint32(np.round(self.left*factor))
        r = np.uint32(np.round(self.right*factor))
        
        return DrawRect(t, b, l, r)
    
    def shift(self, x, y):
        """
        shift the rectangle by the x and y (placeholder)
        """
        pass
    
    def reshape(self, del_x, del_y):
        """
        rescale differently in x and y (placeholder)
        """
        pass
    
    def __repr__(self):
        """
        string representation for debugging
        """
        
        return "<DrawRect at {}: ({}, {}, {}, {})>".format(
            id(self), self.top, self.bottom, self.left, self.right)
        
    def __str__(self):
        """
        string representationf for user
        """
        return "({}, {}, {}, {})".format(
            self.top, self.bottom, self.left, self.right)
    
# import UI
from Ui_CrystalGrowthTrackerMain import Ui_CrystalGrowthTrackerMain

class ImageLabel(qw.QLabel):
    """
    subclass of label allowing selection of region by drawing rectangle and 
    displaying a list of already selected rectangles.
    """
    def __init__(self, parent=None):
        """
        Set up the label
        """
        super(qw.QLabel, self).__init__()
        self._parent = parent
        self.NAME = self.tr("ImageLabel")
        
        self._selecting = False
        self._start = None
        self._end = None
        
        self._rectangles = []
        
        self._logger = lazylogger.logging.getLogger(self.NAME)
        self._logger.setLevel(lazylogger.logging.WARNING)       
        
    def __iter__(self):
        return iter(self._rectangles)
        
    # signal to indicate user selection
    new_selection = qc.pyqtSignal()

    def mousePressEvent(self, e):
        """
        detect the start of selection
        """
        if e.button() == qc.Qt.LeftButton:
            if not self._selecting:
                self._selecting = True
                self._start = e.pos()
        
    def mouseMoveEvent(self, e):
        """
        If selecting draw rectangle
        """
        if self._selecting:
            self._end = e.pos()
            self.repaint()
            
    def mouseReleaseEvent(self, e):
        """
        select rectangle
        """
        if e.button() == qc.Qt.LeftButton and self._selecting:
            self._end = e.pos()
            self.repaint()
            reply = qw.QMessageBox.question(
                    self,
                    self.tr("Region Selection"),
                    self.tr("Do you wish to select region?"))
            
            if reply == qw.QMessageBox.Yes:
                #self._parent.extract_subimage(self._start, self._end)
                self.add_rectangle()
                
            self._selecting = False
            
    def add_rectangle(self):
        # get horizontal range
        horiz = (self._start.x(), self._end.x())
        zoom = self._parent.get_zoom()
        
        sh = np.uint32(np.round(min(horiz)/zoom))
        eh = np.uint32(np.round(max(horiz)/zoom))
        
        # get vertical range
        vert = (self._start.y(), self._end.y())
        sv = np.uint32(np.round(min(vert)/zoom))
        ev = np.uint32(np.round(max(vert)/zoom))
                
        # add the rectangle to the ImageLabel

        rect = DrawRect(sv, ev, sh, eh)

        self._rectangles.append(rect)
        self.new_selection.emit()
            
    def paintEvent(self, e):
        """
        if selecting than draw a rectagle
        """
        qw.QLabel.paintEvent(self, e)
        
        self.draw_rectangles()
        
    def draw_rectangles(self):
        """
        Draw the alreay selected rectangles and, if in selecting mode
        the current selection

        Returns
        -------
        None.
        """
        if not self._selecting and not len(self._rectangles):
            return
        
        pen = qg.QPen(qg.QColor(qc.Qt.black), 1, qc.Qt.DashLine)
        brush = qg.QBrush(qg.QColor(255,255,255,120))
        painter = qg.QPainter(self)
        painter.setPen(pen)
        painter.setBrush(brush)
        
        for rect in self._rectangles:
            zoomed = rect.scale(self._parent.get_zoom())
            qr = qc.QRect(
                qc.QPoint(int(zoomed.left), int(zoomed.top)), 
                qc.QPoint(int(zoomed.right), int(zoomed.bottom)))
            
            painter.drawRect(qr)
        
        if self._selecting:
            selectionRect = qc.QRect(self._start, self._end)
            painter.drawRect(selectionRect)
            
    @property
    def number_rectangles(self):
        """
        getter for the number of rectangles

        Returns
        -------
        int
            the number of rectangles currently stored.
        """
        return len(self._rectangles)
    
    def get_rectangle(self, index):
        return self._rectangles[index]
        

class CrystalGrowthTrackerMain(qw.QMainWindow, Ui_CrystalGrowthTrackerMain):
    """
    The implementation of the GUI, all the functions and 
    data-structures required to implement the intended behaviour
    """

    def __init__(self, parent=None):
        super(CrystalGrowthTrackerMain, self).__init__()
        self._parent = parent
        self.NAME = self.tr("CrystalGrowthTracker")
        self.setupUi(self)
        
        self._sourceLabel = None
        
        self._subimageLabel = qw.QLabel(self)
        self._subimageLabel.setAlignment(qc.Qt.AlignTop | qc.Qt.AlignLeft)
        self._subimageLabel.setSizePolicy(
                qw.QSizePolicy.Ignored, qw.QSizePolicy.Fixed)

        source_width = int(round(self.size().width()*0.6))
        sub_width = int(round(source_width))
        
        sizes = list() 
        sizes.append(source_width)
        sizes.append(200)
        sizes.append(sub_width)
        sizes.append(200)
        
        self._splitter.setSizes(sizes)
               
        self._subScrollArea.setWidget(self._subimageLabel)
        
        self._raw_image = None
        self._image_source = None
        self._zoom = 1.0
        
        self._logger = lazylogger.logging.getLogger(self.NAME)
        self._logger.setLevel(lazylogger.logging.WARNING) 

    def set_title(self, source):
        """
        assignes the source and sets window title
        """
        self._image_source = source
        title = self.NAME + " - " + source
        self.setWindowTitle(title)
        
    @qc.pyqtSlot()
    def feature_detect(self, method=2):
        """
        @brief find the outlines of any crystals in the currently selected sub-image
        @param method the number of the method to be used
        """
        from PolyLineExtract import PolyLineExtract
        self._logger.debug(self.tr("feature_detect method: {}").format(method))
        
        index = self._subimageComboBox.currentIndex()
        self._logger.debug(self.tr("feature({})").format(index))
        
        if index < 0:
            return
        
        rect = self._sourceLabel.get_rectangle(index)
        
        ple = PolyLineExtract()
        ple.image = self._raw_image[rect.top:rect.bottom, rect.left:rect.right]
    
        try:
            ple.find_lines(method)
        except AttributeError as error:
            self._logger.error(
                self.tr("Unknown image analysis function: {}").format(error))
            return
    
        print("Number of vertices found: {}".format(ple.size))
        for vert in ple:
            print(vert)
            
    @qc.pyqtSlot()
    def save_current_subimage(self):
        import pickle as pk
        
        if self._sourceLabel.number_rectangles < 1:
            qw.QMessageBox.information(
                self, 
                self.tr('Save'), 
                self.tr("You have not made any subimages yet!"))
            return
            
        options = qw.QFileDialog.Options()
        options |= qw.QFileDialog.DontUseNativeDialog
        file_name, file_type = qw.QFileDialog().getSaveFileName(
                self,
                self.tr("Select File"),
                "",
                self.tr("Growth Analyser Files (*.pki);;All Files (*)"), 
                options=options)
        
        if file_name:
            if not file_name.endswith('.pki'):
                file_name = file_name + '.pki'
                    
            img = self.get_current_subimage()
            
            with open(file_name, 'wb') as out_f:
                pk.dump(img, out_f)
            
            qw.QMessageBox.information(
                self, 
                self.tr('Save'), 
                self.tr("Subimage written to: {}").format(file_name))
     
    @qc.pyqtSlot()
    def load_image(self):
        """
        Get file name from user and, if good
        """
        
        # file types
        fi = self.tr("Image Files (*.png *.jpg))")
        fg = self.tr("Growth Tracker Files (*.ga))")
        fn = self.tr("Growth Tracker subimage (*.pki))")
        fa = self.tr("All Files (*)")
        
        files_all = [fi, fg, fn, fa]
        files = ";;".join(files_all)
        
        options = qw.QFileDialog.Options()
        options |= qw.QFileDialog.DontUseNativeDialog
        file_name, file_type = qw.QFileDialog.getOpenFileName(
                self,
                self.tr("Select File"),
                "",
                files, 
                options=options)
        
        if not file_name:
            return
        elif file_type == fi:
            self.read_image(file_name)
        elif file_type == fg:
            self.read_ga_image(file_name)
        elif file_type == fn:
            self.read_numpy_image(file_name)
        else:
            message = self.tr("Unknown file type: {}").format(file_name)
            qw.QMessageBox.warning(self,
                                   self.NAME,
                                   message)
            
    def read_numpy_image(self, file_name):
        import pickle as pk
        
        with open(file_name, 'rb') as in_f:
            self._raw_image = pk.load(in_f)
            
        self.display_image()
        self.set_title(file_name)
        
    def read_ga_image(self, file_name):
        """
        read a numpy array
        """        
        import pickle as pk
        
        with open(file_name, 'rb') as in_f:
            tmp = pk.load(in_f)
            
        self._raw_image = tmp["image"]
        
        self.display_image()
        self.set_title(file_name)

    def read_image(self, file_name):
        """
        Load an image file (jpg or png), convert to numpy grayscal in process
        """        
        import matplotlib.image as mpimg
        from skimage import color
        
        # convert 0.0 to 1.0 float to 0 to 255 unsigned int
        def to_gray(value):
            return np.uint8(np.round(value*255))

        img = color.rgb2gray(mpimg.imread(file_name))
        self._raw_image = to_gray(img)   
        
        self.display_image()
        self.set_title(file_name)
        
    def get_zoom(self):
        """getter for the zoom"""
        return self._zoom
        
    @property
    def has_image(self):
        return isinstance(self._raw_image, np.ndarray)
            
    def display_image(self):
        """
        creeate a new label 
        """        
        if not self.has_image:
            return
        
        self._sourceLabel = ImageLabel(self)
        self._sourceLabel.setAlignment(qc.Qt.AlignTop | qc.Qt.AlignLeft)
        self._sourceLabel.setSizePolicy(
                qw.QSizePolicy.Ignored, qw.QSizePolicy.Fixed)
        self._sourceLabel.new_selection.connect(self.new_subimage)
        self._sourceScrollArea.setWidget(self._sourceLabel) 
        
        self.redisplay_image()
        
    def redisplay_image(self):
        """
        display the raw image in the existing label 

        Returns
        -------
        None.

        """
        import array as arr
        
        # cash the zoom
        self._zoom = self._sourceZoomSpinBox.value()
        
        height, width = self._raw_image.shape
        
        self._display_image = arr.array(
                'B', 
                self._raw_image.reshape(self._raw_image.size))
        
        # use constructor with bytes per line
        image = qg.QImage(
                self._display_image, 
                width, 
                height, 
                width,
                qg.QImage.Format_Grayscale8)
        
        pixmap = qg.QPixmap.fromImage(image)
        size = pixmap.size()
        size *= self._zoom

        pixmap = pixmap.scaled(
                size, 
                qc.Qt.KeepAspectRatio, 
                qc.Qt.SmoothTransformation)
        
        self._sourceLabel.setPixmap(pixmap)
        
        self._sourceLabel.setScaledContents(True);
        self._sourceLabel.setSizePolicy(
                qw.QSizePolicy.Fixed, qw.QSizePolicy.Fixed)
        self._sourceLabel.setMargin(0);
    
    @qc.pyqtSlot()
    def new_subimage(self):
        """
        update the combobox of subimages
        """
        self._subimageComboBox.addItem(str(self._sourceLabel.number_rectangles))
            
        self._subimageComboBox.setCurrentIndex(
            self._sourceLabel.number_rectangles-1)
        
        if self._sourceLabel.number_rectangles and not self._detectButton.isEnabled():
            self._detectButton.setEnabled(True)
        
    @qc.pyqtSlot()
    def source_zoom(self):
        """
        callback for change of zoom on source image
        """
        if self.has_image:
            self.redisplay_image()
            
    @qc.pyqtSlot()
    def subimage_zoom(self):
        """
        callback for change of zoom on subimage image
        """
        
        if self._sourceLabel.number_rectangles:
            self.display_subimage()
    
    @qc.pyqtSlot()
    def save_subimages(self):
        """
        save the selected sub-image
        """
        import pickle as pk

        if self._sourceLabel.number_rectangles < 1:
            qw.QMessageBox.information(
                self, 
                'Save', 
                "You have not made any subimages yet!")
            return
        
        options = qw.QFileDialog.Options()
        options |= qw.QFileDialog.DontUseNativeDialog
        file_name, file_type = qw.QFileDialog().getSaveFileName(
            self,
            self.tr("Select File"),
            "",
            self.tr("Growth Analyser Files (*.ga);;All Files (*)"), 
            options=options)
    
        if file_name:
            if not file_name.endswith('.ga'):
                file_name = file_name + '.ga'
                
            with open(file_name, 'wb') as out_f:
                for index in range(self._sourceLabel.number_rectangles):
                    rect = self._sourceLabel.get_rectangle(index)
                    # store as raw data because pickel will not export Qt objects
                    tmp = {}
                    tmp["top left (v,h)"] = (rect.left, rect.bottom)
                    tmp["source"] = self._image_source
                    tmp["image"] = self._raw_image[rect.left:rect.right, rect.top:rect.bottom]
                    pk.dump(tmp, out_f)
                    
                qw.QMessageBox.information(
                    self, 
                    self.tr('Save'), 
                    self.tr("Subimages written to: {}").format(file_name))
                    
    @qc.pyqtSlot()
    def display_subimage(self):
        """
        view the selected subimge
        """
        import array as arr
        
        img = self.get_current_subimage()
        
        height, width = img.shape
        tmp = arr.array(
                'B', 
                img.reshape(img.size))
        
        # use constructor with bytes per line
        image = qg.QImage(
                tmp, 
                width, 
                height, 
                width,
                qg.QImage.Format_Grayscale8)
        
        pixmap = qg.QPixmap.fromImage(image)
        size = pixmap.size()
        size *= self._subimageZoomSpinBox.value()

        pixmap = pixmap.scaled(
                size, 
                qc.Qt.KeepAspectRatio, 
                qc.Qt.SmoothTransformation)
        
        self._subimageLabel.setPixmap(pixmap)
        
        self._subimageLabel.setScaledContents(True);
        self._subimageLabel.setSizePolicy(
                qw.QSizePolicy.Fixed, qw.QSizePolicy.Fixed)
        self._subimageLabel.setMargin(0);
        self._subScrollArea.setWidget(self._subimageLabel)
        
    def get_current_subimage(self):
        """
        get the pixels of the currently displayed subimage

        Returns
        -------
        np.array
            the pixels in the current subimage

        """
        index = self._subimageComboBox.currentIndex()

        if index < 0:
            return None
        
        rect = self._sourceLabel.get_rectangle(index)
        
        return self._raw_image[rect.top:rect.bottom, rect.left:rect.right]

    @qc.pyqtSlot()
    def closeEvent(self, event):
        """
        This will be called whenever a MyApp object recieves a QCloseEvent.
        All actions required befor closing widget are here.
        """
        mb_reply = qw.QMessageBox.question(self, 
                                        self.tr('Leave Question'), 
                                        self.tr("Do you want to leave?"), 
                                        qw.QMessageBox.Yes | qw.QMessageBox.No, 
                                        qw.QMessageBox.No)
        
        if mb_reply == qw.QMessageBox.Yes:
            """
            clean-up and exit signalling 
            """
            
            # the event must be accepted
            event.accept()
            
            # to get rid tell the event-loop to schedul for deleteion
            # do not destroy as a pointer may survive in event-loop
            # which will trigger errors if it recieves a queued signal
            self.deleteLater()             
            
        else:
            # dispose of the event in the approved way
            event.ignore()

######################################
            
def run_growth_tracker():
    """
    use a local function to make an isolated the QApplication object
    """

    def inner_run():
        app = qw.QApplication(sys.argv)
        window = CrystalGrowthTrackerMain(app)
        window.show()
        app.exec_()
        
    file_name = "growth_tracker.log"
    lazylogger.set_up_logging(file_name, append=True)
    inner_run()
    lazylogger.end_logging(file_name)

if __name__ == "__main__":
    run_growth_tracker()