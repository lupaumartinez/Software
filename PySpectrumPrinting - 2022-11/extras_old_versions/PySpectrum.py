# -*- coding: utf-8 -*-
"""
Created on Thu Apr  4 11:10:29 2019

@author: Luciana
"""

import os
import time
from tkinter import filedialog
import tkinter as tk
import numpy as np

from pyqtgraph.Qt import QtGui, QtCore
from pyqtgraph.dockarea import DockArea, Dock
from PyQt5.QtCore import pyqtSignal, pyqtSlot

import Camera
import Spectrum
import StepandGlue
import Confocal_Spectrum
import Confocal_Spectrum_Fast

from Instrument import pi_device, Flipper_notch532

import Nanopositioning
import Cursor
import Shutters

import Confocal
import Trace
import Focus

import Luminescence
import Growth

class Frontend(QtGui.QMainWindow):
    
    selectDirSignal = pyqtSignal()
    createDirSignal = pyqtSignal()
    openDirSignal = pyqtSignal()
    loadpositionSignal = pyqtSignal()
    closeSignal = pyqtSignal()

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.setWindowTitle('PySpectrum')

        self.cwidget = QtGui.QWidget()
        self.setCentralWidget(self.cwidget)
        self.setGeometry(30, 30, 300, 300)
        

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
        load_position_Action.setStatusTip('Load last position when PyPrinting closed.')
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
        
    # Open Tools: Confocal Spectrum (Zero Order, First Order)
        tools_confocal_spectrum_Action = QtGui.QAction('&Confocal Spectrum', self)
        tools_confocal_spectrum_Action.triggered.connect(self.tools_confocal_spectrum)

    # Measurment Luminescence
        luminescence_Action = QtGui.QAction('&Do Luminescence', self)
        luminescence_Action.triggered.connect(self.measurement_luminescence)
        
    # Measurment Growth
        growth_Action = QtGui.QAction('&Do Growth', self)
        growth_Action.triggered.connect(self.measurement_growth)

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
        fileMenu2.addAction(tools_confocal_spectrum_Action)

        fileMenu3 = menubar.addMenu('&Measurements')
        fileMenu3.addAction(luminescence_Action)
        fileMenu3.addAction(growth_Action)
        
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

        confocalDock = Dock("SLOW: Confocal First order")
        self.confocalSWidget = Confocal_Spectrum.Frontend()
        confocalDock.addWidget(self.confocalSWidget)
        subdockArea3.addDock(confocalDock)

            ## Confocal_Spectrum_Fast

        confocal_fast_Dock = Dock("FAST: Confocal First order")
        self.confocalS_fast_Widget = Confocal_Spectrum_Fast.Frontend()
        confocal_fast_Dock.addWidget(self.confocalS_fast_Widget)
        subdockArea3.addDock(confocal_fast_Dock, 'right', confocalDock)

           ## Luminescence

        self.luminescenceWidget =  Luminescence.Frontend()
        
           ## Growth

        self.growthWidget =  Growth.Frontend()


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
    
        
    def tools_confocal_spectrum(self):
        
        self.tools_confocal_spectrum_Widget.show()

    def measurement_luminescence(self):
        
        self.luminescenceWidget.show()
        
    def measurement_growth(self):
        
        self.growthWidget.show()
    
         
    def make_connection(self, backend):

        backend.cameraWorker.make_connection(self.cameraWidget)
        backend.spectrumWorker.make_connection(self.spectrumWidget)
        backend.stepandglueWorker.make_connection(self.stepandglueWidget)
        backend.confocalSWorker.make_connection(self.confocalSWidget)
        backend.confocalS_fast_Worker.make_connection(self.confocalS_fast_Widget)

        backend.shuttersWorker.make_connection(self.shuttersWidget)
        backend.nanopositioningWorker.make_connection(self.nanopositioningWidget)
        backend.cursorWorker.make_connection(self.cursorWidget)
        
        backend.confocal_PH_Worker.make_connection(self.confocal_PH_Widget)
        backend.focus_PH_Worker.make_connection(self.focus_PH_Widget)
        backend.trace_PH_Worker.make_connection(self.trace_PH_Widget)

        backend.luminescenceWorker.make_connection(self.luminescenceWidget)
        backend.growthWorker.make_connection(self.growthWidget)
        
        backend.stepandglueWorker.imageSignal.connect(self.cameraWidget.get_image)
        backend.confocalSWorker.imageSignal.connect(self.cameraWidget.get_image)
        backend.confocalS_fast_Worker.imageSignal.connect(self.cameraWidget.get_image)

    def make_connection_frontends(self):

        self.stepandglueWidget.show_lineparametersSignal.connect(self.cameraWidget.create_line_horizontal)
        self.stepandglueWidget.lineparametersSignal.connect(self.cameraWidget.line_horizontal)

        self.confocalSWidget.show_filterSignal.connect(self.cameraWidget.create_line_horizontal)
        self.confocalSWidget.spectrum_parameters_filterSignal.connect(self.cameraWidget.line_horizontal)

        self.confocalS_fast_Widget.show_filterSignal.connect(self.cameraWidget.create_line_horizontal)
        self.confocalS_fast_Widget.spectrum_parameters_filterSignal.connect(self.cameraWidget.line_horizontal)
        

    def closeEvent(self, event):

        reply = QtGui.QMessageBox.question(self, 'Quit', 'Are you sure to quit?',
                                           QtGui.QMessageBox.No |
                                           QtGui.QMessageBox.Yes)
        if reply == QtGui.QMessageBox.Yes:
            print("YES")
            self.closeSignal.emit()
            event.accept()
            self.close()
            PySpectrumThread.exit()

        else:
            event.ignore()
            print("NO")
        
#%%
        
class Backend(QtCore.QObject):
    
    fileSignal = pyqtSignal(str)
    close_all_instrument_Signal = pyqtSignal()
    
    def __init__(self, *args, **kwargs):
        
        super().__init__(*args, **kwargs)
        
        self.cameraWorker = Camera.Backend()
        self.spectrumWorker = Spectrum.Backend()
        self.stepandglueWorker = StepandGlue.Backend()
        self.confocalSWorker = Confocal_Spectrum.Backend()
        self.confocalS_fast_Worker = Confocal_Spectrum_Fast.Backend()

        self.shuttersWorker = Shutters.Backend()
        self.nanopositioningWorker = Nanopositioning.Backend()
        self.cursorWorker = Cursor.Backend()

        self.confocal_PH_Worker = Confocal.Backend()
        self.focus_PH_Worker = Focus.Backend()
        self.trace_PH_Worker = Trace.Backend()

        self.luminescenceWorker = Luminescence.Backend()
        self.growthWorker = Growth.Backend()
        
        self.file_path = os.path.abspath("C:\Julian\Data_PySpectrum")  #por default, por si se olvida de crear la carpeta del día
        
        self.make_connection_backends()
        self.make_connection_luminescence()
        self.make_connection_growth()
        
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
                
        pi_device.MOV(['A', 'B', 'C'], targets)
        time.sleep(0.01)
     
    @pyqtSlot()
    def closeAll(self):
        self.close_all_instrument_Signal.emit()
        Flipper_notch532('down')


            
    def make_connection(self, frontend):

        frontend.cameraWidget.make_connection(self.cameraWorker)  
        frontend.stepandglueWidget.make_connection(self.stepandglueWorker)  

        frontend.nanopositioningWidget.make_connection(self.nanopositioningWorker)
        frontend.cursorWidget.make_connection(self.cursorWorker)
        frontend.confocalSWidget.make_connection(self.confocalSWorker)
        frontend.confocalS_fast_Widget.make_connection(self.confocalS_fast_Worker)

        frontend.confocal_PH_Widget.make_connection(self.confocal_PH_Worker)
        frontend.focus_PH_Widget.make_connection(self.focus_PH_Worker)
        frontend.trace_PH_Widget.make_connection(self.trace_PH_Worker)

        frontend.luminescenceWidget.make_connection(self.luminescenceWorker)
        frontend.growthWidget.make_connection(self.growthWorker)
        
        frontend.selectDirSignal.connect(self.selectDir)
        frontend.openDirSignal.connect(self.openDir)
        frontend.createDirSignal.connect(self.create_daily_directory)
        frontend.loadpositionSignal.connect(self.load_last_position)
        frontend.closeSignal.connect(self.closeAll)

    def make_connection_backends(self):
        
        self.spectrumWorker.gratingSignal.connect(self.stepandglueWorker.set_wavelength_window)

        self.confocalSWorker.scandoneSignal.connect(self.nanopositioningWorker.read_pos)
        self.confocalS_fast_Worker.scandoneSignal.connect(self.nanopositioningWorker.read_pos)
        
        self.nanopositioningWorker.read_pos_signal.connect(self.cursorWorker.real_cursor)

        self.focus_PH_Worker.gotomaxdoneSignal.connect(self.nanopositioningWorker.read_pos)
        self.focus_PH_Worker.lockdoneSignal.connect(self.nanopositioningWorker.read_pos)
        self.focus_PH_Worker.autodoneSignal.connect(self.nanopositioningWorker.read_pos)
        self.confocal_PH_Worker.scandoneSignal.connect(self.nanopositioningWorker.read_pos)

        self.luminescenceWorker.grid_move_finishSignal.connect(self.nanopositioningWorker.read_pos)
        self.luminescenceWorker.goSignal.connect(self.nanopositioningWorker.read_pos)
        
        self.growthWorker.grid_move_finishSignal.connect(self.nanopositioningWorker.read_pos)
        self.growthWorker.goSignal.connect(self.nanopositioningWorker.read_pos)
        
        self.fileSignal.connect(self.trace_PH_Worker.direction)
        self.fileSignal.connect(self.confocal_PH_Worker.direction)

        self.fileSignal.connect(self.cameraWorker.get_direction)
        self.fileSignal.connect(self.stepandglueWorker.get_direction)
        self.fileSignal.connect(self.confocalSWorker.get_direction)
        self.fileSignal.connect(self.confocalS_fast_Worker.get_direction)
        
        self.fileSignal.connect(self.luminescenceWorker.grid_direction)
        self.fileSignal.connect(self.growthWorker.grid_direction)
        
        self.close_all_instrument_Signal.connect(self.cameraWorker.close)
        self.close_all_instrument_Signal.connect(self.spectrumWorker.close)
        self.close_all_instrument_Signal.connect(self.nanopositioningWorker.close)

    def make_connection_luminescence(self):

        self.luminescenceWorker.grid_move_finishSignal.connect(self.luminescenceWorker.grid_autofoco)
        self.luminescenceWorker.grid_autofocusSignal.connect(self.focus_PH_Worker.focus_autocorr_lin_x2)
        self.focus_PH_Worker.autofinishSignal_luminescence.connect(self.luminescenceWorker.grid_finish_autofoco)

        self.luminescenceWorker.grid_scanSignal.connect(self.confocal_PH_Worker.start_scan_ramp_xy)
        self.luminescenceWorker.grid_scan_stopSignal.connect(self.confocal_PH_Worker.stop_scan_ramp_xy)
        self.confocal_PH_Worker.scanfinishSignal_luminescence.connect(self.luminescenceWorker.grid_center_scan_detect)

        self.luminescenceWorker.grid_spectrumSignal.connect(self.confocalSWorker.start_scan_step_xy)
        self.luminescenceWorker.grid_spectrum_stopSignal.connect(self.confocalSWorker.stop_scan_step_xy)
        self.confocalSWorker.scanfinishSignal_luminescence.connect(self.luminescenceWorker.grid_confocal_spectrum_detect)
  
    def make_connection_growth(self):

        self.growthWorker.grid_move_finishSignal.connect(self.growthWorker.grid_autofoco)
        self.growthWorker.grid_autofocusSignal.connect(self.focus_PH_Worker.focus_autocorr_lin_x2)
        self.focus_PH_Worker.autofinishSignal_growth.connect(self.growthWorker.grid_finish_autofoco)

        self.growthWorker.grid_scanSignal.connect(self.confocal_PH_Worker.start_scan_ramp_xy)
        self.growthWorker.grid_scan_stopSignal.connect(self.confocal_PH_Worker.stop_scan_ramp_xy)
        self.confocal_PH_Worker.scanfinishSignal_growth.connect(self.growthWorker.grid_center_scan_detect)

        self.growthWorker.grid_spectrumSignal.connect(self.stepandglueWorker.start_REC_liveview)
        self.stepandglueWorker.umbral_Signal_growth.connect(self.growthWorker.grid_liveview_spectrum_detect)
        self.growthWorker.grid_spectrum_stopSignal.connect(self.stepandglueWorker.stop_REC_liveview)
  
if __name__ == '__main__':

    app = QtGui.QApplication([])
    
    gui = Frontend()
    worker = Backend()
    
    gui.make_connection(worker)
    worker.make_connection(gui)
    
    PySpectrumThread = QtCore.QThread()
    
    gui.moveToThread(PySpectrumThread)

   #  worker.shuttersWorker.moveToThread(PySpectrumThread)
   #  worker.nanopositioningWorker.moveToThread(PySpectrumThread)
    
  #   worker.confocal_PH_Worker.moveToThread(PySpectrumThread)
  #   worker.focus_PH_Worker.moveToThread(PySpectrumThread)
   #  worker.trace_PH_Worker.moveToThread(PySpectrumThread)
    
  #   worker.cameraWorker.moveToThread(PySpectrumThread)
  #   worker.spectrumWorker.moveToThread(PySpectrumThread)
   #  worker.stepandglueWorker.moveToThread(PySpectrumThread)
   #  worker.confocalSWorker.moveToThread(PySpectrumThread)
   #  worker.confocalS_fast_Worker.moveToThread(PySpectrumThread)
    
    PySpectrumThread.start()
      
    gui.show()
    app.exec_()
        
        