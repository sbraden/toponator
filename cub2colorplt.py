#!/usr/bin/env python
# -*- coding: utf-8 -*-

# cub2colorplt.py

import os, re
import pandas as pd

from pysis import isis, CubeFile
from pysis.labels import parse_file_label
from pysis.util.file_manipulation import ImageName, write_file_list

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.ticker import LinearLocator, FormatStrFormatter
import matplotlib.patches as mpatches
import os.path
from pysis import isis
from pysis import CubeFile
import pyfits

GROUP_RE = re.compile(r'(Group.*End_Group)', re.DOTALL)

def make_scalebar():
    samples = image.samples
    print image.samples, image.lines
    # scalebar_width must be in pixels
    # TODO: scalebar is broken now. 
    # Just grab scale from label
    scalebar_width = samples/5 # 100 pixels = 10 km


def color_plot_2D(image, args):



    # An matplotlib.image.AxesImage instance is returned (plot1)
    # the 0 tells it to plot the first band only
    image_data = image.apply_numpy_specials()[0].astype(np.float64)
    plot1 = plt.imshow(image_data)
    ax = plt.gca() # not sure what this does but it works

    # color bar properties
    cbar = plt.colorbar(plot1, orientation="vertical")
    cbar.set_label('Elevation (m)', fontsize=20)

    # Set the color map
    plot1.set_cmap('jet')
    plt.axis('off') # by turning the axis off, you make the grid disappear

    # Draw a box
    # this remains even after you turn the axes off
    xy = 0.75*image.samples, 0.90*image.lines # upper left hand corner location
    width, height = scalebar_width, scalebar_width/4
    ax.add_patch(mpatches.Rectangle(xy, width, height, facecolor="black",
        edgecolor="white", linewidth=1))

    text_x = xy[0] + width/2
    text_y = xy[1] + height/2

    plt.text(text_x, text_y, str((scalebar_width*100)/1000) +' km', fontsize=10, rotation=0.,
        horizontalalignment="center", verticalalignment="center", color='white',
        bbox = dict(boxstyle="square", edgecolor='black', facecolor='black'))

    plt.draw()

    plt.savefig(args.outname + '.png', dpi=300)

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

    parser = ArgumentParser(description='Create plots for topo data')
    parser.add_argument('image', metavar='cub',
                        help='the cube file(s) (.cub) to process, no NULL pixels')
    parser.add_argument('outname',
                        help='the output filename, no extension')
    parser.add_argument('--type', '-t', default='2D',
                       help='type of plot: 2D or 3D')
    parser.add_argument('--contours', '-c', default=True,
                       help='set to True for contour lines')
    parser.add_argument('--cinterval', '-i', default='10',
                       help='interval in meters for contour lines')
    args = parser.parse_args()

    img = CubeFile.open(args.image)
    
    if args.type == '2D':
        color_plot_2D(img, args)

    if args.type == '3D':
        color_topo_3D(img, args)

    img.data 
