# -*- coding: utf-8 -*-
"""
Created on Tue Sep 13 11:55:57 2022

@author: Steph
"""
from datetime import datetime
import os
import vxi11

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
    # Sixth line mentions dither settings and the curve type
    curveName = ("IV" if self.IV else "V\u03C6")
    k.write("Dither: " + self.dither() + "\tCurve Type: " + curveName + "\n")
    # Formatting the next line
    k.write("I_Flux\tI_Bias\tVoltage\tdV/dI F(\u03A9)\tRd(\u03A9)\tSv\tSi")
    # Close the file once you are done appending
    k.close()

    return fullPath


def startStopButton_clicked(self):
    # Call the function to change the text
    startStopButtonTextChange(self)
    if self.startStopButton.text() == "STOP": #specifically: you are now running kalamari
        kalamariMain(self)

def kalamariMain(self):
    #Make the data file
    filename = createKalamariFile(self)
    kalamariData = []

    #Convert flux/bias inputs to their voltages (V = IR)
    minFluxV = self.minFlux() * self.rFlux() / 1000000
    maxFluxV = self.maxFlux() * self.rFlux() / 1000000
    minBiasV = self.minBias() * self.rBias() / 1000000
    maxBiasV = self.maxBias() * self.rBias() / 1000000

    #Get the array of points to use. May as well have numpy do it.
    fluxPointsV = np.linspace(minFluxV,maxFluxV,num = self.fluxSteps()+1)
    biasPointsV = np.linspace(minBiasV,maxBiasV,num = self.biasSteps()+1)

    #Keep the array of bias points on hand for appending to the data docs
    fluxPoints = np.linspace(self.minFlux(),self.maxFlux(),num = self.fluxSteps()+1)
    biasPoints = np.linspace(self.minBias(),self.maxBias(),num = self.biasSteps()+1)

    #Set up inner/outer loop based on curve type
    if self.IV: #looking at this and considering it: i'm not sure I know how kalamari gets one of these.
        innerPoints = fluxPointsV
        outerPoints = biasPointsV
    else:
        innerPoints = biasPointsV
        outerPoints = fluxPointsV

    if self.noise():
        #Establish connection with the spectrum analyzer
        instr = vxi11.Instrument("10.20.4.3")
        #Make sure the connection was successful
        instr.ask("*IDN?")
        #We don't care what it says; if the connection fails it'll throw an error.
        #you WILL still get a response, though, so print it to console if that's something you want to do.

        #set a low timeout to reduce the amount of waiting you have to do.
        instr.timeout = 1

        filedir = str(self.wafer()) + " " + str(self.die())
        command = ":Instrument:MakeDir \"{}\"".format(filedir) #insert variable into string
        try:
            instr.ask(command)
        except Exception:
            pass


    
    #Setup is done; just run the loops
    #Running by index makes data logging simpler; x1 and x2 are effectively tied to the index
    #Assuming use of DACs A and B
    for i in range(0,len(outerPoints)):
        x1 = outerPoints[i]
        SetDACVoltage(0,x1)
        for j in range(0,len(innerPoints)):
            x2 = innerPoints[j]
            SetDACVoltage(1,x2)

            #Put the data in the file as you gather it
            k = open(filename, 'a')

            #Get the data
            voltage = ReadADC(0)

            if self.noise():
                noiseFileName = filedir + "\\Noise trace {}, {}".format(i,j)
                try:
                    instr.ask(":Displays:Graph(1):SaveTrace 101,\"{}.txt\",0".format(noiseFileName))
                except Exception:
                    pass
                #Now we WANT the output.
                output = instr.ask(":Instrument:TransferFile: \"{}.txt\",0".format(noiseFileName))
                #take the output and the 10kHz point and save it
                sV = output[10]


            if self.dither() != 0:
                #dither up x1
                SetDACVoltage(0,x1 + DACLSB*self.dither())
                ditherRight = ReadADC(0)
                #dither down x1
                SetDACVoltage(0,x1 - DACLSB*self.dither())
                ditherLeft = ReadADC(0)
                #reset x1
                SetDACVoltage(0,x1)
                x1Slope = (ditherLeft-ditherRight)/(DACLSB*self.dither()*2)

                #dither up x2
                SetDACVoltage(1,x2 + DACLSB*self.dither())
                ditherUp = ReadADC(0)
                #dither down x2
                SetDACVoltage(1,x2 - DACLSB*self.dither())
                ditherDown = ReadADC(0)
                #reset x2
                SetDACVoltage(1,x2)
                x2Slope = (ditherUp-ditherDown)/(DACLSB*self.dither()*2)
            


            




            


