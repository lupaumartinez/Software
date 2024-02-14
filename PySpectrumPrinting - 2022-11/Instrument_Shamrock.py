#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb  4 13:51:07 2020

@author: luciana
"""

#%% initializing Shamrock

DEVICE = 0
GRATING_150_LINES = 1
GRATING_1200_LINES = 2
GRATING_MIRROR = 3
SHAMROCK_INPUT_FLIPPER = 1
SHAMROCK_OUTPUT_FLIPPER = 2
SHAMROCK_DIRECT_PORT = 0
SHAMROCK_SIDE_PORT = 1
INPUT_SLIT_PORT = 1

#Camera Andor 885
NumberofPixel = 1002
PixelWidth = 8 #um

namePortsIN = ['Port 0: Optical fiber', 'Port 1: Slit']
namePortsOUT =  ['Port 0: Camera Andor', 'Port 1: Not used']
nameGrating = ['150 lines/mm', '1200 lines/mm', 'Mirror']

