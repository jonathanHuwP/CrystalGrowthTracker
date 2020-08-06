'''
overviewplots.py

This python module contains functions that create plots
that provide an overview of an unprocessed (without Euler's Magnifier) 
video file showing dynamic crystallisation of X-ray synchrotron videos.

Joanna Leng (an EPSRC funded Research Software Engineering Fellow (EP/R025819/1)
University of Leeds
June 2020

Copyright 2020

Licensed under the Apache License, Version 2.0 (the "License"); you may not use
this file except in compliance with the License. You may obtain a copy of the
License at
http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed
under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.

'''
import os
import seaborn as sns
import matplotlib.pyplot as plt


def plot_means(outpath, numbers, means):
    '''
    Function to plot graph of mean image values and save it in a temp directory
    in the source directory.

    Args:
        outpath (str): All output files are saved in a temp directory at the same
                            in the source code directory structure.
        numbers (array of int): An array of the frame_numbers.
        means (array of floats): An array of the mean grayscale value for each frame
                                     of the video.
        frame_rate (int): The frame rate of the video.

    Returns:
        Nothing
    '''
    #print("hi from plot_means")
    fig_mean = plt.figure(facecolor='w', edgecolor='k')
    plt.title('Mean Across All Video Frames', {'fontsize':'22'})
    plt.plot(numbers, means, 'b', label='Frame Mean')
    #plt.xlabel('Frame\n (' + str(frame_rate) + ' frames per second)', {'fontsize':'22'})
    plt.xlabel('Frame')
    plt.ylabel('Grayscale value', {'fontsize':'22'})
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), prop={'size': 14})
    plt.xticks(fontsize=18)
    plt.yticks(fontsize=18)

    filename = outpath + r'/Mean1.png'

    if os.path.isfile(filename):
        os.remove(filename)

    fig_mean.savefig(filename, bbox_inches='tight')
    plt.close(fig_mean)

    return filename


def plot_histogram(outpath, img, frame_number, mean, std):
    '''
    Function to plot histogram of image values for one frame (an image) that
    are saved in a temp directory at the same in the source code directory structure.

    Args:
        outpath (str): All output files are saved in a temp directory at the same
                            in the source code directory structure.
        img: One frame of the video in the format of an image.
        frame_number (int): The numbers of the frame to be plotted.
        mean (float): The mean grayscale value for the frame to be plotted.
        std (float): The standard deviation grayscale value for the frame to be plotted.

    Returns:
        Nothing
    '''
    #print("hi from plot_histogram")
    img = img.ravel()
    fig_hist = plt.figure()
    title = r"Histogram for image {:d}: mean={:0.3f} std={:0.3f}".format(frame_number, mean, std)
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
    number = r"{0:05d}".format(frame_number)

    filename = outpath+'/HistogramFrame'+str(number)+'.png'

    if os.path.isfile(filename):
        os.remove(filename)

    fig_hist.savefig(filename, bbox_inches='tight')
    plt.close(fig_hist)

    return filename


def save_grayscale_frame(outpath, img, frame_number):
    '''
    Takes an image and turns it into a gray scale plot with a title
    and scale information and saves it in a temp directory in the source
    code directory structure.

    Args:
        outpath (str): All output files are saved in a temp directory at the same
                            in the source code directory structure.
        img: One frame of the video in the format of an image.
        frame_number (int): The numbers of the frame to be plotted.
        frame_rate (int): The frame rate of the video.

    Returns:
        Nothing
    '''
    #print("hi from save_grayscale_frame")
    fig_grayscale = plt.figure(facecolor='w', edgecolor='k')
    #if frame_number == 0:
    #    time = 0
    #else:
    #    time = frame_number/int(frame_rate)
    #plt.title('Grayscale for frame {:d} at time {:0.3f} s'.format(frame_number, time))
    plt.title('Grayscale for frame {:d}'.format(frame_number))
    plt.imshow(img, cmap='gray', vmin=100, vmax=175)
    number = r"{0:05d}".format(frame_number)

    filename = outpath+r'/GrayscaleFrame'+number+'.png'

    if os.path.isfile(filename):
        os.remove(filename)

    fig_grayscale.savefig(filename, bbox_inches='tight')
    plt.close(fig_grayscale)
    
    return filename
