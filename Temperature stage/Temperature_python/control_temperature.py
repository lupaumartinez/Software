
import time
import numpy as np
import os
from datetime import datetime

import pyqtgraph.ptime as ptime
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
from pyqtgraph.dockarea import Dock, DockArea
from PyQt5.QtCore import pyqtSignal, pyqtSlot

from instrument_arduino import arduino

class Frontend(QtGui.QFrame):

    valuesSignal = pyqtSignal(float, float, float, float, float)
    controlSignal = pyqtSignal(bool)
    line_set_pointSignal = pyqtSignal(bool, float, float) #ira para el ploteo de read_temperature.py
    closeSignal = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setUpGUI()    

    def setUpGUI(self):

    	#Setear temperatura deseada, con su error para ON/OFF 

    	set_point_temperature= QtGui.QLabel('Set point temperature (°C)')
    	self.set_point_temperature = QtGui.QLineEdit('30')
    	error_temperature= QtGui.QLabel('Error temperature (°C)')
    	self.error_temperature = QtGui.QLineEdit('2')

    	#Control PID

    	proporcional_label = QtGui.QLabel('k proporcional')
    	integral_label = QtGui.QLabel('k integral')
    	derivative_label = QtGui.QLabel('k derivative')
    	self.P = QtGui.QLineEdit('-10')
    	self.I = QtGui.QLineEdit('0')
    	self.D = QtGui.QLineEdit('0')

    	# play/stop set temperature button
    	self.setvaluesButton = QtGui.QPushButton('Set Values')
    	self.setvaluesButton.clicked.connect(self.check_setvalues_button)
    	self.setvaluesButton.setToolTip('Se envian estos valores al Arduino')

    	# play/stop set temperature button
    	self.controlButton = QtGui.QPushButton('► Play / ◘ Stop control temperature')
    	self.controlButton.setCheckable(True)
    	self.controlButton.clicked.connect(self.check_control_button)
    	self.controlButton.setToolTip('Play o Stop el control de temperatura')

    	self.paramWidget = QtGui.QWidget()
    	subgrid = QtGui.QGridLayout()
    	self.paramWidget.setLayout(subgrid)

    	subgrid.addWidget(set_point_temperature,                 1,0)
    	subgrid.addWidget(self.set_point_temperature,            1,1)
    	subgrid.addWidget(error_temperature,                     2,0)
    	subgrid.addWidget(self.error_temperature,                2,1)
    	subgrid.addWidget(proporcional_label ,                   3,0)
    	subgrid.addWidget(self.P ,                               3,1)
    	subgrid.addWidget(integral_label ,                       4,0)
    	subgrid.addWidget(self.I ,                               4,1)
    	subgrid.addWidget(derivative_label,                      5,0)
    	subgrid.addWidget(self.D ,                               5,1)
    	subgrid.addWidget(self.setvaluesButton ,                 6,0)
    	subgrid.addWidget(self.controlButton ,                   7,0)

    	#Dock

    	hbox = QtGui.QHBoxLayout(self)
    	dockArea = DockArea()

    	controlDock = Dock('')
    	controlDock.addWidget(self.paramWidget)
    	dockArea.addDock(controlDock)

    	hbox.addWidget(dockArea) 
    	self.setLayout(hbox)


    def check_control_button(self):
    	if self.controlButton.isChecked():
   	       self.controlSignal.emit(True)
    	else:
           self.controlSignal.emit(False)

    def check_setvalues_button(self):

    	set_point_temperature =  float(self.set_point_temperature.text())
    	error_temperature =  float(self.error_temperature.text())
    	proporcional  =  float(self.P.text())
    	integral  =  float(self.I.text())
    	derivative  =  float(self.D.text())

    	if self.setvaluesButton.isChecked:
     	    self.valuesSignal.emit(set_point_temperature,error_temperature, proporcional, integral, derivative)
     	    self.line_set_pointSignal.emit(True, set_point_temperature, error_temperature)

    def closeEvent(self, *args, **kwargs):    
    	self.closeSignal.emit()
    	super().closeEvent(*args, **kwargs)


class Backend(QtCore.QObject):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @pyqtSlot(float, float, float, float, float)
    def set_parameters_control(self, set_poin_t, error_t, P,D,I):
    	print('completar')
    	#comunicar al arduino estos valores

    @pyqtSlot(bool)
    def play_stop_control(self, controlbool):
        
        if controlbool:
            self.start_control_temperature()
        else:
            self.stop_control_temperature()

    def start_control_temperature(self):

        arduino.write(b'250')
        #comunicar al arduino que arranque el control, con los valores seteados

    def stop_control_temperature(self):

        print('completar')

    	#comunicar al arduino que no mande corriente, que lo deje a "0 Volt".

    @pyqtSlot()
    def close_connection(self):

        arduino.close()

    def make_connection(self, frontend):
        frontend.valuesSignal.connect(self.set_parameters_control)
        frontend.controlSignal.connect(self.play_stop_control)
        frontend.closeSignal.connect(self.close_connection)


if __name__ == '__main__':

    from instrument_arduino  import arduino

    app = QtGui.QApplication([])

    gui = Frontend()   
    worker = Backend()

    worker.make_connection(gui)

    temperatureThread = QtCore.QThread()
    worker.moveToThread(temperatureThread) 
    temperatureThread.start()

    gui.show()
    app.exec_()                  













