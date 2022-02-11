# -*- coding: utf-8 -*-
"""
Created on Fri Feb 11 14:09:30 2022

@author: TBaker
"""

import serial
import numpy


ser = serial.Serial('COM7', 9600, timeout=1)

command = 4


ser.close()
