# -*- coding: utf-8 -*-
"""
Created on Thu Apr  4 11:10:29 2019

@author: Luciana
"""

import os
import time
from datetime import datetime

from tkinter import filedialog
import tkinter as tk
import numpy as np

from pyqtgraph.Qt import QtGui, QtCore
from pyqtgraph.dockarea import DockArea, Dock
from PyQt5.QtCore import pyqtSignal, pyqtSlot

from pyqtgraph.console import ConsoleWidget

import nidaqmx
from Instrument_nidaqmx import initial_nidaqmx

from pipython import GCSDevice
import Instrument_PI

from ccd import CCD

from Shamrock import Shamrock
from Instrument_Shamrock import DEVICE

import Camera
import Spectrum
import StepandGlue
import Confocal_Spectrum
#import Confocal_Spectrum_Fast

import Nanopositioning
import Cursor
import Shutters

import Confocal
import Trace
import Focus

import Luminescence
import Growth
import Luminescence_steps

import Printing
import Dimers

class Frontend(QtGui.QMainWindow):
    
    selectDirSignal = pyqtSignal()
    createDirSignal = pyqtSignal()
    openDirSignal = pyqtSignal()
    loadpositionSignal = pyqtSignal()
    loadgridSignal = pyqtSignal()
    closeSignal = pyqtSignal()

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.setWindowTitle('PySpectrum')

        self.cwidget = QtGui.QWidget()
        self.setCentralWidget(self.cwidget)
        self.setGeometry(30, 30, 500, 500)
        

        # Create de file location
        localDirAction = QtGui.QAction('&Select Dir (Ctrl+A)', self)
        localDirAction.setStatusTip('Select the work folder')
        localDirAction.triggered.connect(self.get_selectDir)

        # Create de create daily directory
        dailyAction = QtGui.QAction('&Create daily Dir (Ctrl+S)', self)
        dailyAction.setStatusTip('Create the work folder')
        dailyAction.triggered.connect(self.get_create_daily_directory)
        
        # Open directory
        openAction = QtGui.QAction('&Open Dir (Ctrl+D)', self)
        openAction.setStatusTip('Open document')
        openAction.triggered.connect(self.get_openDir)
        
        # Load las position
        load_position_Action = QtGui.QAction('&Load Last position', self)
        load_position_Action.setStatusTip('Load last position when PySpectrum closed.')
        load_position_Action.triggered.connect(self.load_last_position)
        
        QtGui.QShortcut(
            QtGui.QKeySequence('Ctrl+A'), self, self.get_selectDir)
       
        QtGui.QShortcut(
            QtGui.QKeySequence('Ctrl+S'), self, self.get_create_daily_directory)
         
        QtGui.QShortcut(
            QtGui.QKeySequence('Ctrl+D'), self, self.get_openDir)

    # Create a save dock action
        save_docks_Action = QtGui.QAction(QtGui.QIcon('algo.png'), '&Save Docks', self)
        save_docks_Action.setStatusTip('Saves the Actual Docks configuration')
        save_docks_Action.triggered.connect(self.save_docks)

    # Create a restore dock action
        load_docks_Action = QtGui.QAction(QtGui.QIcon('algo.png'), '&Restore Docks', self)
        load_docks_Action.setStatusTip('Load a previous Docks configuration')
        load_docks_Action.triggered.connect(self.load_docks)

    # Open Tools:  Photodiode (confocal, trace, go to maximum), Nanopositioning and Shutters
        tools_Action = QtGui.QAction('&Photodiode, Nanopositioning and Shutters', self)
        tools_Action.triggered.connect(self.tools)

    # Open Tools: Cursor
        tools_cursor_Action = QtGui.QAction('&Cursor', self)
        tools_cursor_Action.triggered.connect(self.tools_cursor)
        
    # Open Tools: Load grid
        load_grid_Action = QtGui.QAction('&Load Grid', self)
        load_grid_Action.triggered.connect(self.load_grid)
        
    # Open Tools: Confocal Spectrum (Zero Order, First Order)
        tools_confocal_spectrum_Action = QtGui.QAction('&Confocal Spectrum', self)
        tools_confocal_spectrum_Action.triggered.connect(self.tools_confocal_spectrum)
        
    # Console Widget
        console_Action = QtGui.QAction('&Console Widget', self)
        console_Action.triggered.connect(self.open_console_widget) 
        self.consoleWidget = ConsoleWidget()

    # Measurment Luminescence
        luminescence_Action = QtGui.QAction('&Do Luminescence', self)
        luminescence_Action.triggered.connect(self.measurement_luminescence)
        
    # Measurment Growth
        growth_Action = QtGui.QAction('&Do Growth', self)
        growth_Action.triggered.connect(self.measurement_growth)
        
     # Measurment Luminescence_steps
        luminescence_steps_Action = QtGui.QAction('&Do Luminescence Steps and Glue', self)
        luminescence_steps_Action.triggered.connect(self.measurement_luminescence_steps)
         
    # Measurment Printing
        printing_Action = QtGui.QAction('&Do Printing', self)
        printing_Action.triggered.connect(self.measurement_printing)
        
    # Measurment Dimers
        dimers_Action = QtGui.QAction('&Do Dimers', self)
        dimers_Action.triggered.connect(self.measurement_dimers)

        
        # Actions in menubar
    
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(localDirAction)
        fileMenu.addAction(openAction)
        fileMenu.addAction(dailyAction)
        fileMenu.addAction(load_position_Action)

        fileMenu2 = menubar.addMenu('&Tools')
        fileMenu2.addAction(tools_Action)
        fileMenu2.addAction(tools_cursor_Action)
        fileMenu2.addAction(load_grid_Action)
        fileMenu2.addAction(tools_confocal_spectrum_Action)
        fileMenu2.addAction(console_Action)
        
        fileMenu3 = menubar.addMenu('&Measurements')
        fileMenu3.addAction(luminescence_Action)
        fileMenu3.addAction(growth_Action)
        fileMenu3.addAction(luminescence_steps_Action)
        fileMenu3.addAction(printing_Action)
        fileMenu3.addAction(dimers_Action)
        
        
        fileMenu4 = menubar.addMenu('&Docks config')
        fileMenu4.addAction(save_docks_Action)
        fileMenu4.addAction(load_docks_Action)

        
        # GUI layout

        grid = QtGui.QGridLayout()
        self.cwidget.setLayout(grid)

        # Dock Area

        dockArea = DockArea()
        grid.addWidget(dockArea)
        
        
        ## Spectrum Shamrock

        spectrumDock = Dock("Shamrock spectrometer")
        self.spectrumWidget = Spectrum.Frontend()
        spectrumDock.addWidget(self.spectrumWidget)
        dockArea.addDock(spectrumDock)

        ## Camera Andor

        cameraDock = Dock("Camera Andor")
        self.cameraWidget = Camera.Frontend()
        cameraDock.addWidget(self.cameraWidget)
        dockArea.addDock(cameraDock, 'right', spectrumDock)
        
        ## Step and Glue Parameters
        
        stepandGlueDock = Dock("Measurment spectrum")
        self.stepandglueWidget = StepandGlue.Frontend()
        stepandGlueDock.addWidget(self.stepandglueWidget)
        dockArea.addDock(stepandGlueDock, 'right', cameraDock)
 
        
        ## Tools: Photodiode, Nanopositioning and Shutters
        
        
        self.toolsWidget = QtGui.QWidget()
        subgrid = QtGui.QGridLayout()
        self.toolsWidget.setLayout(subgrid)
        subdockArea = DockArea()
        subgrid.addWidget(subdockArea)

            ## Photodiode Confocal

        confocal_PH_Dock = Dock("Confocal Photodiode")
        self.confocal_PH_Widget = Confocal.Frontend()
        confocal_PH_Dock.addWidget(self.confocal_PH_Widget)
        subdockArea.addDock(confocal_PH_Dock)
        
            ## Photodiode Trace

        trace_PH_Dock = Dock("Trace Photodiode")
        self.trace_PH_Widget = Trace.Frontend()
        trace_PH_Dock.addWidget(self.trace_PH_Widget)
        subdockArea.addDock(trace_PH_Dock, 'right', confocal_PH_Dock)

            ## Nanopositioning

        nanopositioningDock = Dock("Nanopositioning")
        self.nanopositioningWidget =  Nanopositioning.Frontend()
        nanopositioningDock.addWidget(self.nanopositioningWidget)
        subdockArea.addDock(nanopositioningDock)

            ## Photodiode Focus

        focus_PH_Dock = Dock("Focus Photodiode")
        self.focus_PH_Widget = Focus.Frontend()
        focus_PH_Dock.addWidget(self.focus_PH_Widget)
        subdockArea.addDock(focus_PH_Dock, 'right', nanopositioningDock)
        
             ## Shutters

        shuttersDock = Dock("Shutters and Flipper")
        self.shuttersWidget = Shutters.Frontend()
        shuttersDock.addWidget(self.shuttersWidget)
        subdockArea.addDock(shuttersDock, 'right', focus_PH_Dock)
        

        ## Tools: Cursor
        self.cursorWidget =  Cursor.Frontend()
    

        ## Tools: Confocal Spectrum
        
        self.tools_confocal_spectrum_Widget = QtGui.QWidget()
        subgrid3 = QtGui.QGridLayout()
        self.tools_confocal_spectrum_Widget.setLayout(subgrid3)
        subdockArea3 = DockArea()
        subgrid3.addWidget(subdockArea3)
            
            ## Confocal_Spectrum

        confocalDock = Dock("HyperSpectral Confocal")
        self.confocalSWidget = Confocal_Spectrum.Frontend()
        confocalDock.addWidget(self.confocalSWidget)
        subdockArea3.addDock(confocalDock)

            ## Confocal_Spectrum_Fast

      #  confocal_fast_Dock = Dock("FAST: Confocal First order")
      #  self.confocalS_fast_Widget = Confocal_Spectrum_Fast.Frontend()
      #  confocal_fast_Dock.addWidget(self.confocalS_fast_Widget)
      #  subdockArea3.addDock(confocal_fast_Dock, 'right', confocalDock)

           ## Luminescence

        self.luminescenceWidget =  Luminescence.Frontend()
        
           ## Growth

        self.growthWidget =  Growth.Frontend()
        
            ## Luminescence_steps

        self.luminescence_stepsWidget =  Luminescence_steps.Frontend()
        
            ## Dimers

        self.dimersWidget =  Dimers.Frontend()
        
            ## Printing

        self.printingWidget =  Printing.Frontend()
        
        

        self.make_connection_frontends()


    def get_openDir(self):
        self.openDirSignal.emit()
        
    def get_selectDir(self):
        self.selectDirSignal.emit()
        
    def get_create_daily_directory(self):
        self.createDirSignal.emit()
        
    def load_last_position(self):
        self.loadpositionSignal.emit()

    def save_docks(self):  # Funciones para acomodar los Docks
        self.state = self.dockArea.saveState()

    def load_docks(self):
        self.dockArea.restoreState(self.state)

    def tools(self):

        self.toolsWidget.show()

    def tools_cursor(self):

        self.cursorWidget.show()
        
    def load_grid(self):
        self.loadgridSignal.emit()
        
    def tools_confocal_spectrum(self):
        
        self.tools_confocal_spectrum_Widget.show()
        
        
    def open_console_widget(self):
        
        self.consoleWidget.show()

    def measurement_luminescence(self):
        
        self.luminescenceWidget.show()
        
    def measurement_growth(self):
        
        self.growthWidget.show()
        
    def measurement_luminescence_steps(self):
        
        self.luminescence_stepsWidget.show()
        
        
    def measurement_printing(self):
        
        self.printingWidget.show()
        
    def measurement_dimers(self):
        
        self.dimersWidget.show()
        
         
    def make_connection(self, backend):

        backend.cameraWorker.make_connection(self.cameraWidget)
        backend.spectrumWorker.make_connection(self.spectrumWidget)
        backend.stepandglueWorker.make_connection(self.stepandglueWidget)
        backend.confocalSWorker.make_connection(self.confocalSWidget)
      #  backend.confocalS_fast_Worker.make_connection(self.confocalS_fast_Widget)

        backend.shuttersWorker.make_connection(self.shuttersWidget)
        backend.nanopositioningWorker.make_connection(self.nanopositioningWidget)
        backend.cursorWorker.make_connection(self.cursorWidget)
        
        backend.confocal_PH_Worker.make_connection(self.confocal_PH_Widget)
        backend.focus_PH_Worker.make_connection(self.focus_PH_Widget)
        backend.trace_PH_Worker.make_connection(self.trace_PH_Widget)

        backend.luminescenceWorker.make_connection(self.luminescenceWidget)
        backend.growthWorker.make_connection(self.growthWidget)
        backend.luminescence_stepsWorker.make_connection(self.luminescence_stepsWidget)
        
        backend.printingWorker.make_connection(self.printingWidget)
        backend.dimersWorker.make_connection(self.dimersWidget)
        
        backend.stepandglueWorker.imageSignal.connect(self.cameraWidget.get_image)
        backend.confocalSWorker.imageSignal.connect(self.cameraWidget.get_image)
    #    backend.confocalS_fast_Worker.imageSignal.connect(self.cameraWidget.get_image)

    def make_connection_frontends(self):

        self.stepandglueWidget.show_lineparametersSignal.connect(self.cameraWidget.create_line_horizontal)
        self.stepandglueWidget.lineparametersSignal.connect(self.cameraWidget.line_horizontal)

        self.confocalSWidget.show_filterSignal.connect(self.cameraWidget.create_line_horizontal)
        self.confocalSWidget.spectrum_parameters_filterSignal.connect(self.cameraWidget.line_horizontal)

    #    self.confocalS_fast_Widget.show_filterSignal.connect(self.cameraWidget.create_line_horizontal)
    #    self.confocalS_fast_Widget.spectrum_parameters_filterSignal.connect(self.cameraWidget.line_horizontal)
        

    def closeEvent(self, event):

        reply = QtGui.QMessageBox.question(self, 'Quit', 'Are you sure to quit?',
                                           QtGui.QMessageBox.No |
                                           QtGui.QMessageBox.Yes)
        if reply == QtGui.QMessageBox.Yes:
            print("YES")
            self.closeSignal.emit()
            event.accept()
            self.close()
            
            shuttersThread.exit()
            nanopositioningThread.exit()
          #  traceThread.exit()
            confocalThread.exit()
           # focusThread.exit()
            cameraThread.exit()
            shamrockThread.exit()
            stepandglueThread.exit()
            confocalSpectrumThread.exit()
         #   routineThread.exit()
            
        else:
            event.ignore()
            print("NO")
        
#%%
        
class Backend(QtCore.QObject):
    
    fileSignal = pyqtSignal(str)
    gridSignal = pyqtSignal(str, np.ndarray)
    close_all_instrument_Signal = pyqtSignal()
    
    def __init__(self, pi_device, task_nidaqmx, myAndor, mySpectrometer, *args, **kwargs):
        
        super().__init__(*args, **kwargs)
        
        self.pi_device = pi_device
        
        self.shuttersWorker = Shutters.Backend(task_nidaqmx)
        self.nanopositioningWorker = Nanopositioning.Backend(pi_device)
        self.cursorWorker = Cursor.Backend(pi_device)
        
        self.focus_PH_Worker = Focus.Backend(pi_device, task_nidaqmx)
        self.trace_PH_Worker = Trace.Backend(task_nidaqmx)
        self.confocal_PH_Worker = Confocal.Backend(pi_device, task_nidaqmx)
        
        self.cameraWorker = Camera.Backend(myAndor)
        self.spectrumWorker = Spectrum.Backend(mySpectrometer)
        
        self.stepandglueWorker = StepandGlue.Backend(myAndor, mySpectrometer)
        self.confocalSWorker = Confocal_Spectrum.Backend(pi_device, task_nidaqmx, myAndor, mySpectrometer)
    #    self.confocalS_fast_Worker = Confocal_Spectrum_Fast.Backend(pi_device, task_nidaqmx, myAndor, mySpectrometer)

        self.luminescenceWorker = Luminescence.Backend(pi_device, task_nidaqmx)
        self.growthWorker = Growth.Backend(pi_device, task_nidaqmx)
        self.luminescence_stepsWorker = Luminescence_steps.Backend(pi_device, task_nidaqmx)
        
        self.printingWorker = Printing.Backend(pi_device, task_nidaqmx)
        self.dimersWorker = Dimers.Backend(pi_device, task_nidaqmx)
        
        self.file_path = os.path.abspath("C:\Julian\Data_PySpectrum")  #por default, por si se olvida de crear la carpeta del día
        
        self.make_connection_backends()
        self.make_connection_luminescence()
        self.make_connection_growth()
        self.make_connection_luminescence_steps()
        
        self.make_connection_printing()
        self.make_connection_dimers()
        
    @pyqtSlot()    
    def selectDir(self):
        root = tk.Tk()
        root.withdraw()

        file_path = filedialog.askdirectory()
        if not file_path:
            print("No elegiste nada")
        else:
            self.file_path = file_path
            self.fileSignal.emit(self.file_path)   #Lo reciben los módulos de traza, confocal y printing
             
    @pyqtSlot()  
    def openDir(self):
        os.startfile(self.file_path)
        print('Open: ', self.file_path)
        
    @pyqtSlot()      
    def create_daily_directory(self):
        root = tk.Tk()
        root.withdraw()

        file_path = filedialog.askdirectory()
        if not file_path:
            print("No elegiste nada ==> No crea la carpeta")
        else:
            timestr = time.strftime("%Y-%m-%d")  # -%H%M%S")

            newpath = file_path + "/" + timestr
            if not os.path.exists(newpath):
                os.makedirs(newpath)
                print("Carpeta creada!")
            else:
                print("Ya existe esa carpeta")

            self.file_path = newpath 
            self.fileSignal.emit(self.file_path)
                   
    @pyqtSlot()             
    def load_last_position(self): 
        
        filepath = "C:/Users/CibionPC/Desktop/PySpectrum/"
        name = str(filepath  + "/" + "Last_position.txt")
     
        last_position = np.loadtxt(name)
        print(last_position)
        
        targets = list(last_position)
                
        self.pi_device.MOV(['A', 'B', 'C'], targets)
        time.sleep(0.01)
        
    @pyqtSlot()             
    def load_grid(self):
        
        root = tk.Tk()
        root.withdraw()
        
        name = filedialog.askopenfilename()  
        f = open(name, "r")
        datos = np.loadtxt(name, unpack=True)
        f.close()
        grid_name = 'Load_grid'
       
        self.gridSignal.emit(grid_name, datos)
     
    @pyqtSlot()
    def closeAll(self):
        self.close_all_instrument_Signal.emit()
            
    def make_connection(self, frontend):

        frontend.cameraWidget.make_connection(self.cameraWorker)  
        frontend.stepandglueWidget.make_connection(self.stepandglueWorker)  

        frontend.nanopositioningWidget.make_connection(self.nanopositioningWorker)
        frontend.cursorWidget.make_connection(self.cursorWorker)
        frontend.confocalSWidget.make_connection(self.confocalSWorker)
     #   frontend.confocalS_fast_Widget.make_connection(self.confocalS_fast_Worker)

        frontend.confocal_PH_Widget.make_connection(self.confocal_PH_Worker)
        frontend.focus_PH_Widget.make_connection(self.focus_PH_Worker)
        frontend.trace_PH_Widget.make_connection(self.trace_PH_Worker)

        frontend.luminescenceWidget.make_connection(self.luminescenceWorker)
        frontend.growthWidget.make_connection(self.growthWorker)
        frontend.luminescence_stepsWidget.make_connection(self.luminescence_stepsWorker)
        
        frontend.printingWidget.make_connection(self.printingWorker)    
        frontend.dimersWidget.make_connection(self.dimersWorker)
        
        frontend.selectDirSignal.connect(self.selectDir)
        frontend.openDirSignal.connect(self.openDir)
        frontend.createDirSignal.connect(self.create_daily_directory)
        frontend.loadpositionSignal.connect(self.load_last_position)
        frontend.loadgridSignal.connect(self.load_grid)
        frontend.closeSignal.connect(self.closeAll)

    def make_connection_backends(self):
        
        self.spectrumWorker.gratingSignal.connect(self.stepandglueWorker.set_wavelength_window)

        self.confocalSWorker.scandoneSignal.connect(self.nanopositioningWorker.read_pos)
      #  self.confocalS_fast_Worker.scandoneSignal.connect(self.nanopositioningWorker.read_pos)
        
        self.nanopositioningWorker.read_pos_signal.connect(self.cursorWorker.real_cursor)

        self.focus_PH_Worker.gotomaxdoneSignal.connect(self.nanopositioningWorker.read_pos)
        self.focus_PH_Worker.lockdoneSignal.connect(self.nanopositioningWorker.read_pos)
        self.focus_PH_Worker.autodoneSignal.connect(self.nanopositioningWorker.read_pos)
        self.confocal_PH_Worker.scandoneSignal.connect(self.nanopositioningWorker.read_pos)

        self.luminescenceWorker.grid_move_finishSignal.connect(self.nanopositioningWorker.read_pos)
        self.luminescenceWorker.goSignal.connect(self.nanopositioningWorker.read_pos)
        
        self.growthWorker.grid_move_finishSignal.connect(self.nanopositioningWorker.read_pos)
        self.growthWorker.goSignal.connect(self.nanopositioningWorker.read_pos)
        
        self.luminescence_stepsWorker.grid_move_finishSignal.connect(self.nanopositioningWorker.read_pos)
        self.luminescence_stepsWorker.goSignal.connect(self.nanopositioningWorker.read_pos)
        
        self.printingWorker.grid_move_finishSignal.connect(self.nanopositioningWorker.read_pos)
        self.printingWorker.goSignal.connect(self.nanopositioningWorker.read_pos)
        
        self.dimersWorker.grid_move_finishSignal.connect(self.nanopositioningWorker.read_pos)
        self.dimersWorker.goSignal.connect(self.nanopositioningWorker.read_pos)
        
        self.fileSignal.connect(self.trace_PH_Worker.direction)
        self.fileSignal.connect(self.confocal_PH_Worker.direction)

        self.fileSignal.connect(self.cameraWorker.get_direction)
        self.fileSignal.connect(self.stepandglueWorker.get_direction)
        self.fileSignal.connect(self.confocalSWorker.get_direction)
       # self.fileSignal.connect(self.confocalS_fast_Worker.get_direction)
        
        self.fileSignal.connect(self.luminescenceWorker.grid_direction)
        self.fileSignal.connect(self.growthWorker.grid_direction)
        self.fileSignal.connect(self.luminescence_stepsWorker.grid_direction)
        
        self.fileSignal.connect(self.printingWorker.grid_direction)
        self.fileSignal.connect(self.dimersWorker.grid_direction)
        
        self.gridSignal.connect(self.printingWorker.grid)
        self.gridSignal.connect(self.dimersWorker.grid)
        self.gridSignal.connect(self.growthWorker.grid)
        self.gridSignal.connect(self.luminescenceWorker.grid)
        self.gridSignal.connect(self.luminescence_stepsWorker.grid)
        
       # self.close_all_instrument_Signal.connect(self.stepandglueWorker.close)
        self.close_all_instrument_Signal.connect(self.cameraWorker.close)
        self.close_all_instrument_Signal.connect(self.spectrumWorker.close)
        self.close_all_instrument_Signal.connect(self.nanopositioningWorker.close)
        self.close_all_instrument_Signal.connect(self.shuttersWorker.close)
        
        #conection from continually acquisition
        
        self.stepandglueWorker.continually_acSignal.connect(self.stepandglueWorker.continually_acquisition)
        self.cameraWorker.continually_acSignal.connect(self.stepandglueWorker.continually_acquisition)
        self.confocalSWorker.continually_acSignal.connect(self.stepandglueWorker.continually_acquisition)
    #    self.confocalS_fast_Worker.continually_acSignal.connect(self.stepandglueWorker.continually_acquisition)
        
    def make_connection_luminescence(self):

        self.luminescenceWorker.grid_move_finishSignal.connect(self.luminescenceWorker.grid_autofoco)
        self.luminescenceWorker.grid_autofocusSignal.connect(self.focus_PH_Worker.focus_autocorr_lin_x2)
        self.focus_PH_Worker.autofinishSignal_luminescence.connect(self.luminescenceWorker.grid_finish_autofoco)

        self.luminescenceWorker.grid_scanSignal.connect(self.confocal_PH_Worker.start_scan_routines)
        self.luminescenceWorker.grid_scan_stopSignal.connect(self.confocal_PH_Worker.stop_scan)
        self.confocal_PH_Worker.scanfinishSignal_luminescence.connect(self.luminescenceWorker.grid_center_scan_detect)

        self.luminescenceWorker.grid_spectrumSignal.connect(self.confocalSWorker.start_scan_step_xy)
        self.luminescenceWorker.grid_spectrum_stopSignal.connect(self.confocalSWorker.stop_scan_step_xy)
        self.confocalSWorker.scanfinishSignal_luminescence.connect(self.luminescenceWorker.grid_confocal_spectrum_detect)

       # self.luminescenceWorker.grid_spectrum_fast_Signal.connect(self.confocalS_fast_Worker.start_scan_step_xy)
      #  self.luminescenceWorker.grid_spectrum_stopSignal.connect(self.confocalS_fast_Worker.stop_scan_step_xy)
      #  self.confocalS_fast_Worker.scanfinishSignal_luminescence.connect(self.luminescenceWorker.grid_confocal_spectrum_fast_detect)
  
        self.luminescenceWorker.grid_traceSignal.connect(self.trace_PH_Worker.trace_configuration_routines)
        self.luminescenceWorker.grid_trace_stopSignal.connect(self.trace_PH_Worker.stop_trace_routines)
        
    def make_connection_growth(self):

        self.growthWorker.grid_move_finishSignal.connect(self.growthWorker.grid_autofoco)
        self.growthWorker.grid_autofocusSignal.connect(self.focus_PH_Worker.focus_autocorr_lin_x2)
        self.focus_PH_Worker.autofinishSignal_growth.connect(self.growthWorker.grid_finish_autofoco)

        self.growthWorker.grid_scanSignal.connect(self.confocal_PH_Worker.start_scan_routines)
        self.growthWorker.grid_scan_stopSignal.connect(self.confocal_PH_Worker.stop_scan)
        self.confocal_PH_Worker.scanfinishSignal_growth.connect(self.growthWorker.grid_center_scan_detect)

        self.growthWorker.grid_spectrumSignal.connect(self.stepandglueWorker.start_REC_liveview_kinetics)
        self.stepandglueWorker.umbral_Signal_growth.connect(self.growthWorker.grid_liveview_spectrum_detect)
        self.growthWorker.grid_spectrum_stopSignal.connect(self.stepandglueWorker.stop_REC_liveview_kinetics)
          
        self.growthWorker.grid_traceSignal.connect(self.trace_PH_Worker.trace_configuration_routines)
        self.growthWorker.grid_trace_stopSignal.connect(self.trace_PH_Worker.stop_trace_routines)
        
    def make_connection_luminescence_steps(self):

        self.luminescence_stepsWorker.grid_move_finishSignal.connect(self.luminescence_stepsWorker.grid_autofoco)
        self.luminescence_stepsWorker.grid_autofocusSignal.connect(self.focus_PH_Worker.focus_autocorr_lin_x2)
        self.focus_PH_Worker.autofinishSignal_luminescence_steps.connect(self.luminescence_stepsWorker.grid_finish_autofoco)

        self.luminescence_stepsWorker.grid_scanSignal.connect(self.confocal_PH_Worker.start_scan_routines)
        self.luminescence_stepsWorker.grid_scan_stopSignal.connect(self.confocal_PH_Worker.stop_scan)
        self.confocal_PH_Worker.scanfinishSignal_luminescence_steps.connect(self.luminescence_stepsWorker.grid_center_scan_detect)

        self.luminescence_stepsWorker.grid_spectrumSignal.connect(self.stepandglueWorker.luminescence_numbers_of_steps)
        self.stepandglueWorker.luminescence_steps_finish_Signal.connect(self.luminescence_stepsWorker.grid_step_and_glue_spectrum_detect)
        

    def make_connection_printing(self):
    
        self.printingWorker.grid_move_finishSignal.connect(self.printingWorker.grid_autofoco)
        self.printingWorker.grid_autofocusSignal.connect(self.focus_PH_Worker.focus_autocorr_lin_x2)
        self.focus_PH_Worker.autofinishSignal.connect(self.printingWorker.grid_finish_autofoco)
        
        self.printingWorker.grid_traceSignal.connect(self.trace_PH_Worker.trace_configuration)
        self.trace_PH_Worker.data_printingSignal.connect(self.printingWorker.grid_trace_detect)
        self.printingWorker.grid_trace_stopSignal.connect(self.trace_PH_Worker.stop)
        
        self.printingWorker.grid_detectSignal.connect(self.printingWorker.grid_scan)
        self.printingWorker.grid_scanSignal.connect(self.confocal_PH_Worker.start_scan_routines)
        self.printingWorker.grid_scan_stopSignal.connect(self.confocal_PH_Worker.stop_scan)
        self.confocal_PH_Worker.scanfinishSignal.connect(self.printingWorker.grid_scan_detect)

    def make_connection_dimers(self):

        self.dimersWorker.grid_move_finishSignal.connect(self.dimersWorker.grid_autofoco)
        self.dimersWorker.grid_autofocusSignal.connect(self.focus_PH_Worker.focus_autocorr_lin_x2)
        self.focus_PH_Worker.autofinishSignal_dimers.connect(self.dimersWorker.grid_finish_autofoco)
        
        self.dimersWorker.grid_traceSignal.connect(self.trace_PH_Worker.trace_configuration)
        self.trace_PH_Worker.data_printingSignal_dimers.connect(self.dimersWorker.grid_trace_detect)
        self.dimersWorker.grid_trace_stopSignal.connect(self.trace_PH_Worker.stop)
    
        self.dimersWorker.grid_scanSignal.connect(self.confocal_PH_Worker.start_scan_routines)
        self.dimersWorker.grid_scan_stopSignal.connect(self.confocal_PH_Worker.stop_scan)
        
        self.confocal_PH_Worker.scanfinishSignal_dimers_center.connect(self.dimersWorker.grid_center_scan_detect)
        self.confocal_PH_Worker.scanfinishSignal_dimers_pree.connect(self.dimersWorker.grid_pree_scan_detect)
        self.confocal_PH_Worker.scanfinishSignal_dimers_post.connect(self.dimersWorker.grid_post_scan_detect)

        self.dimersWorker.grid_detectSignal.connect(self.dimersWorker.grid_finish)
  
if __name__ == '__main__':


   #app = QtGui.QApplication([])

    if not QtGui.QApplication.instance():
        app = QtGui.QApplication([])
        open_terminal = True
    else:
     #   print('PySpectrum Open, can use Terminal too.')
        open_terminal = False
        app = QtGui.QApplication.instance() 
        
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
    print(datetime.now(), '[Camera] IDN = {}'.format(myAndor.idn))
    
        ##Shamrock
    
    mySpectrometer = Shamrock()
    inipath = 'C:\\Program Files (x86)\\Andor SOLIS\\SPECTROG.ini'
    mySpectrometer.ShamrockInitialize(inipath)
    ret, serial_number = mySpectrometer.ShamrockGetSerialNumber(DEVICE)
    print(datetime.now(), '[Shmarock] Serial number = {}'.format(serial_number))
    
    worker = Backend(pi_device, task_nidaqmx, myAndor, mySpectrometer)
    
    ## MAKE CONNECTIONS

    gui.make_connection(worker)
    worker.make_connection(gui)
    
    ##THREADS

    ## Shutters laser, flipper's Thread
    
    shuttersThread = QtCore.QThread()
    worker.shuttersWorker.moveToThread(shuttersThread)
    shuttersThread.start()
    
    ## Nanopositioning Thread
    
    nanopositioningThread = QtCore.QThread()
    worker.nanopositioningWorker.moveToThread(nanopositioningThread)
    nanopositioningThread.start()
    
    ## Confocal Photodiode Thread, Trace Photodiode Thread,  Focus Z Photodiode Thread
    
    confocalThread = QtCore.QThread()
    
  #  traceThread = QtCore.QThread()
    worker.trace_PH_Worker.moveToThread(confocalThread)
    worker.trace_PH_Worker.pointtimer.moveToThread(confocalThread)
    worker.trace_PH_Worker.pointtimer.timeout.connect(worker.trace_PH_Worker.trace_update)
    worker.trace_PH_Worker.plot_pointtimer.moveToThread(confocalThread)
    worker.trace_PH_Worker.plot_pointtimer.timeout.connect(worker.trace_PH_Worker.plot_trace_update)
   # traceThread.start()
    
    #gui_traceThread = QtCore.QThread()
    #gui.trace_PH_Widget.moveToThread(traceThread)
    #gui_traceThread.start()
    
    ##
    
  #  focusThread = QtCore.QThread()
    worker.focus_PH_Worker.moveToThread(confocalThread)
   # focusThread.start()
    
    ## 
    
    worker.confocal_PH_Worker.moveToThread(confocalThread)
    worker.confocal_PH_Worker.PDtimer_stepxy.moveToThread(confocalThread)
    worker.confocal_PH_Worker.PDtimer_rampxy.moveToThread(confocalThread)
    worker.confocal_PH_Worker.PDtimer_rampxz.moveToThread(confocalThread)
    worker.confocal_PH_Worker.drifttimer.moveToThread(confocalThread)
    worker.confocal_PH_Worker.PDtimer_stepxy.timeout.connect(worker.confocal_PH_Worker.scan_step_xy)
    worker.confocal_PH_Worker.PDtimer_rampxy.timeout.connect(worker.confocal_PH_Worker.scan_ramp_xy)
    worker.confocal_PH_Worker.PDtimer_rampxz.timeout.connect(worker.confocal_PH_Worker.scan_ramp_xz)
    worker.confocal_PH_Worker.PDtimer_rampyx.timeout.connect(worker.confocal_PH_Worker.scan_ramp_yx)
    worker.confocal_PH_Worker.PDtimer_rampyz.timeout.connect(worker.confocal_PH_Worker.scan_ramp_yz)
    worker.confocal_PH_Worker.drifttimer.timeout.connect(worker.confocal_PH_Worker.drift)
    
    worker.luminescenceWorker.moveToThread(confocalThread)
    worker.growthWorker.moveToThread(confocalThread)
    worker.luminescence_stepsWorker.moveToThread(confocalThread)
    worker.printingWorker.moveToThread(confocalThread)
    worker.dimersWorker.moveToThread(confocalThread)
    
    confocalThread.start()
    
    ## Camera Andor Thread
        
    cameraThread = QtCore.QThread()
    worker.cameraWorker.moveToThread(cameraThread)
    worker.cameraWorker.temperatureTimer.moveToThread(cameraThread)
    worker.cameraWorker.viewTimer.moveToThread(cameraThread)
    worker.cameraWorker.temperatureTimer.timeout.connect(worker.cameraWorker.get_camera_temperature)
    worker.cameraWorker.viewTimer.timeout.connect(worker.cameraWorker.update_view)   
    cameraThread.start()
    
        ## Shamrock Thread
        
    shamrockThread = QtCore.QThread()
    worker.spectrumWorker.moveToThread(shamrockThread)
    shamrockThread.start()
    
    ## Step and Glue Thread
    
    stepandglueThread = QtCore.QThread()
    worker.stepandglueWorker.moveToThread(stepandglueThread)
    worker.stepandglueWorker.viewTimer.moveToThread(stepandglueThread)
    worker.stepandglueWorker.viewRECTimer.moveToThread(stepandglueThread)
    worker.stepandglueWorker.viewRECTimer_kinetics.moveToThread(stepandglueThread)
    worker.stepandglueWorker.viewTimer.timeout.connect(worker.stepandglueWorker.update_view) 
    worker.stepandglueWorker.viewRECTimer.timeout.connect(worker.stepandglueWorker.update_REC_view)   
    worker.stepandglueWorker.viewRECTimer_kinetics.timeout.connect(worker.stepandglueWorker.update_REC_view_kinetics)
    stepandglueThread.start()
    
    
    ## Confocal Spectrum Thread (Slow and Fast)
    
    confocalSpectrumThread = QtCore.QThread()
    
    worker.confocalSWorker.moveToThread(confocalSpectrumThread)
    worker.confocalSWorker.PDtimer_stepxy.moveToThread(confocalSpectrumThread)
    worker.confocalSWorker.PDtimer_stepxy.timeout.connect(worker.confocalSWorker.scan_step_xy)
    
  #  worker.confocalS_fast_Worker.moveToThread(confocalSpectrumThread)
  #  worker.confocalS_fast_Worker.PDtimer_stepxy.moveToThread(confocalSpectrumThread)
 #   worker.confocalS_fast_Worker.PDtimer_stepxy.timeout.connect(worker.confocalS_fast_Worker.scan_step_xy)
    
    confocalSpectrumThread.start()
  
    ## Routines PySpetrum Threads
    
   # routineThread = QtCore.QThread()
   # worker.luminescenceWorker.moveToThread(routineThread)
   # worker.growthWorker.moveToThread(routineThread)
   # worker.luminescence_stepsWorker.moveToThread(routineThread)
   # worker.printingWorker.moveToThread(routineThread)
  #  worker.dimersWorker.moveToThread(routineThread)
  #  routineThread.start()
    
    ##
 
    gui.show()
    
 #   if open_terminal:
      #  print('PySpectrum Open, can not use Terminal.')
    
    app.exec_()