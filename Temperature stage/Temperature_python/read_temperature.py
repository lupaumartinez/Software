

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

    readSignal = pyqtSignal(bool)
    saveSignal = pyqtSignal()
    closeSignal = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setUpGUI()

    def setUpGUI(self):

    	# play/stop read temperature button
        self.readButton = QtGui.QPushButton('► Play / ◘ Stop read temperature')
        self.readButton .setCheckable(True)
        self.readButton .clicked.connect(self.check_read_button)
        self.readButton .setToolTip('Play o Stop la lectura del sensor de temperatura LM35')

        # save button
        self.saveButton = QtGui.QPushButton('Save')
        self.saveButton.clicked.connect(self.check_save_button)
        self.saveButton.setStyleSheet(
                "QPushButton { background-color: rgb(200, 200, 10); }")
        
        #last temperature lecture
        self.temperature_lecture = QtGui.QLabel('<strong>0.00')

        self.paramWidget = QtGui.QWidget()
        subgrid = QtGui.QGridLayout()
        self.paramWidget.setLayout(subgrid)

        subgrid.addWidget(self.readButton,            1,1)
        subgrid.addWidget(self.saveButton,            1,4)
        subgrid.addWidget(self.temperature_lecture,  1,10)

        #temperature lecture - curve on time
        self.traceWidget = pg.GraphicsLayoutWidget()
        self.plot_temperature = self.traceWidget.addPlot(row=2, col=1, title="Sensor LM35")
        self.plot_temperature .showGrid(x=True, y=True)
        self.plot_temperature .setLabel('left', "Temperature (°C)")
        self.plot_temperature .setLabel('bottom', "Time (s)")
        self.curve = self.plot_temperature.plot(open='y')

        #Para graficar un set_point de referencia de control_temperature.py:
        self.line_set_point_up =  self.plot_temperature.plot(open='y')
        self.line_set_point_down =  self.plot_temperature.plot(open='y')
        self.set_point_bool = False
        self.temperature_up = 0
        self.temperature_down = 0
        
        #duty cycle lecture - curve on time
        self.traceDCWidget = pg.GraphicsLayoutWidget()
        self.plot_dutycycle = self.traceDCWidget.addPlot(row=2, col=1, title="Duty Cycle")
        self.plot_dutycycle.showGrid(x=True, y=True)
        self.plot_dutycycle.setLabel('left', "Duty Cycle")
        self.plot_dutycycle.setLabel('bottom', "Time (s)")
        self.curve_DC = self.plot_dutycycle.plot(open='y')
        

        #Dock

        hbox = QtGui.QHBoxLayout(self)
        dockArea = DockArea()

        traceDock = Dock('', size=(100,1))
        traceDock.addWidget(self.paramWidget)
        dockArea.addDock(traceDock)
      
        viewDock = Dock('Viewbox',size=(100,4))
        viewDock.addWidget(self.traceWidget)
        dockArea.addDock(viewDock, 'bottom', traceDock)

        hbox.addWidget(dockArea) 
        self.setLayout(hbox)

    def check_read_button(self):
        if self.readButton.isChecked():
           self.readSignal.emit(True)
#           self.traceDCWidget.show()
        else:
           self.readSignal.emit(False)
           #self.traceDCWidget.close()

    def check_save_button(self):
        if self.saveButton.isChecked:
            self.saveSignal.emit() 

    @pyqtSlot(list, float)
    def get_data(self, data, last_value): 
        
        n = data[0]
        time = data[1]
        temperature = data[2]

        self.curve.setData(time, temperature,
                           pen=pg.mkPen('y', width=1),
                           shadowPen=pg.mkPen('w', width=3))

        #show = 1000 #opcion de que refrescar la curva
        #if n < show:
           # self.curve.setData(time, temperature,
                       #    pen=pg.mkPen('y', width=1),
                          # shadowPen=pg.mkPen('w', width=3))
        #else:
          #  self.curve.setData(time[n-show:n], temperature[n-show:n],
                     #     pen=pg.mkPen('y', width=1),
                        #   shadowPen=pg.mkPen('w', width=3))   

        self.temperature_lecture.setText(str(last_value))

        if self.set_point_bool:

            self.line_set_point_up.setData(time, np.ones(len(time))*self.temperature_up,
                                           pen=pg.mkPen('r', width=1),
                                         shadowPen=pg.mkPen('r', width=3))

            self.line_set_point_down.setData(time,np.ones(len(time))*self.temperature_down,
                                           pen=pg.mkPen('r', width=1),
                                         shadowPen=pg.mkPen('r', width=3))
            
    @pyqtSlot(list)
    def get_data_dc(self, data): 
        
        n = data[0]
        time = data[1]
        dc = data[2]

        self.curve_DC.setData(time, dc,
                           pen=pg.mkPen('b', width=1),
                           shadowPen=pg.mkPen('w', width=3))

        #show = 1000 #opcion de que refrescar la curva
        #if n < show:
           # self.curve.setData(time, temperature,
                       #    pen=pg.mkPen('y', width=1),
                          # shadowPen=pg.mkPen('w', width=3))
        #else:
          #  self.curve.setData(time[n-show:n], temperature[n-show:n],
                     #     pen=pg.mkPen('y', width=1),
                        #   shadowPen=pg.mkPen('w', width=3))   


    @pyqtSlot(bool, float, float) #de control_temperature.py
    def plot_line_set_point(self, set_point_bool, set_point_temperature, error_temperature):

        self.set_point_bool = set_point_bool

        self.temperature_up = set_point_temperature + error_temperature/2
        self.temperature_down = set_point_temperature - error_temperature/2
  
        self.line_set_point_up.setData(np.linspace(0,10,10), np.ones(10)*self.temperature_up,
                                       pen=pg.mkPen('r', width=1),
                                     shadowPen=pg.mkPen('r', width=3))

        self.line_set_point_down.setData(np.linspace(0,10,10), np.ones(10)*self.temperature_down,
                                       pen=pg.mkPen('r', width=1),
                                     shadowPen=pg.mkPen('r', width=3))

    def closeEvent(self, *args, **kwargs):
        
        self.closeSignal.emit()
        
        super().closeEvent(*args, **kwargs)


    def make_connection(self, backend):
        backend.dataSignal.connect(self.get_data)
        backend.data_dcSignal.connect(self.get_data_dc)

class Backend(QtCore.QObject):

    dataSignal = pyqtSignal(list, float)
    data_dcSignal = pyqtSignal(list)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.myArduino = arduino

        #poner alguna dirección por default:
        self.file_path = os.path.abspath("C:/Users/Alumno") #direccion por default

        self.Temperaturetimer = QtCore.QTimer()
        self.Temperaturetimer.timeout.connect(self.get_values)

        self.time_refresh = 1 #segundos

    @pyqtSlot(bool)
    def play_stop_read(self, readbool):
        
        if readbool:
            self.start_read_temperature()
        else:
            self.stop_read_temperature()

    def start_read_temperature(self):
        
        self.step = 1
        self.timeaxis = []
        self.dataaxis = []

        self.step2 = 1
        self.timeaxis2 = []
        self.dataaxis2 = []

        self.timer_inicio = ptime.time()  
        self.Temperaturetimer.start(self.time_refresh*10**3) 
#        self.Temperaturetimer.start(0) 
        
    def stop_read_temperature(self):

        self.timer_end = ptime.time()
        self.Temperaturetimer.stop()

        #print(self.timer_end - self.timer_inicio, self.step*self.time_refresh, self.step2*self.time_refresh)
        #self.save_data_temperature() 

    def get_values(self):

        self.myArduino.write(b'0')
        self.myArduino.flush()
#        time.sleep(0.1)
        output = self.myArduino.readline()
        
        value = output.decode("utf-8")

        value = value.strip()
        
#        print(value)
        
        self.get_temperature(value)

        self.get_values_dc(value)
        
        self.get_actual_setpoint(value)

    def get_values_dc(self, value):

        value_dc = float(value.split(":")[5])
        print('Actual duty cycle value:', value_dc)
            
    def get_temperature(self, value):
        
        value_temp = float(value.split(":")[3])
        new_time = self.step*self.time_refresh

        self.timeaxis.append(new_time)
        self.dataaxis.append(value_temp)
        self.step += 1
            
        data = [self.step, self.timeaxis, self.dataaxis]
        self.dataSignal.emit(data, value_temp)
                    
    def get_actual_setpoint(self, value):
        
        value_setpoint = float(value.split(":")[1])
        print('Actual setpoint value:', value_setpoint)

    @pyqtSlot()
    def save_data_temperature(self):
        
        filepath = self.file_path
        timestr = time.strftime("%Y%m%d_%H%M%S")
        name = str(filepath + "/" + timestr + "_temperature_vs_time" + ".txt")

        #name = str("temperature-vs-time"  + timestr + ".txt")
                       
        np.savetxt(name,
                        np.transpose([self.timeaxis,
                                     self.dataaxis]))

        print("\n Save temperature vs time.")
        
        name_dc = str(filepath + "/" + timestr + "_dutycycle_vs_time" + ".txt")

        #name = str("temperature-vs-time"  + timestr + ".txt")
                       
        np.savetxt(name_dc,
                        np.transpose([self.timeaxis2,
                                     self.dataaxis2]))

        print("\n Save duty cycle vs time.")


    @pyqtSlot(str)  #viene de PyTemperature.py directorio
    def get_direction(self, file_path):
        self.file_path = file_path


    @pyqtSlot()
    def close_connection(self):

        self.myArduino.close()

    def make_connection(self, frontend):
        frontend.readSignal.connect(self.play_stop_read)
        frontend.saveSignal.connect(self.save_data_temperature)
        frontend.closeSignal.connect(self.close_connection)


if __name__ == '__main__':

    app = QtGui.QApplication([])

    gui = Frontend()   
    worker = Backend()

    worker.make_connection(gui)
    gui.make_connection(worker)

    temperatureThread = QtCore.QThread()
    worker.moveToThread(temperatureThread) 
    worker.Temperaturetimer.moveToThread(temperatureThread)
    temperatureThread.start()

    gui.show()
    app.exec_()                  
