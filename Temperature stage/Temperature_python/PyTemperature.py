# -*- coding: utf-8 -*-
"""

@author: Luciana
"""

import os
import time
from tkinter import filedialog
import tkinter as tk
import numpy as np
from datetime import datetime

from pyqtgraph.Qt import QtGui, QtCore
from pyqtgraph.dockarea import DockArea, Dock
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PIL import Image
import pyqtgraph as pg

import read_temperature
import control_temperature

class Frontend(QtGui.QMainWindow):
    
    selectDirSignal = pyqtSignal()
    createDirSignal = pyqtSignal()
    openDirSignal = pyqtSignal()
    closeSignal = pyqtSignal()

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.setWindowTitle('PyTemperature')

        self.cwidget = QtGui.QWidget()
        self.setCentralWidget(self.cwidget)
        self.setGeometry(30, 30, 50, 50)
        

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
        
        QtGui.QShortcut(
            QtGui.QKeySequence('Ctrl+A'), self, self.get_selectDir)
       
        QtGui.QShortcut(
            QtGui.QKeySequence('Ctrl+S'), self, self.get_create_daily_directory)
         
        QtGui.QShortcut(
            QtGui.QKeySequence('Ctrl+D'), self, self.get_openDir)

        # Actions in menubar
    
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(localDirAction)
        fileMenu.addAction(openAction)
        fileMenu.addAction(dailyAction)
        
        # GUI layout

        grid = QtGui.QGridLayout()
        self.cwidget.setLayout(grid)

        # Dock Area

        dockArea = DockArea()
        grid.addWidget(dockArea)
        
        ## Control temperature

        controlDock = Dock("Control temperature")
        self.controlWidget = control_temperature.Frontend()
        controlDock.addWidget(self.controlWidget)
        dockArea.addDock(controlDock)

        ## Read temperature

        readDock = Dock("Read temperature")
        self.readWidget = read_temperature.Frontend()
        readDock.addWidget(self.readWidget)
        dockArea.addDock(readDock, 'right', controlDock)

        ##Conections:

        self.make_connection_frontend()

    def get_openDir(self):
        self.openDirSignal.emit()
        
    def get_selectDir(self):
        self.selectDirSignal.emit()
        
    def get_create_daily_directory(self):
        self.createDirSignal.emit()
         
    def make_connection(self, backend):

        backend.readWorker.make_connection(self.readWidget)
        backend.controlWorker.make_connection(self.controlWidget)

    def make_connection_frontend(self):
        self.controlWidget.line_set_pointSignal.connect(self.readWidget.plot_line_set_point)

    def closeEvent(self, event):

        reply = QtGui.QMessageBox.question(self, 'Quit', 'Are you sure to quit?',
                                           QtGui.QMessageBox.No |
                                           QtGui.QMessageBox.Yes)
        if reply == QtGui.QMessageBox.Yes:
            print("YES")
            event.accept()
            self.closeSignal.emit()
            self.close()
        else:
            event.ignore()
            print("NO")
        
        
class Backend(QtCore.QObject):
    
    fileSignal = pyqtSignal(str)
    
    def __init__(self, *args, **kwargs):
        
        super().__init__(*args, **kwargs)
        
        self.controlWorker = control_temperature.Backend()
        self.readWorker = read_temperature.Backend()

        #poner alguna dirección por default:
        self.file_path = os.path.abspath("C:/Users/Alumno")
        
        self.make_connection_backends()
        
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
    def close_connection(self):
        print('Close')
        #arduino.close()
            
    def make_connection(self, frontend):

        #frontend.controlWidget.make_connection(self.controlWorker)  
        frontend.readWidget.make_connection(self.readWorker)  
        
        frontend.selectDirSignal.connect(self.selectDir)
        frontend.openDirSignal.connect(self.openDir)
        frontend.createDirSignal.connect(self.create_daily_directory)
        frontend.closeSignal.connect(self.close_connection)

    def make_connection_backends(self):

        self.fileSignal.connect(self.readWorker.get_direction)
      
if __name__ == '__main__':

    app = QtGui.QApplication([])
    
    gui = Frontend()
    worker = Backend()
    
    gui.make_connection(worker)
    worker.make_connection(gui)
    
    TemperatureThread = QtCore.QThread()

    worker.moveToThread(TemperatureThread)
    worker.controlWorker.moveToThread(TemperatureThread)
    worker.readWorker.moveToThread(TemperatureThread)
    worker.readWorker.Temperaturetimer.moveToThread(TemperatureThread)
    TemperatureThread.start()
      
    gui.show()
    app.exec_()
        
        