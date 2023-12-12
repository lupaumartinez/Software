# -*- coding: utf-8 -*-
"""
Created on Thu Apr  4 11:10:29 2019

@author: Luciana
"""

from pyqtgraph.Qt import QtGui, QtCore
from pyqtgraph.dockarea import DockArea, Dock
from PyQt5.QtCore import pyqtSignal

import Cursor
import Nanopositioning

from Instrument import pi_device

class Frontend(QtGui.QMainWindow):
    

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.setWindowTitle('PyPrinting')

        self.cwidget = QtGui.QWidget()
        self.setCentralWidget(self.cwidget)
        self.setGeometry(30, 30, 50, 50)
        
        # GUI layout

        grid = QtGui.QGridLayout()
        self.cwidget.setLayout(grid)

        # Dock Area

        dockArea = DockArea()
        grid.addWidget(dockArea)

        
        ## Cursor

        cursorDock = Dock("Cursor picture")
        self.cursorWidget = Cursor.Frontend()
        cursorDock.addWidget(self.cursorWidget)
        dockArea.addDock(cursorDock)
        
         ## Nanopositioning

        nanopositioningDock = Dock("Nanopositioning")
        self.nanopositioningWidget =  Nanopositioning.Frontend()
        nanopositioningDock.addWidget(self.nanopositioningWidget)
        dockArea.addDock(nanopositioningDock)
         
    def make_connection(self, backend):
        
        backend.cursorWorker.make_connection(self.cursorWidget)
        backend.nanopositioningWorker.make_connection(self.nanopositioningWidget)

    def closeEvent(self, event):

        reply = QtGui.QMessageBox.question(self, 'Quit', 'Are you sure to quit?',
                                           QtGui.QMessageBox.No |
                                           QtGui.QMessageBox.Yes)
        if reply == QtGui.QMessageBox.Yes:
            print("PyCursor Close")
            event.accept()
            pi_device.MOV(['A','B','C'], [0, 0, 0])
            pi_device.CloseConnection()
            print('Platina CloseConnection')
            self.close()

        else:
            event.ignore()
        
class Backend(QtCore.QObject):
    
    fileSignal = pyqtSignal(str)
    
    def __init__(self, *args, **kwargs):
        
        super().__init__(*args, **kwargs)
        
        self.cursorWorker = Cursor.Backend()
        self.nanopositioningWorker = Nanopositioning.Backend()

        self.make_connection_backends()

    def make_connection(self, frontend):
       
        
        frontend.cursorWidget.make_connection(self.cursorWorker)
        frontend.nanopositioningWidget.make_connection(self.nanopositioningWorker)

    def make_connection_backends(self):

        self.nanopositioningWorker.read_pos_signal.connect(self.cursorWorker.real_cursor)
  
      
if __name__ == '__main__':

    app = QtGui.QApplication([])
    
    gui = Frontend()
    worker = Backend()
    
    gui.make_connection(worker)
    worker.make_connection(gui)
    
    gui.show()
    app.exec_()
        
        