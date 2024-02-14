# -*- coding: utf-8 -*-
"""
Created on Thu Feb  7 17:18:06 2019

@author: Luciana
"""

from datetime import datetime
import numpy as np

from pyqtgraph.Qt import QtCore, QtGui
#from pyqtgraph.dockarea import DockArea, Dock
from PyQt5.QtCore import pyqtSignal, pyqtSlot

from Shamrock import Shamrock
from Instrument_Shamrock import DEVICE, SHAMROCK_DIRECT_PORT, SHAMROCK_INPUT_FLIPPER, SHAMROCK_OUTPUT_FLIPPER, SHAMROCK_SIDE_PORT, INPUT_SLIT_PORT, NumberofPixel, PixelWidth, GRATING_1200_LINES, GRATING_150_LINES, GRATING_MIRROR, nameGrating, namePortsIN, namePortsOUT

class Frontend(QtGui.QFrame):

    modesSignal = pyqtSignal(str, str, str)

    zeroorderSignal = pyqtSignal()
    setslitSignal = pyqtSignal(float)

    offsetSignal = pyqtSignal(list)
    wavelengthSignal = pyqtSignal(float)

    closeSignal = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setUpGUI()

    def setUpGUI(self):

        #Spectrometer Shamrock

        mode_portIN_Label = QtGui.QLabel('Input Fliper Mirror:')
        self.mode_portIN = QtGui.QComboBox()
        self.mode_portIN.addItems(namePortsIN)
        self.mode_portIN.setCurrentIndex(1)
        
        mode_portOUT_Label = QtGui.QLabel('Output Fliper Mirror:')
        self.mode_portOUT = QtGui.QComboBox()
        self.mode_portOUT.addItems(namePortsOUT)
        self.mode_portOUT.setCurrentIndex(0)
        
        mode_grating_Label = QtGui.QLabel('Grating:')
        self.mode_grating = QtGui.QComboBox()
        self.mode_grating.addItems(nameGrating)
        self.mode_grating.setCurrentIndex(0)
        
        self.set_configuration_button = QtGui.QPushButton('Set configuration')
        self.set_configuration_button.clicked.connect(self.spectrum_configuration)

        slit_Label =  QtGui.QLabel('Side Input Slit (µm):')
        self.slit_Edit = QtGui.QLineEdit('10') 
        self.set_slit_button = QtGui.QPushButton('Set slit')
        self.set_slit_button.clicked.connect(self.set_slit)

        self.zero_order_button = QtGui.QPushButton('Go to zero order')
        self.zero_order_button.clicked.connect(self.zero_order_check)

        grating_offset_Label = QtGui.QLabel('Grating offset:')
        self.grating_offset_Edit = QtGui.QLineEdit('100') 
        detector_offset_Label = QtGui.QLabel('Detector offset:')
        self.detector_offset_Edit = QtGui.QLineEdit('0')
        self.offsets_button = QtGui.QPushButton('Set Offsets')
        self.offsets_button.clicked.connect(self.spectrum_set_offsets)  
        
        lambda_Label = QtGui.QLabel('λ(nm):')
        self.lambda_Edit = QtGui.QLineEdit('532')
        self.set_wavelength_button = QtGui.QPushButton('Set Wavelength')
        self.set_wavelength_button.clicked.connect(self.spectrum_set_wavelength)
                  

        self.spectrum = QtGui.QWidget()
        spectrum_parameters_layout = QtGui.QGridLayout()
        self.spectrum.setLayout(spectrum_parameters_layout)
        
        spectrum_parameters_layout.addWidget(mode_portIN_Label,                  0, 0)
        spectrum_parameters_layout.addWidget(self.mode_portIN,                   0, 1)
        spectrum_parameters_layout.addWidget(mode_portOUT_Label,                 1, 0)
        spectrum_parameters_layout.addWidget(self.mode_portOUT,                  1, 1)
        spectrum_parameters_layout.addWidget(mode_grating_Label,                 2, 0)
        spectrum_parameters_layout.addWidget(self.mode_grating,                  2, 1)
        spectrum_parameters_layout.addWidget(self.set_configuration_button,      3, 0)

        spectrum_parameters_layout.addWidget(slit_Label,                         4, 0)
        spectrum_parameters_layout.addWidget(self.slit_Edit,                     4, 1)
        spectrum_parameters_layout.addWidget(self.set_slit_button,               5, 0)

        spectrum_parameters_layout.addWidget(self.zero_order_button,             6, 0)

        spectrum_parameters_layout.addWidget(grating_offset_Label,               7, 0)
        spectrum_parameters_layout.addWidget(self.grating_offset_Edit,           7, 1)
        spectrum_parameters_layout.addWidget(detector_offset_Label,              8, 0)
        spectrum_parameters_layout.addWidget(self.detector_offset_Edit,          8, 1)
        spectrum_parameters_layout.addWidget(self.offsets_button,                9, 0)
        
        spectrum_parameters_layout.addWidget(lambda_Label,                      10, 0)
        spectrum_parameters_layout.addWidget(self.lambda_Edit,                  10, 1)
        spectrum_parameters_layout.addWidget(self.set_wavelength_button,        11, 1)
        

        # GUI layout
        
        grid = QtGui.QGridLayout()
        self.setLayout(grid)
        grid.addWidget(self.spectrum)

    def spectrum_configuration(self):

        port_in = str(self.mode_portIN.currentText())
        port_out = str(self.mode_portOUT.currentText())
        mode_grating = str(self.mode_grating.currentText())
       
        self.modesSignal.emit(port_in, port_out, mode_grating) 
        
    def spectrum_set_offsets(self):

        offset = [int(self.grating_offset_Edit.text()), int(self.detector_offset_Edit.text())]

        self.offsetSignal.emit(offset)
        
    def spectrum_set_wavelength(self):
        
        wavelength = float(self.lambda_Edit.text())

        self.wavelengthSignal.emit(wavelength)
        
    def set_slit(self):
        #if self.self_slit_button.isChecked:
        slit_width = float(self.slit_Edit.text())
        self.setslitSignal.emit(slit_width)

    def zero_order_check(self):
        #if self.zero_order_button.isChecked:
        self.zeroorderSignal.emit()

    def closeEvent(self, *args, **kwargs):
        
        self.closeSignal.emit()
        
        super().closeEvent(*args, **kwargs)

class Backend(QtCore.QObject):
    
    gratingSignal = pyqtSignal(str)
    
    def __init__(self, mySpectrometer, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.mySpectrometer = mySpectrometer

        mySpectrometer.ShamrockSetNumberPixels(DEVICE, NumberofPixel)
        mySpectrometer.ShamrockSetPixelWidth(DEVICE, PixelWidth)
        
        mySpectrometer.ShamrockSetFlipperMirror(DEVICE, SHAMROCK_INPUT_FLIPPER, SHAMROCK_SIDE_PORT)
        self.port_in = namePortsIN[1]
        
        mySpectrometer.ShamrockSetFlipperMirror(DEVICE, SHAMROCK_OUTPUT_FLIPPER, SHAMROCK_DIRECT_PORT)
        
        mySpectrometer.ShamrockSetGrating(DEVICE, GRATING_150_LINES)
        self.grating = GRATING_150_LINES
        
    @pyqtSlot(str, str, str)
    def set_configuration(self, port_in, port_out, mode_grating):

        if port_in == namePortsIN[0]:
           ret = self.mySpectrometer.ShamrockSetFlipperMirror(DEVICE, SHAMROCK_INPUT_FLIPPER, SHAMROCK_DIRECT_PORT)
           print(datetime.now(), '[Shamrock] Port IN = ', namePortsIN[0], ret)
           self.port_in = port_in
        else:
           ret = self.mySpectrometer.ShamrockSetFlipperMirror(DEVICE, SHAMROCK_INPUT_FLIPPER, SHAMROCK_SIDE_PORT)
           print(datetime.now(), '[Shamrock] Port IN = ', namePortsIN[1], ret)
           self.port_in = port_in
           
        if port_out == namePortsOUT[0]:
           ret = self.mySpectrometer.ShamrockSetFlipperMirror(DEVICE, SHAMROCK_OUTPUT_FLIPPER, SHAMROCK_DIRECT_PORT)
           print(datetime.now(), '[Shamrock] Port OUT = ', namePortsOUT[0], ret)
        else:
           ret = self.mySpectrometer.ShamrockSetFlipperMirror(DEVICE, SHAMROCK_OUTPUT_FLIPPER, SHAMROCK_SIDE_PORT)
           print(datetime.now(), '[Shamrock] Port OUT = ', namePortsOUT[1], ret)

        if mode_grating == nameGrating[0]:
           ret = self.mySpectrometer.ShamrockSetGrating(DEVICE, GRATING_150_LINES)
           self.grating = GRATING_150_LINES
           print(datetime.now(), '[Shamrock] Mode Grating = ', nameGrating[0], ret)
           self.gratingSignal.emit(nameGrating[0])  #to StepandGlue set_wavelength_window
        elif mode_grating == nameGrating[1]:
           ret = self.mySpectrometer.ShamrockSetGrating(DEVICE, GRATING_1200_LINES)
           self.grating = GRATING_1200_LINES
           self.gratingSignal.emit(nameGrating[1]) #to StepandGlue set_wavelength_window
           print(datetime.now(), '[Shamrock] Mode Grating = ', nameGrating[1], ret)
        else:
           ret = self.mySpectrometer.ShamrockSetGrating(DEVICE, GRATING_MIRROR)
           self.grating = GRATING_MIRROR
           print(datetime.now(), '[Shamrock] Mode Grating = ', nameGrating[2], ret)

    @pyqtSlot(float)
    def open_slit(self, slit_width):

        ret = self.mySpectrometer.ShamrockSetAutoSlitWidth(DEVICE, INPUT_SLIT_PORT, slit_width)
        print(datetime.now(), '[Shamrock] Open Slit with ', slit_width, ret)

          
    @pyqtSlot(list)
    def set_offsets(self, offset):

        grating_offset = offset[0] 
        detector_offset = offset[1]

        ret = self.mySpectrometer.ShamrockSetGratingOffset(DEVICE, self.grating, grating_offset)
        print(datetime.now(), '[Shamrock] Grating Offset with ', grating_offset, ret)

        ret = self.mySpectrometer.ShamrockSetDetectorOffset(DEVICE, detector_offset)
        print(datetime.now(), '[Shamrock] Detector Offset with ', detector_offset, ret)

    @pyqtSlot()
    def goto_zeroorder(self):

        self.mySpectrometer.ShamrockGotoZeroOrder(DEVICE)
        print(datetime.now(), '[Shamrock] Wavelength = ', self.mySpectrometer.ShamrockGetWavelength(DEVICE))
        
    @pyqtSlot(float)
    def set_wavelength(self, Wavelength):

        self.mySpectrometer.ShamrockSetWavelength(DEVICE, Wavelength)
        print(datetime.now(), '[Shamrock] Wavelength = ', self.mySpectrometer.ShamrockGetWavelength(DEVICE))
       
        ret, calibration = self.mySpectrometer.ShamrockGetCalibration(DEVICE, NumberofPixel)
        cal = np.array(list(calibration))
        #'ver el liveview de la camara'
        
        print(datetime.now(), '[Shamrock] Calibration center Wavelength = ', cal)
        
        return cal 

    @pyqtSlot()    
    def close(self):

        self.mySpectrometer.ShamrockClose()
        print(datetime.now(), '[Shamrock] Close')
             
    def make_connection(self, frontend): 

        frontend.modesSignal.connect(self.set_configuration)
        frontend.setslitSignal.connect(self.open_slit)
        frontend.offsetSignal.connect(self.set_offsets)
        frontend.zeroorderSignal.connect(self.goto_zeroorder) 
        frontend.wavelengthSignal.connect(self.set_wavelength)
        frontend.closeSignal.connect(self.close)

if __name__ == '__main__':

    app = QtGui.QApplication([])

    gui = Frontend()
    
    mySpectrometer = Shamrock()
    inipath = 'C:\\Program Files (x86)\\Andor SOLIS\\SPECTROG.ini'
    mySpectrometer.ShamrockInitialize(inipath)
    ret, serial_number = mySpectrometer.ShamrockGetSerialNumber(DEVICE)
    print(datetime.now(), '[Shmarock] Serial number = {}'.format(serial_number))

    worker = Backend(mySpectrometer)

    worker.make_connection(gui)
    #gui.make_connection(worker)

    spectrumThread = QtCore.QThread()
    worker.moveToThread(spectrumThread)
    spectrumThread.start()

    gui.show()
   # app.exec_()

    