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

import nidaqmx
from Instrument_nidaqmx import initial_nidaqmx

from pipython import GCSDevice
import Instrument_PI

import Focus
import Shutters
import Nanopositioning
import Trace
import Confocal
import Printing
import Dimers
import Cursor

#%%

class Frontend(QtGui.QMainWindow):
    
    selectDirSignal = pyqtSignal()
    createDirSignal = pyqtSignal()
    openDirSignal = pyqtSignal()
    loadpositionSignal = pyqtSignal()
    loadgridSignal = pyqtSignal()
    closeSignal = pyqtSignal()

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.setWindowTitle('PyPrinting')

        self.cwidget = QtGui.QWidget()
        self.setCentralWidget(self.cwidget)
        self.setGeometry(30, 30, 200, 200)

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

    # Create de create daily directory action
        save_docks_Action = QtGui.QAction(QtGui.QIcon('algo.png'), '&Save Docks', self)
        save_docks_Action.setStatusTip('Saves the Actual Docks configuration')
        save_docks_Action.triggered.connect(self.save_docks)

    # Create de create daily directory action
        load_docks_Action = QtGui.QAction(QtGui.QIcon('algo.png'), '&Restore Docks', self)
        load_docks_Action.setStatusTip('Load a previous Docks configuration')
        load_docks_Action.triggered.connect(self.load_docks)
        
    # Open Tools: Cursor
        tools_cursor_Action = QtGui.QAction('&Cursor', self)
        tools_cursor_Action.triggered.connect(self.tools_cursor)
        
    # Open Tools: Load grid
        load_grid_Action = QtGui.QAction('&Load Grid', self)
        load_grid_Action.triggered.connect(self.load_grid)
        
    # Measurment Printing
        printing_Action = QtGui.QAction('&Do Printing', self)
        printing_Action.triggered.connect(self.measurement_printing)
        
    # Measurment Dimers
        dimers_Action = QtGui.QAction('&Do Dimers', self)
        dimers_Action.triggered.connect(self.measurement_dimers)

        # Actions in menubar
    
        menubar = self.menuBar()

        fileMenu = menubar.addMenu('&Files Direction')
        fileMenu.addAction(localDirAction)
        fileMenu.addAction(openAction)
        fileMenu.addAction(dailyAction)
        fileMenu.addAction(load_position_Action)
        
        fileMenu2 = menubar.addMenu('&Tools')
        fileMenu2.addAction(tools_cursor_Action)
        fileMenu2.addAction(load_grid_Action)

        fileMenu3 = menubar.addMenu('&Measurements')
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
        self.dockArea = dockArea
        grid.addWidget(self.dockArea)
        
        ## Confocal

        confocalDock = Dock("Confocal")
        self.confocalWidget = Confocal.Frontend()
        confocalDock.addWidget(self.confocalWidget)
        self.dockArea.addDock(confocalDock)
        
        ## Trace

        traceDock = Dock("Trace")
        self.traceWidget = Trace.Frontend()
        traceDock.addWidget(self.traceWidget)
        self.dockArea.addDock(traceDock, 'right', confocalDock)
        
        ## Focus

        focusDock = Dock("Focus z")
        self.focusWidget = Focus.Frontend()
        focusDock.addWidget(self.focusWidget)
        self.dockArea.addDock(focusDock)
        
        ## Shutters

        shuttersDock = Dock("Shutters and Flipper")
        self.shuttersWidget = Shutters.Frontend()
        shuttersDock.addWidget(self.shuttersWidget)
        self.dockArea.addDock(shuttersDock ,'right',focusDock)
        
         ## Nanopositioning

        nanopositioningDock = Dock("Nanopositioning")
        self.nanopositioningWidget =  Nanopositioning.Frontend()
        nanopositioningDock.addWidget(self.nanopositioningWidget)
        self.dockArea.addDock( nanopositioningDock ,'left',focusDock)
        
        ## Tools: Cursor
        self.cursorWidget =  Cursor.Frontend()
    

        ## Dimers

        self.dimersWidget =  Dimers.Frontend()
        
        ## Printing

        self.printingWidget =  Printing.Frontend()

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
        
    def measurement_printing(self):
        
        self.printingWidget.show()
        
    def measurement_dimers(self):
        
        self.dimersWidget.show()
        
    def tools_cursor(self):

        self.cursorWidget.show()
        
    def load_grid(self):
        self.loadgridSignal.emit()
         
    def make_connection(self, backend):
        
        backend.focusWorker.make_connection(self.focusWidget)
        backend.shuttersWorker.make_connection(self.shuttersWidget)
        backend.nanopositioningWorker.make_connection(self.nanopositioningWidget)
        backend.traceWorker.make_connection(self.traceWidget)
        backend.confocalWorker.make_connection(self.confocalWidget)
        backend.printingWorker.make_connection(self.printingWidget)
        backend.dimersWorker.make_connection(self.dimersWidget)
        backend.cursorWorker.make_connection(self.cursorWidget)
        
    def closeEvent(self, event):

        reply = QtGui.QMessageBox.question(self, 'Quit', 'Are you sure to quit?',
                                           QtGui.QMessageBox.No |
                                           QtGui.QMessageBox.Yes)
        if reply == QtGui.QMessageBox.Yes:
            print("PyPrinting Close")
            self.closeSignal.emit()
            event.accept()
            self.close()
            
            shuttersThread.exit()
            nanopositioningThread.exit()
          #  focusThread.exit()
          #  traceThread.exit()
            confocalThread.exit()
         #   routineThread.exit()

        else:
            event.ignore()
            print("NO")
        
#%%
        
class Backend(QtCore.QObject):
    
    fileSignal = pyqtSignal(str)
    close_all_instrument_Signal = pyqtSignal()
    gridSignal = pyqtSignal(str, np.ndarray)
    
    def __init__(self, pi_device, task_nidaqmx, *args, **kwargs):
        
        super().__init__(*args, **kwargs)
        
        self.pi_device = pi_device
        
        self.focusWorker = Focus.Backend(pi_device, task_nidaqmx)
        self.shuttersWorker = Shutters.Backend(task_nidaqmx)
        self.nanopositioningWorker = Nanopositioning.Backend(pi_device)
        self.traceWorker = Trace.Backend(task_nidaqmx)
        self.confocalWorker = Confocal.Backend(pi_device, task_nidaqmx)
        self.printingWorker = Printing.Backend(pi_device, task_nidaqmx)
        self.dimersWorker = Dimers.Backend(pi_device, task_nidaqmx)
        self.cursorWorker = Cursor.Backend(pi_device)
        
        self.make_connection_backends()
        self.make_connection_printing()
        self.make_connection_dimers()
        
        self.file_path = os.path.abspath("C:\Julian\Data_PyPrinting")  #por default, por si se olvida de crear la carpeta del día
        
    @pyqtSlot()    
    def selectDir(self):
        root = tk.Tk()
        root.withdraw()

        file_path = filedialog.askdirectory()
        if not file_path:
            print("Don't choose a folder...")
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
            print("If you don't choose a folder... ==> Doesn't make a folder")
        else:
            timestr = time.strftime("%Y-%m-%d")  # -%H%M%S")

            newpath = file_path + "/" + timestr
            if not os.path.exists(newpath):
                os.makedirs(newpath)
                print("Folder ok!")
            else:
                print("Folder already exixts ok.")

            self.file_path = newpath 
            self.fileSignal.emit(self.file_path) 
            
            
    @pyqtSlot()             
    def load_last_position(self): 
        
        filepath = "C:/Julian/PyPrinting/PyPrinting - 02_06_ThreadsOK"
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
        
        frontend.selectDirSignal.connect(self.selectDir)
        frontend.openDirSignal.connect(self.openDir)
        frontend.createDirSignal.connect(self.create_daily_directory)
        frontend.loadpositionSignal.connect(self.load_last_position)
        frontend.loadgridSignal.connect(self.load_grid)
        frontend.closeSignal.connect(self.closeAll)
        
        frontend.focusWidget.make_connection(self.focusWorker)
        frontend.nanopositioningWidget.make_connection(self.nanopositioningWorker)
        frontend.traceWidget.make_connection(self.traceWorker)
        frontend.confocalWidget.make_connection(self.confocalWorker)
        frontend.printingWidget.make_connection(self.printingWorker)    
        frontend.dimersWidget.make_connection(self.dimersWorker)
        frontend.cursorWidget.make_connection(self.cursorWorker)
        
    def make_connection_backends(self):
        
        self.focusWorker.gotomaxdoneSignal.connect(self.nanopositioningWorker.read_pos)
        self.focusWorker.lockdoneSignal.connect(self.nanopositioningWorker.read_pos)
        self.focusWorker.autodoneSignal.connect(self.nanopositioningWorker.read_pos)
        self.confocalWorker.scandoneSignal.connect(self.nanopositioningWorker.read_pos)
        
        self.printingWorker.grid_move_finishSignal.connect(self.nanopositioningWorker.read_pos)
        self.printingWorker.goSignal.connect(self.nanopositioningWorker.read_pos)
        self.dimersWorker.grid_move_finishSignal.connect(self.nanopositioningWorker.read_pos)
        self.dimersWorker.goSignal.connect(self.nanopositioningWorker.read_pos)
        self.nanopositioningWorker.read_pos_signal.connect(self.cursorWorker.real_cursor)

        self.fileSignal.connect(self.printingWorker.grid_direction)
        self.fileSignal.connect(self.dimersWorker.grid_direction)
        self.fileSignal.connect(self.traceWorker.direction)
        self.fileSignal.connect(self.confocalWorker.direction)

        self.gridSignal.connect(self.printingWorker.grid)
        self.gridSignal.connect(self.dimersWorker.grid)
        
        self.close_all_instrument_Signal.connect(self.nanopositioningWorker.close)
        self.close_all_instrument_Signal.connect(self.shuttersWorker.close)
        
    def make_connection_printing(self):
    
        self.printingWorker.grid_move_finishSignal.connect(self.printingWorker.grid_autofoco)
        self.printingWorker.grid_autofocusSignal.connect(self.focusWorker.focus_autocorr_lin_x2)
        self.focusWorker.autofinishSignal.connect(self.printingWorker.grid_finish_autofoco)
        
        self.printingWorker.grid_traceSignal.connect(self.traceWorker.trace_configuration)
        self.traceWorker.data_printingSignal.connect(self.printingWorker.grid_trace_detect)
        self.printingWorker.grid_trace_stopSignal.connect(self.traceWorker.stop)
        
        self.printingWorker.grid_detectSignal.connect(self.printingWorker.grid_scan)
        self.printingWorker.grid_scanSignal.connect(self.confocalWorker.start_scan_routines)
        self.printingWorker.grid_scan_stopSignal.connect(self.confocalWorker.stop_scan)
        self.confocalWorker.scanfinishSignal.connect(self.printingWorker.grid_scan_detect)

    def make_connection_dimers(self):

        self.dimersWorker.grid_move_finishSignal.connect(self.dimersWorker.grid_autofoco)
        self.dimersWorker.grid_autofocusSignal.connect(self.focusWorker.focus_autocorr_lin_x2)
        self.focusWorker.autofinishSignal_dimers.connect(self.dimersWorker.grid_finish_autofoco)
        
        self.dimersWorker.grid_traceSignal.connect(self.traceWorker.trace_configuration)
        self.traceWorker.data_printingSignal_dimers.connect(self.dimersWorker.grid_trace_detect)
        self.dimersWorker.grid_trace_stopSignal.connect(self.traceWorker.stop)
    
        self.dimersWorker.grid_scanSignal.connect(self.confocalWorker.start_scan_routines)
        self.dimersWorker.grid_scan_stopSignal.connect(self.confocalWorker.stop_scan)
        
        self.confocalWorker.scanfinishSignal_dimers_center.connect(self.dimersWorker.grid_center_scan_detect)
        self.confocalWorker.scanfinishSignal_dimers_pree.connect(self.dimersWorker.grid_pree_scan_detect)
        self.confocalWorker.scanfinishSignal_dimers_post.connect(self.dimersWorker.grid_post_scan_detect)

        self.dimersWorker.grid_detectSignal.connect(self.dimersWorker.grid_finish)
    

      
if __name__ == '__main__':

        #app = QtGui.QApplication([])

    if not QtGui.QApplication.instance():
        app = QtGui.QApplication([])
        open_terminal = True
    else:
      #  print('PyPrinting Open, can use Terminal too.')
        open_terminal = False
        app = QtGui.QApplication.instance() 
        
    
    gui = Frontend()
    
    ##INSTRUMENTS
    
    ##Platina
    
    pi_device= GCSDevice()
    Instrument_PI.initial_pi_device(pi_device)
    
    ##Nidaqmx: shutters, flippers, photodiodes
    task_nidaqmx = initial_nidaqmx(nidaqmx)
    
    worker = Backend(pi_device, task_nidaqmx)
    
    ## MAKE CONNECTIONS

    gui.make_connection(worker)
    worker.make_connection(gui)

    ## Shutters laser, flipper's Thread
    
    shuttersThread = QtCore.QThread()
    worker.shuttersWorker.moveToThread(shuttersThread)
    shuttersThread.start()
    
    ## Nanopositioning Thread
    
    nanopositioningThread = QtCore.QThread()
    worker.nanopositioningWorker.moveToThread(nanopositioningThread)
    nanopositioningThread.start()
    
    ## Photodiodo Thread Trace Photodiode Thread, Focus Z Photodiode Thread, Confocal Photodiode Thread
  
    confocalThread = QtCore.QThread()
    
    ## Trace Photodiode Thread
    
 #   traceThread = QtCore.QThread()
    worker.traceWorker.moveToThread(confocalThread)
    worker.traceWorker.pointtimer.moveToThread(confocalThread)
    worker.traceWorker.pointtimer.timeout.connect(worker.traceWorker.trace_update)
    worker.traceWorker.plot_pointtimer.moveToThread(confocalThread)
    worker.traceWorker.plot_pointtimer.timeout.connect(worker.traceWorker.plot_trace_update)
  #  traceThread.start()
        
    ## Focus Z Photodiode Thread
    
   # focusThread = QtCore.QThread()
    worker.focusWorker.moveToThread(confocalThread)
   # focusThread.start()
    
    ## Confocal Photodiode Thread
    
    worker.confocalWorker.moveToThread(confocalThread)
    worker.confocalWorker.PDtimer_stepxy.moveToThread(confocalThread)
    worker.confocalWorker.PDtimer_rampxy.moveToThread(confocalThread)
    worker.confocalWorker.PDtimer_rampxz.moveToThread(confocalThread)
    worker.confocalWorker.PDtimer_rampyx.moveToThread(confocalThread)
    worker.confocalWorker.PDtimer_rampyz.moveToThread(confocalThread)
    worker.confocalWorker.drifttimer.moveToThread(confocalThread)
    worker.confocalWorker.PDtimer_stepxy.timeout.connect(worker.confocalWorker.scan_step_xy)
    worker.confocalWorker.PDtimer_rampxy.timeout.connect(worker.confocalWorker.scan_ramp_xy)
    worker.confocalWorker.PDtimer_rampxz.timeout.connect(worker.confocalWorker.scan_ramp_xz)
    worker.confocalWorker.PDtimer_rampyx.timeout.connect(worker.confocalWorker.scan_ramp_yx)
    worker.confocalWorker.PDtimer_rampyz.timeout.connect(worker.confocalWorker.scan_ramp_yz)
    worker.confocalWorker.drifttimer.timeout.connect(worker.confocalWorker.drift)

    worker.printingWorker.moveToThread(confocalThread)
    worker.dimersWorker.moveToThread(confocalThread)
    
    confocalThread.start()
    
    ## Routines Printing Threads
    
   ## routineThread = QtCore.QThread()
   ## worker.printingWorker.moveToThread(routineThread)
   ## worker.dimersWorker.moveToThread(routineThread)
   ## routineThread.start()
    ##
 
    gui.show()
    
    #if open_terminal:
       # print('PyPrinting Open, can not use Terminal.')
    app.exec_()
        
    

        
        
        