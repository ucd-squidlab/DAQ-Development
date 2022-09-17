# -*- coding: utf-8 -*-
"""
Created on Tue Sep 13 11:55:57 2022

@author: Steph
"""
from datetime import datetime
import os

# Change the text of the button according to its clicked status


def startStopButtonTextChange(self):
    if self.startStopButton is not None:
        text = self.startStopButton.text()
        self.startStopButton.setText("STOP" if text == "START" else "START")


# Create a function to get the current points for the graph


def getXPoints(self):
    # Calculate the range by subtracting the beginning value from the end value
    fluxRange = int(self.maxFlux()) - int(self.minFlux())
    # Calculates the interval by dividing the range by the number of steps
    fluxInterval = fluxRange / int(self.stepsFlux())
    # Adding one sets the first step as step 0
    stepsFluxInput = int(self.stepsFlux()) + 1
    # Set start point
    fluxStart = int(self.minFlux())
    # Create an array
    xPointsArray = []
    # Append the previously made array with a for loop
    # Calculate each point on the x axis
    for i in range(stepsFluxInput):
        xPointsArray.append(fluxStart)
        fluxStart = fluxStart + fluxInterval
    return xPointsArray

# Create a function to get the bias points for the graph


def getYPoints(self):
    # Calculate the range by subtracting the beginning value from the end value
    biasRange = int(self.maxBias()) - int(self.minBias())
    # Calculates the interval by dividing the range by the number of steps
    biasInterval = biasRange / int(self.stepsBias())
    # Adding one sets the first step as step 0
    stepsBiasInput = int(self.stepsBias()) + 1
    # Set start point
    biasStart = int(self.minBias())
    # Create an array
    yPointsArray = []
    # Append the previously made array with a for loop
    # Calculate each point on the y axis
    for i in range(stepsBiasInput):
        yPointsArray.append(biasStart)
        biasStart = biasStart + biasInterval
    return yPointsArray

# Convert the start and end points to volts to pass to ConvertRangeDAC


def convertToVolts(self, startI, endI):
    # Multiply the start point by the resistance
    startV = startI * int(self.rFlux())
    # Multiply the end point by the resistance
    endV = endI * int(self.rFlux())
    return startV, endV

# Somewhere in here I think is where my toggle checks need to happen

def graphToggle(self):
    self.VPhiIVSlider.valueChanged[1].connect(self.changeValue)


def noiseToggle(self):
    self.noiseNoNoiseSlider.valueChanged[1].connect(self.changeValue)


def slopeToggle(self):
    self.slopeSlider.valueChanged[1].connect(self.changeValue)


def ditherToggle(self):
    self.ditherSlider.valueChanged[1].connect(self.changeValue)

# Create a function to get the current date for file purposes


def getDate():
    # Use the method datetime.now() to get the current date and time
    now = datetime.now()
    # Format the retrieved date and time
    getDate.dt_string = now.strftime("%Y%m%d %H%M%S")
    return


def createKalamariFile(self):
    # Call the function to get the date so we can title the file
    getDate()
    # Get the file path as either the placeholder text or the user input
    filePath = self.path() or self.pathInput.placeholderText()
    # This variable should remain the same even when brought to the mac
    fileName = str("Kalamari Data " + str(self.wafer()) +
                   " " + str(self.die()) + " " + getDate.dt_string)
    # Joining both the path and the fileName
    fullPath = os.path.join(filePath, fileName+".txt")
    # For now I have my path directory written so that
    # it will actually appear on my computer
    # When this is brought to run on one of the Macs,
    # the file will be the inputted path directory + the fileName
    k = open(fullPath, 'w')
    # Test to see if stuff is actually being written to the file
    # by writing the first line
    k.write("Kalamari Generated Noise File\n")
    # Write the second line
    k.write("Date: " + getDate.dt_string + " Wafer-Die: " +
            self.wafer() + self.die() + " Initials: " +
            self.initials() + " Book/Page: " + self.book()
            + "/" + self.page() + "\n")
    # Third line is just the one string
    k.write("Paramters: \n")
    # Fourth line is everything pertaining to flux
    k.write("Flux From: " + self.minFlux() + " Flux To: " +
            self.maxFlux() + " Flux Steps: " +
            self.stepsFlux() + " Flux Resistance(RFlux): " +
            self.rFlux() + "\n")
    # Fifth line is everything pertaining to bias
    k.write("Bias From: " + self.minBias() + " Bias To: " +
            self.maxBias() + " Bias Steps: " +
            self.stepsBias() + " Bias Resistance(RBias): " +
            self.rBias() + "\n")
    # Sixth line is everything pertaining to multimeter settings.
    # THE CODE IS ANGRY RIGHT NOW BECAUSE THE VARIABLE DITHERVALUE IS STILL
    # COMMENTED OUT FROM ABOVE
    # k.write("Tsettle: " + self.tSettle() + " Gain: " +
    # self.gain() + " NPLC: " + self.NPLC() + " Range: " +
    # self.range() + " Dither: " + ditherValue + "\n")
    # Seventh line defines what type of graph it is
    # I STILL HAVE NOT WRITTEN THE CODE FOR THE VPHI IV TOGGLE
    k.write("Curve Type: \n")
    # Formatting the next line
    # SOMETHING WENT TERRIBLY WRONG HERE
    k.write("I_Flux\tI_Bias\tVoltage\tdV/dI F(\omega)\tRd(\omega)\tSv\tSi")
    # Close the file once you are done appending
    k.close()


def startStopButton_clicked(self):
    # Call the function to change the text
    startStopButtonTextChange(self)
    createKalamariFile(self)
    # Call the function and pass the arguments of the fromFlux and toFlux Input
    startV, endV = convertToVolts(self, int(self.minFlux()), int(self.maxFlux()))

    #daq.ConvertRangeDAC(startV, endV, int(self.stepsFlux()))
