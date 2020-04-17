# -*- coding: utf-8 -*-
"""
Created on Mon Feb 24 15:45:07 2020

@author: j.h.pickering@leeds.ac.uk
"""

import sys

import PyQt5.QtWidgets as qw
import PyQt5.QtGui as qg
import PyQt5.QtCore as qc

import numpy as np

# import UI
from Ui_CrystalGrowthTrackerMain import Ui_CrystalGrowthTrackerMain

class ImageLabel(qw.QLabel):
    """
    subclass of label allowing selection of region by drawing rectangle
    """
    def __init__(self, parent=None):
        """
        Set up the label
        """
        super(qw.QLabel, self).__init__()
        self._parent = parent
        
        self._selecting = False
        self._start = None
        self._end = None
        
    # signal to indicate user selection
    selected = qc.pyqtSignal(qg.QMouseEvent, qg.QMouseEvent)

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
                    "Crystal Growth Analyser",
                    "Do you wish to select region?")
            
            if reply == qw.QMessageBox.Yes:
                self._parent.extract_subimage(self._start, self._end)
                
            self._selecting = False
            
    def paintEvent(self, e):
        """
        if selecting than draw a rectagle
        """
        qw.QLabel.paintEvent(self, e)
        
        if self._selecting:
            pen = qg.QPen(qg.QColor(qc.Qt.black), 1, qc.Qt.DashLine)
            brush = qg.QBrush(qg.QColor(255,255,255,120))
            painter = qg.QPainter(self)
            painter.setPen(pen)
            painter.setBrush(brush)
            
            selectionRect = qc.QRect(self._start, self._end)
            painter.drawRect(selectionRect)

class CrystalGrowthTrackerMain(qw.QMainWindow, Ui_CrystalGrowthTrackerMain):
    """
    The implementation of the GUI, all the functions and 
    data-structures required to implement the intended behaviour
    """
    NAME = "CrystalGrowthTracker"
    
    def __init__(self, parent=None):
        super(CrystalGrowthTrackerMain, self).__init__()
        self._parent = parent
                
        self.setupUi(self)
        
        self._sourceLabel = ImageLabel(self)        
        self._sourceLabel.setAlignment(qc.Qt.AlignTop | qc.Qt.AlignLeft)
        self._sourceLabel.setSizePolicy(
                qw.QSizePolicy.Ignored, qw.QSizePolicy.Fixed)
        self._sourceLabel.selected.connect(self.extract_subimage)
        
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
        
        self._sourceScrollArea.setWidget(self._sourceLabel)        
        self._subScrollArea.setWidget(self._subimageLabel)
        
        self._raw_image = None
        self._image_source = None
        self._zoom = 1.0
        self._subimages = []

    def set_title(self, source):
        """
        assignes the source and sets window title
        """
        self._image_source = source
        title = self.NAME + " - " + source
        self.setWindowTitle(title)
        
    @qc.pyqtSlot()
    def feature_detect(self):
        print("feature_detect")
     
    @qc.pyqtSlot()
    def load_image(self):
        """
        Get file name from user and, if good
        """
        
        # file types
        fi = "Image Files (*.png *.jpg)"
        fn = "Growth Analyser Files (*.ga)"
        fa = "All Files (*)"
        
        files_all = [fi, fn, fa]
        files = ";;".join(files_all)
        
        options = qw.QFileDialog.Options()
        options |= qw.QFileDialog.DontUseNativeDialog
        fileName, fileType = qw.QFileDialog.getOpenFileName(
                self,
                "Select File",
                "",
                files, 
                options=options)
        
        if not fileName:
            return
        elif fileType == fi:
            self.read_image(fileName)
        elif fileType == fn:
            self.read_ga_image(fileName)
        else:
            message = "Unknown file type: {}".format(fileName)
            qw.QMessageBox.warning(self,
                                   "Crystal Growth Analyser",
                                   message)

    def read_ga_image(self, fileName):
        """
        read a numpy array
        """        
        import pickle as pk
        
        with open(fileName, 'rb') as in_f:
            tmp = pk.load(in_f)
            
        self._raw_image = tmp["image"]
        
        self.display_image()
        self.set_title(fileName)

    def read_image(self, fileName):
        """
        Load an image file (jpg or png), convert to numpy grayscal in process
        """        
        import matplotlib.image as mpimg
        from skimage import color
        
        # convert 0.0 to 1.0 float to 0 to 255 unsigned int
        def to_gray(value):
            return np.uint8(np.round(value*255))

        img = color.rgb2gray(mpimg.imread(fileName))
        self._raw_image = to_gray(img)   
        
        self.display_image()
        self.set_title(fileName)
        
    @property
    def has_image(self):
        return isinstance(self._raw_image, np.ndarray)
            
    def display_image(self):
        """
        display the raw image in the label
        """
        import array as arr
        
        if not self.has_image:
            return
        
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
    
    @qc.pyqtSlot(qg.QMouseEvent, qg.QMouseEvent)
    def extract_subimage(self, start, end):
        """
        generate slice of raw image using pixel coordinages supplied
        """
        
        if not self.has_image:
            return
        
        # get horizontal range
        horiz = (start.x(), end.x())
        sh = np.uint32(np.round(min(horiz)/self._zoom))
        eh = np.uint32(np.round(max(horiz)/self._zoom))
        
        # get vertical range
        vert = (start.y(), end.y())
        sv = np.uint32(np.round(min(vert)/self._zoom))
        ev = np.uint32(np.round(max(vert)/self._zoom))
        
        tmp = {}
        tmp["top left (v,h)"] = (sv, sh)
        tmp["source"] = self._image_source
        tmp["image"] = self._raw_image[sv:ev, sh:eh]
        
        self._subimages.append(tmp)
        self.update_subimages()        
            
    def update_subimages(self):
        """
        clear the subimages combobox then fill
        """
        num_subimages = len(self._subimages)
        
        self._subimageComboBox.clear()
        for i in range(num_subimages):
            self._subimageComboBox.addItem(str(i+1))
            
        self._subimageComboBox.setCurrentIndex(num_subimages-1)
        #self.display_subimage()
        
    @qc.pyqtSlot()
    def source_zoom(self):
        """
        callback for change of zoom on source image
        """
        if self.has_image:
            self.display_image()
            
    @qc.pyqtSlot()
    def subimage_zoom(self):
        """
        callback for change of zoom on subimage image
        """
        if len(self._subimages) > 0:
            self.display_subimage()
    
    @qc.pyqtSlot()
    def save_subimage(self, index=None):
        """
        save the selected sub-image
        """
        import pickle as pk
        
        if not index:
            index = self._subimageComboBox.currentIndex()
        
        assert(index < len(self._subimages) and index >= 0)
        
        image = self._subimages[index]
        
        if image["image"].size:
            options = qw.QFileDialog.Options()
            options |= qw.QFileDialog.DontUseNativeDialog
            fileName, fileType = qw.QFileDialog().getSaveFileName(
                self,
                "Select File",
                "",
                "Growth Analyser Files (*.ga);;All Files (*)", 
                options=options)
        
            if fileName:
                if not fileName.endswith('.ga'):
                    fileName = fileName + '.ga'
                with open(fileName, 'wb') as out_f:
                    pk.dump(image, out_f)
                    qw.QMessageBox.information(self, 
                                        'Save', 
                                        "Subimage written to: " + fileName)
                    
    @qc.pyqtSlot()
    def display_subimage(self):
        """
        view the selected subimge
        """
        import array as arr
        
        index = self._subimageComboBox.currentIndex()
        
        if index < 0:
            return
        
        # get the zoom
        zoom = self._subimageZoomSpinBox.value()
        
        img = self._subimages[index]["image"]
        
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
        size *= zoom

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
        
        self._findButton.setEnabled(True)
        
    @qc.pyqtSlot()
    def save_subimage2(self, dialog):
        """
        slot for recieving signal from sub-image viewer
        """
        self.save_subimage(dialog.source_index)

    @qc.pyqtSlot()
    def closeEvent(self, event):
        """
        This will be called whenever a MyApp object recieves a QCloseEvent.
        All actions required befor closing widget are here.
        """
        mb_reply = qw.QMessageBox.question(self, 
                                        'Leave Question', 
                                        "Do you want to leave?", 
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
            
def run_growth_analayser():
    """
    use a local function to make an isolated the QApplication object
    """

    def inner_run():
        app = qw.QApplication(sys.argv)
        window = CrystalGrowthTrackerMain(app)
        window.show()
        app.exec_()
        
    inner_run()

if __name__ == "__main__":
    run_growth_analayser()