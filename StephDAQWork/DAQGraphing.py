# -*- coding: utf-8 -*-
"""
Created on Wed Oct 19 12:02:56 2022

@author: Steph
"""

# Import the matplotlib library as plt
# This will be our sole graphing library for all intents and purposes
import numpy as np
import matplotlib.pyplot as plt

# We must also import matplotlib.patches for our legend
import matplotlib.patches as mpatches

# We also need to import the code for the daq that collects the data
# We pull our data from this program
'''import DaqCode.py as daq'''

# Import the numpy library as np
# This will aid with data management (mostly arrays for our purposes)

'''
Begin inputting the parameters to create a basic line graph
'''

# Chose the style of our graph
# I chose this one specifically off of matplotlib's style sheet reference
# It's brightly colored for a nice contrast and has a grid
plt.style.use('seaborn-colorblind')

# Create subplots
# 'Subplots' are used to plot multiple graphs on the same window
# We want a 2 x 2 window of graphs
# Create a figure with 4 axes
fig, axs = plt.subplots(2, 2)

# Name the figure
'''chipName is currently a placeholder variable'''
chipName = "CHIP"
fig.suptitle(chipName)

# Now we can name each axes
'''biasX is currently a placeholder variable'''
biasOne = "ONE"
biasTwo = "TWO"
biasThree = "THREE"
biasFour = "FOUR"
axs[0, 0].set_title('Bias 1 = ' + biasOne)
axs[0, 1].set_title('Bias 2 = ' + biasTwo)
axs[1, 0].set_title('Bias 3 = ' + biasThree)
axs[1, 1].set_title('Bias 4 = ' + biasFour)

'''Labeling the axes is on hold until I get clarification on units'''
# Label each x and y axes
axs[0, 0].set_xlabel('ABC')
# Create one y axis label for voltage values
axs[0, 0].set_ylabel('DEF')

# Create a second axes that shares the same x-axis
twinOne = axs[0, 0].twinx()

# Label this "twin" axis
twinOne.set_ylabel('GHI')

# Repeat this process for the remaining subplots
axs[0, 1].set_xlabel('CBA')
axs[0, 1].set_ylabel('FED')
twinTwo = axs[0, 1] = axs[0, 1].twinx()
twinTwo.set_ylabel('IHG')

axs[1, 0].set_xlabel('XYZ')
axs[1, 0].set_ylabel('QRS')
twinThree = axs[1, 0] = axs[1, 0].twinx()
twinThree.set_ylabel('TUV')

axs[1, 1].set_xlabel('ZYX')
axs[1, 1].set_ylabel('SRQ')
twinFour = axs[1, 1] = axs[1, 1].twinx()
twinFour.set_ylabel('VUT')


# Create the legend
# Using matplotlib.patches, we create 'patches' of color that will correspond
# to the color of the lines in our graphs
# Our parameters are the color of the patch and its label
# Create two patches, one for voltage and the other for noise
voltagePatch = mpatches.Patch(color='blue', label='Si')
noisePatch = mpatches.Patch(color='red', label='Voltage')

# To place the legend on our figure, we use figlegend
# Our 'handles' are the entries in our legend
# loc determines the position of the legend on the figure
plt.figlegend(handles=[voltagePatch, noisePatch], loc='lower center')


'''
Extract the data
'''


# Create a while loop to graph the data
# Create a if check statement that checks the bias value and deteremines
# Whether or not to increment the graph


# Superimpose all the graphs on each other

# Boom, done, jupyter script replica
