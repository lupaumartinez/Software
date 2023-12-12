


import numpy as np
import time
from datetime import datetime
import os

import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from pyqtgraph.dockarea import Dock, DockArea

from scipy.optimize import curve_fit


def transform_str(str_values):

	values = list(str(str_values).split(","))

	data = []

	for i in range(len(values)):
		data.append(float(values[i]))

	return data


def ajuste_lineal(x, y, ey):
	f = lambda xl, A, B: A*xl+B # la función modelo, con la que ajustamos
	popt, pcov = curve_fit(f, x, y, sigma = ey, absolute_sigma=True)
	sigmas = np.sqrt([pcov[0,0],pcov[1,1]])

	pendiente = round(popt[0], 3)
	error_pendiente = round(sigmas[0],3)

	ordenada = round(popt[1], 3)
	error_ordenada = round(sigmas[1],3)

	ajuste = [pendiente, ordenada]
	error_ajuste = [error_pendiente, error_ordenada]

	return ajuste, error_ajuste

class Frontend(QtGui.QFrame):
    
    linearSignal = pyqtSignal(list, list, float)
    saveSignal = pyqtSignal(list, list, str, str)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setUpGUI()

    def setUpGUI(self):

        x_Label = QtGui.QLabel('Values X')
        self.x_Edit = QtGui.QLineEdit('0,1,2')

        y_Label = QtGui.QLabel('Values Y')
        self.y_Edit = QtGui.QLineEdit('0,2,4')

        y_error_Label =  QtGui.QLabel('Error Value Y')
        self.y_error_Edit = QtGui.QLineEdit('0.1')

        self.plot_button = QtGui.QPushButton('Plot Y vs X')
        self.plot_button.clicked.connect(self.plot_button_check)

        self.linear_button = QtGui.QPushButton('Do linear calibration')
        self.linear_button.clicked.connect(self.linear_button_check)

        pendiente_Label = QtGui.QLabel('Pendiente')
        self.pendiente_Edit = QtGui.QLabel('')
        self.error_pendiente_Edit = QtGui.QLabel('')

        ordenada_Label = QtGui.QLabel('Ordenada')
        self.ordenada_Edit = QtGui.QLabel('')
        self.error_ordenada_Edit = QtGui.QLabel('')

        self.save_legend = QtGui.QLineEdit('Calibration_green_laser.txt')
        self.save_direction = QtGui.QLineEdit('C:/Users/Alumno')
        
        self.save_button = QtGui.QPushButton('Save')
        self.save_button.clicked.connect(self.save_button_check)
        self.save_button.setStyleSheet(
                "QPushButton { background-color: orange; }"
                "QPushButton:pressed { background-color: blue; }")

        self.values_calibration = QtGui.QWidget()
        values_calibration_layout = QtGui.QGridLayout()
        self.values_calibration.setLayout(values_calibration_layout)

        values_calibration_layout.addWidget(x_Label,               1, 1)
        values_calibration_layout.addWidget(self.x_Edit,           1, 2)

        values_calibration_layout.addWidget(y_Label,               2, 1)
        values_calibration_layout.addWidget(self.y_Edit,           2, 2)

        values_calibration_layout.addWidget(y_error_Label,         3, 1)
        values_calibration_layout.addWidget(self.y_error_Edit,     3, 2)

        values_calibration_layout.addWidget(self.plot_button,      4, 1)
        values_calibration_layout.addWidget(self.save_button,      4, 2)
        
        values_calibration_layout.addWidget(self.save_legend,      5, 1)
        values_calibration_layout.addWidget(self.save_direction,   6, 1)


        self.values_calibration_ajuste = QtGui.QWidget()
        calibration_layout = QtGui.QGridLayout()
        self.values_calibration_ajuste.setLayout(calibration_layout)

        calibration_layout.addWidget(self.linear_button,                  1, 1)
        calibration_layout.addWidget(QtGui.QLabel('Values'),              1, 2)
        calibration_layout.addWidget(QtGui.QLabel('Error'),               1, 3)
        calibration_layout.addWidget(pendiente_Label,                     2, 1)
        calibration_layout.addWidget(self.pendiente_Edit,                 2, 2)
        calibration_layout.addWidget(self.error_pendiente_Edit,           2, 3)
        calibration_layout.addWidget(ordenada_Label,                      3, 1)
        calibration_layout.addWidget(self.ordenada_Edit,                  3, 2)
        calibration_layout.addWidget(self.error_ordenada_Edit,            3, 3)
        
      
        calibration_Widget = pg.GraphicsLayoutWidget()  
        plot_calibration =  calibration_Widget.addPlot(row=1, col=1, title="Curve calibration")
        plot_calibration.setLabels(bottom=('X'),
                                left=('Y'))
        plot_calibration.showGrid(x=True, y=True)
        self.curve_data = plot_calibration.plot(open='y')
        self.curve_calibration = plot_calibration.plot(open='y')
        
        #docks

        hbox = QtGui.QHBoxLayout(self)
        dockArea = DockArea()
        hbox.addWidget(dockArea)
        self.setLayout(hbox)
        
        values_dock = Dock('Values calibration')
        values_dock.addWidget(self.values_calibration)
        dockArea.addDock(values_dock)

        values_ajuste_dock = Dock('Linear calibration')
        values_ajuste_dock.addWidget(self.values_calibration_ajuste)
        dockArea.addDock(values_ajuste_dock)

        calibration_dock = Dock('Curve calibration', size = (50, 50))
        calibration_dock.addWidget(calibration_Widget)
        dockArea.addDock(calibration_dock, 'right', values_dock)

    def plot_button_check(self):

        x = str(self.x_Edit.text())
        y = str(self.y_Edit.text())

        self.data_x = transform_str(x)
        self.data_y = transform_str(y)


        if len(self.data_x) == len(self.data_y):

        	self.curve_data.setData(self.data_x, self.data_y, symbol ='o')
        else:
        	print('Error de ploteo. Distintas dimensión X e Y')


    def linear_button_check(self):

        self.error_data_y = float(self.y_error_Edit.text())

        if len(self.data_x) == len(self.data_y):
            self.linearSignal.emit(self.data_x, self.data_y, self.error_data_y)
        else:
        	print('No se puede realizar ajuste lineal. Distintas dimensión X e Y')

    @pyqtSlot(list, list)
    def plot_linear_calibration(self, calibration, error_calibration):

        pendiente = calibration[0]
        ordenada = calibration[1]

        error_pendiente = error_calibration[0]
        error_ordenada = error_calibration[1]

        x = np.linspace(self.data_x[0], self.data_x[-1], 10)
        y = pendiente*x+ordenada

        self.curve_calibration.setData(x, y,
                           pen=pg.mkPen('r', width=1))

        self.pendiente_Edit.setText(format(pendiente))
        self.ordenada_Edit.setText(format(ordenada))

        self.error_pendiente_Edit.setText(format(error_pendiente))
        self.error_ordenada_Edit.setText(format(error_ordenada))

    def save_button_check(self):

        save_legend = str(self.save_legend.text())
        save_direction = str(self.save_direction.text())

        x = str(self.x_Edit.text())
        y = str(self.y_Edit.text())

        self.data_x = transform_str(x)
        self.data_y = transform_str(y)

        if len(self.data_x) == len(self.data_y):
        	self.saveSignal.emit(self.data_x, self.data_y, save_legend, save_direction)
        else:
        	print('No se puede guardar. Distintas dimensión X e Y')
           
        
    def closeEvent(self, *args, **kwargs):
        
        super().closeEvent(*args, **kwargs)
        
    def make_connection(self, backend):
        backend.calibrationSignal.connect(self.plot_linear_calibration)
        
        
class Backend(QtCore.QObject):

    calibrationSignal = pyqtSignal(list, list)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.linearbool = False
        self.calibration = [0, 0]  #ordenada y pendiente
        self.error_calibration = [0, 0]


    @pyqtSlot(list, list, float)
    def linear_calibration(self, data_x, data_y, error_data_y):

    	self.linearbool = True

    	x = np.array(data_x)
    	y = np.array(data_y)
    	error_y = np.ones(len(y))*error_data_y

    	ajuste, error_ajuste = ajuste_lineal(x, y, error_y)
    	self.calibration = ajuste
    	self.error_calibration = error_ajuste

    	self.calibrationSignal.emit(self.calibration, self.error_calibration)

       
    @pyqtSlot(list, list, str, str)    
    def save_data(self, data_x, data_y, name, direction):

        filepath = os.path.abspath(direction)
        timestr = time.strftime("%Y%m%d_%H%M%S_")
        filename =  timestr + 'X_Y_' + name
        full_filename = os.path.join(filepath, filename)

        np.savetxt(full_filename,
                        np.transpose([data_x,
                                     data_y]))

        print("\n Values saved\n")

        if self.linearbool:

        	filename2 = timestr + "pendiente_ordenada_" + name
       		full_filename2 = os.path.join(filepath, filename2)

        	np.savetxt(full_filename2, np.transpose([self.calibration, self.error_calibration]))

        	print("\n Linear calibration saved\n")
        

    def make_connection(self, frontend):

        frontend.linearSignal.connect(self.linear_calibration)
        frontend.saveSignal.connect(self.save_data)

if __name__ == '__main__':

    app = QtGui.QApplication([])

    gui = Frontend()   
    worker = Backend()

    worker.make_connection(gui)
    gui.make_connection(worker)

    gui.show()
    app.exec_()