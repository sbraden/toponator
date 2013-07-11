#!/usr/bin/env python
# -*- coding: utf-8 -*-

# cub2colorplt.py
"""
Takes input a single band cube and makes a 2d color plot with scalebar and colorbar.
"""

import os, re
import pandas as pd
import numpy as np
import os.path

from pysis import isis, CubeFile
from pysis.labels import parse_file_label
from pysis.util.file_manipulation import ImageName, write_file_list
from argparse import ArgumentParser

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.ticker import LinearLocator, FormatStrFormatter
import matplotlib.patches as mpatches

# import pyfits
import isistools # my module

def get_scalebar_size(filename, image):
    """
    Scalebar_width must be in pixels for plotting.
    Args: image filename, image object
    Returns: scalebar width for plotting
    example: mpp = 100, image width = 20 km, or 20000 m.
    Thus image.samples = 200
    """
    samples = image.samples
    image_scale = isistools.get_proj_pixel_scale(filename) # units = meter per pixel
    print image_scale #debug
    image_width = samples * image_scale # units = meters
    scalebar_width_pixels = int(samples/5) # units = pixels
    if image_width > 3000:
        scalebar_width_label = (image_width/1000)/5 # units = kilometers
        units = ' km'
    else:
        scalebar_width_label = image_width/5 # units = meters
        units = ' m'

    return scalebar_width_pixels, scalebar_width_label, units

def make_colorbar(plotname, pixel_units):
    """
    Sets colorbar properties, colormap, and label
    """
    cbar = plt.colorbar(plot1, orientation="vertical")
    plot1.set_cmap('jet')
    cbar.set_label(pixel_units, fontsize=20)    


def color_plot_2D(image, args):

    # An matplotlib.image.AxesImage instance is returned (plot1)
    # the 0 tells it to plot the first band only
    image_data = image.apply_numpy_specials()[0].astype(np.float64)
    plot1 = plt.imshow(image_data)
    ax = plt.gca() # not sure what this does but it works

    pixel_units = 'Standard deviation of slope'
    #pixel_units = 'Slope (degrees)'
    # pixel_units = 'Elevation (m)'
    make_colorbar(plot1, pixel_units)

    plt.axis('off') # by turning the axis off, you make the grid disappear

    # Draw a box that will be the scalebar
    # this remains even after you turn the axes off
    xy = 0.75*image.samples, 0.90*image.lines # upper left hand corner location
    width_pixels, width_label, units = get_scalebar_size(args.image, image)
    width, height = width_pixels, width_pixels/4
    ax.add_patch(mpatches.Rectangle(xy, 
                                    width, 
                                    height, 
                                    facecolor="black",
                                    edgecolor="white", 
                                    linewidth=1
                                    )
    )

    # Plot text that is the scalebar label
    text_x = xy[0] + width/2
    text_y = xy[1] + height/2

    plt.text(text_x, 
            text_y, 
            str(width_label) + units, 
            fontsize=10, 
            rotation=0.,
            horizontalalignment="center", 
            verticalalignment="center", 
            color='white',
            bbox = dict(boxstyle="square", 
                        edgecolor='black', 
                        facecolor='black'
                    )
    )

    plt.draw()

    plt.savefig(args.outname + '.png', dpi=300)

    # TODO: make this a separate function
    if args.contours == True:
        print 'CONTOURS IN PROGRESS'
        print image.samples, image.lines
        X = np.arange(0, image.samples, 1)
        Y = np.arange(0, image.lines, 1)
        X, Y = np.meshgrid(X, Y)
        Z = image.apply_numpy_specials()[0].astype(np.float64)
        # N is number of levels for the contours
        N = 8
        interval = (Z.max() - Z.min()) / N
        ''' OVERRIDE '''
        #interval = (-1160 - -1569) / N

        # You can set negative contours to be solid instead of dashed:
        matplotlib.rcParams['contour.negative_linestyle'] = 'solid'
        #plt.figure()
        print 'Z.max:', Z.max()
        print 'Z.min:', Z.min()
        print 'contour interval:', interval
        contour1 = plt.contour(X, Y, Z, N, colors='k') # negative contours will be dashed by default
        # plots labels to go with the contours
        #plt.clabel(contour1, fontsize=9, inline=1)
        plt.show()
        plt.axis('off')
        plt.savefig(args.outname + '_contours.png', dpi=300)
    pass

def main():

    parser = ArgumentParser(description='Create plots for topo data')
    parser.add_argument('image', metavar='cub',
                        help='the cube file(s) (.cub) to process, no NULL pixels')
    parser.add_argument('outname',
                        help='the output filename, no extension')
    parser.add_argument('--contours', '-c', default=True,
                       help='set to True for contour lines')
    parser.add_argument('--cinterval', '-i', default='10',
                       help='interval in meters for contour lines')
    args = parser.parse_args()

    img = CubeFile.open(args.image)

    color_plot_2D(img, args)
    
if __name__ == '__main__':
    main()

     
