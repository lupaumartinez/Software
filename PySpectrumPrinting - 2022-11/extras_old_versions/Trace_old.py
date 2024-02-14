
import numpy as np
import time
import os

import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph.ptime as ptime
from pyqtgraph.dockarea import Dock, DockArea

from PyQt5.QtCore import pyqtSignal, pyqtSlot

from Instrument_nidaqmx import channels_photodiodos, shutters, openShutter, closeShutter, PDchans, PD_channels, rateNI


class Frontend(QtGui.QFrame):

    traceSignal = pyqtSignal(bool, int)
    stopSignal = pyqtSignal()
    playSignal = pyqtSignal()
    saveSignal = pyqtSignal()
    parametersSignal = pyqtSignal(list)
    calibrationBS_Signal =  pyqtSignal(float, float)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setUpGUI()
        self.calibration_Widget()

    def get_trace(self):
        if self.traceButton.isChecked():
           self.traceSignal.emit(True, self.trace_laser.currentIndex())
        else:
           self.traceSignal.emit(False,  self.trace_laser.currentIndex()) 

    def get_play(self):
        self.playSignal.emit()
   
    def get_stop(self):
        self.stopSignal.emit()

    def get_save_trace(self):
        if self.saveButton.isChecked:
            self.saveSignal.emit()
            
    def get_power_BS(self):
        self.calbirationWidget.show()
            
    def parameters_trace(self):
        steps_after_umbral = int(self.steps_after_Edit.text())
        steps_before_umbral = int(self.steps_before_Edit.text())
        steps = [steps_after_umbral, steps_before_umbral]
        self.parametersSignal.emit(steps)

    def setUpGUI(self):
        
        self.play_Action = QtGui.QAction(self)
        QtGui.QShortcut(QtGui.QKeySequence('F1'), self, self.get_play)
        
        self.stop_Action = QtGui.QAction(self)
        QtGui.QShortcut(QtGui.QKeySequence('F2'), self, self.get_stop)        

    # Defino el laser
        self.trace_laser = QtGui.QComboBox()
        self.trace_laser.addItems(shutters)
        self.trace_laser.setCurrentIndex(0)
        self.trace_laser.setFixedWidth(80)
        self.trace_laser.activated.connect(lambda: self.color_menu(self.trace_laser))
        self.color_menu(self.trace_laser)  
            
    # play button
        self.traceButton = QtGui.QPushButton('► Play / ◘ Stop Trace || (F1/F2)')
        self.traceButton.setCheckable(True)
        self.traceButton.clicked.connect(self.get_trace)
        self.traceButton.setToolTip('Play o Stop la traza (F1)')


    # save button
        self.saveButton = QtGui.QPushButton('Save trace')
        self.saveButton.clicked.connect(self.get_save_trace)
        self.saveButton.setStyleSheet(
                "QPushButton { background-color: rgb(200, 200, 10); }")
        
    # calibration button
        self.setPowerBSButton = QtGui.QPushButton('View Power BS')
        self.setPowerBSButton.clicked.connect(self.get_power_BS)
        
    # trace umbral parameters
        self.steps_after_Label = QtGui.QLabel('Steps after umbral')
        self.steps_after_Edit = QtGui.QLineEdit('10')
        
        self.steps_before_Label = QtGui.QLabel('Steps before umbral')
        self.steps_before_Edit = QtGui.QLineEdit('10')
        
        self.steps_after_Edit.textChanged.connect(self.parameters_trace)
        self.steps_before_Edit.textChanged.connect(self.parameters_trace)
        
        self.PointLabel = QtGui.QLabel('<strong>0.00|0.00')
        
        self.paramWidget = QtGui.QWidget()
        subgrid = QtGui.QGridLayout()
        self.paramWidget.setLayout(subgrid)
        
        subgrid.addWidget(self.trace_laser, 1,1)
        subgrid.addWidget(self.traceButton, 1,2)
        
        subgrid.addWidget(self.steps_before_Label,  1,3)
        subgrid.addWidget(self.steps_before_Edit,   1,4)
        subgrid.addWidget(self.steps_after_Label,   1,5)
        subgrid.addWidget(self.steps_after_Edit,    1,6)
        subgrid.addWidget(self.PointLabel,  1,7)
        
        subgrid.addWidget(self.setPowerBSButton,  1,10)
          
        self.traceWidget = pg.GraphicsLayoutWidget()
        self.p6 = self.traceWidget.addPlot(row=2, col=1, title="Trace")
        self.p6.showGrid(x=True, y=True)
        self.p6.setLabel('left', "Photodiode (V)")
        self.p6.setLabel('bottom', "Time (s) (No es el real)")
        self.curve = self.p6.plot(open='y')
       
        self.pBS = self.traceWidget.addPlot(row=2, col=2, title="Trace on BS") 
        self.pBS.showGrid(x=True, y=True)
        self.pBS.setLabel('left', "Photodiode BS (V)")
        self.pBS.setLabel('bottom', "Time (s) (No es el real)")
        self.curve_BS = self.pBS.plot(open='y')
        
    # Docks

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
            
    def color_menu(self, QComboBox):
        """ le pongo color a los menus"""
        if QComboBox.currentText() == shutters[0]:  # verde
            QComboBox.setStyleSheet("QComboBox{color: rgb(0,128,0);}\n")
        elif QComboBox .currentText() == shutters[1]:  # rojo
            QComboBox.setStyleSheet("QComboBox{color: rgb(255,0,0);}\n")
        elif QComboBox .currentText() == shutters[2]: # azul
            QComboBox.setStyleSheet("QComboBox{color: rgb(0,0,255);}\n")
        elif QComboBox .currentText() == shutters[3]: # IR
            QComboBox.setStyleSheet("QComboBox{color: rgb(100,0,0);}\n")
            
           
    def calibration_Widget(self):
        
        High_Label = QtGui.QLabel('High:')
        Low_Label = QtGui.QLabel('Low:')
        
        Power_Label = QtGui.QLabel('Power BFP (mW):')
        Photodiode_Label = QtGui.QLabel('Photodiode (V):')
        
        self.High_mW = QtGui.QLineEdit('3.3')
        self.High_BS = QtGui.QLabel('Nan')
        
        self.Low_mW = QtGui.QLineEdit('1.0')
        self.Low_BS = QtGui.QLabel('Nan')
        
        self.High_Button = QtGui.QPushButton('set High')
        self.High_Button.clicked.connect(self.set_High_BS)
        self.High_Button.setToolTip('Set High Power with medium value on Trace BS')
        
        self.Low_Button = QtGui.QPushButton('set Low')
        self.Low_Button.clicked.connect(self.set_Low_BS)
        self.Low_Button.setToolTip('Set Low Power with medium value on Trace BS')
        
        self.calibration_Button = QtGui.QPushButton('set Calibration')
        self.calibration_Button.clicked.connect(self.set_calibration_BS)
        self.calibration_Button.setToolTip('First set High and Low Power of BS.')
        
        intercept_Label = QtGui.QLabel('Intercept (mW):')
        self.intercept = QtGui.QLineEdit('0')
        
        slope_Label = QtGui.QLabel('Slope (mW/V):')
        self.slope = QtGui.QLineEdit('3')
        
        power_BS_Label = QtGui.QLabel('Power mean on BS (mW):')
        self.power_mean_BS = QtGui.QLabel('')
        self.power_mean_BS.setStyleSheet(
                    "QLabel { color : red; font: 150pt Arial;}")
        
        self.calbirationWidget = QtGui.QWidget()
        subgrid = QtGui.QGridLayout()
        self.calbirationWidget.setLayout(subgrid)
        
        subgrid.addWidget(Power_Label,       1,2)
        subgrid.addWidget(Photodiode_Label,  1,3)
        
        subgrid.addWidget(High_Label,        2,1)
        subgrid.addWidget(Low_Label,         3,1)
        
        subgrid.addWidget(self.High_mW,      2,2)
        subgrid.addWidget(self.Low_mW,       3,2)
        
        subgrid.addWidget(self.High_BS,      2,3)
        subgrid.addWidget(self.Low_BS,       3,3)
        
        subgrid.addWidget(self.High_Button,  2,4)
        subgrid.addWidget(self.Low_Button,   3,4)
        
        subgrid.addWidget(self.calibration_Button,   4,1)
        subgrid.addWidget(intercept_Label,           5,1)
        subgrid.addWidget(slope_Label,               6,1)
        
        subgrid.addWidget(self.intercept,            5,2)
        subgrid.addWidget(self.slope,                6,2)
        
        subgrid.addWidget(power_BS_Label,        7,1)
        subgrid.addWidget(self.power_mean_BS,    8,1)
        
        
    def set_High_BS(self):
        
        self.High_BS.setText(format(self.mean_BS))
        
    def set_Low_BS(self):
        
        self.Low_BS.setText(format(self.mean_BS))

    def set_calibration_BS(self):
        
        xo =  float(self.Low_BS.text())
        x1 =  float(self.High_BS.text())
        
        yo =  float(self.Low_mW.text())
        y1 =  float(self.High_mW.text())
        
        slope = np.round((y1-yo)/(x1-xo), 2)
        intercept = np.round(yo-slope*xo,3)
        
        self.slope.setText(format(slope))
        self.intercept.setText(format(intercept))
        
        self.calibrationBS_Signal.emit(slope, intercept)


    @pyqtSlot(list)
    def get_data(self, data): 
        
        n = data[0]
        time = data[1]
        intensity = data[2]
        
        medio2 = data[3]
        medio = data[4]
        
        intensity_BS = data[5]
        mean_BS = data[6]
        
        show = 1000
        if n < show:
             self.curve.setData(time, intensity,
                           pen=pg.mkPen('y', width=1),
                           shadowPen=pg.mkPen('w', width=3))
             
             self.curve_BS.setData(time, intensity_BS,
                      pen=pg.mkPen('r', width=1),
                         shadowPen=pg.mkPen('r', width=3))   
        else:
            
            self.curve.setData(time[n-show:n], intensity[n-show:n],
                          pen=pg.mkPen('y', width=1),
                           shadowPen=pg.mkPen('w', width=3)) 
            
            self.curve_BS.setData(time[n-show:n], intensity_BS[n-show:n],
                      pen=pg.mkPen('r', width=1),
                         shadowPen=pg.mkPen('r', width=3))  

        self.PointLabel.setText("<strong>{:.3}|{:.3}".format(
                                float(medio2), float(medio)))
        
        self.mean_BS = np.round(mean_BS,3)
        
        slope = float(self.slope.text())
        intercept = float(self.intercept.text())
        power_mean_BS = slope*self.mean_BS + intercept
        power_mean_BS = np.round(power_mean_BS, 3)
        self.power_mean_BS.setText(format(power_mean_BS))
        

    def make_connection(self, backend):
        backend.dataSignal.connect(self.get_data)
        
class Backend(QtCore.QObject):

    dataSignal = pyqtSignal(list)
    
    data_printingSignal = pyqtSignal(list)
    data_printingSignal_dimers = pyqtSignal(list)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.file_path = os.path.abspath("C:\Julian\Data_PySpectrum") 
        self.pointtimer = QtCore.QTimer() 
        self.pointtimer.timeout.connect(self.trace_update) 
        self.trace_parameters()
        self.get_trace_parameters([10, 10])
        
    def trace_parameters(self):
        
        ratePDchannel = rateNI/100
        self.N = 10 # cantidad de puntos por bucket  
        self.time = (self.N/ratePDchannel) # s, refresca la traza cada este tiempo
        self.ratePDchannel = ratePDchannel     
        
    @pyqtSlot(list)    
    def get_trace_parameters(self, steps):
        self.steps_after_umbral = steps[0]
        self.steps_before_umbral = steps[1]

    @pyqtSlot(bool, int)
    def play_pause(self, tracebool, color_laser):

        self.laser = shutters[color_laser]
        self.mode_printing = 'none'
        
        if tracebool:
            self.start_trace()
        else:
            self.stop_trace()

    @pyqtSlot()
    def start_trace(self):
        print("play trace")
        openShutter(self.laser)
        time.sleep(0.01)
        self.trace_configuration(self.laser, self.mode_printing) 
        
    @pyqtSlot()   
    def stop_trace(self):
        print("stop trace")
        self.pointtimer.stop()
        self.timer_end = ptime.time()
        
        closeShutter(self.laser)
        self.timer_real = round(self.timer_end- self.timer_inicio, 2)
        #print(self.timer_real, self.ptr1*self.time, 'tiempo')         
        print('Time trace', self.timer_real, 'tiempo no real', round(self.timeaxis[-1], 2))
        self.save_trace()
       
    @pyqtSlot() 
    def stop(self):
        self.pointtimer.stop()
        
    @pyqtSlot() 
    def stop_trace_routines(self):
        
        self.pointtimer.stop()
        timer_end = ptime.time()
       
        timer_real = round(timer_end- self.timer_inicio, 2)      
        print('Time trace', timer_real, 'tiempo no real', round(self.timeaxis[-1], 2))
        
        name = str(self.new_save_folder + "/" + "Trace_BS.txt")
        time_real = list(np.linspace(0.01, timer_real, self.ptr))
        
        np.savetxt(name, np.transpose([time_real, self.data_BS]), fmt='%.3e')
        
    @pyqtSlot(str, str, str)    
    def trace_configuration_routines(self, laser, mode_printing, folder_routines):
        
        self.new_save_folder = folder_routines
        self.trace_configuration(laser, mode_printing)

        
    @pyqtSlot(str, str)
    def trace_configuration(self, laser, mode_printing): 
        
        self.laser = laser
        self.mode_printing = mode_printing

        self.ptr = 0
        self.step_time = 0
        
        self.timeaxis = []
        self.data1 = []
        self.data_BS = []
        
        self.timer_inicio = ptime.time()  
        
        #self.pointtimer.start(self.time*10**3)
        
        self.pointtimer.start(0)  
             
    def trace_update(self):     
        
        tic = ptime.time()
        
        PDtask = channels_photodiodos(self.ratePDchannel, self.N)  
        lectura_total = PDtask.read(self.N)
        PDtask.wait_until_done()
        PDtask.close()
        
        self.points = lectura_total[PDchans.index(PD_channels[self.laser])]
        m = np.mean(self.points)
        self.data1.append(m)
        
        self.points_BS = lectura_total[PDchans.index(PD_channels['BS'])]
        m_BS = np.mean(self.points_BS)
        self.data_BS.append(m_BS)
        
        # trace looks like this:
        # ...........|''''''''''''
        # second window|first window
        # before event|after event
        # "|" symbol indicates event
        
        # 1 - august - 2019 , mean value of time step = 10 ms
        
        M = self.steps_after_umbral
        M2 = self.steps_before_umbral
       # M = 10 # first window or after event
       # M2 = 10 # second window or before event
        
        if self.ptr < M:
            self.mediochico = np.mean(self.data1[:self.ptr])
            self.timeaxis2 = self.timeaxis[:self.ptr]
            
            self.mean_BS = np.mean(self.data_BS[:self.ptr])
            
            if self.ptr < M2:
                self.mediochico2 = np.mean(self.data1[:self.ptr])
            else:
                self.mediochico2 = np.mean(self.data1[:self.ptr-M2])
        else:
            
            self.mediochico = np.mean(self.data1[self.ptr-M:self.ptr])
            self.mediochico2 = np.mean(self.data1[self.ptr-M-M2:self.ptr-M])
            
            self.mean_BS = np.mean(self.data_BS[self.ptr-M:self.ptr])
            
        tiempo = ptime.time() - tic
        self.step_time = self.step_time + tiempo
        self.timeaxis.append(self.step_time)
        
        self.ptr = self.ptr + 1
    
        data = [self.ptr, self.timeaxis, self.data1, self.mediochico2, self.mediochico, self.data_BS, self.mean_BS]
        
        self.dataSignal.emit(data)
        
            
        if self.mode_printing == 'printing':
            self.data_printingSignal.emit(data)
            
        if self.mode_printing == 'dimers':
            self.data_printingSignal_dimers.emit(data)
            
    @pyqtSlot(float, float)
    def save_calibration_BS(self, slope, intercept):
        
        filepath = self.file_path
        timestr = time.strftime("%Y%m%d-%H%M%S")
        name = str(filepath + "/" + "Calibration_Power"  + timestr + ".txt")
        header_txt = 'Laser, Slope (mW/V), Intercept (mW)'
        
        f = open(name, "w")
        
        np.savetxt(name, [self.laser, str(slope), str(intercept)], fmt="%s", header = header_txt)
        
        f.close()
        
        print("\n Save calibration of power (mW) laser", self.laser)
    
    
    @pyqtSlot(str)        
    def direction(self, file_name):
        self.file_path = file_name
        
    @pyqtSlot()
    def save_trace(self):
        
        filepath = self.file_path
        timestr = time.strftime("%Y%m%d-%H%M%S")
        name = str(filepath + "/" + "timetrace-"  + timestr + ".txt")
        
        f = open(name, "w")
            
        time_real = list(np.linspace(0.01, self.timer_real, self.ptr))
        
        np.savetxt(name, np.transpose([time_real, self.data1, self.data_BS]), fmt='%.3e')
                       
           # np.savetxt(name,
                     #   np.transpose([self.timeaxis[:self.ptr1],
                                     # self.data1[:self.ptr1]]))
    
        f.close()
        print("\n Save the trace.")

    def make_connection(self, frontend):
        frontend.traceSignal.connect(self.play_pause)
        frontend.stopSignal.connect(self.stop_trace)
        frontend.playSignal.connect(self.start_trace)
        frontend.saveSignal.connect(self.save_trace)
        frontend.parametersSignal.connect(self.get_trace_parameters)
        frontend.calibrationBS_Signal.connect(self.save_calibration_BS)

if __name__ == '__main__':

    app = QtGui.QApplication([])

    gui = Frontend()   
    worker = Backend()

    worker.make_connection(gui)
    gui.make_connection(worker)
    
   # multipleThread = QtCore.QThread()
  #  gui.moveToThread(multipleThread)
   # multipleThread.start()

    gui.show()
  #  app.exec_()                  
