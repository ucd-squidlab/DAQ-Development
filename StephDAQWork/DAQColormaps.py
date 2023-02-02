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
import matplotlib
import matplotlib.pyplot as plt
import numpy as np

""" I'm not sure yet as to why these were imported """


# We will have 3 (sub)plots
# Each plot will have the same x and y axis
# The color will be the depedent variable

# For plot 1, our depdent variable will be Isot
# For plot 2, our depdent variable will be dIsot/dphi
# For plot 3, our depdent variable will be noise

# The last key part of this code is that it needs to incorporate some sort of
# crosshair or dial that can scan along the x and y axes of each plot
# simultaneously and read the 'color value' off each plot


""" 
The following code is 'dummy code' I used to test the custom cmap capabilities 
"""

# Randomly generate x and y values

x = np.random.random(200)
y = np.random.random(200)

# This part was retrieved from a youtube tutorial I had watched
# I'm not necessarily sure why he calls it 'classes' because that makes me
# associate it with python class(es)
# I'm not sure what randint means

classes = np.random.randint(0, 100, 200)

# Create a custom color map for all intents and purposes
# LinearSegmentedColormap will give us a spectrum of colors
# "custom" is an arbitrary name I chose for a required input
# Some colors are listed by names others are listed by hex code because they
# do not have a name recognized by matplotlib
# This spectrum should mimic the colorbars in the other SOT journals

custom_cmap = matplotlib.colors.LinearSegmentedColormap.from_list(
    "custom", ["#00008B", "blue", "cyan", "green", "yellow", "orange", "red", "#8B0000"])

# When plotting
plt.scatter(x, y, c=classes, cmap=custom_cmap)
plt.colorbar()
plt.show()
