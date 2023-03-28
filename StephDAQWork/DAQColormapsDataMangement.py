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

# It looks like the array thisData is going to be what I will use
# How do I interpret the indices?
# Maybe it is best then to read off the data file
# However, maybe I could change the data to use pandas

# The x and y values should be the same across all 3 graphs
# It will be the color values that change across each graph

# For the first plot, our color value will be the voltage measured
'''colorsVoltage = dc.I'm not yet sure what to put here'''
