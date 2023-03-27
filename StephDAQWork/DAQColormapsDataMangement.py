# -*- coding: utf-8 -*-
"""
Created on Mon Mar 27 14:11:30 2023

@author: Steph
"""

# This code will be used for the data management portion of the colormaps code

# I suspect I will be using pandas, but I am not entirely sure

import pandas as pd
import DaqCode as dc

'''I need to make the decision of if this data will be read from the code or 
the data file the code saves to '''

# Suppose this script graphs for a SQUID array
# Given this, we can assign our x and y values

# The variable xPointsArray contains every flux value that will be measured at
x = dc.xPointsArray
# The variable yPointsArray contains every bias value that will be measured at
y = dc.yPointsArray

# The x and y values should be the same across all 3 graphs
# It will be the color values that change across each graph

# For the first plot, our color value will be the voltage measured
'''colorsVoltage = dc.I'm not yet sure what to put here'''
