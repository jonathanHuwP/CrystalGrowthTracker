## -*- coding: utf-8 -*-
"""
Created on Mon Feb 24 15:45:07 2020

This code is made available by the University of Leeds under the Apache License,
see associated licence documents, all rights are reserved.

@author: j.h.pickering@leeds.ac.uk
"""

import sys

import PyQt5.QtWidgets as qw
import PyQt5.QtGui as qg
import PyQt5.QtCore as qc

import numpy as np

import lazylogger
from ImageLabel import ImageLabel
  
# import UI
from Ui_CrystalGrowthTrackerMain import Ui_CrystalGrowthTrackerMain

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
        self._sourceLabel1 = None
        self._sourceLabel2 = None
        
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
    def tab_changed(self):
        """
        callback for the tab widget to use when the tab is changed, put all
        state change required between the two tabs in here. the currentIndex 
        function in _tabWidger will act as a state variable.
        
        Returns
        -------
        None.
        """ 
        
        self._logger.info(
            "tab changed to {}".format(self._tabWidget.currentIndex()))
        
    @qc.pyqtSlot()
    def feature_detect(self):
        """
        @brief find the outlines of any crystals in the currently selected sub-image
        @param method the number of the method to be used
        """
        from PolyLineExtract import PolyLineExtract, IAParameters
        from ImageEnhancer import ImageEnhancer
        
        from skimage.restoration import denoise_bilateral, denoise_wavelet
        
        index = self._subimageComboBox.currentIndex()
        self._logger.debug("running on subimage ({})".format(index))
        
        if index < 0:
            return
        
        rect = self._sourceLabel1.get_rectangle(index)
        
        # line_threshold, line_length, line_gap, verts_min_distance
        params = IAParameters(10, 50, 5, 5)
        ple = PolyLineExtract(params)
        ie = ImageEnhancer(
            self._raw_image[rect.top:rect.bottom, rect.left:rect.right])
        
        tmp1 = ie.constrast_stretch((25, 75))
        tmp2 = denoise_wavelet(
            tmp1, 
            multichannel=False, 
            rescale_sigma=True)

        tmp2 = tmp2 / np.amax(tmp2) # normalize the data to 0 - 1
        tmp2 = 255.0 * tmp2 # Now scale by 255
        tmp2 = tmp2.astype(np.uint8)
        #tmp2 = ie.adaptive_equalization()
        #tmp3 = ie.adaptive_equalization(0.1)
        
        ple.image = tmp2
        ple.find_vertices()
        ple.find_lines()
        
        # print("Number of vertices found: {}".format(ple.number_vertices))
        # for vert in ple.vertices:
        #     print(vert)
            
        # print("Number of lines found: {}".format(ple.number_lines))
        # print("Start, , End")
        # print("y, x, y, x, theta, r, length")
        # for l in ple.lines:
        #     s = "{}, {}, {}, {}, {}, {}, {}".format(
        #         l.start[0], l.start[1], 
        #         l.end[0], l.end[1],
        #         l.theta, l.r, l.length)
        #     print(s)
        # print("End")
        
        self.display_subimage(ple.image_all)
        #self.display_subimage(ple.image_lines)
        
        #ple.merge()
            
    @qc.pyqtSlot()
    def save_current_subimage(self):
        import pickle as pk
        
        if self._sourceLabel1 is None or self._sourceLabel1.number_rectangles < 1:
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
                self.tr("CrystalGrowthTracker Files (*.pki);;All Files (*)"), 
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
        fi = self.tr("Image Files (*.png *.jpg)")
        fg = self.tr("CrystalGrowthTracker Files (*.ga)")
        fn = self.tr("CrystalGrowthTracker Subimage Files(*.pki)")
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
            message = self.tr("Unknown file type: {}").format(file_type)
            self._logger.error("bad file type: {}".format(file_type))
            self._logger.error("should be {}".format(fi))
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
        
        self._sourceLabel1 = ImageLabel(self)
        self._sourceLabel1.setAlignment(qc.Qt.AlignTop | qc.Qt.AlignLeft)
        self._sourceLabel1.setSizePolicy(
                qw.QSizePolicy.Ignored, qw.QSizePolicy.Fixed)
        self._sourceLabel1.new_selection.connect(self.new_subimage)
        self._sourceScrollArea.setWidget(self._sourceLabel1) 
        
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
        
        self._sourceLabel1.setPixmap(pixmap)
        
        self._sourceLabel1.setScaledContents(True);
        self._sourceLabel1.setSizePolicy(
                qw.QSizePolicy.Fixed, qw.QSizePolicy.Fixed)
        self._sourceLabel1.setMargin(0);
    
    @qc.pyqtSlot()
    def new_subimage(self):
        """
        update the combobox of subimages
        """
        self._subimageComboBox.addItem(str(self._sourceLabel1.number_rectangles))
            
        self._subimageComboBox.setCurrentIndex(
            self._sourceLabel1.number_rectangles-1)
        
        if self._sourceLabel1.number_rectangles and not self._detectButton.isEnabled():
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
        
        if self._sourceLabel1.number_rectangles:
            self.display_subimage()
    
    @qc.pyqtSlot()
    def save_subimages(self):
        """
        save the selected sub-image
        """
        import pickle as pk

        if self._sourceLabel1 is None or self._sourceLabel1.number_rectangles < 1:
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
            self.tr("CrystalGrowthTracker Files (*.ga);;All Files (*)"), 
            options=options)
    
        if file_name:
            if not file_name.endswith('.ga'):
                file_name = file_name + '.ga'
                
            with open(file_name, 'wb') as out_f:
                for index in range(self._sourceLabel1.number_rectangles):
                    rect = self._sourceLabel1.get_rectangle(index)
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
    def display_subimage(self, img=None):
        """
        view the selected subimge
        """
        import array as arr
        
        if img is None:
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
        
        rect = self._sourceLabel1.get_rectangle(index)
        
        return self._raw_image[rect.top:rect.bottom, rect.left:rect.right]

    @qc.pyqtSlot()
    def closeEvent(self, event):
        """
        This will be called whenever a MyApp object recieves a QCloseEvent.
        All actions required befor closing widget are here.
        """
        mb_reply = qw.QMessageBox.question(self, 
                                           self.tr('CrystalGrowthTracker'), 
                                           self.tr('Do you want to leave?'), 
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

def get_translators(lang):
    qt_translator = qc.QTranslator()
    system_trans = qc.QTranslator()
    
    if "German" == lang:
        if not qt_translator.load("./translation/cgt_german.qm"):
            sys.stderr.write("failed to load file cgt_german.qm")
        if not system_trans.load("qtbase_de.qm", 
                   qc.QLibraryInfo.location(qc.QLibraryInfo.TranslationsPath)):
            sys.stderr.write("failed to load file qtbase_de.qm")
    
    return [qt_translator, system_trans]
    
def select_translator():
    languages = ["English", "German"]
    
    lang = qw.QInputDialog.getItem(
        None, "Select Language", "Language", languages)
    
    if not lang[1]:
        return None
    else:
        return get_translators(lang[0])
        
def run_growth_tracker():
    """
    use a local function to make an isolated the QApplication object
    """

    def inner_run():
        app = qw.QApplication(sys.argv)
        
        translators = select_translator()
        for translator in translators:
            qc.QCoreApplication.installTranslator(translator)

        window = CrystalGrowthTrackerMain(app)
        window.show()
        app.exec_()
        
    file_name = "growth_tracker.log"
    lazylogger.set_up_logging(file_name, append=True)
    inner_run()
    lazylogger.end_logging(file_name)

if __name__ == "__main__":
    run_growth_tracker()