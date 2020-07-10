import sys

import PyQt5.QtWidgets as qw
import PyQt5.QtGui as qg
import PyQt5.QtCore as qc
#from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer

#import PyQt5.QtMultimediaWidgets
#import PyQt5.QtMultimediaWidgets
#from PyQt5.QtMultimediaWidgets import QtVideoWidget

import numpy as np
import matplotlib.pyplot as plt

#import lazylogger
#from ImageLabel import ImageLabel

    
# import UI
#import Ui_VideoOverviewWindow
from Ui_VideoOverviewWindow import Ui_VideoOverviewWindow
from PyQt5.QtGui import QPixmapCache
from envs.CGT.Lib.ctypes import c_char
from _pylief import NONE

class VideoOverviewWindow(qw.QMainWindow, Ui_VideoOverviewWindow):
    """
    The implementation of the GUI, all the functions and 
    data-structures required to implement the intended behaviour
    """

    def __init__(self, parent=None):
        super(VideoOverviewWindow, self).__init__()
        self._parent = parent
        self.NAME = self.tr("VideoOverviewWindow")
        self.setupUi(self)
        
        #self.FrameSlider.rangeChange


        
        self._raw_image = None
        self._frame_numbers = []
        self._frame_means = []
        self._frame_stds = []
        self._frame_images = []
        
        self._outpath = 'E:\\Projects\\learn_qt5_designer\\temp'
        self._in_file_name = ""
        self._frame_rate = 20
        self._frame_total = 0
        self._frame_min = 0
        self._frame_max = 1000
        self._frame_range = NONE
        self._video_there = False
        
    
 

    def set_title(self, source):
        """
        assignes the source and sets window title
        """
        self._image_source = source
        title = self.NAME + " - " + source
        self.setWindowTitle(title)
        
    @qc.pyqtSlot()
    def change_frame(self):
        """
        Get frame number when the FrameSlider changes its value
        """                
        print("hi from change_frame")
        value = self.FrameSlider.value()
        print(value)
        
        if not self._video_there:
            print("You need to load a video.")
        if self._video_there:
            print("The video is loaded.")
            print("The total number of frames is: ", self._frame_total)
            if value > self._frame_total:
                self.VideoDisplay.setPixmap(qg.QPixmap("temp/blank.png"))
                self.MeanValueGraphDisplay.setPixmap(qg.QPixmap("temp/Mean1.png"))
                self.HistogramDisplay.setPixmap(qg.QPixmap("temp/blank.png"))
            if value > -1 and value < self._frame_total:
                self.read_video_frame(value)

 
             
     
    @qc.pyqtSlot()
    def load_video(self):
        """
        Get file name from user and, if good
        """
        
        # file types
        fi = self.tr("Image Files (*.png *.jpg)")
        fv = self.tr("Video Files (*.avi)")
#        fg = self.tr("CrystalGrowthTracker Files (*.ga)")
#        fn = self.tr("CrystalGrowthTracker Subimage Files(*.pki)")
        fa = self.tr("All Files (*)")
        
        files_all = [fv, fi, fa]
        files = ";;".join(files_all)
        print(files_all)
        print(files)
        
        
        options = qw.QFileDialog.Options()
        print(options)
        options |= qw.QFileDialog.DontUseNativeDialog
        print(options)
        file_name, file_type = qw.QFileDialog.getOpenFileName(
                self,
                self.tr("Select File"),
                "",
                files, 
                options=options)
        print(file_name)
        print(not file_name)
        print(file_type)
        
        
        if not file_name:
            return
        elif file_type == fi:
            self.read_image(file_name)
        elif file_type == fv:
            self.read_video(file_name)
        #elif file_type == fa:
            #self.read_ga_image(file_name)
        else:
            message = self.tr("Unknown file type: {}").format(file_type)
            qw.QMessageBox.warning(self,
                                   self.NAME,
                                   message)

           
    def read_video_frame(self, frame_number):        
        ''' opens the avi input file '''
        from imageio import get_reader
        from datetime import timedelta 
        import os
        from timeit import default_timer as timer

        start = timer()
        
        #print("hi read_video_frame")
        file_name = self.in_file_name
        print(file_name)
        print("frame_number: ", frame_number)
        
        try:        
            video = get_reader(file_name, 'ffmpeg')
        except:
            print("Unexpected error:", sys.exc_info()[0])
            raise
            
        try:
            if not os.path.exists(self._outpath):
                os.makedirs(self._outpath)
        except OSError:
            sys.exit('Fatal: output directory ' + self._outpath + ' does not exist and cannot be created') 

        num = 0
        img = None
        for img in video.iter_data():            
            if num == int(frame_number):
                self.save_grayscale_frame(self._outpath, img, num, self._frame_rate)
                self.plot_histogram(self._outpath, img, num, img.mean(), img.std())
                break
            
            num = num+1
 
        number = r"{0:05d}".format(frame_number)
        filename = str(self._outpath)+r'/GrayscaleFrame'+number+'.png'
        self.VideoDisplay.setPixmap(qg.QPixmap(filename))
        filename = str(self._outpath)+'/HistogramFrame'+number+'.png'
        self.HistogramDisplay.setPixmap(qg.QPixmap(filename))   
        end = timer()
        time = str(timedelta(seconds = (end-start)))
        print("The time to read and process the video was: ", time) # Time in seconds

            
    def read_video(self, file_name):        
        ''' opens the avi input file '''
        from imageio import get_reader
        from datetime import timedelta 
        import os
        from timeit import default_timer as timer
        
        self.in_file_name = file_name

        start = timer()
        
        #print("hi read_video")
        
        try:        
            video = get_reader(file_name, 'ffmpeg')
        except:
            print("Unexpected error:", sys.exc_info()[0])
            raise
        
        if self._frame_numbers:
            self._frame_numbers.clear()
        if self._frame_images:
            self._frame_images.clear()
        if self._frame_means:
            self._frame_means.clear()
        if self._frame_stds:
            self._frame_stds.clear()
            
        try:
            if not os.path.exists(self._outpath):
                os.makedirs(self._outpath)
        except OSError:
            sys.exit('Fatal: output directory ' + self._outpath + ' does not exist and cannot be created') 

        num = 0
        img = None
        for img in video.iter_data():
            self._frame_numbers.append(num)
            if num == 0:
                self.save_grayscale_frame(self._outpath, img, num, self._frame_rate)
            mean = img.mean()
            std = img.std()
            if num == 0:
                self.plot_histogram(self._outpath, img, num, mean, std)
            self._frame_means.append(mean)
            self._frame_stds.append(std)
            if num < 5:
                print("number: ", num, " image mean: %4.3f" % mean, "std: %4.3f" % std)
            num = num+1
            #f num is 7:
            #   break

        metadata = video.get_meta_data()
        print(metadata)
    
        self.plot_means(self._outpath, self._frame_numbers, self._frame_means, self._frame_rate)
        
        self._frame_total = num
        
        self.initial_video_display()
        self._video_there = True
        end = timer()
        time = str(timedelta(seconds = (end-start)))
        print("The time to read and process the video was: ", time) # Time in seconds
        
        
    def initial_video_display(self):
        self.VideoDisplay.setPixmap(qg.QPixmap("temp/GrayscaleFrame00000.png"))
        self.MeanValueGraphDisplay.setPixmap(qg.QPixmap("temp/Mean1.png"))
        self.HistogramDisplay.setPixmap(qg.QPixmap("temp/HistogramFrame00000.png"))


        
    def save_grayscale_frame(self, outpath, img, n, frame_rate):
        ''' plotimage as grayscale '''
        import os
        #print("hi from save_grayscale_frame")
        fig_grayscale = plt.figure(facecolor='w', edgecolor='k')
        if n == 0:
            time = 0
        else:
            time=n/int(frame_rate)
        plt.title('Grayscale for frame {:d} at time {:0.3f} s'.format(n,time))
        plt.imshow(img, cmap='gray', vmin=100, vmax=175)
        number = r"{0:05d}".format(n)
        
        filename = outpath+r'/GrayscaleFrame'+number+'.png'
        
        print(filename)
        
        if os.path.isfile(filename):
            os.remove(filename)
        
        fig_grayscale.savefig(filename, bbox_inches='tight')
        plt.close(fig_grayscale)
    
 
    def plot_means(self, outpath, numbers, means, frame_rate):
        ''' plot graph of mean image values '''
        import os
        print("hi from plot_means")
        fig_mean = plt.figure(facecolor='w', edgecolor='k')
        plt.title('Mean Across All Video Frames',  {'fontsize':'22'})
        plt.plot(numbers, means, 'b', label='Frame Mean')
        plt.xlabel('Frame\n ('+str(frame_rate)+' frames per second)', {'fontsize':'22'})
        plt.ylabel('Grayscale value', {'fontsize':'22'})
        plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), prop={'size': 14})
        plt.xticks(fontsize=18)
        plt.yticks(fontsize=18)
        #fig_mean.show()
        filename = outpath+r'/Mean1.png'
        
        if os.path.isfile(filename):
            os.remove(filename)
  
        fig_mean.savefig(filename, bbox_inches='tight')
        plt.close(fig_mean)
        
    def plot_histogram(self, outpath, img, n, mean, std):
        ''' plot histogram of image values of one frame'''
        import seaborn as sns
        import os
        #print("hi from plot_histogram")
        img = img.ravel()
        fig_hist = plt.figure()
        title = r"Histogram for image {:d}: mean={:0.3f} std={:0.3f}".format(n,mean,std)
        plt.title(title)
        plt.xlabel('Data Value (0 is black and 255 is white)')
        plt.ylabel('Normalised Probability Density')
        sns.distplot(img.ravel(), hist=True, kde=True, bins=int(180/5), color = 'darkblue', hist_kws={'edgecolor':'black'}, kde_kws={'linewidth': 1})
        #fig_hist.show()
        number = r"{0:05d}".format(n)
        
        filename = outpath+'/HistogramFrame'+str(number)+'.png'
        
        if os.path.isfile(filename):
            os.remove(filename)
   
        fig_hist.savefig(filename, bbox_inches='tight')
        plt.close(fig_hist)
    
    def read_image(self, file_name):
        """
        Load an image file (jpg or png), convert to numpy grayscal in process
        """        
        import matplotlib.image as mpimg
        from skimage.io import imread, imshow
        from skimage import color
        
        # convert 0.0 to 1.0 float to 0 to 255 unsigned int
        def to_gray(value):
            return np.uint8(np.round(value*255))

        #img = color.rgb2gray(mpimg.imread(file_name))
        img = color.rgb2gray(imread(file_name))
        #img = imread(file_name)
        #imshow(img)
        #self._raw_image = to_gray(img) 
        self._raw_image = img
        
        print("hi from read image")
        print(type(self._raw_image))  
        
        self.display_image()
        self.set_title(file_name)
        
            
    
    def read_numpy_image(self, file_name):
        import pickle as pk
        
        with open(file_name, 'rb') as in_f:
            self._raw_image = pk.load(in_f)
            
        self.display_image()
        self.set_title(file_name)
        
    @property
    def has_image(self):
        return isinstance(self._raw_image, np.ndarray)
            
    def display_image(self):
        """
        creeate a new label 
        """ 
        import array as arr
        from skimage.transform import rescale, resize, downscale_local_mean       
        #if not self.has_image:
        #    return
        print("hi from display_image")
        #print(self.has_image)
        print("VideoDisplay type is ",type(self.VideoDisplay))
        print("raw_image type is ",type(self._raw_image))
        
        
        display_width = self.VideoDisplay.width()
        display_height = self.VideoDisplay.height()
    
        print("display_width: ", display_width)
        print("display_height: ", display_height)
        
        #img_height, img_width, channel = self._raw_image.shape
        
        shape_info = self._raw_image.shape
        
        channel = 1
        if len(shape_info) is 2 or 3:
            img_height = shape_info[0]
            img_width = shape_info[1]
        if len(shape_info) is 3:
            channel = shape_info[2]
        if len(shape_info) is 0:
            message = self.tr("Image is not a recognised shape.")
            qw.QMessageBox.warning(self,
                                   self.NAME,
                                   message)
               
        print("img_width: ", img_width)
        print("img_height: ", img_height)
        print("channel: ", channel)

        ##scale_width = (display_width) / img_width
        ##scale_height = (display_height) / img_height
        
        ##scale = 1
        
        ##if scale_width > scale_height:
        ##    scale = scale_height
        ##else:
        ##    scale = scale_width
        
        ##print("scale_width: ", scale_width)
        ##print("scale_height: ", scale_height) 
        ##print("scale: ", scale)            
        
        ##img_rescaled = rescale(self._raw_image, scale, anti_aliasing=False)
        
        ##print(img_rescaled.shape)
        
        ##img_rescale_height, img_rescale_width = img_rescaled.shape
        
        ##a = arr.array('B', [2, 4, 6, 8])
        
        ##display_image = self._raw_image.astype(np.char).tolist()
        #print(self._raw_image.size)
        #
        #size = self._raw_image.size
        
        #raw_image_1d_list = self._raw_image.reshape(size).astype(c_char).tolist()
        
        #print(type(raw_image_1d_list))
        #print(type(raw_image_1d_list[1]))
        
        ##display_image = arr.array(
        ##        'B',
        ##        raw_image_1d_list)
                ##self._raw_image.reshape(self._raw_image.size))
        
        ##print(display_image.shape)
    
        #bytesPerLine = channel * img_width
         
        #print("bytesPerLine: ", bytesPerLine)
         
        #qImg = qg.QImage(
        #         self._raw_image.data,
        #         img_width, 
        #         img_height, 
        #         bytesPerLine,
        #         qg.QImage.Format_Grayscale8)
        
        #print(type(qImg))
         
        #pixmap = qg.QPixmap.fromImage(qImg)
         
        #pixmap_size = pixmap.size()
                 
        #pixmap = pixmap.scaled(
        #        pixmap_size, 
        #        qc.Qt.KeepAspectRatio, 
        #        qc.Qt.SmoothTransformation)
         
        #self.VideoDisplay.setPixmap(pixmap)
         
        #self.VideoDisplay.setScaledContents(True);
        #self.VideoDisplay.setSizePolicy(
        #        qw.QSizePolicy.Fixed, qw.QSizePolicy.Fixed)
        #self.VideoDisplay.setMargin(0);
        
        
        self.VideoDisplay.setPixmap(qg.QPixmap(self._raw_image))
        
        
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
        
def run_video_overview():
    """
    use a local function to make an isolated the QApplication object
    """

    def inner_run():
        app = qw.QApplication(sys.argv)
        
        translators = select_translator()
        for translator in translators:
            qc.QCoreApplication.installTranslator(translator)

        window = VideoOverviewWindow(app)
        window.show()
        app.exec_()
        
    inner_run()

if __name__ == "__main__":
    run_video_overview()
    