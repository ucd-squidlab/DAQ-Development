# -*- coding: utf-8 -*-
"""
Created on Mon Jan 30 13:59:58 2023

@author: Steph
"""

# This program is designed to make colormaps of various data from Kalamari'
# The x-axis is intended to plot flux
# The y-axis is intended to plot bias current
# And for SOTs, the color is intended to plot current through the SOT

# As always, begin by importing the matplotlib library
# To make a clear distinction between commands pertaining to our colormaps
# and plotting, I chose to import matplotlib as mlp and our
# pyplot functions as plt

from matplotlib.colors import ListedColormap, LinearSegmentedColormap
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.axes_grid1 import make_axes_locatable


# We will have 3 (sub)plots
# The 1 parameter creates 1 row, the 3 parameter creates 3 columns
fig, axs = plt.subplots(1, 3, figsize=(15, 15))

# Name the figure
''' "CHIP" is a placeholder variable. Some value will probably be passed from
DaqCode'''
chipName = "CHIP"
fig.suptitle(chipName)


# For all intents and purposes, the y axis will be shared
# The color will be the depedent variable

# For plot 1, our depdent variable will be Isot
# For plot 2, our depdent variable will be dIsot/dphi
# For plot 3, our depdent variable will be noise
axs[0].title.set_text('I' + u'\u209B' + u'\u2092' + u'\u209C')
axs[1].title.set_text('dI' + u'\u209B' + u'\u2092' + u'\u209C' + '/dt')
axs[2].title.set_text('Noise')


""" 
The following data is mock data 
"""

# Randomly generate x and y values

x = np.random.random(200)
y = np.random.random(200)

# This creates data for our color values

colors = np.random.randint(0, 30, 200)

# Create a custom color map for all intents and purposes
# LinearSegmentedColormap will give us a spectrum of colors
# "custom" is an arbitrary name I chose for a required input
# Some colors are listed by names others are listed by hex code because they
# do not have a name recognized by matplotlib
# This spectrum should mimic the colorbars in the other SOT journals
custom_cmap = mpl.colors.LinearSegmentedColormap.from_list(
    "custom", ["#00008B", "blue", "cyan", "green", "yellow", "orange", "red", "#8B0000"])

# Plot commands

# Creates a scatter plot, plotting x and y
# c is the list of colors
# I think this format of code will work better for our processes

# Now the real question, why is this only plotting on axs[2]
plot1 = axs[0].scatter(x, y, c=colors, cmap=custom_cmap)
plot2 = axs[1].scatter(x, y, c=colors, cmap=custom_cmap)
plot3 = axs[2].scatter(x, y, c=colors, cmap=custom_cmap)

# Do the colorbars

cbar1 = fig.colorbar(plot1, ax=axs[0], orientation='horizontal')
cbar2 = fig.colorbar(plot2, ax=axs[1], orientation='horizontal')
cbar3 = fig.colorbar(plot3, ax=axs[2], orientation='horizontal')

# The last key part of this code is that it needs to incorporate some sort of
# crosshair or dial that can scan along the x and y axes of each plot
# simultaneously and read the 'color value' off each plot
