'''
This is a stand alone Windowed application that looks at
how the image mean value changes over the course of a video.
This is used an unprocessed (with Euler's Magnifier) video file
showing dynamic crystallisation of X-ray synchrotron videos.

This was created by Joanna Leng at the University of leeds in June 2020

'''
import sys
import os
from datetime import timedelta
from timeit import default_timer as timer
import pickle as pk
from imageio import get_reader
from skimage.io import imread
from skimage import color
import seaborn as sns
import matplotlib.pyplot as plt
#import PyQt5.QtWidgets as qw
from PyQt5 import QtWidgets as qw
#import PyQt5.QtGui as qg
from PyQt5 import QtGui as qg
#import PyQt5.QtCore as qc
from PyQt5 import QtCore as qc
from Ui_VideoOverviewWindow import Ui_VideoOverviewWindow


class VideoOverviewWindow(qw.QMainWindow, Ui_VideoOverviewWindow):
    """
    The implementation of the GUI, all the functions and
    data-structures required to implement the intended behaviour
    """

    def __init__(self, parent=None):
        super(VideoOverviewWindow, self).__init__()
        self._parent = parent
        self.name = self.tr("VideoOverviewWindow")
        self.setupUi(self)
        self._raw_image = None
        self._frame_numbers = []
        self._frame_means = []
        self._frame_stds = []
        self._frame_images = []
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self._outpath = dir_path + '\\temp'
        self._outpath1 = 'E:\\Projects\\learn_qt5_designer\\temp'
        self._in_file_name = ""
        self._frame_rate = 20
        self._frame_total = 0
        self._frame_min = 0
        self._frame_max = 1000
        self._video_there = False


    def set_title(self):
        """
        Sets the window title.
        """
        source = self._in_file_name
        title = self.name + " - " + source
        self.setWindowTitle(title)

    @qc.pyqtSlot()
    def change_frame(self):
        """
        Gets the frame number when the FrameSlider changes its value.
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
            if -1 < value < self._frame_total:
                self.read_video_frame(value)




    @qc.pyqtSlot()
    def load_video(self):
        """
        Get file name from user and check if it is good.
        """

        # file types
        image_file_type = self.tr("Image Files (*.png *.jpg)")
        video_file_type = self.tr("Video Files (*.avi)")
#        fg = self.tr("CrystalGrowthTracker Files (*.ga)")
#        fn = self.tr("CrystalGrowthTracker Subimage Files(*.pki)")
        all_file_types = self.tr("All Files (*)")

        files_all = [video_file_type, image_file_type, all_file_types]
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
        elif file_type == image_file_type:
            self.read_image(file_name)
        elif file_type == video_file_type:
            self.read_video(file_name)
        #elif file_type == all_file_types:
            #self.read_ga_image(file_name)
        else:
            message = self.tr("Unknown file type: {}").format(file_type)
            qw.QMessageBox.warning(self,
                                   self.NAME,
                                   message)


    def read_video_frame(self, frame_number):
        '''
        Opens an avi input file and parses it to get a frame.
        '''
        start = timer()

        #print("hi read_video_frame")
        file_name = self._in_file_name
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
            sys.exit('Fatal: output directory ' + self._outpath +
                     ' does not exist and cannot be created')

        num = 0
        img = None
        for img in video.iter_data():
            if num == int(frame_number):
                self.save_grayscale_frame(self._outpath, img, num, self._frame_rate)
                plot_histogram(self._outpath, img, num, img.mean(), img.std())
                break

            num = num+1

        number = r"{0:05d}".format(frame_number)
        filename = str(self._outpath)+r'/GrayscaleFrame'+number+'.png'
        self.VideoDisplay.setPixmap(qg.QPixmap(filename))
        filename = str(self._outpath)+'/HistogramFrame'+number+'.png'
        self.HistogramDisplay.setPixmap(qg.QPixmap(filename))
        end = timer()
        time = str(timedelta(seconds=(end-start)))
        print("The time to read and process the video was: ", time) # Time in seconds


    def read_video(self, file_name):
        ''' opens the avi input file '''

        self._in_file_name = file_name

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
            sys.exit('Fatal: output directory ' + self._outpath +
                     ' does not exist and cannot be created')

        num = 0
        img = None
        for img in video.iter_data():
            self._frame_numbers.append(num)
            if num == 0:
                self.save_grayscale_frame(self._outpath, img, num, self._frame_rate)
            mean = img.mean()
            std = img.std()
            if num == 0:
                plot_histogram(self._outpath, img, num, mean, std)
            self._frame_means.append(mean)
            self._frame_stds.append(std)
            if num < 5:
                print("number: ", num, " image mean: %4.3f" % mean, "std: %4.3f" % std)
            num = num+1
            #f num is 7:
            #   break

        metadata = video.get_meta_data()
        print(metadata)

        plot_means(self._outpath, self._frame_numbers, self._frame_means, self._frame_rate)

        self._frame_total = num

        self.initial_video_display()
        self._video_there = True
        end = timer()
        time = str(timedelta(seconds=(end-start)))
        print("The time to read and process the video was: ", time) # Time in seconds


    def initial_video_display(self):
        '''
        Displays the initial blank images.
        '''
        self.VideoDisplay.setPixmap(qg.QPixmap("temp/GrayscaleFrame00000.png"))
        self.MeanValueGraphDisplay.setPixmap(qg.QPixmap("temp/Mean1.png"))
        self.HistogramDisplay.setPixmap(qg.QPixmap("temp/HistogramFrame00000.png"))



    def save_grayscale_frame(self, outpath, img, n, frame_rate):
        '''
        Takes an image and turns it into a gray scale plot with a title
        and scale information.
        '''
        #print("hi from save_grayscale_frame")
        fig_grayscale = plt.figure(facecolor='w', edgecolor='k')
        if n == 0:
            time = 0
        else:
            time = n/int(frame_rate)
        plt.title('Grayscale for frame {:d} at time {:0.3f} s'.format(n, time))
        plt.imshow(img, cmap='gray', vmin=100, vmax=175)
        number = r"{0:05d}".format(n)

        filename = outpath+r'/GrayscaleFrame'+number+'.png'

        print(filename)

        if os.path.isfile(filename):
            os.remove(filename)

        fig_grayscale.savefig(filename, bbox_inches='tight')
        plt.close(fig_grayscale)



#     def plot_histogram(self, outpath, img, n, mean, std):
#         '''
#         Plots histogram of image values for one frame (an image).
#         '''
#         #print("hi from plot_histogram")
#         img = img.ravel()
#         fig_hist = plt.figure()
#         title = r"Histogram for image {:d}: mean={:0.3f} std={:0.3f}".format(n, mean, std)
#         plt.title(title)
#         plt.xlabel('Data Value (0 is black and 255 is white)')
#         plt.ylabel('Normalised Probability Density')
#         sns.distplot(img.ravel(),
#                      hist=True,
#                      kde=True,
#                      bins=int(180/5),
#                      color='darkblue',
#                      hist_kws={'edgecolor':'black'},
#                      kde_kws={'linewidth': 1})
#         #fig_hist.show()
#         number = r"{0:05d}".format(n)
#
#         filename = outpath+'/HistogramFrame'+str(number)+'.png'
#
#         if os.path.isfile(filename):
#             os.remove(filename)
#
#         fig_hist.savefig(filename, bbox_inches='tight')
#         plt.close(fig_hist)


    def read_image(self, file_name):
        """
        Load an image file (jpg or png), convert to numpy grayscal in process
        """

        img = color.rgb2gray(imread(file_name))

        self._raw_image = img

        print("hi from read image")
        print(type(self._raw_image))

        self.display_image()
        self.set_title()



    def read_numpy_image(self, file_name):
        '''
        Reads an image into a numpy array.
        '''

        with open(file_name, 'rb') as in_f:
            self._raw_image = pk.load(in_f)

        self.display_image()
        self.set_title()


    def display_image(self):
        """
        create a new label
        """
        print("hi from display_image")
        #print(self.has_image)
        print("VideoDisplay type is ", type(self.VideoDisplay))
        print("raw_image type is ", type(self._raw_image))


        display_width = self.VideoDisplay.width()
        display_height = self.VideoDisplay.height()

        print("display_width: ", display_width)
        print("display_height: ", display_height)

        shape_info = self._raw_image.shape

        channel = 1
        if len(shape_info) == 2 or 3:
            img_height = shape_info[0]
            img_width = shape_info[1]
        if len(shape_info) == 3:
            channel = shape_info[2]
        if len(shape_info) == 0:
            message = self.tr("Image is not a recognised shape.")
            qw.QMessageBox.warning(self,
                                   self.NAME,
                                   message)

        print("img_width: ", img_width)
        print("img_height: ", img_height)
        print("channel: ", channel)


        self.VideoDisplay.setPixmap(qg.QPixmap(self._raw_image))


#
def plot_means(outpath, numbers, means, frame_rate):
    '''
    Function to plot graph of mean image values.
    '''
    print("hi from plot_means")
    fig_mean = plt.figure(facecolor='w', edgecolor='k')
    plt.title('Mean Across All Video Frames', {'fontsize':'22'})
    plt.plot(numbers, means, 'b', label='Frame Mean')
    plt.xlabel('Frame\n (' + str(frame_rate) + ' frames per second)', {'fontsize':'22'})
    plt.ylabel('Grayscale value', {'fontsize':'22'})
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), prop={'size': 14})
    plt.xticks(fontsize=18)
    plt.yticks(fontsize=18)

    filename = outpath + r'/Mean1.png'

    if os.path.isfile(filename):
        os.remove(filename)

    fig_mean.savefig(filename, bbox_inches='tight')
    plt.close(fig_mean)


def plot_histogram(outpath, img, n, mean, std):
    '''
    Function to plot histogram of image values for one frame (an image).
    '''
    print("hi from plot_histogram")
    img = img.ravel()
    fig_hist = plt.figure()
    title = r"Histogram for image {:d}: mean={:0.3f} std={:0.3f}".format(n, mean, std)
    plt.title(title)
    plt.xlabel('Data Value (0 is black and 255 is white)')
    plt.ylabel('Normalised Probability Density')
    sns.distplot(img.ravel(),
                 hist=True,
                 kde=True,
                 bins=int(180/5),
                 color='darkblue',
                 hist_kws={'edgecolor':'black'},
                 kde_kws={'linewidth': 1})
    #fig_hist.show()
    number = r"{0:05d}".format(n)

    filename = outpath+'/HistogramFrame'+str(number)+'.png'

    if os.path.isfile(filename):
        os.remove(filename)

        fig_hist.savefig(filename, bbox_inches='tight')
        plt.close(fig_hist)


######################################

def get_translators(lang):
    '''
    Get translations to be displayed through the GUI.
    '''
    qt_translator = qc.QTranslator()
    system_trans = qc.QTranslator()

    if lang == "German":
        if not qt_translator.load("./translation/cgt_german.qm"):
            sys.stderr.write("failed to load file cgt_german.qm")
        if not system_trans.load("qtbase_de.qm",
                                 qc.QLibraryInfo.location(qc.QLibraryInfo.TranslationsPath)):
            sys.stderr.write("failed to load file qtbase_de.qm")

    return [qt_translator, system_trans]

def select_translator():
    '''
    Set up the translator for the GUI so that translated versions of
    information and comments made through the GUI are possible.
    '''
    languages = ["English", "German"]

    lang = qw.QInputDialog.getItem(
        None, "Select Language", "Language", languages)

    if not lang[1]:
        return None
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
