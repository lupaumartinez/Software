# -*- coding: utf-8 -*-
"""
Created on Thu Feb  7 17:18:06 2019

@author: Luciana
"""

from ccd import CCD
import ctypes as ct

import numpy as np
import time
from datetime import datetime
import os

import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from pyqtgraph.dockarea import Dock, DockArea
from PIL import Image

import viewbox_tools

shape = (1002, 1002)
PreAmpGain = ['1','1.9', '3.7']

class Frontend(QtGui.QFrame):
    
    settemperatureSignal = pyqtSignal(float)
    pictureSignal = pyqtSignal(float)
    parametersgainSignal = pyqtSignal(str, int)
    
    shutterSignal = pyqtSignal(bool)
    continually_acquisitionSignal = pyqtSignal(bool)
    
    saveSignal = pyqtSignal()
    liveSignal = pyqtSignal(bool, float)
    
    closeSignal =  pyqtSignal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setUpGUI()

    def setUpGUI(self):

    #Camera Andor
    
        # temperature

        self.set_temperature_button = QtGui.QPushButton('Set temperature (°C)')
        self.set_temperature_button.clicked.connect(self.set_temperature_button_check)
        self.set_temperature_button.setStyleSheet(
                    "QPushButton { color : blue;}" )

        self.settemperature_Edit = QtGui.QLineEdit('-70')
        self.settemperature_Edit.setStyleSheet(
                    "QLineEdit { color : blue;}" )
        
        temperature_Label = QtGui.QLabel('Get Temperature (°C):')
        self.temperature_Read = QtGui.QLabel('')
        self.temperature_Read.setStyleSheet(
                    "QLabel { color : red; font: 15pt Arial;}")
        self.temperature_Message = QtGui.QLabel('')

        self.camera_temperature = QtGui.QWidget()
        camera_temperature_layout = QtGui.QGridLayout()
        self.camera_temperature.setLayout(camera_temperature_layout)

        camera_temperature_layout.addWidget(self.set_temperature_button,      0, 1)
        camera_temperature_layout.addWidget(self.settemperature_Edit,         0, 2)
        camera_temperature_layout.addWidget(temperature_Label,                1, 1)
        camera_temperature_layout.addWidget(self.temperature_Read,            1, 2)
        camera_temperature_layout.addWidget(self.temperature_Message,         2, 1)
        
        # taking picture 
        
        time_Label = QtGui.QLabel('Exposure Time (s):')
        self.time_Edit = QtGui.QLineEdit('0.1')
        
        preamp_Label = QtGui.QLabel('Pre-Amplification Gain:')
        self.preamp_Edit = QtGui.QComboBox()
        self.preamp_Edit.addItems(PreAmpGain)
        self.preamp_Edit.setCurrentIndex(2)
        self.preamp_Edit.setFixedWidth(80)
        
        EM_Label = QtGui.QLabel('Electron Multiplication Gain (Linear)):')
        self.EM_Edit = QtGui.QSpinBox()
        self.EM_Edit.setValue(0)
        self.EM_Edit.setMinimum(0)
        self.EM_Edit.setMaximum(300)
        self.EM_Edit.setSingleStep(1)
        
        self.preamp_Edit.currentTextChanged.connect(self.parameters_gain)
        self.EM_Edit.valueChanged.connect(self.parameters_gain)
        
        self.shutter_button = QtGui.QCheckBox('Shutters Camera and Shamrock')
        self.shutter_button.clicked.connect(self.shutter_button_check)
        self.shutter_button.setToolTip('Check is Permanently Open Shutter Camera and Shamrock. Not check is Permanently Close')
        
        self.continually_acquisition_button = QtGui.QCheckBox('Continually Acquisition')
        self.continually_acquisition_button.clicked.connect(self.continually_acquisition_button_check)
        self.continually_acquisition_button.setToolTip('Check is permanently taking picture every 4s')
        
        self.picture_button = QtGui.QPushButton('Taking picture')
        self.picture_button.clicked.connect(self.picture_button_check)
        self.picture_button.setStyleSheet(
                "QPushButton { background-color: orange; }"
                "QPushButton:pressed { background-color: blue; }")
        
        self.save_picture_button = QtGui.QPushButton('Save picture')
        self.save_picture_button.clicked.connect(self.save_button_check)
        self.save_picture_button.setStyleSheet(
                "QPushButton { background-color: orange; }"
                "QPushButton:pressed { background-color: blue; }")

        self.liveview_button = QtGui.QPushButton('LIVEVIEW')
        self.liveview_button.setCheckable(True)
        self.liveview_button.clicked.connect(self.liveview_button_check)
        self.liveview_button.setStyleSheet(
                "QPushButton { background-color: yellow; }"
                "QPushButton:pressed { background-color: blue; }")

        self.ROI_button = QtGui.QPushButton('ROI square')
        self.ROI_button.setCheckable(True)
        self.ROI_button.clicked.connect(self.create_ROI)
        self.ROI_button.setStyleSheet(
                "QPushButton:pressed { background-color: blue; }")

        self.lineprofile_button = QtGui.QPushButton('Line Profile')
        self.lineprofile_button.setCheckable(True)
        self.lineprofile_button.clicked.connect(self.create_line_profile)
        self.lineprofile_button.setStyleSheet(
                "QPushButton:pressed { background-color: blue; }")


        self.camera = QtGui.QWidget()
        camera_parameters_layout = QtGui.QGridLayout()
        self.camera.setLayout(camera_parameters_layout)
        
        camera_parameters_layout.addWidget(self.shutter_button,     0, 1)
      #  camera_parameters_layout.addWidget(self.continually_acquisition_button, 0, 2)
        
        camera_parameters_layout.addWidget(time_Label,              1, 1)
        camera_parameters_layout.addWidget(self.time_Edit,          1, 2)
        
        camera_parameters_layout.addWidget(preamp_Label,           2, 1)
        camera_parameters_layout.addWidget(self.preamp_Edit,       2, 2)
        camera_parameters_layout.addWidget(EM_Label,               3, 1)
        camera_parameters_layout.addWidget(self.EM_Edit,           3, 2)
        
        camera_parameters_layout.addWidget(self.liveview_button,    4, 1)
        camera_parameters_layout.addWidget(self.picture_button,     4, 2)
       # camera_parameters_layout.addWidget(self.save_picture_button,4, 3)

        camera_parameters_layout.addWidget(self.ROI_button,         5, 1)
        camera_parameters_layout.addWidget(self.lineprofile_button, 5, 2)
        
        # image widget layout
        
        imageWidget = pg.GraphicsLayoutWidget()
        imageWidget.setAspectLocked(True)
       # imageWidget.setMinimumHeight(100)
        #imageWidget.setMinimumWidth(100)
        
        #self.vb = imageWidget.addViewBox(row=0, col=0)
        #self.vb.setAspectLocked(True)
        #self.vb.setMouseMode(pg.ViewBox.RectMode)
        
        self.vb = imageWidget.addPlot()
        
        self.img = pg.ImageItem()
        self.vb.addItem(self.img)
    
        # set up histogram for the liveview image

        self.hist = pg.HistogramLUTItem(image=self.img)
       # lut = viewbox_tools.generatePgColormap(cmaps.parula)
       # self.hist.gradient.setColorMap(lut)
        self.hist.gradient.loadPreset('greyclip')
# 'thermal', 'flame', 'yellowy', 'bipolar', 'spectrum',
# 'cyclic', 'greyclip', 'grey' # Solo son estos

        self.hist.vb.setLimits(yMin=0, yMax=16384)

        for tick in self.hist.gradient.ticks:
            tick.hide()
        imageWidget.addItem(self.hist, row=0, col=1)

        traceROI_Widget = pg.GraphicsLayoutWidget()  
        self.roi = None
        plot_traceROI =  traceROI_Widget.addPlot(row=1, col=1, title="Trace")
        plot_traceROI.showGrid(x=True, y=True)
        self.curve_ROI = plot_traceROI.plot(open='y')
        
        self.lineplotWidget = viewbox_tools.linePlotWidget_pixel()
        self.lineROI = None
        self.curve_line = self.lineplotWidget.linePlot.plot(open='y')
        
        self.mouse_cursor_x = viewbox_tools.TwolinesHorizontal_fixed(self.vb , 0, 0)
        self.mouse_cursor_y = viewbox_tools.TwolinesVertical_fixed(self.vb , 0, 0)
        
        #docks

        hbox = QtGui.QHBoxLayout(self)
        dockArea = DockArea()
        hbox.addWidget(dockArea)
        self.setLayout(hbox)
        
        camera_temperature_dock = Dock('Temperature')
        camera_temperature_dock.addWidget(self.camera_temperature)
        dockArea.addDock(camera_temperature_dock)

        camera_dock = Dock('Parameters')
        camera_dock.addWidget(self.camera)
        dockArea.addDock(camera_dock, 'right', camera_temperature_dock)
        
        viewbox_dock = Dock('View', size = (70, 70))
        viewbox_dock.addWidget(imageWidget)
        dockArea.addDock(viewbox_dock)
        
        traceROI_dock = Dock('Trace ROI')
        traceROI_dock.addWidget(traceROI_Widget)
        dockArea.addDock(traceROI_dock)
        

    def set_temperature_button_check(self):
        if self.set_temperature_button.isChecked:
           self.settemperatureSignal.emit(float(self.settemperature_Edit.text()))
           self.set_temperature_button.setEnabled(False)
           self.settemperature_Edit.setEnabled(False)
           
    def parameters_gain(self):
        
        preamp_gain = self.preamp_Edit.currentText()
        EM_gain = int(self.EM_Edit.value())
        
        self.parametersgainSignal.emit(preamp_gain, EM_gain)

    def liveview_button_check(self):
        exposure_time = float(self.time_Edit.text())
        if self.liveview_button.isChecked():
           self.liveSignal.emit(True, exposure_time)
        else:
           self.liveSignal.emit(False, exposure_time)

    def picture_button_check(self):
        exposure_time = float(self.time_Edit.text())
        if self.picture_button.isChecked:
           self.pictureSignal.emit(exposure_time)

    def save_button_check(self):
        if self.save_picture_button.isChecked:
           self.saveSignal.emit()
           
    def shutter_button_check(self):
        if self.shutter_button.isChecked():
           self.shutterSignal.emit(True)
           self.shutter_button.setText('Shutter Permanently Open')
        else:
           self.shutterSignal.emit(False)
           self.shutter_button.setText('Shutter Permanently Close')
           
    def continually_acquisition_button_check(self):
        if self.continually_acquisition_button.isChecked():
           self.continually_acquisitionSignal.emit(True)
           self.continually_acquisition_button.setText('YES Continually Aquisition Picture')
        else:
           self.continually_acquisitionSignal.emit(False)
           self.continually_acquisition_button.setText('NOT Continually Aquisition Picture')
           
    @pyqtSlot(float, str)
    def get_camera_temperature(self, temperature_lecture, status):
        self.temperature_Read.setText(str(temperature_lecture))
        self.temperature_Message.setText(status)
        
    @pyqtSlot(np.ndarray)
    def get_image(self, image):

        self.img.setImage(image, autoLevels=True)

        if self.ROI_button.isChecked():
            self.update_ROI(image)
            
        if self.lineprofile_button.isChecked():
            self.update_LINE(image)
            
    def create_ROI(self):
        
        numberofPixels = 1002
        ROIpos = (0.5 *numberofPixels-0.5*100, 0.5 *numberofPixels-0.5*100)

        if self.ROI_button.isChecked():
            
            self.roi = viewbox_tools.ROI(100, self.vb, ROIpos,
                                         handlePos=(1, 0),
                                         handleCenter=(0, 1),
                                         scaleSnap=True,
                                         translateSnap=True)
            
            self.ptr = 0
            self.timeaxis = []
            self.data_ROI = []

            #self.tiempo = 10
            #self.ROIupdateTimer.start(self.tiempo)
       
        else:
            #self.ROIupdateTimer.stop()
            self.vb.removeItem(self.roi)
            self.roi.hide()
    
    def update_ROI(self, image):
        
        array_intensity = self.roi.getArrayRegion(image, self.img)
        mean_intensity = np.round(np.mean(array_intensity), 2)
        
        step = self.ptr
                      
        self.timeaxis.append(step)
        self.data_ROI.append(mean_intensity)
        self.ptr += 1
        
        show_points = 200

        if step < show_points:
            self.curve_ROI.setData(self.timeaxis, self.data_ROI,
                           pen=pg.mkPen('g', width=1),
                           shadowPen=pg.mkPen('w', width=3))
        else:
            self.curve_ROI.setData(self.timeaxis[step-show_points:], self.data_ROI[step-show_points:],
                           pen=pg.mkPen('g', width=1),
                           shadowPen=pg.mkPen('w', width=3))
        
    def create_line_profile(self):
        
        if self.lineprofile_button.isChecked():

            self.lineROI = pg.LineSegmentROI([[0, 309], [1001, 309]], pen='r')
            self.vb.addItem(self.lineROI)
            self.lineplotWidget.show()
                            
        else:

            self.lineplotWidget.close()
            self.vb.removeItem(self.lineROI)
            
            
    def update_LINE(self, image):
        
        array_intensity = self.lineROI.getArrayRegion(image, self.img)
        
        xmin, ymin = self.lineROI.pos() + self.lineROI.listPoints()[0]
        xmax, ymax = self.lineROI.pos() + self.lineROI.listPoints()[1]
                
        array_pos_x = np.linspace(xmin,  xmax, len(array_intensity))
        
        self.curve_line.setData(array_pos_x, array_intensity,
                           pen=pg.mkPen('m', width=1),
                           shadowPen=pg.mkPen('m', width=3)) 


    @pyqtSlot(bool,int, int) 
    def create_line_horizontal(self, show_bool, center_row, spot_size):

        if show_bool:
            self.mouse_cursor_x.show() 
        else:
            self.mouse_cursor_x.hide()

    @pyqtSlot(int, int)        
    def line_horizontal(self, center_row, spot_size):
        
        down_row = center_row - int((spot_size-1)/2)
        up_row = center_row + int((spot_size-1)/2)+1
        
        self.mouse_cursor_x.hLine_up.setPos(up_row) 
        self.mouse_cursor_x.hLine_down.setPos(down_row)
        
        #x_hu, y_hu = self.mouse_cursor_x.hLine_up.pos()
        #x_hd, y_hd = self.mouse_cursor_x.hLine_down.pos()
        
        #print(y_hd, y_hu)

    @pyqtSlot(bool,int, int) 
    def create_line_vertical(self, show_bool, center_column, spot_size):

        if show_bool:
            self.mouse_cursor_y.show()
        else:
            self.mouse_cursor_y.hide()

    @pyqtSlot(int, int)        
    def line_vertical(self, center_column, spot_size):
                    
        left_column = center_column - int((spot_size-1)/2)
        rigth_column = center_column + int((spot_size-1)/2) + 1  

        self.mouse_cursor_y.vLine_left.setPos(left_column) 
        self.mouse_cursor_y.vLine_rigth.setPos(rigth_column)

    @pyqtSlot(bool, list)
    def create_cross_lines(self, show_bool, filter_ROI):

        spot_size = filter_ROI[0]
        center_row = filter_ROI[1]
        center_column = filter_ROI[2]

        if show_bool:

            self.create_line_horizontal(show_bool, center_row, spot_size)
            self.create_line_vertical(show_bool, center_column, spot_size)

        else:

            self.create_line_horizontal(show_bool, center_row, spot_size)
            self.create_line_vertical(show_bool, center_column, spot_size)

    @pyqtSlot(list)
    def cross_lines(self, filter_ROI):

        spot_size = filter_ROI[0]
        center_row = filter_ROI[1]
        center_column = filter_ROI[2]

        self.line_horizontal(center_row, spot_size)
        self.line_vertical(center_column, spot_size)

    def closeEvent(self, *args, **kwargs):
        
        self.closeSignal.emit()
        
        super().closeEvent(*args, **kwargs)
        
    def make_connection(self, backend):
        backend.temperatureSignal.connect(self.get_camera_temperature)
        backend.imageSignal.connect(self.get_image)
        
        
class Backend(QtCore.QObject):

    temperatureSignal = pyqtSignal(float, str)
    imageSignal = pyqtSignal(np.ndarray)
    
    continually_acSignal = pyqtSignal()

    def __init__(self, myAndor, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.myAndor = myAndor
        
        self.file_path = os.path.abspath("C:\Julian\Data_PySpectrum")  #direccion por default
        
        self.temperatureTimer = QtCore.QTimer()

        self.viewTimer = QtCore.QTimer()
        
        self.continuallyTimer = QtCore.QTimer()
        
        self.set_camera_parameters()

    @pyqtSlot(float)
    def set_camera_temperature(self, set_temperature_value):
        
        self.myAndor.cooler_on = True
        self.myAndor.temperature_setpoint = set_temperature_value

        time.sleep(2) #arbitrario
        self.get_camera_temperature()
        self.temperatureTimer.start(10*10**3)   # cada 10s pregunta el estado
        
        print('[Camera] Temperature Set = {} Cº'.format(set_temperature_value))

    def get_camera_temperature(self):

        temp = np.round(self.myAndor.temperature,2)
        temp_status = self.myAndor.temperature_status
        
        self.temperatureSignal.emit(temp, temp_status)
        
    def set_preamp_gain(self, preamp_gain):
        
        if preamp_gain == PreAmpGain[0]:
            self.myAndor.preamp = 0 # # index 0 for preamp gain = 1  
        elif preamp_gain == PreAmpGain[1]:
            self.myAndor.preamp = 1  # index 1 for preamp gain = 1.9 
        elif preamp_gain == PreAmpGain[2]:
            self.myAndor.preamp = 2  # index 2 for preamp gain = 3.7 
            
        print(datetime.now(), '[Camera]  Pre-Amp gain = {}'.format(self.myAndor.preamp))
        
    def set_EM_gain(self, value_EM_gain):
        
        print(datetime.now(), '[Camera]  EM gain range = {}'.format(self.myAndor.EM_gain_mode))
        
        self.myAndor.EM_gain = value_EM_gain
         
        print(datetime.now(), '[Camera]  EM gain = {}'.format(self.myAndor.EM_gain))
        
         
    @pyqtSlot(str, int)       
    def set_parameters_gain(self, pream_gain, value_EM_gain):
        
        self.set_preamp_gain(pream_gain)
        self.set_EM_gain(value_EM_gain)

        
    def set_camera_parameters(self):  

        self.shape = shape
        self.myAndor.set_image(shape= self.shape)
        
        # Pre-Amp gain
        self.myAndor.preamp = 2 # index 2 for preamp gain = 3.7 
        #self.myAndor.preamp = 1  # index 1 for preamp gain = 1.9 
        #self.myAndor.preamp = 0  # index 0 for preamp gain = 1 
        
        # this function retrieves the amount of gain that is stored for a particular index
        #gain = self.myAndor.true_preamp(2)
        
        print(datetime.now(), '[Camera]  Pre-Amp gain = {}'.format(self.myAndor.preamp))
              
        # EM gain
        self.myAndor.EM_advanced_enabled = False
        self.myAndor.EM_gain_mode = 'Linear' # 'RealGain' is not supported in our camera iXon+ 885
        
        print(datetime.now(), '[Camera]  EM gain range = {}'.format(self.myAndor.EM_gain_mode))
        
        self.myAndor.EM_gain = 0 # to NO EM mode
        EMgain = ct.c_int()
        self.myAndor.lib.GetEMCCDGain(ct.pointer(EMgain))
        
        print(datetime.now(), '[Camera]  EM gain = {}'.format(self.myAndor.EM_gain))
        
        # Horizontal shift speed
        ad = 0    # 14-bit DAC
        typ = 0   # EM mode
        index = 2   # 0 = 35 MHz, 1 = 27 MHz, 2 = 13 MHz       
        self.myAndor.lib.SetHSSpeed(ct.c_int(ad), ct.c_int(typ), ct.c_int(index))
        
        # Vertical shift speed
        self.myAndor.vert_shift_speed = 2 # 2 for 1.9 us
        
        # Vertical shiftter voltage
        self.myAndor.set_vert_clock(0) # set to 'Normal' as Andor SOLIS
        
        self.myAndor.frame_transfer_mode = True
        print(datetime.now(), '[Camera]  frame transfer mode = {}'.format(self.myAndor.frame_transfer_mode))
        
        self.myAndor.set_kinetic_cycle_time(0)
        print(datetime.now(), '[Camera]  kinetic cycle time = {}'.format(0))
        
        self.myAndor.set_n_accum(1)
        print(datetime.now(), '[Camera]  Number accum= {}'.format(1))
        
        self.myAndor.set_accum_time(0)
        print(datetime.now(), '[Camera]  accum time = {}'.format(0))
        
        self.myAndor.cr_filter_enabled = True  
        print(datetime.now(), '[Camera]  cosmic ray filter mode  = {}'.format(self.myAndor.cr_filter_enabled))
        
        # Baseline, to copy Andor SOLIS configuration do:
        self.myAndor.baseline_clamp = True
        print(datetime.now(), '[Camera]  baseline clamp  = {}'.format(self.myAndor.baseline_clamp))
        # baseline level is set by Andor
        # approximattely 400 counts for -75 °C are reported
        # we got 382 counts at -70 °C
        
        self.myAndor.shutter(1, 2, 0, 0, 2) #cierra shutter camera y shamrock 
        print(datetime.now(), '[Camera]  shutter = Permanently Close')
        
        self.myAndor.set_exposure_time(1)
        print(datetime.now(), '[Camera]  Exposure time = {} s'.format(1))
                
    @pyqtSlot(bool)
    def shutter_change(self, shutterbool):
        if shutterbool:
           self.myAndor.shutter(1, 1, 0, 0, 1)  #abre shutter camera y shamrock 
           print(datetime.now(), '[Camera]  shutter = Permanently Open')
           
        else:
            
           self.myAndor.shutter(1, 2, 0, 0, 2) #cierra shutter camera y shamrock 
           print(datetime.now(), '[Camera]  shutter = Permanently Close')
           
           
    @pyqtSlot(bool)
    def continually_acquisition_change(self, flag):
        
        if flag:
           self.continuallyTimer.start(3*10**3) # cada 3s saca fotos del exposure time que tenga la camara.
           print(datetime.now(), '[Camera] WARNING: Start Continually Acquisition.')
        else:
           self.continuallyTimer.stop()
           print(datetime.now(), '[Camera] Stop Continually Acquisition.')
     
    @pyqtSlot(bool, float)
    def liveview(self, livebool, exposure_time):
        
        if livebool:
            
           self.exposure_time = exposure_time   
           self.start_liveview()
           
        else:
           self.stop_liveview()
    
    def start_liveview(self):
        
        if self.myAndor.status == ('Acquisition in progress.'):
            self.myAndor.wait_for_acquisition()  
            self.myAndor.abort_acquisition()
        
        self.myAndor.acquisition_mode = 'Run till abort'
            
        self.myAndor.set_exposure_time(self.exposure_time)
     
     #   self.myAndor.shutter(1, 1 , 0, 0, 1) # opens both shutter

        print(datetime.now(), '[Camera] Acquisition mode = {}'.format(self.myAndor.acquisition_mode))
        print(datetime.now(), '[Camera] Status = {}'.format(self.myAndor.status))
        print(datetime.now(),'Start liveview')
        print('[Camera] Exposure time = {} s'.format(self.exposure_time))

        self.myAndor.start_acquisition()       
        self.myAndor.wait_for_acquisition()   
  
        #image = self.myAndor.most_recent_image16(self.shape)
        image = np.transpose(self.myAndor.most_recent_image16(self.shape))
        self.imageSignal.emit(image) 

        self.viewTimer.start(1.5*self.exposure_time*10**3) # ms  , DON'T USE time.sleep() inside the update()
        
    def update_view(self):
        """ Image update while in Liveview mode """
        #image = self.myAndor.most_recent_image16(self.shape)
        image = np.transpose(self.myAndor.most_recent_image16(self.shape))
        self.imageSignal.emit(image)
        
    def stop_liveview(self):  

        self.viewTimer.stop()
        self.myAndor.wait_for_acquisition()   
        self.myAndor.abort_acquisition()
      #  self.myAndor.shutter(1, 2, 0, 0, 2)
        print(datetime.now(), 'Stop liveview')
        
        self.continually_acSignal.emit()
        
    @pyqtSlot(float)
    def taking_picture(self, exposure_time):
        
        self.exposure_time = exposure_time
        
        if self.myAndor.status == ('Acquisition in progress.'):
            self.myAndor.wait_for_acquisition()  
            self.myAndor.abort_acquisition()
            
        self.myAndor.set_exposure_time(self.exposure_time)
        
        # set shutters configuration
       # self.myAndor.shutter(1, 1, 0, 0, 0) # standard mode for us
        self.myAndor.acquisition_mode = 'Single Scan'
        
        print(datetime.now(), '[Camera] Acquisition mode = {}'.format(self.myAndor.acquisition_mode))

        self.myAndor.set_exposure_time(self.exposure_time)
        print(datetime.now(), '[Camera] Status = {}'.format(self.myAndor.status))
       
        self.myAndor.start_acquisition()    
        self.myAndor.wait_for_acquisition()  
        self.myAndor.abort_acquisition()
        
        image = np.transpose(self.myAndor.most_recent_image16(self.shape))
        self.imageSignal.emit(image)
        
        print(datetime.now(),'Taking picture')
        print('[Camera] Exposure time = {} s'.format(self.exposure_time))
        
        self.image = image #me sirve para guardar la ultima imagen
        
        self.save_picture()
        
        self.continually_acSignal.emit()

        return image

    @pyqtSlot(str)  #viene de PySpectrum si creo directorio del dia, sino usa la q que esta por default
    def get_direction(self, file_name):
        self.file_path = file_name
        
    @pyqtSlot()    
    def save_picture(self):
        
        filepath = self.file_path
        timestr = time.strftime("%Y%m%d_%H%M%S")
#        name = str(filepath + "/" + "Photo_Andor" + timestr + ".tiff")
        filename = "Photo_Andor_" + timestr + ".tiff"
        full_filename = os.path.join(filepath,filename)
        guardado = Image.fromarray(np.transpose(self.image))
        guardado.save(full_filename)
        print("\n Image saved\n")
        
        
    def continually_acquisition(self):
        
        status = self.myAndor.status
        
        print('Continually Acquision si paso 0', status)
        
        if status == ('Camera is idle, waiting for instructions.'):
            
            print('Continually Acquision si paso 1')
            
            self.myAndor.acquisition_mode = 'Single Scan'
            
            self.myAndor.start_acquisition()    
            self.myAndor.wait_for_acquisition()  
            self.myAndor.abort_acquisition()
            self.myAndor.most_recent_image16(self.shape)
            
            print('Continually Acquision si paso 2')
        
    @pyqtSlot()    
    def close(self):
        
       # self.continuallyTimer.stop()
        
        self.temperatureTimer.stop()
                
        self.myAndor.shutter(1, 2, 0, 0, 2) #cierra shutter camera y shamrock 
        print(datetime.now(), '[Camera]  shutter = Permanently Close')
        
        self.myAndor.finalize()

        print(datetime.now(), '[Camera] Close')

    def make_connection(self, frontend):
        
        frontend.shutterSignal.connect(self.shutter_change)
        frontend.continually_acquisitionSignal.connect(self.continually_acquisition_change)
        frontend.settemperatureSignal.connect(self.set_camera_temperature)
        frontend.parametersgainSignal.connect(self.set_parameters_gain)
        frontend.liveSignal.connect(self.liveview)
        frontend.pictureSignal.connect(self.taking_picture)
        frontend.saveSignal.connect(self.save_picture)
        frontend.closeSignal.connect(self.close)

if __name__ == '__main__':

    app = QtGui.QApplication([])

    gui = Frontend()
    
    ##initializing Camera Andor

    myAndor = CCD()
    myAndor.lib.Initialize()
    shape = (1002, 1002)
    PreAmpGain = ['1','1.9', '3.7']
    print('[Camera] IDN = {}'.format(myAndor.idn))
    
    worker = Backend(myAndor)

    worker.make_connection(gui)
    gui.make_connection(worker)

    cameraThread = QtCore.QThread()
    worker.moveToThread(cameraThread)
    worker.temperatureTimer.moveToThread(cameraThread)
    worker.viewTimer.moveToThread(cameraThread)
    
    worker.temperatureTimer.timeout.connect(worker.get_camera_temperature)
    worker.viewTimer.timeout.connect(worker.update_view)   
        
    cameraThread.start()

    gui.show()
    app.exec_()