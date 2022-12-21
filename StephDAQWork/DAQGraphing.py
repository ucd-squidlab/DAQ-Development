# -*- coding: utf-8 -*-
"""
Created on Wed Oct 19 12:02:56 2022

@author: Steph
"""

# Import the matplotlib library as plt
# This will be our sole graphing library for all intents and purposes
import matplotlib as plt

# We must also import matplotlib.patches for our legend
import matplotlib.patches as mpatches

# Import the numpy library as np
# This will aid with data management (mostly arrays for our purposes)
import numpy as np

'''
Begin inputting the parameters to create a basic line graph
'''

# Chose the style of our graph
# I chose this one specifically off of matplotlib's style sheet reference
# It's brightly colored for a nice contrast and has a grid
plt.style.use('seaborn--v0_8-whitegrid')

# Create subplots
# 'Subplots' are used to plot multiple graphs on the same window
# We want a 2 x 2 window of graphs
# Create a figure with 4 axes
fig, axs = plt.subplots(2, 2)

# Name the figure
'''chipName is currently a placeholder variable'''
fig.suptitle(chipName)

# Now we can name each axes
'''biasX is currently a placeholder variable'''
axs[0, 0].set_title('Bias 1 = ' + biasOne)
axs[0, 1].set_title('Bias 2 = ' + biasTwo)
axs[1, 0].set_title('Bias 3 = ' + biasThree)
axs[1, 1].set_title('Bias 4 = ' + biasFour)

'''Labeling the axes is on hold until I get clarification on units'''
# Label each x and y axes
axs[0, 0].set_xlabel('')
# Create one y axis label for voltage values
axs[0, 0].set_ylabel('')
# Create a twin y axis for noise values
axs[0, 0].twin.set_ylabel('')

axs[0, 1].set_xlabel('')
axs[0, 1].set_ylabel('')
axs[0, 1].twin.set_ylabel('')

axs[1, 0].set_xlabel('')
axs[1, 0].set_ylabel('')
axs[1, 0].twin.set_ylabel('')

axs[1, 1].set_xlabel('')
axs[1, 1].set_ylabel('')
axs[1, 1].twin.set_ylabel('')

# Creating multiple scales for the same plot
# Since we are graphing both voltage and noise onto the same plot
# we need to add two y-scales to each graph


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
fig.figlegend(handles=[voltagePatch, noisePatch], loc='lower center')


'''
Create the data
'''


# All this graphing should automatically be done in a separate window
# according to the settings I have picked

# Begin on graph 1
# Take flux values and graph voltage values
# Increment graphs as bias increases
# Some sort of while statement that plots the data for a specific bias value
# Read data from Kalamari Code for the specific bias value
# Increment the axs[] as the bias increases

# Create 4 graphs
# Constrained layout
# Automatically adjusts things so they cleanly fit in the figure window
# Needs to be activated before any axes are added
# It looks like you actually plot the graph using a for loop and increment
# through axs[i] after you format according to the constrained layout

# Superimpose all the graphs on each other

# Boom, done, jupyter script replica
