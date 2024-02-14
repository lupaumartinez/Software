# -*- coding: utf-8 -*-
"""
Created on Thu Apr  4 11:10:29 2019

@author: Luciana
"""

import os
import time
import numpy as np
from datetime import datetime
from scipy import signal

from pyqtgraph.Qt import QtGui, QtCore
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PIL import Image
import pyqtgraph as pg
from pyqtgraph.dockarea import DockArea, Dock
import pyqtgraph.ptime as ptime

from ccd import CCD

from Shamrock import Shamrock
from Instrument_Shamrock import DEVICE, NumberofPixel

import viewbox_tools

from Lampara import lamp
from Lampara import glue_steps

from Fit_raman_water import fit_signal_raman
from Fit_polynomial import fit_signal_polynomial

nameGrating = ['150 lines/mm', '1200 lines/mm', 'Mirror']

class Frontend(QtGui.QFrame):

    spectrumSignal = pyqtSignal(float, float)
    spectrum_sandg_Signal = pyqtSignal(list, float)
    
    liveSignal = pyqtSignal(bool, float, float)
    RECSignal = pyqtSignal(bool, float, float)
    REC_kinetics_Signal = pyqtSignal(bool, float, float, int)

    show_lineparametersSignal = pyqtSignal(bool, int, int)
    lineparametersSignal = pyqtSignal(int, int, int)
    parameters_filter_waveSignal = pyqtSignal(float, float)
    normalized_lamp_Signal = pyqtSignal(bool, int, int)
    
    fit_raman_Signal = pyqtSignal(bool)
    fit_poly_Signal = pyqtSignal(bool, int)
    
    continually_acquisitionSignal = pyqtSignal(bool)

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.setUpGUI()

    def setUpGUI(self):
        
        #Measurment Spectrum - Step and Glue buttons

        time_Label = QtGui.QLabel('Exposure Time (s):')
        self.time_Edit = QtGui.QLineEdit('1')   
        
         
        #Step = 1

        center_lambda_Label = QtGui.QLabel('Only one step, Center λ (nm):')
        self.center_lambda = QtGui.QLineEdit('532')
        self.spectrum_button = QtGui.QPushButton('Measurment Spectrum')
        self.spectrum_button.clicked.connect(self.spectrum_wavelength)
        
        #Number of Kinetics Serial
        
        n_kinetics_Label = QtGui.QLabel('Number of Kinetics Serial:')
        self.n_kinetics_Edit =  QtGui.QLineEdit('600')
        
        self.liveview_button = QtGui.QPushButton('LIVEVIEW/STOP')
        self.liveview_button.setCheckable(True)
        self.liveview_button.clicked.connect(self.liveview_button_check)
        self.liveview_button.setStyleSheet(
                "QPushButton { background-color: yellow; }"
                "QPushButton:pressed { background-color: blue; }")
        
        self.REC_button = QtGui.QPushButton('REC/STOP')
        self.REC_button.setCheckable(True)
        self.REC_button.clicked.connect(self.REC_button_check)
        self.REC_button.setStyleSheet(
                "QPushButton { background-color: yellow; }"
                "QPushButton:pressed { background-color: blue; }")
        
        self.REC_kinetics_button = QtGui.QPushButton('REC/STOP Kinetics')
        self.REC_kinetics_button.setCheckable(True)
        self.REC_kinetics_button.clicked.connect(self.REC_kinetics_button_check)
        self.REC_kinetics_button.setStyleSheet(
                "QPushButton { background-color: yellow; }"
                "QPushButton:pressed { background-color: blue; }")
        
        #Steps = N

        first_lambda_Label = QtGui.QLabel('First λ (nm):')
        self.first_lambda = QtGui.QLineEdit('400')
        last_lambda_Label = QtGui.QLabel('Last λ (nm):')
        self.last_lambda = QtGui.QLineEdit('800')
        overlap_Label = QtGui.QLabel('Overlap Steps:')
        self.overlap =  QtGui.QLineEdit('0.2')
        overlap_Label.setToolTip('Percentage 0.00-1.00')
        stepandglue_Label = QtGui.QLabel('Step and glue #:')
        self.stepandglue = QtGui.QLabel('')
        self.spectrum_sandg_button = QtGui.QPushButton('Measurment with Step and Glue')
        self.spectrum_sandg_button.clicked.connect(self.spectrum_sandg_wavelength)  
        
        #Line profile Spectrum

        size_spot_Label = QtGui.QLabel('Size Bin:')
        self.size_spot_Edit = QtGui.QLineEdit('25')
        self.size_spot_Edit.textChanged.connect(self.spectrum_line_parameters)

        self.center_row_sl = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.center_row_sl.setMinimum( int(self.size_spot_Edit.text()) )
        self.center_row_sl.setMaximum(1002 - int(self.size_spot_Edit.text()) )
        self.center_row_sl.setValue(438)
        self.center_row_sl.setTickPosition(QtGui.QSlider.TicksBelow)
        self.center_row_sl.setTickInterval(1)
        self.center_row_sl.valueChanged.connect(self.spectrum_line_parameters)

        center_row_Label = QtGui.QLabel('Center row (pixel):')
        self.center_row_Label = QtGui.QLabel('0')
        self.center_row_Label.setText(format(int(self.center_row_sl.value())))

        lower_wavelength_Label = QtGui.QLabel('Lower wavelength (nm):')
        self.lower_wavelength_Edit = QtGui.QLineEdit('540')   
        upper_wavelength_Label = QtGui.QLabel('Upper wavelength (nm):')
        self.upper_wavelength_Edit = QtGui.QLineEdit('580')  
        self.lower_wavelength_Edit.textEdited.connect(self.spectrum_parameters_filter_wavelength)
        self.upper_wavelength_Edit.textEdited.connect(self.spectrum_parameters_filter_wavelength)
        
        self.normalized_lamp_option = QtGui.QCheckBox('Normalized with lamp')
        self.normalized_lamp_option.clicked.connect(self.spectrum_line_parameters)
        self.normalized_lamp_option.setToolTip('Check is Normalized')
        self.normalized_bool = False
        
        self.fit_raman_option = QtGui.QCheckBox('Fit Lorentz')
        self.fit_raman_option.clicked.connect(self.spectrum_line_parameters)
        self.fit_raman_bool = False
        
        self.fit_poly_option = QtGui.QCheckBox('Fit Polynomial')
        self.fit_poly_option.clicked.connect(self.spectrum_line_parameters)
        self.fit_poly_bool = False
        
        n_polynomial_Label = QtGui.QLabel('Order polynomial:')
        self.n_polynomial_Edit = QtGui.QLineEdit('5')
        self.n_polynomial_Edit.textChanged.connect(self.spectrum_line_parameters)
        
        center_row_bkg_Label = QtGui.QLabel('Center row Background (pixel):')
        self.center_row_bkg_Edit = QtGui.QLineEdit('200')
        self.center_row_bkg_Edit.textChanged.connect(self.spectrum_line_parameters)

        window_smooth_Label = QtGui.QLabel('Window smooth')
        self.window_smooth_Edit = QtGui.QLineEdit('11')
        self.window_smooth_Edit.textChanged.connect(self.spectrum_line_parameters)
        
        self.line_spectrum_button = QtGui.QPushButton('Show line profile')
        self.line_spectrum_button.setCheckable(True)
        self.line_spectrum_button.clicked.connect(self.show_spectrum_line_parameters)
        
        self.continually_acquisition_button = QtGui.QCheckBox('Continually Acquisition')
        self.continually_acquisition_button.clicked.connect(self.continually_acquisition_button_check)
        self.continually_acquisition_button.setToolTip('Check is permanently taking picture every 4s')

        self.parameters = QtGui.QWidget()
        parameters_layout = QtGui.QGridLayout()
        self.parameters.setLayout(parameters_layout)

        parameters_layout.addWidget(time_Label,                         0, 0)
        parameters_layout.addWidget(self.time_Edit,                     0, 1)
        
        parameters_layout.addWidget( QtGui.QLabel('<strong> ONE STEP ON:'),                 1, 0)
        parameters_layout.addWidget(center_lambda_Label,                2, 0)
        parameters_layout.addWidget(self.center_lambda,                 2, 1)
        parameters_layout.addWidget(self.spectrum_button,               3, 0)
        
        parameters_layout.addWidget(self.liveview_button,               4, 0)
        parameters_layout.addWidget(self.continually_acquisition_button,4, 1)
        parameters_layout.addWidget(self.REC_button,                    5, 0)
        
        parameters_layout.addWidget(n_kinetics_Label,                   6, 0)
        parameters_layout.addWidget(self.n_kinetics_Edit,               6, 1)
        parameters_layout.addWidget(self.REC_kinetics_button,           7, 0)
        
        
        parameters_layout.addWidget(QtGui.QLabel('<strong> STEP AND GLUE ON:'),             8 ,0)             
        parameters_layout.addWidget(first_lambda_Label,                 9, 0)
        parameters_layout.addWidget(self.first_lambda,                  9, 1)
        parameters_layout.addWidget(last_lambda_Label,                  10, 0)
        parameters_layout.addWidget(self.last_lambda,                   10, 1)
        parameters_layout.addWidget(overlap_Label,                      11, 0)
        parameters_layout.addWidget(self.overlap,                       11, 1)
        
        parameters_layout.addWidget(stepandglue_Label,                  12, 0)
        parameters_layout.addWidget(self.stepandglue,                   12, 1)
        parameters_layout.addWidget(self.spectrum_sandg_button,         13, 0)
        
        parameters_layout.addWidget(QtGui.QLabel('<strong> VIEW SPECTRUM ON:'),             14,0)  
        parameters_layout.addWidget(self.line_spectrum_button,          15, 0)

        parameters_layout.addWidget(center_row_Label,                   16, 0)
        parameters_layout.addWidget(self.center_row_Label,              16, 1)
        parameters_layout.addWidget(self.center_row_sl,                 17, 0)
        parameters_layout.addWidget(size_spot_Label,                    18, 0)
        parameters_layout.addWidget(self.size_spot_Edit,                18, 1)

        parameters_layout.addWidget(lower_wavelength_Label,             19, 0)
        parameters_layout.addWidget(self.lower_wavelength_Edit,         19, 1)
        parameters_layout.addWidget(upper_wavelength_Label,             20, 0)
        parameters_layout.addWidget(self.upper_wavelength_Edit,         20, 1)
        
        parameters_layout.addWidget(self.fit_poly_option,               21, 0)
        parameters_layout.addWidget(n_polynomial_Label,                 22, 0)
        parameters_layout.addWidget(self.n_polynomial_Edit,             22, 1)
        
        parameters_layout.addWidget(self.fit_raman_option,              23, 0)
        parameters_layout.addWidget(center_row_bkg_Label,               24, 0)
        parameters_layout.addWidget(self.center_row_bkg_Edit,           24, 1)
        
        parameters_layout.addWidget(self.normalized_lamp_option,        25, 0)
        parameters_layout.addWidget(window_smooth_Label,                26, 0)
        parameters_layout.addWidget(self.window_smooth_Edit,            26, 1)
        
        # GUI layout

        grid = QtGui.QGridLayout()
        self.setLayout(grid)
        grid.addWidget(self.parameters)
        
        # Plot LIVE SPECTRUM on Dock
        
        self.lineplotWidget = viewbox_tools.linePlotWidget_spectrum()
        self.curve_spectrum = self.lineplotWidget.linePlot.plot(open='y')
        self.curve_fit_spectrum = self.lineplotWidget.linePlot.plot(open='y')
        self.curve_fitpoly_spectrum = self.lineplotWidget.linePlot.plot(open='y')
        
        self.lineplot_integrate_Widget = viewbox_tools.linePlotWidget_integrate()
        self.curve_integrate = self.lineplot_integrate_Widget.linePlot.plot(open='y')
        
        self.lineplot_wavemax_Widget = viewbox_tools.linePlotWidget_max_spectrum()
        self.curve_wavemax = self.lineplot_wavemax_Widget.linePlot.plot(open='y')
        self.curve_londa_spr = self.lineplot_wavemax_Widget.linePlot.plot(open='y')
        self.curve_wavemax_poly = self.lineplot_wavemax_Widget.linePlot.plot(open='y')
        
        self.show_live_Widget = QtGui.QWidget()
        subgrid = QtGui.QGridLayout()
        self.show_live_Widget.setLayout(subgrid)
        subdockArea = DockArea()
        subgrid.addWidget(subdockArea)

        spectrumDock = Dock("Live Spectrum")
        spectrumDock.addWidget(self.lineplotWidget)
        subdockArea.addDock(spectrumDock)
        
        integrateDock = Dock("Integrate")
        integrateDock.addWidget(self.lineplot_integrate_Widget)
        subdockArea.addDock(integrateDock, 'right', spectrumDock)
        
        maxwaveDock = Dock("Max Wavelength")
        maxwaveDock.addWidget(self.lineplot_wavemax_Widget)
        subdockArea.addDock(maxwaveDock, 'right', integrateDock)

        
    def spectrum_wavelength(self):

        exposure_time = float(self.time_Edit.text())
        center_wavelength = float(self.center_lambda.text())
        self.spectrumSignal.emit(center_wavelength, exposure_time)
        
        self.show_live_Widget.show()
        
    def spectrum_sandg_wavelength(self):

        exposure_time = float(self.time_Edit.text())
                                             
        parameters_wavelength = [float(self.first_lambda.text()), float(self.last_lambda.text()), float(self.overlap.text())]

        self.spectrum_sandg_Signal.emit(parameters_wavelength, exposure_time)
        
        self.show_live_Widget.show()

    def show_spectrum_line_parameters(self):

        center_row = int(self.center_row_Label.text())  
        spot_size = int(self.size_spot_Edit.text())

        if self.line_spectrum_button.isChecked():  
            self.show_lineparametersSignal.emit(True, center_row, spot_size)
        else:
             self.show_lineparametersSignal.emit(False, center_row, spot_size)

    def spectrum_line_parameters(self):

        self.center_row_Label.setText(format(int(self.center_row_sl.value()))) 

        self.center_row = int(self.center_row_Label.text())                                      
        self.spot_size = int(self.size_spot_Edit.text())
        
        self.center_bkg = int(self.center_row_bkg_Edit.text())
        
        self.window_smooth = int(self.window_smooth_Edit.text())
        
        n_poly = int(self.n_polynomial_Edit.text())

        self.lineparametersSignal.emit(self.center_row, self.spot_size, self.center_bkg)
            
        if self.normalized_lamp_option.isChecked():
            self.normalized_bool = True
            self.normalized_lamp_Signal.emit(self.normalized_bool, self.center_bkg, self.window_smooth)
        else:
            self.normalized_bool = False
            self.normalized_lamp_Signal.emit(self.normalized_bool, self.center_bkg, self.window_smooth)
            
        if self.fit_raman_option.isChecked():
            self.fit_raman_bool = True
            self.fit_raman_Signal.emit(self.fit_raman_bool)
        else:
            self.fit_raman_bool = False
            self.fit_raman_Signal.emit(self.fit_raman_bool)
            self.curve_fit_spectrum.clear()
            self.curve_londa_spr.clear()
            
        if self.fit_poly_option.isChecked():
            self.fit_poly_bool = True
            self.fit_poly_Signal.emit(self.fit_poly_bool, n_poly)
        else:
            self.fit_poly_bool = False
            self.fit_poly_Signal.emit(self.fit_poly_bool, n_poly)
            self.curve_fitpoly_spectrum.clear()
            self.curve_wavemax_poly.clear()

        self.show_spectrum_line_parameters()

    def spectrum_parameters_filter_wavelength(self):

        lower_wavelength = float(self.lower_wavelength_Edit.text())
        upper_wavelength = float(self.upper_wavelength_Edit.text())
        
        self.parameters_filter_waveSignal.emit(lower_wavelength, upper_wavelength)
        
    @pyqtSlot(np.ndarray, np.ndarray)
    def spectrum_line_show(self, array_wavelength, array_profile):
        
        self.curve_spectrum.setData(array_wavelength, array_profile,
                           pen=pg.mkPen('g', width=3)) 
        
    @pyqtSlot(np.ndarray, np.ndarray)
    def spectrum_fit_line_show(self, array_wavelength, array_profile):
        
        self.curve_fit_spectrum.setData(array_wavelength, array_profile,
                           pen=pg.mkPen('r', width=3)) 
        
    @pyqtSlot(np.ndarray, np.ndarray)
    def spectrum_fitpoly_line_show(self, array_wavelength, array_profile):
        
        self.curve_fitpoly_spectrum.setData(array_wavelength, array_profile,
                           pen=pg.mkPen('m', width=3)) 
        
    def liveview_button_check(self):
        
        exposure_time = float(self.time_Edit.text())
        center_wavelength = float(self.center_lambda.text())
        
        if self.liveview_button.isChecked():
           self.liveSignal.emit(True, center_wavelength, exposure_time)

           self.show_live_Widget.show()
           
        else:
           self.liveSignal.emit(False, center_wavelength, exposure_time)
           
    @pyqtSlot(list)
    def show_plot_max_wavelength(self, data): 
        
        time = data[0]
        wave_max = data[1]

        self.curve_wavemax.setData(time, wave_max,
                           pen=pg.mkPen('g', width=0.5), symbol='o')
        
    @pyqtSlot(list)
    def show_plot_londa_spr(self, data): 
        
        time = data[0]
        londa_spr = data[1]

        self.curve_londa_spr.setData(time, londa_spr,
                           pen=pg.mkPen('r', width=0.5), symbol='o')
        
    @pyqtSlot(list)
    def show_plot_max_wavelength_poly(self, data): 
        
        time = data[0]
        wave_max = data[1]

        self.curve_wavemax_poly.setData(time, wave_max,
                           pen=pg.mkPen('m', width=0.5), symbol='o')
        
    @pyqtSlot(list)
    def show_plot_integrate_spectrum(self, data): 
        
        time = data[0]
        integrate_spectrum = data[1]

        self.curve_integrate.setData(time, integrate_spectrum,
                           pen=pg.mkPen('b', width=0.5), symbol='o')   
           
    def REC_button_check(self):
        
        exposure_time = float(self.time_Edit.text())
        center_wavelength = float(self.center_lambda.text())
        
        if self.REC_button.isChecked():
                
            self.RECSignal.emit(True, center_wavelength, exposure_time)
            self.show_live_Widget.show()
            
        else:
           self.RECSignal.emit(False, center_wavelength, exposure_time)
           
    def REC_kinetics_button_check(self):
        
        exposure_time = float(self.time_Edit.text())
        center_wavelength = float(self.center_lambda.text())
        n_kinetics = int(self.n_kinetics_Edit.text())
        
        if self.REC_kinetics_button.isChecked():
                
            self.REC_kinetics_Signal.emit(True, center_wavelength, exposure_time, n_kinetics)
            self.show_live_Widget.show()
            
        else:
           self.REC_kinetics_Signal.emit(False, center_wavelength, exposure_time, n_kinetics)
           
           
    def continually_acquisition_button_check(self):
        if self.continually_acquisition_button.isChecked():
           self.continually_acquisitionSignal.emit(True)
           self.continually_acquisition_button.setText('YES Continually Aquisition Picture')
        else:
           self.continually_acquisitionSignal.emit(False)
           self.continually_acquisition_button.setText('NOT Continually Aquisition Picture')
         
    def make_connection(self, backend):

        backend.line_spectrumSignal.connect(self.spectrum_line_show)
        backend.max_wave_Signal.connect(self.show_plot_max_wavelength)
        backend.integrate_Signal.connect(self.show_plot_integrate_spectrum)
        
        backend.line_fit_spectrumSignal.connect(self.spectrum_fit_line_show)
        backend.londa_spr_Signal.connect(self.show_plot_londa_spr)
        
        backend.line_fitpoly_spectrumSignal.connect(self.spectrum_fitpoly_line_show)
        backend.max_wave_poly_Signal.connect(self.show_plot_max_wavelength_poly)
        
    def closeEvent(self, event):

        reply = QtGui.QMessageBox.question(self, 'Quit', 'Are you sure to quit?',
                                           QtGui.QMessageBox.No |
                                           QtGui.QMessageBox.Yes)
        if reply == QtGui.QMessageBox.Yes:
            print("YES")
            event.accept()
            self.close()
        
        else:
            event.ignore()
            print("NO")
        
#%%
        
class Backend(QtCore.QObject):

    imageSignal = pyqtSignal(np.ndarray) #esto es para el view de Camera
    
    line_spectrumSignal = pyqtSignal(np.ndarray, np.ndarray)
    line_fit_spectrumSignal = pyqtSignal(np.ndarray, np.ndarray)
    line_fitpoly_spectrumSignal = pyqtSignal(np.ndarray, np.ndarray)
    
    max_wave_Signal = pyqtSignal(list)
    integrate_Signal = pyqtSignal(list)
    londa_spr_Signal = pyqtSignal(list)
    max_wave_poly_Signal = pyqtSignal(list)
    
    umbral_Signal_growth = pyqtSignal(float)
    
    luminescence_steps_finish_Signal = pyqtSignal()
    
    continually_acSignal = pyqtSignal()
    
    def __init__(self, myAndor, mySpectrometer, *args, **kwargs):
        
        super().__init__(*args, **kwargs)
        
        self.myAndor = myAndor
        self.mySpectrometer = mySpectrometer

        self.file_path = os.path.abspath("C:\Julian\Data_PySpectrum")   #por default, por si se olvida de crear la carpeta del día
      
        self.shape = (NumberofPixel, NumberofPixel)
        self.wavelength_window = 103 #nm   #mode_grating default = '150 lines/mm'
        
        self.exposure_time = 1
        
        self.center_row = 438   #fiber
        self.spot_size = 25     #fiber

        self.lower_wavelength = 540
        self.upper_wavelength = 580

        self.normalized_lamp_bool = False
        self.center_bkg = 200
        self.window_smooth = 11
        
        self.lamp = lamp # ver como cargarlo
        
        self.fit_raman_water = False
        self.fit_poly = False
        self.npol = 5
        
        self.step = 1

        self.calibration = np.zeros(NumberofPixel)
        self.image = np.zeros(self.shape)
        
        self.viewTimer = QtCore.QTimer()
        
        self.viewRECTimer = QtCore.QTimer()
        
        self.viewRECTimer_kinetics = QtCore.QTimer()
        self.n_kinetics = 600 #puntos para los videos para REC Kinetics, tiempo total = exposure_time*n_kinetics
        
      #  self.continuallyTimer = QtCore.QTimer()
      #  self.continuallyTimer.timeout.connect(self.continually_acquisition_timer)
        
        self.mode_printing = 'none'
        
        self.mode_continually_acquisition = False

    @pyqtSlot(str)  #viene de PySpectrum si creo directorio del dia, sino usa la q que esta por default
    def get_direction(self, file_name):
        self.file_path = file_name

    def set_wavelength(self, Wavelength):

        self.mySpectrometer.ShamrockSetWavelength(DEVICE, Wavelength)
        print(datetime.now(), '[Shamrock] Wavelength = ', self.mySpectrometer.ShamrockGetWavelength(DEVICE))
       
        ret, calibration = self.mySpectrometer.ShamrockGetCalibration(DEVICE, NumberofPixel)
        cal = np.array(list(calibration))
        cal = np.round(cal, 4)
        
        return cal 

    def taking_picture(self, exposure_time):
        
        self.myAndor.acquisition_mode = 'Single Scan'
        print(datetime.now(), 'Acquisition mode = {}'.format(self.myAndor.acquisition_mode))
       
       # self.myAndor.acquisition_mode = 'Run till abort'
       
        self.myAndor.status
        self.myAndor.set_exposure_time(exposure_time)
        
        # set shutters configuration
       # self.myAndor.shutter(1, 1 , 0, 0, 1)
       # self.myAndor.shutter(1, 1, 0, 0, 0)
        
        self.myAndor.start_acquisition()
        self.myAndor.wait_for_acquisition()  
        self.myAndor.abort_acquisition()

        #image = np.transpose(np.flip(self.myAndor.most_recent_image16(self.shape), 1))
        image = np.transpose(self.myAndor.most_recent_image16(self.shape))
        self.imageSignal.emit(image)
        
        print('[Camera] Exposure time = {} s'.format(exposure_time))
        
        self.image = image

        return image
    
    @pyqtSlot(float, float)
    def measurment_center_spectrum(self, Wavelength, exposure_time):
        
        if self.myAndor.status == ('Acquisition in progress.'):
            self.myAndor.wait_for_acquisition()  
            self.myAndor.abort_acquisition()
        
        new_folder = self.create_folder(self.file_path, self.step)
        os.makedirs(new_folder)
        self.new_folder = new_folder

        calibration = self.set_wavelength(Wavelength)
        
       # self.myAndor.shutter(1, 1, 0, 0, 0)
        image = self.taking_picture(exposure_time)
        
        self.line_spectrum(calibration, image)

        self.calibration = calibration
        
        self.save_calibration_spectrum(calibration, self.step)
        self.save_picture_spectrum(image, self.step)
        
        self.continually_acSignal.emit()
        
       # return calibration, image
           
    def save_picture_spectrum(self, image, step):
        
        filepath = self.new_folder
        
        timestr = time.strftime("%Y%m%d_%H%M%S")
        
        filename = timestr + "_Picture_Andor_Spectrum_step_%04d.tiff"%(int(step))

        full_filename = os.path.join(filepath,filename)
        guardado = Image.fromarray(np.transpose(image))
        guardado.save(full_filename)

        print(datetime.now(), '[PySpectrum]', 'Save Image spectrum')        
    
    def save_calibration_spectrum(self, calibration, step):
        
        filepath = self.new_folder
        timestr = time.strftime("%Y%m%d_%H%M%S")
        filename = timestr + "_Calibration_Shamrock_Spectrum_step_%04d.txt"%(int(step))

        full_filename = os.path.join(filepath, filename)
        np.savetxt(full_filename, np.array(calibration), fmt='%.4f')

        print(datetime.now(), '[PySpectrum]', 'Save Calibration spectrum')
        
    @pyqtSlot(int, int, int)
    def line_spectrum_parameters(self, center_row, spot_size, center_bkg):

        self.center_row = center_row
        self.spot_size = spot_size
        self.center_bkg = center_bkg
        
        wavelength, spectrum_bkg = self.line_spectrum_bkg(self.calibration, self.image)

        if not self.normalized_lamp_bool:
            
            wavelength, spectrum_NP = self.line_spectrum(self.calibration, self.image)
            self.line_spectrumSignal.emit(wavelength, spectrum_NP)   
            
            if self.fit_raman_water:
                
                try:
                
                    fit_wavelength, fit_spectrum_NP, best_parameters = fit_signal_raman(wavelength, spectrum_NP, self.lower_wavelength, self.upper_wavelength)
                    
                    self.fit_parameters = best_parameters
                    self.fit_wavelength = fit_wavelength
                    self.fit_spectrum = fit_spectrum_NP
                    
                    self.londa_spr = np.round(best_parameters[2],2)
                    self.line_fit_spectrumSignal.emit(fit_wavelength, fit_spectrum_NP) 
                
                except: pass
        
            if self.fit_poly:
               
                   fitpoly_wavelength, fitpoly_spectrum_NP, max_wavelength = fit_signal_polynomial(wavelength, spectrum_NP, self.lower_wavelength, self.upper_wavelength, self.npol)
                   
                   self.fitpoly_wavelength = fitpoly_wavelength
                   self.fitpoly_spectrum = fitpoly_spectrum_NP
                   self.max_wavelength_poly = np.round(max_wavelength,2)
                   
                   self.line_fitpoly_spectrumSignal.emit(fitpoly_wavelength, fitpoly_spectrum_NP) 
            
        if self.normalized_lamp_bool:
            
            wavelength, spectrum_NP = self.line_spectrum_normalized_lamp(self.calibration, self.image, self.lamp, self.center_bkg, self.window_smooth)
            self.line_spectrumSignal.emit(wavelength, spectrum_NP)   
              
        return wavelength, spectrum_NP, spectrum_bkg
            
    def line_spectrum(self, calibration, image):
        
        down_row = self.center_row - int((self.spot_size-1)/2)
        up_row = self.center_row + int((self.spot_size-1)/2) + 1  
        roi_rows = range(down_row, up_row)
         
        spectrum = np.round(np.mean(image[:,roi_rows], axis=1), 3)
        wavelength = calibration 

        return wavelength, spectrum
    
    def line_spectrum_bkg(self, calibration, image):
        
        down_row = self.center_bkg - int((self.spot_size-1)/2)
        up_row = self.center_bkg + int((self.spot_size-1)/2) + 1  
        roi_rows = range(down_row, up_row)
         
        spectrum = np.round(np.mean(image[:,roi_rows], axis=1), 3)
        wavelength = calibration 

        return wavelength, spectrum
    
    @pyqtSlot(bool, int, int)
    def normalized_lamp(self, normalized_lamp_bool, center_bkg, window_smooth):
        
        self.normalized_lamp_bool = normalized_lamp_bool
        self.window_smooth = window_smooth
        self.center_bkg = center_bkg

        if not self.normalized_lamp_bool:
            
            wavelength, spectrum_NP = self.line_spectrum(self.calibration, self.image)

            self.line_spectrumSignal.emit(wavelength, spectrum_NP)

        else:

            wavelength, spectrum_NP_normalized = self.line_spectrum_normalized_lamp(self.calibration, self.image, self.lamp, self.center_bkg, self.window_smooth)
            self.line_spectrumSignal.emit(wavelength, spectrum_NP_normalized)
            
            
    @pyqtSlot(bool)
    def fit_signal(self, fit_signal_bool):
        
        self.fit_raman_water = fit_signal_bool

        wavelength, spectrum_NP = self.line_spectrum(self.calibration, self.image)
        self.line_spectrumSignal.emit(wavelength, spectrum_NP)
                
        if self.fit_raman_water:
                
                fit_wavelength, fit_spectrum_NP, best_parameters = fit_signal_raman(wavelength, spectrum_NP, self.lower_wavelength, self.upper_wavelength)
                self.line_fit_spectrumSignal.emit(fit_wavelength, fit_spectrum_NP)
                
                self.fit_parameters = best_parameters
                self.fit_wavelength = fit_wavelength
                self.fit_spectrum = fit_spectrum_NP
                
                self.londa_spr = np.round(best_parameters[2],2)
                
    @pyqtSlot(bool, int)
    def fit_signal_poly(self, fit_signal_bool, npol):
        
        self.fit_poly = fit_signal_bool

        wavelength, spectrum_NP = self.line_spectrum(self.calibration, self.image)
        self.line_spectrumSignal.emit(wavelength, spectrum_NP)
        
        self.npol = npol
        
        if self.fit_poly:
            
                fitpoly_wavelength, fitpoly_spectrum_NP, max_wavelength = fit_signal_polynomial(wavelength, spectrum_NP, self.lower_wavelength, self.upper_wavelength, self.npol)
                self.line_fitpoly_spectrumSignal.emit(fitpoly_wavelength, fitpoly_spectrum_NP) 
                   
                self.fitpoly_wavelength = fitpoly_wavelength
                self.fitpoly_spectrum = fitpoly_spectrum_NP
                self.max_wavelength_poly = np.round(max_wavelength,2)

    def line_spectrum_normalized_lamp(self, calibration, image, lamp, center_bkg, window_smooth):

        wavelength, spectrum_NP = self.line_spectrum(calibration, image)
        wavelength, spectrum_bkg = self.line_spectrum_bkg(calibration, image)

        spectrum_NP = [spectrum_NP for _,spectrum_NP in sorted(zip(wavelength,spectrum_NP))]
        spectrum_bkg = [spectrum_bkg for _,spectrum_bkg in sorted(zip(wavelength,spectrum_bkg))]

        wavelength = np.sort(wavelength)
        spectrum_NP = np.array(spectrum_NP)
        spectrum_bkg = np.array(spectrum_bkg)
        
        spectrum_NP = spectrum_NP - spectrum_bkg
        
        wavelength_gs, signal_gs = glue_steps(wavelength, spectrum_NP, 1002, 2)
        
        spec_lamp_interp = self.interpolated_lamp(wavelength_gs, [lamp[0], lamp[1]])
        
        desired = np.where((wavelength_gs >= 500) & (wavelength_gs <= 850)) #zona buena de la lampara
        
        londa = wavelength_gs[desired]
        spectrum = signal_gs[desired]
        spectrum_lamp = spec_lamp_interp[desired]
        
        smooth_spectrum_NP =  signal.savgol_filter(spectrum, window_smooth, 0, mode = 'mirror')
        smooth_spectrum_lamp =  signal.savgol_filter(spectrum_lamp, window_smooth, 0, mode = 'mirror')

        normalized_spectrum_lamp = smooth_spectrum_lamp/max(smooth_spectrum_lamp)
        
        spectrum_NP_normalized = smooth_spectrum_NP/normalized_spectrum_lamp
        
        return londa, spectrum_NP_normalized
    
    def interpolated_lamp(self, calibration, lamp):

        lower_lambda = calibration[0]
        upper_lambda = calibration[-1]
        step = len(calibration)
        
        wavelength_lamp = lamp[0]
        spectrum_lamp = lamp[1]

        wavelength_new = np.linspace(lower_lambda, upper_lambda, step)

        desired_range = np.where((wavelength_lamp>=lower_lambda) & (wavelength_lamp<=upper_lambda))
        wavelength_lamp = wavelength_lamp[desired_range]
        spectrum_lamp = spectrum_lamp[desired_range]

        new_lamp_spectrum = np.interp(wavelength_new, wavelength_lamp, spectrum_lamp)

        return new_lamp_spectrum

    @pyqtSlot(float, float)
    def filter_parameters_wavelength(self, lower_wavelength, upper_wavelength):

        self.lower_wavelength = lower_wavelength
        self.upper_wavelength = upper_wavelength

    def find_max_wavelength(self, wavelength, spectrum):
        
        desired_range = np.where((wavelength>=self.lower_wavelength) & (wavelength <= self.upper_wavelength))
        desired_wavelength = wavelength[desired_range]
        desired_spectrum = spectrum[desired_range]
        
        index_max_wavelength = np.argmax(desired_spectrum)
        wavelength_max = desired_wavelength[index_max_wavelength]
            
        return wavelength_max
    
    def find_integrate_spectrum(self, wavelength, spectrum):
        
        desired_range = np.where((wavelength>=self.lower_wavelength) & (wavelength <= self.upper_wavelength))
        desired_spectrum = spectrum[desired_range]
        integrate_spectrum = np.sum(desired_spectrum)
        
        return integrate_spectrum
   
    def save_line_spectrum(self, wavelength, profile, profile_bkg, step):

        filepath = self.new_folder
        
        filename =  "Line_Spectrum_step_%04d.txt"%(int(step))
        full_filename = os.path.join(filepath, filename)
        np.savetxt(full_filename, np.array(profile), fmt='%.3f')
        
        filename_bkg =  "Background_Line_Spectrum_step_%04d.txt"%(int(step))
        full_filename_bkg = os.path.join(filepath, filename_bkg)
        np.savetxt(full_filename_bkg, np.array(profile_bkg), fmt='%.3f')
        
        print(datetime.now(), '[PySpectrum]', 'Save spectrum')
        
    def save_fit_spectrum(self, wavelength, profile, best_parameters, step):

        filepath = self.new_folder
        
        filename =  "FitSpectrum_step_%04d.txt"%(int(step))
        full_filename = os.path.join(filepath, filename)
        np.savetxt(full_filename, np.array([wavelength, profile]).T, fmt='%.4f')
        
        filename_parameters =  "Parameters_FitSpectrum_step_%04d.txt"%(int(step))
        full_filename_p = os.path.join(filepath, filename_parameters)
        header_txt = 'I_spr, width_spr, londa_spr, I_649nm, I_702m, C'
        np.savetxt(full_filename_p, np.array(best_parameters).T, fmt='%.4f', delimiter = ',', header = header_txt)
        
     #   print(datetime.now(), '[PySpectrum]', 'Save Fit Lorentz spectrum and best parameters.')
        
    def save_fitpoly_spectrum(self, wavelength, profile, data_max_wavelength, step):

        filepath = self.new_folder
        
        filename =  "PolySpectrum_step_%04d.txt"%(int(step))
        full_filename = os.path.join(filepath, filename)
        np.savetxt(full_filename, np.array([wavelength, profile]).T,fmt='%.4f')
        
        filename_parameters =  "Max_PolySpectrum_step_%04d.txt"%(int(step))
        full_filename_p = os.path.join(filepath, filename_parameters)
        header_txt = 'Time (s), Max wavelength (nm)'
        np.savetxt(full_filename_p, np.array(data_max_wavelength).T, fmt='%.4f', delimiter = ',', header = header_txt)
        
     #   print(datetime.now(), '[PySpectrum]', 'Save Fit Poly spectrum and best parameters.')
        
    @pyqtSlot(str)    
    def set_wavelength_window(self, mode_grating):
        
        if mode_grating == nameGrating[0]:
            wavelength_window = 103 #nm, ventana estimativa
            print(datetime.now(), '[Step and Glue] wavelength window (nm) = ', wavelength_window)

        elif mode_grating == nameGrating[1]:
            wavelength_window = 12 #nm, ventana estimativa
            print(datetime.now(), '[Step and Glue] wavelength window (nm) = ', wavelength_window)
            
        self.wavelength_window = wavelength_window
   

    @pyqtSlot(list, float)
    def numbers_of_steps(self, parameters, exposure_time):
        
        self.mode_printing = 'none'

        self.exposure_time = exposure_time

        self.first_lambda = parameters[0]
        self.last_lambda = parameters[1]
        self.overlap = parameters[2]
        
        Nstep = (self.last_lambda- self.first_lambda)/self.wavelength_window
        
        first_wavelength = self.first_lambda
        last_wavelength = self.last_lambda
        
        self.measurment_spectrum(Nstep, first_wavelength, last_wavelength, self.wavelength_window, self.overlap)
    
    def measurment_spectrum(self, Nstep, first_wavelength, last_wavelength, wavelength_window, overlap):
        
        if self.myAndor.status == ('Acquisition in progress.'):
            self.myAndor.wait_for_acquisition()  
            self.myAndor.abort_acquisition()
        
        self.step = 1

        if Nstep > 1:
           self.measurment_spectrum_Nstep(first_wavelength, last_wavelength, wavelength_window, overlap)
        else:
           self.measurment_spectrum_1step(first_wavelength, last_wavelength)
           
    def measurment_spectrum_1step(self, first_wavelength, last_wavelength):
        
        #self.myAndor.shutter(1, 1, 0, 0, 1)
        
        Wavelength = (last_wavelength + first_wavelength)/2

        calibration = self.set_wavelength(Wavelength) 
        image = self.taking_picture(self.exposure_time)
        
        self.line_spectrum(calibration, image)
        
        self.calibration = calibration
        self.image = image
        
       # self.myAndor.shutter(1, 2, 0, 0, 2)
       
        self.continually_acSignal.emit()
        
        return calibration, image
         
    def measurment_spectrum_Nstep(self, first_wavelength, last_wavelength, wavelength_window, overlap):
        
     #   overlap = 0.2 #porcentaje, poner en botones #TODO
        window_overlap = wavelength_window*overlap
            
        inf = first_wavelength
        sup = inf + wavelength_window
        
        list_of_inf = [inf]
        list_of_sup = [sup]
        
        while sup < last_wavelength:
            inf = sup - window_overlap
            sup = inf + wavelength_window
            list_of_inf.append(inf)
            list_of_sup.append(sup)
        
        steps = len(list_of_inf)
         
        stack_of_centers = [(inf + sup)/2 for inf, sup in zip(list_of_inf, list_of_sup)]
        
        print('stack of centers', stack_of_centers)
        
        calibration_Nstep = []
        image_Nstep = np.zeros(1002)
        
     #   self.myAndor.shutter(1, 1, 0, 0, 1)
        
        #for N in range(steps):
        for inf, sup in zip(list_of_inf, list_of_sup):
            
            Wavelength = (inf + sup)/2

            calibration = self.set_wavelength(Wavelength) 
            image = self.taking_picture(self.exposure_time)
            self.line_spectrum(calibration, image)
            
            image_Nstep = np.vstack((image_Nstep, image))
            calibration_Nstep = np.hstack((calibration_Nstep, calibration))
            
            self.step = 1 + self.step
            
    #    self.myAndor.shutter(1, 2, 0, 0, 2)
  
        self.calibration = calibration_Nstep
        self.image = image_Nstep[1:]
        
        self.imageSignal.emit(image_Nstep)
        
        wavelength, spectrum, spectrum_bkg = self.line_spectrum_parameters(self.center_row, self.spot_size, self.center_bkg)
        
        self.continually_acSignal.emit()
        
        if self.mode_printing == 'none':
            
            new_folder = self.create_folder(self.file_path, steps)
            os.makedirs(new_folder)
        
            self.new_folder = new_folder
            self.save_calibration_spectrum(self.calibration, self.step-1)
            self.save_picture_spectrum(self.image, self.step-1)
            self.save_line_spectrum(wavelength, spectrum, spectrum_bkg, self.step-1)
                
        elif self.mode_printing == 'luminescence_steps':
            
            new_folder = self.folder_luminescence
            os.makedirs(new_folder)
        
            self.new_folder = new_folder
            self.save_calibration_spectrum(self.calibration, self.step-1)
            self.save_picture_spectrum(self.image, self.step-1)
            self.save_line_spectrum(wavelength, spectrum, spectrum_bkg, self.step-1)
            
            self.luminescence_steps_finish_Signal.emit()
            
        self.step = 1
            
        
    def create_folder(self, file_path, step):
        """ Crea una carpeta para este archivo particular."""

        timestr = time.strftime("%Y%m%d-%H%M%S")
        new_folder = os.path.join(file_path,  timestr + "_" + "Spectrum_Measurment_step_%02d"%(int(step)))   
        
        return new_folder
    
    @pyqtSlot(bool, float, float)
    def liveview(self, livebool, Wavelength, exposure_time):
        
        if livebool:
            
           calibration = self.set_wavelength(Wavelength)
           self.calibration = calibration
           
           self.exposure_time = exposure_time
           
           self.start_liveview()
           
        else:
            
           self.stop_liveview()
        
    def start_liveview(self):
        
        if self.myAndor.status == ('Acquisition in progress.'):
            self.myAndor.wait_for_acquisition()  
            self.myAndor.abort_acquisition()
        
        self.myAndor.set_exposure_time(self.exposure_time)
     
        self.myAndor.acquisition_mode = 'Run till abort'
      #  self.myAndor.shutter(1, 1 , 0, 0, 1) # opens both shutter

        print(datetime.now(), '[Camera] Acquisition mode = {}'.format(self.myAndor.acquisition_mode))
        print(datetime.now(), '[Camera] Status = {}'.format(self.myAndor.status))
        print(datetime.now(),'Start liveview')
        print('[Camera] Exposure time = {} s'.format(self.exposure_time))

        self.myAndor.start_acquisition()       
        self.myAndor.wait_for_acquisition()  
  
        #image = self.myAndor.most_recent_image16(self.shape)
        self.image = np.transpose(self.myAndor.most_recent_image16(self.shape))
        self.imageSignal.emit(self.image) 
        
        wavelength, spectrum_NP, spectrum_bkg = self.line_spectrum_parameters(self.center_row, self.spot_size, self.center_bkg )
        
        self.time_axis = []
        self.n = 1
        step_time = self.exposure_time*self.n
        self.time_axis.append(step_time)
        
        self.max_wavelength_axis = []
        max_wavelength = self.find_max_wavelength(wavelength, spectrum_NP)
        self.max_wavelength_axis.append(max_wavelength)
        
        self.integrate_spectrum_axis = []
        integrate_spectrum = self.find_integrate_spectrum(wavelength, spectrum_NP)
        self.integrate_spectrum_axis.append(integrate_spectrum)
        
        data= [self.time_axis, self.max_wavelength_axis]
        self.max_wave_Signal.emit(data)
        
        data_integrate = [self.time_axis, self.integrate_spectrum_axis]
        self.integrate_Signal.emit(data_integrate)
        
        self.londa_spr_axis = []
        self.time_axis_2 = []
        
        if self.fit_raman_water:
    
            self.time_axis_2.append(step_time) 
            self.londa_spr_axis.append(self.londa_spr)
            data_fit= [self.time_axis_2, self.londa_spr_axis]
            self.londa_spr_Signal.emit(data_fit)
            
            print('From fit raman, long lspr:', self.londa_spr)
            
        self.max_wave_poly_axis = []
        self.time_axis_3 = []
        
        if self.fit_poly:
    
            self.time_axis_3.append(step_time) 
            self.max_wave_poly_axis.append(self.max_wavelength_poly)
            data_fit= [self.time_axis_3, self.max_wave_poly_axis]
            self.max_wave_poly_Signal.emit(data_fit)
            
            print('From fit poly, max wavelength:', self.max_wavelength_poly)
            
        self.viewTimer.start(1.5*self.exposure_time*10**3) # ms  , DON'T USE time.sleep() inside the update()
        
    def update_view(self):
        """ Image update while in Liveview mode """
        #image = self.myAndor.most_recent_image16(self.shape)
        
        self.n = self.n+1
        
        self.image = np.transpose(self.myAndor.most_recent_image16(self.shape))
        self.imageSignal.emit(self.image)
        
        wavelength, spectrum_NP, spectrum_bkg = self.line_spectrum_parameters(self.center_row, self.spot_size, self.center_bkg )
        
        #if self.normalized_lamp_bool:
        
        step_time = self.n*1.5*self.exposure_time
        max_wavelength = self.find_max_wavelength(wavelength, spectrum_NP)
        integrate_spectrum = self.find_integrate_spectrum(wavelength, spectrum_NP)
             
        self.time_axis.append(step_time)
        self.max_wavelength_axis.append(max_wavelength)
        self.integrate_spectrum_axis.append(integrate_spectrum)
        
        data= [self.time_axis, self.max_wavelength_axis]
        self.max_wave_Signal.emit(data)
                
        data_integrate = [self.time_axis, self.integrate_spectrum_axis]
        self.integrate_Signal.emit(data_integrate)
            
        if self.fit_raman_water:
    
            self.time_axis_2.append(step_time) 
            self.londa_spr_axis.append(self.londa_spr)
            data_fit= [self.time_axis_2, self.londa_spr_axis]
            self.londa_spr_Signal.emit(data_fit)
            
            print('From fit raman, long lspr:', self.londa_spr)
            
        if self.fit_poly:
    
            self.time_axis_3.append(step_time) 
            self.max_wave_poly_axis.append(self.max_wavelength_poly)
            data_fit= [self.time_axis_3, self.max_wave_poly_axis]
            self.max_wave_poly_Signal.emit(data_fit)
            
            print('From fit poly, max wavelength:', self.max_wavelength_poly)
    
        
    def stop_liveview(self):
        
        if self.myAndor.status == ('Acquisition in progress.'):
            self.myAndor.wait_for_acquisition()  
            self.myAndor.abort_acquisition()
            
        self.viewTimer.stop()
     #   self.myAndor.shutter(1, 2, 0, 0, 2) 
        print(datetime.now(), 'Stop liveview')
        
        self.continually_acSignal.emit()
        
    @pyqtSlot(bool, float, float)
    def REC_liveview(self, RECbool, Wavelength, exposure_time):
        
        if RECbool:
          
           calibration = self.set_wavelength(Wavelength)
           self.calibration = calibration
           
           self.exposure_time = exposure_time

           self.mode_printing = 'none'
           timestr = time.strftime("%Y%m%d-%H%M%S")
           new_folder = os.path.join(self.file_path,  timestr + "_" + "Liveview_Spectrum")
           self.start_REC_liveview(self.mode_printing, new_folder)
           
        else:
            
           self.stop_REC_liveview()
           
    #@pyqtSlot(str, str)
    def start_REC_liveview(self, mode_printing, new_folder):
        
        if self.myAndor.status == ('Acquisition in progress.'):
            self.myAndor.wait_for_acquisition()  
            self.myAndor.abort_acquisition()
            
        self.myAndor.set_exposure_time(self.exposure_time)
  
        self.signal_stop = False
        
        self.mode_printing = mode_printing
        
        os.makedirs(new_folder)
        self.new_folder = new_folder
        
        filename = "Calibration_Shamrock_Spectrum.txt"
        full_filename = os.path.join(new_folder, filename)
        np.savetxt(full_filename, np.array(self.calibration), fmt='%.4f')
        print(datetime.now(), '[PySpectrum]', 'Save Calibration spectrum')
     
        self.myAndor.acquisition_mode = 'Run till abort'
        #self.myAndor.acquisition_mode = 'Single Scan'
       # self.myAndor.shutter(1, 1 , 0, 0, 1) # opens both shutter

        print(datetime.now(), '[Camera] Acquisition mode = {}'.format(self.myAndor.acquisition_mode))
        print(datetime.now(), '[Camera] Status = {}'.format(self.myAndor.status))
        print(datetime.now(),'Start REC liveview')
        print('[Camera] Exposure time = {} s'.format(self.exposure_time))

        self.myAndor.start_acquisition()       
        self.myAndor.wait_for_acquisition()   
        
        self.n = 1
  
        #image = self.myAndor.most_recent_image16(self.shape)
        self.image = np.transpose(self.myAndor.most_recent_image16(self.shape))
        self.imageSignal.emit(self.image) 
        self.save_picture_spectrum(self.image, self.n)
        
        wavelength, spectrum_NP, spectrum_bkg = self.line_spectrum_parameters(self.center_row, self.spot_size, self.center_bkg )
        self.save_line_spectrum(wavelength, spectrum_NP, spectrum_bkg, self.n)
        
        self.time_axis = []
        step_time = self.exposure_time*self.n
        self.time_axis.append(step_time)
            
        self.max_wavelength_axis = []
        max_wavelength = self.find_max_wavelength(wavelength, spectrum_NP)
        self.max_wavelength_axis.append(max_wavelength)
        
        self.integrate_spectrum_axis = []
        integrate_spectrum = self.find_integrate_spectrum(wavelength, spectrum_NP)
        self.integrate_spectrum_axis.append(integrate_spectrum)

        self.londa_spr_axis = []
        self.time_axis_2 = []
        
        if self.fit_raman_water:
            self.save_fit_spectrum(self.fit_wavelength, self.fit_spectrum, self.fit_parameters, self.n)
            self.time_axis_2.append(step_time) 
            self.londa_spr_axis.append(self.londa_spr)
            data_fit= [self.time_axis_2, self.londa_spr_axis]
            self.londa_spr_Signal.emit(data_fit)
            
            print('From fit raman, long lspr:', self.londa_spr)
            
        self.max_wave_poly_axis = []
        self.time_axis_3 = []
        
        if self.fit_poly:
            self.save_fitpoly_spectrum(self.fitpoly_wavelength, self.fitpoly_spectrum, [step_time, self.max_wavelength_poly], self.n)
            self.time_axis_3.append(step_time) 
            self.max_wave_poly_axis.append(self.max_wavelength_poly)
            data_fit= [self.time_axis_3, self.max_wave_poly_axis]
            self.max_wave_poly_Signal.emit(data_fit)
            
            print('From fit poly, max wavelength:', self.max_wavelength_poly)
        
        data= [self.time_axis, self.max_wavelength_axis]
        self.max_wave_Signal.emit(data)
        
        data_integrate = [self.time_axis, self.integrate_spectrum_axis]
        self.integrate_Signal.emit(data_integrate)

        self.viewRECTimer.start(1.5*self.exposure_time*10**3) # ms  , DON'T USE time.sleep() inside the update()
        
    def update_REC_view(self):
        """ Image update while in Liveview mode """
        #image = self.myAndor.most_recent_image16(self.shape)
        
        self.n = self.n+1
        
        self.image = np.transpose(self.myAndor.most_recent_image16(self.shape))
        self.imageSignal.emit(self.image)
        self.save_picture_spectrum(self.image, self.n)
        
        wavelength, spectrum, spectrum_bkg = self.line_spectrum_parameters(self.center_row, self.spot_size, self.center_bkg )
        self.save_line_spectrum(wavelength, spectrum, spectrum_bkg, self.n)
        
        step_time = self.n*1.5*self.exposure_time
        self.time_axis.append(step_time)
        
        max_wavelength = self.find_max_wavelength(wavelength, spectrum) 
        self.max_wavelength_axis.append(max_wavelength)
        
        integrate_spectrum = self.find_integrate_spectrum(wavelength, spectrum)
        self.integrate_spectrum_axis.append(integrate_spectrum)
        
        if self.fit_raman_water:
            self.save_fit_spectrum(self.fit_wavelength, self.fit_spectrum, self.fit_parameters, self.n)
            self.time_axis_2.append(step_time) 
            self.londa_spr_axis.append(self.londa_spr)
            data_fit= [self.time_axis_2, self.londa_spr_axis]
            self.londa_spr_Signal.emit(data_fit)
            
            print('From fit raman, long lspr:', self.londa_spr)
        
        if self.fit_poly:
            self.save_fitpoly_spectrum(self.fitpoly_wavelength, self.fitpoly_spectrum, [step_time, self.max_wavelength_poly], self.n)
            self.time_axis_3.append(step_time) 
            self.max_wave_poly_axis.append(self.max_wavelength_poly)
            data_fit= [self.time_axis_3, self.max_wave_poly_axis]
            self.max_wave_poly_Signal.emit(data_fit)
            
            print('From fit poly, max wavelength:', self.max_wavelength_poly)
        
        data= [self.time_axis, self.max_wavelength_axis]
        self.max_wave_Signal.emit(data)
        
        data_integrate = [self.time_axis, self.integrate_spectrum_axis]
        self.integrate_Signal.emit(data_integrate)
        
        if self.mode_printing == 'growth':
            
            if self.fit_poly:
                self.umbral_Signal_growth.emit(self.max_wavelength_poly)
                
            if self.fit_raman_water and not self.fit_poly:
                self.umbral_Signal_growth.emit(self.londa_spr)
                
            if not self.fit_poly and not self.fit_raman_water:
                self.umbral_Signal_growth.emit(max_wavelength)
            
    @pyqtSlot()
    def stop_REC_liveview(self):
        
        if not self.signal_stop: 
            self.viewRECTimer.stop()
            
            if self.myAndor.status == ('Acquisition in progress.'):
                self.myAndor.wait_for_acquisition()  
                self.myAndor.abort_acquisition()
                
         #   self.myAndor.shutter(1, 2, 0, 0, 2) 
            print(datetime.now(), 'Stop REC liveview')
            
            self.signal_stop = True
            
            self.continually_acSignal.emit()
            
            
    @pyqtSlot(bool, float, float, int)
    def REC_liveview_kinetics(self, RECbool, Wavelength, exposure_time, n_kinetics):
        
        if RECbool:
            
           calibration = self.set_wavelength(Wavelength)
           self.calibration = calibration
           
           self.exposure_time = exposure_time
           
           self.n_kinetics = n_kinetics
    
           self.mode_printing = 'none'
           timestr = time.strftime("%Y%m%d-%H%M%S")
           new_folder = os.path.join(self.file_path,  timestr + "_" + "Kinetics_Liveview_Spectrum")
           self.start_REC_liveview_kinetics(self.mode_printing, new_folder)
           
        else:
            
           self.stop_REC_liveview_kinetics()
           
    @pyqtSlot(str, str)
    def start_REC_liveview_kinetics(self, mode_printing, new_folder):
        
        if self.myAndor.status == ('Acquisition in progress.'):
            self.myAndor.wait_for_acquisition()  
            self.myAndor.abort_acquisition()
            
        self.myAndor.set_exposure_time(self.exposure_time)
        
        self.signal_stop_kinetics = False
        
        self.mode_printing = mode_printing
        
        os.makedirs(new_folder)
        self.new_folder = new_folder
        
        filename = "Calibration_Shamrock_Spectrum.txt"
        full_filename = os.path.join(new_folder, filename)
        np.savetxt(full_filename, np.array(self.calibration), fmt='%.4f')
        print(datetime.now(), '[PySpectrum]', 'Save Calibration spectrum')
     
        self.myAndor.acquisition_mode = 'Kinetics'
       # self.myAndor.shutter(1, 1 , 0, 0, 1) # opens both shutter
       
        self.myAndor.free_int_mem()
        self.myAndor.acquisition_mode = 'Kinetics'
        self.myAndor.set_n_kinetics(int(self.n_kinetics))

        print(datetime.now(), '[Camera] Acquisition mode = {}'.format(self.myAndor.acquisition_mode))
        print(datetime.now(), '[Camera] Status = {}'.format(self.myAndor.status))
        print(datetime.now(),'Start REC liveview kinetics')
        print('[Camera] Exposure time = {} s'.format(self.exposure_time))
        print('[Camera] Number Kinetics Serial = {}'.format(self.n_kinetics))
        
        self.myAndor.start_acquisition()
        self.timer_initial = ptime.time() 
        
        time.sleep(1.5*self.exposure_time)
  
        i, self.j = self.myAndor.new_images_index
        newImages = self.myAndor.images16(i, self.j, self.shape,
                                        1, self.n_kinetics)
        
        print('Kinetcis Serie Numero de foto', self.j)
        
        self.image = np.transpose(newImages[-1])
    
        self.imageSignal.emit(self.image) 
                
        self.n = 1
     #   self.save_picture_spectrum(self.image, self.n)
        
        wavelength, spectrum_NP, spectrum_bkg = self.line_spectrum_parameters(self.center_row, self.spot_size, self.center_bkg )
        self.save_line_spectrum(wavelength, spectrum_NP, spectrum_bkg, self.n)
        
        self.time_axis = []
        #step_time = self.exposure_time*self.n
        step_time = round(ptime.time() - self.timer_initial, 2)
        self.time_axis.append(step_time)
            
        self.max_wavelength_axis = []
        max_wavelength = self.find_max_wavelength(wavelength, spectrum_NP)
        self.max_wavelength_axis.append(max_wavelength)
        
        self.integrate_spectrum_axis = []
        integrate_spectrum = self.find_integrate_spectrum(wavelength, spectrum_NP)
        self.integrate_spectrum_axis.append(integrate_spectrum)
        
        self.londa_spr_axis = []
        self.time_axis_2 = []
        
        if self.fit_raman_water:
            self.save_fit_spectrum(self.fit_wavelength, self.fit_spectrum, self.fit_parameters, self.n)
            self.time_axis_2.append(step_time) 
            self.londa_spr_axis.append(self.londa_spr)
            data_fit= [self.time_axis_2, self.londa_spr_axis]
            self.londa_spr_Signal.emit(data_fit)
            
            print('From fit raman, long lspr:', self.londa_spr)
            
        self.max_wave_poly_axis = []
        self.time_axis_3 = []
        
        if self.fit_poly:
            self.save_fitpoly_spectrum(self.fitpoly_wavelength, self.fitpoly_spectrum,  [step_time, self.max_wavelength_poly], self.n)
            self.time_axis_3.append(step_time) 
            self.max_wave_poly_axis.append(self.max_wavelength_poly)
            data_fit= [self.time_axis_3, self.max_wave_poly_axis]
            self.max_wave_poly_Signal.emit(data_fit)
            
            print('From fit poly, max wavelength:', self.max_wavelength_poly)
        
        data= [self.time_axis, self.max_wavelength_axis]
        self.max_wave_Signal.emit(data)
        
        data_integrate = [self.time_axis, self.integrate_spectrum_axis]
        self.integrate_Signal.emit(data_integrate)

     #   self.viewRECTimer_kinetics.start(1.5*self.exposure_time*10**3) # ms  , DON'T USE time.sleep() inside the update()
        self.viewRECTimer_kinetics.start(self.exposure_time*10**3) # ms  , DON'T USE time.sleep() inside the update()
        
    def update_REC_view_kinetics(self):
        """ Image update while in Liveview mode """
        
        if self.j < self.n_kinetics and not self.signal_stop_kinetics:
            
            self.n = self.n+1
       
            i, self.j = self.myAndor.new_images_index
            newImages = self.myAndor.images16(i, self.j, self.shape,
                                        1, self.n_kinetics)
        
            print('Kinetcis Serie Numero de foto', self.j)
       
            self.image = np.transpose(newImages[-1])
            self.imageSignal.emit(self.image) 
            
         #   self.save_picture_spectrum(self.image, self.n)
            
            wavelength, spectrum, spectrum_bkg = self.line_spectrum_parameters(self.center_row, self.spot_size, self.center_bkg )
            self.save_line_spectrum(wavelength, spectrum, spectrum_bkg, self.n)
            
        #    step_time = self.n*self.exposure_time
            step_time = round(ptime.time() - self.timer_initial, 2)
            self.time_axis.append(step_time)
            
            max_wavelength = self.find_max_wavelength(wavelength, spectrum) 
            self.max_wavelength_axis.append(max_wavelength)
            
            integrate_spectrum = self.find_integrate_spectrum(wavelength, spectrum)
            self.integrate_spectrum_axis.append(integrate_spectrum)
        
            if self.fit_raman_water:
                self.save_fit_spectrum(self.fit_wavelength, self.fit_spectrum, self.fit_parameters, self.n)
                self.time_axis_2.append(step_time) 
                self.londa_spr_axis.append(self.londa_spr)
                data_fit= [self.time_axis_2, self.londa_spr_axis]
                self.londa_spr_Signal.emit(data_fit)
                
                print('From fit raman, long lspr:', self.londa_spr)
            
            if self.fit_poly:
                self.save_fitpoly_spectrum(self.fitpoly_wavelength, self.fitpoly_spectrum, [step_time, self.max_wavelength_poly], self.n)
                self.time_axis_3.append(step_time) 
                self.max_wave_poly_axis.append(self.max_wavelength_poly)
                data_fit= [self.time_axis_3, self.max_wave_poly_axis]
                self.max_wave_poly_Signal.emit(data_fit)
                
                print('From fit poly, max wavelength:', self.max_wavelength_poly)
            
            data= [self.time_axis, self.max_wavelength_axis]
            self.max_wave_Signal.emit(data)
            
            data_integrate = [self.time_axis, self.integrate_spectrum_axis]
            self.integrate_Signal.emit(data_integrate)
                
            if self.mode_printing == 'growth':
                
                if self.fit_poly:
                    self.umbral_Signal_growth.emit(self.max_wavelength_poly)
                    
                if self.fit_raman_water and not self.fit_poly:
                    self.umbral_Signal_growth.emit(self.londa_spr)
                    
                if not self.fit_poly and not self.fit_raman_water:
                    self.umbral_Signal_growth.emit(max_wavelength)
                    
        else:
            
            self.stop_REC_liveview_kinetics()
            
    @pyqtSlot()
    def stop_REC_liveview_kinetics(self):
        
        if not self.signal_stop_kinetics: 

            self.viewRECTimer_kinetics.stop()
            
            if self.myAndor.status == ('Acquisition in progress.'):
                self.myAndor.wait_for_acquisition()  
                self.myAndor.abort_acquisition()
                
         #   self.myAndor.shutter(1, 2, 0, 0, 2) 
            print(datetime.now(), 'Stop REC liveview kinetics')
            
            self.signal_stop_kinetics = True
            
            self.continually_acSignal.emit()
            
            
    @pyqtSlot(str, str)
    def luminescence_numbers_of_steps(self, mode_printing, save_folder):
        
        self.folder_luminescence = save_folder
        self.mode_printing = mode_printing
        
        Nstep = (self.last_lambda- self.first_lambda)/self.wavelength_window
        
        first_wavelength = self.first_lambda
        last_wavelength = self.last_lambda
        
        self.measurment_spectrum(Nstep, first_wavelength, last_wavelength, self.wavelength_window, self.overlap)
        
                   
    @pyqtSlot(bool)
    def continually_acquisition_change(self, flag):
        
        if flag:
            
            status = self.myAndor.status
    
            if status == ('Camera is idle, waiting for instructions.'):
            
               self.myAndor.acquisition_mode = 'Run till abort'
               self.myAndor.start_acquisition()
               self.myAndor.wait_for_acquisition()
                
             #  self.continuallyTimer.start(1.5*self.exposure_time*10**3) # cada tantos s 
               print(datetime.now(), '[Camera] WARNING: Start Continually Acquisition.')
               
               self.mode_continually_acquisition = True
               
            else:
                
                print(datetime.now(), status)
                self.mode_continually_acquisition = False
        else:
            
            if self.mode_continually_acquisition:
            
              # self.continuallyTimer.stop()
               
               self.myAndor.wait_for_acquisition() 
               self.myAndor.abort_acquisition()
               
               self.mode_continually_acquisition = False
    
               print(datetime.now(), '[Camera] Stop Continually Acquisition.')
               
          
    @pyqtSlot()           
    def continually_acquisition(self):
        
        if self.mode_continually_acquisition  == True:
            
            self.myAndor.acquisition_mode = 'Run till abort'
            self.myAndor.start_acquisition()
            self.myAndor.wait_for_acquisition()
                
         #   self.continuallyTimer.start(1.5*self.exposure_time*10**3) # cada tantos s 
            print(datetime.now(), '[Camera] WARNING: Start Continually Acquisition.')
               
           
   # def continually_acquisition_timer(self):
            
     #   image = np.transpose(self.myAndor.most_recent_image16(self.shape))
      #  wavelength, spectrum = self.line_spectrum(self.calibration, image)
      #  integrate = self.find_integrate_spectrum(wavelength, spectrum)
        
    #    print('[Camera] WARNING: Continually Acquision with Run till abort, exposure time:', self.exposure_time)
       # print'(Integral ROI:', integrate)  
            
  #  @pyqtSlot()    
  #  def close(self):
        
     #   self.continuallyTimer.stop()
     #   print(datetime.now(), '[Camera]: Stop Continually Acquisition.')
        
         
    def make_connection(self, frontend):
        
        frontend.lineparametersSignal.connect(self.line_spectrum_parameters)
        frontend.parameters_filter_waveSignal.connect(self.filter_parameters_wavelength)
        frontend.normalized_lamp_Signal.connect(self.normalized_lamp)
        frontend.fit_raman_Signal.connect(self.fit_signal)
        frontend.fit_poly_Signal.connect(self.fit_signal_poly)
        
        frontend.spectrumSignal.connect(self.measurment_center_spectrum)
        frontend.spectrum_sandg_Signal.connect(self.numbers_of_steps)
        
        frontend.liveSignal.connect(self.liveview)
        frontend.RECSignal.connect(self.REC_liveview)
        frontend.REC_kinetics_Signal.connect(self.REC_liveview_kinetics)
        frontend.continually_acquisitionSignal.connect(self.continually_acquisition_change)
        
        
if __name__ == '__main__':

    app = QtGui.QApplication([])

    gui = Frontend()   
    
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
    
    worker = Backend(myAndor, mySpectrometer)

    worker.make_connection(gui)
    gui.make_connection(worker)

    
    stepandglueThread = QtCore.QThread()
    worker.moveToThread(stepandglueThread)
    worker.viewTimer.moveToThread(stepandglueThread)
    worker.viewRECTimer.moveToThread(stepandglueThread)
    worker.viewRECTimer_kinetics.moveToThread(stepandglueThread)
    worker.viewTimer.timeout.connect(worker.update_view) 
    worker.viewRECTimer.timeout.connect(worker.update_REC_view)   
    worker.viewRECTimer_kinetics.timeout.connect(worker.update_REC_view_kinetics)
    stepandglueThread.start()

    gui.show()
    app.exec_()