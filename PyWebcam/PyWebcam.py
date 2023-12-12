# -*- coding: utf-8 -*-
"""
Created on Thu Feb  7 17:18:06 2019

@author: Luciana
"""

import numpy as np
import time
from datetime import datetime
import os

import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from pyqtgraph.dockarea import Dock, DockArea
from PIL import Image

import cv2

import viewbox_tools
import lineprofile

camera_port = 0
numberofPixels_x = 640
numberofPixels_y = 480


class Frontend(QtGui.QFrame):
    
    pictureSignal = pyqtSignal()
    saveSignal = pyqtSignal()
    liveSignal = pyqtSignal(bool, float)
    closeSignal =  pyqtSignal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setUpGUI()

    def setUpGUI(self):

    #Camera 
        
        # taking picture 
        
        time_Label = QtGui.QLabel('Time refresh (s):')
        self.time_Edit = QtGui.QLineEdit('0.09')

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

        camera_parameters_layout.addWidget(time_Label,              1, 1)
        camera_parameters_layout.addWidget(self.time_Edit,          1, 2)
        camera_parameters_layout.addWidget(self.liveview_button,    2, 1)
        camera_parameters_layout.addWidget(self.picture_button,     2, 2)
        camera_parameters_layout.addWidget(self.save_picture_button,2, 3)

        camera_parameters_layout.addWidget(self.ROI_button,         3, 1)
        camera_parameters_layout.addWidget(self.lineprofile_button, 3, 2)
        
        
        # image widget layout
        
        imageWidget = pg.GraphicsLayoutWidget()
        imageWidget.setMinimumHeight(350)
        imageWidget.setMinimumWidth(350)
        
        self.vb = imageWidget.addViewBox(row=0, col=0)
        self.vb.setAspectLocked(True)
        self.vb.setMouseMode(pg.ViewBox.RectMode)
        self.img = pg.ImageItem()
        self.img.translate(-0.5, -0.5)
        self.vb.addItem(self.img)
        self.vb.setAspectLocked(True)
        imageWidget.setAspectLocked(True)
        
        # set up histogram for the liveview image

        self.hist = pg.HistogramLUTItem(image=self.img)
       # lut = viewbox_tools.generatePgColormap(cmaps.parula)
       # self.hist.gradient.setColorMap(lut)
        self.hist.gradient.loadPreset('thermal')
# 'thermal', 'flame', 'yellowy', 'bipolar', 'spectrum',
# 'cyclic', 'greyclip', 'grey' # Solo son estos

        #self.hist.vb.setLimits(yMin=0, yMax=65536)

        for tick in self.hist.gradient.ticks:
            tick.hide()
        imageWidget.addItem(self.hist, row=0, col=1)

        traceROI_Widget = pg.GraphicsLayoutWidget()  
        self.roi = None
        plot_traceROI =  traceROI_Widget.addPlot(row=1, col=1, title="Trace")
        plot_traceROI.showGrid(x=True, y=True)
        self.curve_ROI = plot_traceROI.plot(open='y')
        
        self.lineplotWidget = lineprofile.linePlotWidget()
        self.lineROI = None
        self.curve_line = self.lineplotWidget.linePlot.plot(open='y')
        
        #docks

        hbox = QtGui.QHBoxLayout(self)
        dockArea = DockArea()
        hbox.addWidget(dockArea)
        self.setLayout(hbox)
        
        camera_dock = Dock('Parameters')
        camera_dock.addWidget(self.camera)
        dockArea.addDock(camera_dock)
        
        viewbox_dock = Dock('View', size = (500, 500))
        viewbox_dock.addWidget(imageWidget)
        dockArea.addDock(viewbox_dock)
        
        traceROI_dock = Dock('Trace ROI')
        traceROI_dock.addWidget(traceROI_Widget)
        dockArea.addDock(traceROI_dock, 'right', viewbox_dock)

    def liveview_button_check(self):
        refresh_time = float(self.time_Edit.text())
        if self.liveview_button.isChecked():
           self.liveSignal.emit(True, refresh_time)
        else:
           self.liveSignal.emit(False, refresh_time)

        self.refresh_time = refresh_time

    def picture_button_check(self):
        if self.picture_button.isChecked:
           self.pictureSignal.emit()

    def save_button_check(self):
        if self.save_picture_button.isChecked:
           self.saveSignal.emit()
           
        
    @pyqtSlot(np.ndarray)
    def get_image(self, image):

        self.img.setImage(image, autoLevels=True)

        if self.ROI_button.isChecked():
            self.update_ROI(image)
            
        if self.lineprofile_button.isChecked():
            self.update_LINE(image)


    def create_ROI(self):
        

        ROIpos = (0.5 *numberofPixels_x-0.5*100, 0.5 *numberofPixels_y-0.5*100)

        if self.ROI_button.isChecked():
            
            self.roi = viewbox_tools.ROI(100, self.vb, ROIpos,
                                         handlePos=(1, 0),
                                         handleCenter=(0, 1),
                                         scaleSnap=True,
                                         translateSnap=True)
            
            self.ptr = 1
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

        time_step = self.ptr*self.refresh_time

        self.timeaxis.append(time_step)
        self.data_ROI.append(mean_intensity)

        self.ptr += 1

        self.curve_ROI.setData(self.timeaxis, self.data_ROI,
                           pen=pg.mkPen('g', width=1),
                           shadowPen=pg.mkPen('w', width=3))
        
    def create_line_profile(self):
        
        if self.lineprofile_button.isChecked():

            self.lineROI = pg.LineSegmentROI([[0, int(numberofPixels_y/2)], [numberofPixels_x, int(numberofPixels_y/2)]], pen='r')
            self.vb.addItem(self.lineROI)
            self.lineplotWidget.show()
                                  
        else:

            self.lineplotWidget.close()
            self.vb.removeItem(self.lineROI)
            
            
    def update_LINE(self, image):
        
        array_intensity = self.lineROI.getArrayRegion(image, self.img)
        
        xmin, ymin = self.lineROI.pos()
        xmax, ymax = self.lineROI.pos() + self.lineROI.size()
                
        array_pos_x = np.linspace(xmin,  xmax, len(array_intensity))
        
        self.curve_line.setData(array_pos_x, array_intensity,
                           pen=pg.mkPen('m', width=1),
                           shadowPen=pg.mkPen('m', width=3)) 
        
        
    def closeEvent(self, *args, **kwargs):
        
        self.closeSignal.emit()
        
        super().closeEvent(*args, **kwargs)
        
    def make_connection(self, backend):
        backend.imageSignal.connect(self.get_image)
        
        
class Backend(QtCore.QObject):

    imageSignal = pyqtSignal(np.ndarray)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.file_path = os.path.abspath("C:/Users/Alumno") #direccion por default

        self.viewTimer = QtCore.QTimer()
        self.viewTimer.timeout.connect(self.update_view)   
        
        self.set_camera_parameters()

    def set_camera_parameters(self):  

        self.cap = cv2.VideoCapture(camera_port)

     
    @pyqtSlot(bool, float)
    def liveview(self, livebool, refresh_time):
        
        if livebool:
           self.refresh_time = refresh_time      
           self.start_liveview()
        else:
           self.stop_liveview()
    
    def start_liveview(self):
     
        print(datetime.now(),'Start liveview')

        leido, frame = self.cap.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        image = np.flip(np.transpose(gray),1)

        self.imageSignal.emit(image) 

        self.viewTimer.start(1.5*self.refresh_time*10**3) 
        
    def update_view(self):
        """ Image update while in Liveview mode """


        leido, frame = self.cap.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        image = np.flip(np.transpose(gray),1)

        self.imageSignal.emit(image) 

        
    def stop_liveview(self):  

        self.viewTimer.stop()
        
    @pyqtSlot()
    def taking_picture(self):
        
        # set shutters configuration
        leido, frame = self.cap.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        image = np.flip(np.transpose(gray),1)

        self.imageSignal.emit(image) 

        print(datetime.now(),'Taking picture')
        
        self.image = gray #me sirve para guardar la ultima imagen
        
    @pyqtSlot(str)  #viene de PySpectrum si creo directorio del dia, sino usa la q que esta por default
    def get_direction(self, file_name):
        self.file_path = file_name
        
    @pyqtSlot()    
    def save_picture(self):
        
        filepath = self.file_path
        timestr = time.strftime("%Y%m%d_%H%M%S")
#        name = str(filepath + "/" + "Photo_" + timestr + ".tiff")
        filename = "Photo_" + timestr + ".tiff"
        full_filename = os.path.join(filepath, filename)
        guardado = Image.fromarray(self.image)
        guardado.save(full_filename)
        print("\n Image saved\n")
        
    @pyqtSlot()    
    def close(self):
        
        self.cap.release()
        cv2.destroyAllWindows()

    def make_connection(self, frontend):

        frontend.liveSignal.connect(self.liveview)
        frontend.pictureSignal.connect(self.taking_picture)
        frontend.saveSignal.connect(self.save_picture)
        frontend.closeSignal.connect(self.close)

if __name__ == '__main__':

    app = QtGui.QApplication([])

    gui = Frontend()   
    worker = Backend()

    worker.make_connection(gui)
    gui.make_connection(worker)

    cameraThread = QtCore.QThread()
    worker.moveToThread(cameraThread)
    worker.viewTimer.moveToThread(cameraThread)
    cameraThread.start()

    gui.show()
    app.exec_()