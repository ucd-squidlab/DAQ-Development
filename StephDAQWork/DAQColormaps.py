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
import matplotlib as mlp
import matplotlib.pyplot as plt

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
