# -*- coding: utf-8 -*-
"""
Created on Thu Feb  7 17:18:06 2019

@author: Luciana
"""

from pyqtgraph.Qt import QtCore, QtGui
from PyQt5.QtCore import pyqtSignal, pyqtSlot

import nidaqmx
from Instrument_nidaqmx import initial_nidaqmx, shutters, openShutter, closeShutter, downFlipper, upFlipper, Flipper_notch532

class Frontend(QtGui.QFrame):

    shutter0_signal = pyqtSignal(bool)
    shutter1_signal = pyqtSignal(bool)
    shutter2_signal = pyqtSignal(bool)
    shutter3_signal = pyqtSignal(bool)
    shutter4_signal = pyqtSignal(bool)
    flipper_signal = pyqtSignal(bool)
    flipper_notch532_signal = pyqtSignal(bool)
    closeSignal = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setUpGUI()
    
    def shutter0button_check(self):
        if self.shutter0button.isChecked():
           self.shutter0_signal.emit(True)
        else:
           self.shutter0_signal.emit(False)

    def shutter1button_check(self):
        if self.shutter1button.isChecked():
           self.shutter1_signal.emit(True)
        else:
           self.shutter1_signal.emit(False)
   
    def shutter2button_check(self):
        if self.shutter2button.isChecked():
           self.shutter2_signal.emit(True)
        else:
           self.shutter2_signal.emit(False)

    def shutter3button_check(self):
        if self.shutter3button.isChecked():
           self.shutter3_signal.emit(True)
        else:
           self.shutter3_signal.emit(False)
           
    def shutter4button_check(self):
        if self.shutter4button.isChecked():
           self.shutter4_signal.emit(True)
        else:
           self.shutter4_signal.emit(False) 

    def powerbutton_check(self):
        if self.powerbutton.isChecked():
           self.flipper_signal.emit(True)
           self.powerbutton.setText('High \n power')
           self.powerbutton.setStyleSheet("color: rgb(155, 064, 032); ")
        else:
           self.flipper_signal.emit(False)
           self.powerbutton.setText('Low \n power')
           self.powerbutton.setStyleSheet("color: rgb(12, 183, 242); ")
           
    def notch532_check(self):
        if self.notch532button.isChecked():
           self.flipper_notch532_signal.emit(True)
           self.notch532button.setText('Notch 532? Down')
        else:
           self.flipper_notch532_signal.emit(False)
           self.notch532button.setText('Notch 532? Up')
 
    def setUpGUI(self):       
 
        # Shutters
        self.shutter0button = QtGui.QCheckBox('532 nm (green)')
        self.shutter0button.clicked.connect(self.shutter0_signal)
        self.shutter0button.setStyleSheet("color: green; ")

        self.shutter1button = QtGui.QCheckBox('642 nm (red)')
        self.shutter1button.clicked.connect(self.shutter1_signal)
        self.shutter1button.setStyleSheet("color: red; ")

        self.shutter2button = QtGui.QCheckBox('405 nm (blue)')
        self.shutter2button.clicked.connect(self.shutter2_signal)
        self.shutter2button.setStyleSheet("color: blue; ")
        
        self.shutter3button = QtGui.QCheckBox('808 nm (NIR)')
        self.shutter3button.clicked.connect(self.shutter3_signal)
        self.shutter3button.setStyleSheet("color: black; ")
        
        self.shutter4button = QtGui.QCheckBox('592 nm (orange)')
        self.shutter4button.clicked.connect(self.shutter4_signal)
        self.shutter4button.setStyleSheet("color: rgb(190,100,0); ")

        self.shutter0button.setToolTip('Open/close Green 532 shutter')
        self.shutter1button.setToolTip('Open/close Red 640 shutter')
        self.shutter2button.setToolTip('Open/close Blue 405 shutter')
        self.shutter3button.setToolTip('Open/close IR 808 shutter')
        self.shutter4button.setToolTip('Open/close IR 592 shutter')
        
        # Flippers 
        self.powerbutton = QtGui.QCheckBox('Power')
        self.powerbutton.clicked.connect(self.powerbutton_check)
        
        self.notch532button = QtGui.QCheckBox('Notch 532 nm')
        self.notch532button.clicked.connect(self.notch532_check)
        
        self.grid_shutters = QtGui.QWidget()
        grid_shutters_layout = QtGui.QGridLayout()
        self.grid_shutters.setLayout(grid_shutters_layout)
        grid_shutters_layout.addWidget(self.shutter0button, 0, 1)
        grid_shutters_layout.addWidget(self.shutter1button, 1, 1)
        grid_shutters_layout.addWidget(self.shutter2button, 2, 1)
        grid_shutters_layout.addWidget(self.shutter3button, 3, 1)
        grid_shutters_layout.addWidget(self.shutter4button, 4, 1)
        grid_shutters_layout.addWidget(self.powerbutton, 1, 2, 1, 2)
        grid_shutters_layout.addWidget(self.notch532button, 5, 1)
        
      # GUI layout
        
        grid = QtGui.QGridLayout()
        self.setLayout(grid)    
        grid.addWidget(self.grid_shutters)

    def closeEvent(self, event):
        self.closeSignal.emit()
        shuttersThread.exit()

class Backend(QtCore.QObject):

    def __init__(self, task_nidaqmx, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.shuttertask = task_nidaqmx[0]
        self.flippertask = task_nidaqmx[1]
        self.flipper532task = task_nidaqmx[2]
        
    @pyqtSlot(bool)
    def shutter0(self, shutterbool):  # 532
        if shutterbool:
            openShutter(shutters[0], self.shuttertask)
        else:
            closeShutter(shutters[0], self.shuttertask)
            
    @pyqtSlot(bool)
    def shutter1(self, shutterbool):  # 642
        if shutterbool:
            openShutter(shutters[1], self.shuttertask)
        else:
            closeShutter(shutters[1], self.shuttertask)
            
    @pyqtSlot(bool)
    def shutter2(self, shutterbool):  # 405
        if shutterbool:
            openShutter(shutters[2], self.shuttertask)
        else:
            closeShutter(shutters[2], self.shuttertask)
            
    @pyqtSlot(bool)
    def shutter3(self, shutterbool): # 808
        if shutterbool:
            openShutter(shutters[3], self.shuttertask)
        else:
            closeShutter(shutters[3], self.shuttertask)
            
    @pyqtSlot(bool)
    def shutter4(self, shutterbool):  # 592
        if shutterbool:
            openShutter(shutters[4], self.shuttertask)
        else:
            closeShutter(shutters[4], self.shuttertask)
            
    @pyqtSlot(bool)
    def power_change(self, flipperbool):
        if flipperbool:
           downFlipper(self.flippertask) #potencia alta
        else:
           upFlipper(self.flippertask) #potencia baja
           
    @pyqtSlot(bool)
    def notch532_change(self, flipperbool):
        if flipperbool:
           Flipper_notch532(self.flipper532task, 'down') 
        else:
           Flipper_notch532(self.flipper532task,'up')

    @pyqtSlot()
    def close(self):

        Flipper_notch532(self.flipper532task,'down')
        
        self.shuttertask.close()
        self.flippertask[1].close()
        self.flippertask[0].close()
        self.flipper532task.close()

    def make_connection(self, frontend):
        frontend.shutter0_signal.connect(self.shutter0)
        frontend.shutter1_signal.connect(self.shutter1)
        frontend.shutter2_signal.connect(self.shutter2)
        frontend.shutter3_signal.connect(self.shutter3)
        frontend.shutter4_signal.connect(self.shutter4)
        frontend.flipper_signal.connect(self.power_change)
        frontend.flipper_notch532_signal.connect(self.notch532_change)
        frontend.closeSignal.connect(self.close)

if __name__ == '__main__':

        #app = QtGui.QApplication([])
    
    if not QtGui.QApplication.instance():
        app = QtGui.QApplication([])
        open_terminal = True
    else:
        open_terminal = False
        app = QtGui.QApplication.instance() 

    gui = Frontend()   
    task_nidaqmx = initial_nidaqmx(nidaqmx)
    worker = Backend(task_nidaqmx)

    worker.make_connection(gui)
    #gui.make_connection(worker)

    ## Shutters laser, flipper's Thread
    shuttersThread = QtCore.QThread()
    worker.moveToThread(shuttersThread)
    shuttersThread.start()

    gui.show()
   # app.exec_()
        
                