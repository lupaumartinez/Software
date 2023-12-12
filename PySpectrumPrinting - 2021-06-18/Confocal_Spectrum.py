
import numpy as np
import time
import os

import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
from PyQt5.QtCore import pyqtSignal, pyqtSlot
import pyqtgraph.ptime as ptime
from pyqtgraph.dockarea import Dock, DockArea
from PIL import Image
from scipy import ndimage
from datetime import datetime

import nidaqmx
from Instrument_nidaqmx import initial_nidaqmx, shutters, openShutter, closeShutter

from pipython import GCSDevice
import Instrument_PI

from ccd import CCD

from Shamrock import Shamrock
from Instrument_Shamrock import DEVICE,  NumberofPixel

PSFmodes = ['x/y', 'x/z']

class Frontend(QtGui.QFrame):

    scanmodeSignal = pyqtSignal(int, bool)
    stopSignal = pyqtSignal(int, bool)
    parametersstepSignal = pyqtSignal(list)
    spectrum_parametersSignal = pyqtSignal(float, float)

    spectrum_parameters_filterSignal = pyqtSignal(int, int)
    show_filterSignal = pyqtSignal(bool, int, int)
    spectrum_parameters_filter_waveSignal = pyqtSignal(list)

    CMSignal = pyqtSignal()
    saveSignal = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setUpGUI()
        self.set_parameters()

    def spectrum_parameters(self):

        exposure_time = float(self.time_Edit.text())                                     
        center_wavelength = float(self.center_lambda.text())
        
        self.spectrum_parametersSignal.emit(center_wavelength, exposure_time)
   
    def spectrum_parameters_filter(self):

        self.center_row_Label.setText(format(int(self.center_row_sl.value())))  
        
        spot_size = int(self.size_spot_Edit.text())
        center_row = int(self.center_row_Label.text())

        self.spectrum_parameters_filterSignal.emit(center_row, spot_size)
        
        self.show_spectrum_parameters_filter()

    def show_spectrum_parameters_filter(self):

        spot_size = int(self.size_spot_Edit.text())
        center_row = int(self.center_row_Label.text())

        if self.show_filter_button.isChecked():

            self.show_filterSignal.emit(True, center_row, spot_size)

        else:

            self.show_filterSignal.emit(False, center_row, spot_size)
        

    def spectrum_parameters_filter_wavelength(self):

        lower_wavelength = float(self.lower_wavelength_Edit.text())
        upper_wavelength = float(self.upper_wavelength_Edit.text())
        
        filter_wavelenght = [lower_wavelength,upper_wavelength]
        
        self.spectrum_parameters_filter_waveSignal.emit(filter_wavelenght)

    
    def get_scan_mode(self):

        parameters = self.set_parameters()
        self.parametersstepSignal.emit(parameters)

        if PSFmodes[self.PSF_mode.currentIndex()] ==  PSFmodes[0]:
            self.scanmodeSignal.emit(self.scan_laser.currentIndex(),  True)  #modo step x/y
        else:
            self.scanmodeSignal.emit(self.scan_laser.currentIndex(),  False) #modo step x/z
            
    def get_scan(self):
        if self.scanButton.isChecked:
            self.get_scan_mode()
            
    def get_scan_stop(self):  
        if self.scanButtonstop.isChecked:
            if PSFmodes[self.PSF_mode.currentIndex()] ==  PSFmodes[0]:
                self.stopSignal.emit(self.scan_laser.currentIndex(),  True)  #modo step x/y
            else:
                self.stopSignal.emit(self.scan_laser.currentIndex(), False) #modo step x/z

    def get_CM(self):
        if self.CMcheck.isChecked:
            self.CMSignal.emit()
            

    def set_parameters(self):
        
        parameters = [float(self.scanrangeEdit.text()), float(self.scanrangeEdit_y.text()), 
                      int(self.NxEdit.text()), int(self.NyEdit.text())]
        
        return parameters
   
    def get_save_frame(self):
        if self.saveimageButton.isChecked:
            self.saveSignal.emit()
            
    def setUpGUI(self):
        
        imageWidget = pg.GraphicsLayoutWidget()
        self.vb = imageWidget.addViewBox(row=1, col=1)

        self.point_graph_CM = pg.ScatterPlotItem(size=10,
                                                 symbol='+', color='m')      
#  Buttons

    # Defino el laser
        self.scan_laser = QtGui.QComboBox()
        self.scan_laser.addItems(shutters)
        self.scan_laser.setCurrentIndex(0)
        self.scan_laser.setFixedWidth(80)
        self.scan_laser.activated.connect(
                                    lambda: self.color_menu(self.scan_laser))
        self.color_menu(self.scan_laser)
        
    # Button: defino el scan xy,xz,yz 
        self.PSF_mode = QtGui.QComboBox()  
        self.PSF_mode.addItems(PSFmodes)
        self.PSF_mode.setCurrentIndex(0)
        self.PSF_mode.setFixedWidth(80)
        
    # scan
        self.scanButton = QtGui.QPushButton('Start Scan')
        self.scanButton.clicked.connect(self.get_scan)    
        
    # scan
        self.scanButtonstop = QtGui.QPushButton('Stop')
        self.scanButtonstop.clicked.connect(self.get_scan_stop)   
        
    # Scanning parameters
        self.scanrangeLabel = QtGui.QLabel('Range x (µm)')
        self.scanrangeEdit = QtGui.QLineEdit('1')

        self.NxLabel = QtGui.QLabel('Number of pixel x')
        self.NxEdit = QtGui.QLineEdit('20')
        
        self.scanrangeLabel_y = QtGui.QLabel('Range y or z (µm)')        
        self.scanrangeEdit_y = QtGui.QLineEdit('1')
       
        self.NyLabel = QtGui.QLabel('Number of pixel y or z')
        self.NyEdit = QtGui.QLineEdit('20')
        
     # save image Button
        self.saveimageButton = QtGui.QPushButton('Save Frame')
        self.saveimageButton.clicked.connect(self.get_save_frame)
        self.saveimageButton.setStyleSheet(
                "QPushButton { background-color:  rgb(200, 200, 10); }")
        tamaño = 110
        self.saveimageButton.setFixedWidth(tamaño)
        
# Interface

        self.paramWidget = QtGui.QWidget()
        subgrid = QtGui.QGridLayout()
        self.paramWidget.setLayout(subgrid)

        subgrid.addWidget(self.scan_laser,             1, 1)
        subgrid.addWidget(self.PSF_mode,               1, 3)  

        subgrid.addWidget(self.scanrangeLabel,         3, 1)
        subgrid.addWidget(self.scanrangeEdit,          3, 2)  
        subgrid.addWidget(self.scanrangeLabel_y,       4, 1)
        subgrid.addWidget(self.scanrangeEdit_y,        4, 2) 

        subgrid.addWidget(self.NxLabel,                5, 1)
        subgrid.addWidget(self.NxEdit,                 5, 2)        
        subgrid.addWidget(self.NyLabel,                6, 1)
        subgrid.addWidget(self.NyEdit,                 6, 2)      
        
        subgrid.addWidget(self.scanButton,             7, 1)
        subgrid.addWidget(self.scanButtonstop,         7, 3)

        subgrid.addWidget(self.saveimageButton,        8, 3)   #evaluar si vale la pena
        
# Interface and Buttons of CM and Gauss

        self.goCMWidget = QtGui.QWidget()
        layout3 = QtGui.QGridLayout()
        self.goCMWidget.setLayout(layout3) 

        self.CMcheck = QtGui.QPushButton('go to CM')
        self.CMcheck.clicked.connect(self.get_CM)

        self.CMxLabel = QtGui.QLabel('CM X')
        self.CMxValue = QtGui.QLabel('NaN')
        self.CMyLabel = QtGui.QLabel('CM Y')
        self.CMyValue = QtGui.QLabel('NaN')

        layout3.addWidget(self.CMcheck, 1,1)
        layout3.addWidget(self.CMxLabel, 2, 1)
        layout3.addWidget(self.CMxValue, 3, 1)
        layout3.addWidget(self.CMyLabel, 2, 2)
        layout3.addWidget(self.CMyValue, 3, 2)


        #Measurment Spectrum - buttons

        time_Label = QtGui.QLabel('Exposure Time (s):')
        self.time_Edit = QtGui.QLineEdit('2')
        center_lambda_Label = QtGui.QLabel('Only one step, Center λ (nm):')
        self.center_lambda = QtGui.QLineEdit('550')
    
        self.center_lambda.textChanged.connect(self.spectrum_parameters)
        self.time_Edit.textChanged.connect(self.spectrum_parameters)
        
        self.parameters_spectrum = QtGui.QWidget()
        parameters_layout = QtGui.QGridLayout()
        self.parameters_spectrum.setLayout(parameters_layout)

        parameters_layout.addWidget(time_Label,                         0, 0)
        parameters_layout.addWidget(self.time_Edit,                     0, 1)
        parameters_layout.addWidget(center_lambda_Label,                1, 0)
        parameters_layout.addWidget(self.center_lambda,                 1, 1)

        #Measurment Spectrum Filter - buttons
        
        # Defino el filtro
    
        size_spot_Label = QtGui.QLabel('Size Bin:')
        self.size_spot_Edit = QtGui.QLineEdit('25')
        self.size_spot_Edit.textChanged.connect(self.spectrum_parameters_filter)

        self.center_row_sl = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.center_row_sl.setMinimum( int(self.size_spot_Edit.text()) )
        self.center_row_sl.setMaximum(1002 - int(self.size_spot_Edit.text()) )
        self.center_row_sl.setValue(438)
        self.center_row_sl.setTickPosition(QtGui.QSlider.TicksBelow)
        self.center_row_sl.setTickInterval(1)
        self.center_row_sl.valueChanged.connect(self.spectrum_parameters_filter)

        center_row_Label = QtGui.QLabel('Center row (pixel):')
        self.center_row_Label = QtGui.QLabel('0')
        self.center_row_Label.setText(format(int(self.center_row_sl.value())))

        self.show_filter_button = QtGui.QPushButton('Show ROI selected')
        self.show_filter_button.setCheckable(True)
        self.show_filter_button.clicked.connect(self.show_spectrum_parameters_filter)
    
        lower_wavelength_Label = QtGui.QLabel('Lower wavelength (nm):')
        self.lower_wavelength_Edit = QtGui.QLineEdit('540')   
        upper_wavelength_Label = QtGui.QLabel('Upper wavelength (nm):')
        self.upper_wavelength_Edit = QtGui.QLineEdit('580')  

        self.lower_wavelength_Edit.textEdited.connect(self.spectrum_parameters_filter_wavelength)
        self.upper_wavelength_Edit.textEdited.connect(self.spectrum_parameters_filter_wavelength)

        self.parameters_filter = QtGui.QWidget()
        parameters_filter_layout = QtGui.QGridLayout()
        self.parameters_filter.setLayout(parameters_filter_layout)
        
        parameters_filter_layout.addWidget(center_row_Label,                   2, 0)
        parameters_filter_layout.addWidget(self.center_row_Label,              2, 1)
        parameters_filter_layout.addWidget(self.center_row_sl,                 3, 0)
        parameters_filter_layout.addWidget(size_spot_Label,                    4, 0)
        parameters_filter_layout.addWidget(self.size_spot_Edit,                4, 1)
        parameters_filter_layout.addWidget(self.show_filter_button,            5, 0)

        parameters_filter_layout.addWidget(lower_wavelength_Label,             6, 0)
        parameters_filter_layout.addWidget(self.lower_wavelength_Edit,         6, 1)
        parameters_filter_layout.addWidget(upper_wavelength_Label,             7, 0)
        parameters_filter_layout.addWidget(self.upper_wavelength_Edit,         7, 1)
        
      
        # docks

        dockArea = DockArea()
        hbox = QtGui.QHBoxLayout(self)

        viewDock = Dock('Viewbox',size=(150,40))
        viewDock.addWidget(imageWidget)
        viewDock.hideTitleBar()
        dockArea.addDock(viewDock)

        scanDock = Dock('Confocal parameters')
        scanDock.addWidget(self.paramWidget)
        dockArea.addDock(scanDock, 'right', viewDock)

        spectrumDock = Dock('Spectrum parameters')
        spectrumDock.addWidget(self.parameters_spectrum)
        dockArea.addDock(spectrumDock, 'bottom', scanDock)
        
        filterDock = Dock('Filter parameters')
        filterDock.addWidget(self.parameters_filter)
        dockArea.addDock(filterDock, 'right', spectrumDock)

        goCMDock = Dock('CM')
        goCMDock.addWidget(self.goCMWidget)
        dockArea.addDock(goCMDock, 'right', scanDock)
        
        hbox.addWidget(dockArea)
        self.setLayout(hbox)

  #  algunas cosas que ejecutan una vez antes de empezar

        self.vb.setMouseMode(pg.ViewBox.RectMode)
        self.img = pg.ImageItem()
        self.vb.addItem(self.img)

        self.hist = pg.HistogramLUTItem(image=self.img)
        self.hist.gradient.loadPreset('thermal')
# 'thermal', 'flame', 'yellowy', 'bipolar', 'spectrum',
# 'cyclic', 'greyclip', 'grey' # Solo son estos
        #self.hist.vb.setLimits(yMin=0, yMax=66000)

        for tick in self.hist.gradient.ticks:
            tick.hide()
        imageWidget.addItem(self.hist, row=1, col=2)
        
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

    @pyqtSlot(int)
    def get_view_aspect(self, aspect):
        self.vb.setAspectLocked(True, ratio= aspect)
        self.vb.invertY()
        
    @pyqtSlot(np.ndarray)
    def get_img(self, data_img):
        self.img.setImage(data_img)
       
    @pyqtSlot(list)
    def get_CMValues(self, data_cm):
        self.CMxValue.setText(format(data_cm[0]))
        self.CMyValue.setText(format(data_cm[1]))
        self.point_graph_CM.setData([data_cm[3]], [data_cm[2]])
        self.vb.addItem(self.point_graph_CM)

  
    def make_connection(self, backend):
        backend.aspectSignal.connect(self.get_view_aspect)
        backend.dataSignal.connect(self.get_img)
        backend.CMValuesSignal.connect(self.get_CMValues)

class Backend(QtCore.QObject):
    
    aspectSignal = pyqtSignal(int)
    dataSignal = pyqtSignal(np.ndarray)
    CMValuesSignal = pyqtSignal(list)
    
    scandoneSignal = pyqtSignal()  #para módulo Nanopositioning
    imageSignal = pyqtSignal(np.ndarray) #para view de módulo Cámara
    scanfinishSignal_luminescence = pyqtSignal(list)  #para módulo Luminescence
    
    continually_acSignal = pyqtSignal()
    
    def __init__(self, pi_device, task_nidaqmx, myAndor, mySpectrometer, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.pi_device = pi_device
        self.shuttertask = task_nidaqmx[0]
        self.myAndor = myAndor
        self.mySpectrometer = mySpectrometer
        
        self.file_path = os.path.abspath("C:\Julian\Data_PySpectrum") 

        self.PDtimer_stepxy = QtCore.QTimer()

        self.wavelength = 550
        self.exposure_time = 2
        self.shape = (NumberofPixel, NumberofPixel)

        self.center_row = 438
        self.spot_size = 25
        self.set_scan_filter_spectrum(self.center_row, self.spot_size)

        self.lower_wavelength = 540
        self.upper_wavelength = 580

        self.set_scan_filter_wave_spectrum([self.lower_wavelength, self.upper_wavelength])

        
    @pyqtSlot(int, int)
    def set_scan_filter_spectrum(self, center_row, spot_size):
        
        self.spot_size = spot_size
        self.center_row = center_row
        
        down_row = self.center_row - int((self.spot_size-1)/2)
        up_row = self.center_row + int((self.spot_size-1)/2) + 1  
        self.roi_rows = range(down_row, up_row)

    @pyqtSlot(list)
    def set_scan_filter_wave_spectrum(self, filter_wavelength):
        
        self.lower_wavelength = filter_wavelength[0]
        self.upper_wavelength = filter_wavelength[1]

        print(datetime.now(), 'Filter Spectrum integrate between:', self.lower_wavelength, self.upper_wavelength)

    def x_create(self): 
        pos = self.pi_device.qPOS()
        x_pos = pos['A']
        y_pos = pos['B']
        z_pos = pos['C']
 
        return x_pos, y_pos, z_pos

    @pyqtSlot(list)            
    def scan_step_parameters(self, parameters): 
        
        self.range_x = parameters[0]
        self.range_y = parameters[1]
        self.Nx  = parameters[2]
        self.Ny = parameters[3]
        
        self.time_step_x_lin = (self.exposure_time)*self.Nx #aprox. segundos para hacer una linea en x   
       
        self.image_scan = np.zeros((self.Ny, self.Nx))

        aspect = (self.Nx/self.range_x)/(self.Ny/self.range_y)
        self.aspectSignal.emit(aspect) 
        
    @pyqtSlot(int, bool)           
    def start_scan(self, color_laser, psfbool):  
        print("start scan")
        
        timestr = time.strftime("%Y%m%d-%H%M%S")
        name_folder = self.create_folder(timestr)

        self.laser = shutters[color_laser]
        
        self.signal_scan_stop = False
        self.mode_printing = 'none'
        
        #if self.myAndor.status == ('Acquisition in progress.'):
       #     self.myAndor.wait_for_acquisition()  
        #    self.myAndor.abort_acquisition()
        
      #  self.myAndor.set_exposure_time(self.exposure_time)
      #  print('[Camera] Exposure time = {} s'.format(self.exposure_time))
        
        cal = self.set_wavelength(self.wavelength)
        self.calibration = cal    

        if psfbool:
            self.start_scan_step_xy(self.laser, self.mode_printing, name_folder)
        else:
             print('Modo no programado')
     
    @pyqtSlot(int, bool)   
    def stop_scan(self, color_laser, psfbool):
        
        if not self.signal_scan_stop: 
           
           if self.myAndor.status == ('Acquisition in progress.'):
                self.myAndor.abort_acquisition()
           
           laser = shutters[color_laser]
           closeShutter(laser, self.shuttertask)
          
         #  self.myAndor.shutter(1, 2, 0, 0, 2)
           
           print("stop confocal scan slow")
           
           self.continually_acSignal.emit()
           
           if psfbool:
               
               self.PDtimer_stepxy.stop()
               
               print('timer stop')
              
               self.pi_device.MOV(['A','B'], [self.x_pos, self.y_pos])
           else:
               print('Modo no programado')


    @pyqtSlot()             
    def stop_scan_step_xy(self):
        
        if not self.signal_scan_stop:
            
            if self.myAndor.status == ('Acquisition in progress.'):
                self.myAndor.abort_acquisition()
    
            closeShutter(self.laser, self.shuttertask)
            
            print("stop confocal scan slow")
            
            self.PDtimer_stepxy.stop()
            self.pi_device.MOV(['A','B'], [self.x_pos, self.y_pos])   

    @pyqtSlot(str, str, str)             
    def start_scan_step_xy(self, laser, mode_printing, name_folder):  

        self.laser = laser
        self.mode_printing = mode_printing
        self.new_folder = name_folder
        self.signal_scan_stop = False

        self.save_calibration_spectrum(self.calibration)
        
        if self.myAndor.status == ('Acquisition in progress.'):
            self.myAndor.wait_for_acquisition()  
            self.myAndor.abort_acquisition()
        
        self.myAndor.set_exposure_time(self.exposure_time)
        print('[Camera] Exposure time = {} s'.format(self.exposure_time))
        
      #  self.myAndor.shutter(1, 1 , 0, 0, 1) # opens both shutter, mode liveview
      #  time.sleep(1)
          
        self.tic = ptime.time()  
        self.j = 0  
        self.i = 0
        self.x_pos, self.y_pos, self.z_pos = self.x_create()
        openShutter(laser, self.shuttertask)
        self.PDtimer_stepxy.start(0)   
        
    def scan_step_xy(self):   
 
        dy = self.range_y/self.Ny
        dx = self.range_x/self.Nx
        
        if self.j < self.Ny:
            
            if self.i < self.Nx :
        
                self.pi_device.MOV(['A', 'B'], [self.x_pos - self.range_x/2 + self.i*dx, self.y_pos - self.range_y/2 + self.j*dy]) 
                # while self.pi_device.qONT():
                #     time.sleep(0.001)

                step_profile  = self.scan_step()
                
             #   print(self.j, self.i, step_profile)
                
                self.image_scan[self.j, self.i] = step_profile

                self.dataSignal.emit(self.image_scan)
             
                self.i = self.i + 1 
                
            else:
                self.i = 0
            
                self.j = self.j + 1       
           
        else:
           #  self.myAndor.shutter(1, 1, 0, 0, 0)
             self.PDtimer_stepxy.stop()
             self.dataSignal.emit(self.image_scan)
             self.signal_scan_stop = True
             closeShutter(self.laser, self.shuttertask)
             
             x_o, y_o = self.CMmeasure()
             center_mass = [x_o, y_o]
              
             print(ptime.time()-self.tic, "Time scan step x/y")
             
             self.continually_acSignal.emit()
        
             if self.mode_printing == 'none':
                self.saveFrame()
                self.pi_device.MOV(['A','B'], [self.x_pos, self.y_pos])
                self.scandoneSignal.emit()
                            
             if self.mode_printing == 'luminescence':
                self.saveFrame()
                self.scanfinishSignal_luminescence.emit(center_mass)
        
    def scan_step(self):
        """ a pesar de ser Step, hago toda una linea y despues la dibujo"""

        image = self.taking_picture()
        
       # down_row_2 = int(self.roi_rows[0]-(len(self.roi_rows)-1)/2)
       # up_row_2 = int(self.roi_rows[-1]+(len(self.roi_rows)-1)/2 + 1)
       # roi_2 = range(down_row_2, up_row_2)
       # image_roi = image[:,roi_2]  
        #self.save_picture_spectrum(self.i, self.j, image_roi)
       
        array_profile_spectrum = np.sum(image[:,self.roi_rows], axis=1)
        self.save_spectrum(self.i, self.j, self.calibration, array_profile_spectrum)
       
        step_profile = self.option_step_profile(array_profile_spectrum)

        return step_profile

    def option_step_profile(self, array_profile):

        aux_array_profile = np.where(self.calibration <= self.upper_wavelength, array_profile, 0)
        aux_array_profile = np.where(self.calibration >= self.lower_wavelength, aux_array_profile, 0)
        step_profile = np.sum(aux_array_profile)

        return step_profile


    @pyqtSlot(float, float)
    def set_scan_spectrum(self, Wavelength, exposure_time):

        self.wavelength = Wavelength
        self.exposure_time = exposure_time
        
    
    def set_wavelength(self, Wavelength):
        
        ret_0, current_Wavelength = self.mySpectrometer.ShamrockGetWavelength(DEVICE)
        
        if int(current_Wavelength) != int(Wavelength):

            self.mySpectrometer.ShamrockSetWavelength(DEVICE, Wavelength)
            
        print(datetime.now(), '[Shamrock] Wavelength = ', self.mySpectrometer.ShamrockGetWavelength(DEVICE))
       
        ret, calibration = self.mySpectrometer.ShamrockGetCalibration(DEVICE, NumberofPixel)
        cal = np.array(list(calibration))
        cal = np.round(cal, 4)
        
        self.calibration = cal
        
        return cal 

    def taking_picture(self):
        
        # set shutters configuration
        # self.myAndor.shutter(1, 1, 0, 0, 0) # standard mode for us
       
        self.myAndor.acquisition_mode = 'Single Scan'
     #   self.myAndor.acquisition_mode = 'Run till Abort'
       
        self.myAndor.start_acquisition()    
        self.myAndor.wait_for_acquisition()  
        self.myAndor.abort_acquisition()
        
        image = np.transpose(self.myAndor.most_recent_image16(self.shape))
        self.imageSignal.emit(image)

        return image
    
    def create_folder(self, time):
        """ Crea una carpeta para este archivo particular."""
        
        self.old_folder = self.file_path
        new_folder = os.path.join(self.old_folder, time + "_Slow_Confocal_Spectrum")       
        
        self.new_folder = new_folder
        os.makedirs(new_folder)
        
        return new_folder

    def save_picture_spectrum(self, i, j, image):
        
        filepath = self.new_folder
        filename = "Picture_Andor_First_Order_i%04d_j%04d.tiff" % (int(i), int(j))
        
        full_filename = os.path.join(filepath,filename)
        
        guardado = Image.fromarray(np.transpose(image))
        guardado.save(full_filename)

        #print(datetime.now(), '[PySpectrum]', 'Save Image spectrum')        
    
    def save_calibration_spectrum(self, calibration):
        
        filepath = self.new_folder
        timestr = time.strftime("%Y%m%d_%H%M%S")
        filename = "wavelength_" + timestr + ".txt"

        full_filename = os.path.join(filepath, filename)
        np.savetxt(full_filename, np.array(calibration), fmt='%.4f')

        print(datetime.now(), '[PySpectrum]', 'Save Calibration spectrum')

    def save_spectrum(self, i, j, wavelength, profile):

        filepath = self.new_folder
        filename = "Spectrum_i%04d_j%04d.txt" % (int(i), int(j))

        full_filename = os.path.join(filepath, filename)
        #np.savetxt(full_filename, np.transpose([wavelength, profile]))
        np.savetxt(full_filename, np.array(profile), fmt='%.3f')

     #   print(datetime.now(), '[PySpectrum]', 'Save spectrum')

    #  CMmeasure
    def CMmeasure(self):

        Z = self.image_scan  #solo ida
      
        Zn = (Z-min(map(min,Z)))/(max(map(max,Z))-min(map(min,Z))) #filtro de %70
        for i in range(len(Z[:,1])):
            for j in range (len(Z[1,:])):
                if Zn[i,j] < 0.7:
                    Zn[i,j] = 0
                    
        ycm, xcm = ndimage.measurements.center_of_mass(Zn)
        
        Normal_y = self.range_y/self.Ny
        Normal_x = self.range_x/self.Nx

        x_cm = np.round(self.x_pos - self.range_x/2 + (xcm*Normal_x), 3)
        y_cm = np.round(self.y_pos - self.range_y/2 + (ycm*Normal_y), 3)
        
        self.CMValuesSignal.emit([x_cm, y_cm, xcm, ycm])
        
        return x_cm, y_cm

    @pyqtSlot()  
    def goCM(self):
        x_cm, y_cm = self.CMmeasure()
        self.moveto(x_cm, y_cm)

    def moveto(self, x, y):
        """moves the position along the axis to a specified point.
        Cambie todo paraque ande con la PI"""
        axis = ['A', 'B']
        targets = [x, y]
        self.pi_device.MOV(axis, targets)
        while not all(self.pi_device.qONT(axis).values()):
            time.sleep(0.01)
        
    @pyqtSlot(str)        
    def get_direction(self, file_name):
        self.file_path = file_name

    @pyqtSlot()
    def saveFrame(self):
        """ Config the path and name of the file to save, and save it"""   
        
        filepath = self.new_folder
        timestr = time.strftime("%Y%m%d-%H%M%S")
        name = str(filepath + "/" + "Slow_Confocal_Spectrum" + timestr + ".tiff")
        guardado = Image.fromarray(np.transpose(self.image_scan))
        guardado.save(name)
        print("\n Image saved\n")


    def make_connection(self, frontend):
        
        frontend.scanmodeSignal.connect(self.start_scan)
        frontend.stopSignal.connect(self.stop_scan)
        frontend.parametersstepSignal.connect(self.scan_step_parameters)
        frontend.spectrum_parametersSignal.connect(self.set_scan_spectrum)
        frontend.spectrum_parameters_filterSignal.connect(self.set_scan_filter_spectrum)
        frontend.spectrum_parameters_filter_waveSignal.connect(self.set_scan_filter_wave_spectrum)

        frontend.CMSignal.connect(self.goCM)

        frontend.saveSignal.connect(self.saveFrame)

#%%
        
if __name__ == '__main__':

    app = QtGui.QApplication([])

    gui = Frontend() 
    
    ##INSTRUMENTS
    
        ##Platina
    
    pi_device= GCSDevice()
    Instrument_PI.initial_pi_device(pi_device)
    
        ##Nidaqmx: shutters, flippers, photodiodes
    task_nidaqmx = initial_nidaqmx(nidaqmx)
    
        ##Camera Andor
    
    myAndor = CCD()
    myAndor.lib.Initialize()
    print('[Camera] IDN = {}'.format(myAndor.idn))
    
        ##Shamrock
    
    mySpectrometer = Shamrock()
    inipath = 'C:\\Program Files (x86)\\Andor SOLIS\\SPECTROG.ini'
    mySpectrometer.ShamrockInitialize(inipath)
    ret, serial_number = mySpectrometer.ShamrockGetSerialNumber(DEVICE)
    print(datetime.now(), '[Shmarock] Serial number = {}'.format(serial_number))
    
    worker = Backend(pi_device, task_nidaqmx, myAndor, mySpectrometer)

    worker.make_connection(gui)
    gui.make_connection(worker)

    confocalThread = QtCore.QThread()
    worker.moveToThread(confocalThread)
    worker.PDtimer_stepxy.moveToThread(confocalThread)
    worker.PDtimer_stepxy.timeout.connect(worker.scan_step_xy)
    confocalThread.start()

    gui.show()
#    app.exec_()


