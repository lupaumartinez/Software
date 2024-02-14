
import numpy as np
import time
import os

from scipy import optimize

import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
from PyQt5.QtCore import pyqtSignal, pyqtSlot
import pyqtgraph.ptime as ptime
from pyqtgraph.dockarea import Dock, DockArea
from PIL import Image

from matrix_spiral import to_spiral
from PSF import center_of_mass, center_of_gauss2D, find_two_centers, two_centers_of_gauss2D
import imgrvt as rvt

import nidaqmx
from Instrument_nidaqmx import initial_nidaqmx, channels_photodiodos, channels_triggers, shutters, openShutter, closeShutter, PD_channels, PDchans, rateNI

from pipython import GCSDevice
import Instrument_PI 
from Instrument_PI import servo_time

Scanmodes = ['Ramp', 'Step by step']
PSFmodes = ['x/y', 'x/z', 'y/x', 'y/z'] 
ScanImage = ['NPs maximum', 'NPs minimum', 'choose', 'two NP: maximum-minimum']
MethodCenter = ['center of mass', 'center of gauss', 'two NP: center of gauss', 'RVT']

class Frontend(QtGui.QFrame):

    startSignal = pyqtSignal(int)
    stopSignal = pyqtSignal()
    
    parametersrampSignal = pyqtSignal(list)
    parametersstepSignal = pyqtSignal(list)
    
    scan_modeSignal = pyqtSignal(str)
    psf_modeSignal = pyqtSignal(str)
    
    image_scanSignal = pyqtSignal(str)
    method_centerSignal = pyqtSignal(str)
    filterSignal = pyqtSignal(float)
    CMSignal = pyqtSignal()
    CMautoSignal = pyqtSignal(bool)
    CMSignal_NP2 = pyqtSignal()

    driftSignal = pyqtSignal(bool, int, float, float)
    
    saveSignal = pyqtSignal()
    
    closeSignal = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setUpGUI()
        
    def set_parameters(self):
        
        parameters = [float(self.scanrangeEdit.text()), float(self.scanrangeEdit_y.text()), 
                      int(self.NxEdit.text()), int(self.NyEdit.text())]
        
        if self.scan_mode.currentText() == Scanmodes[0]:
            self.parametersrampSignal.emit(parameters)
            
        elif self.scan_mode.currentText() == Scanmodes[1]:
            self.parametersstepSignal.emit(parameters)
            
    def get_scan(self):
        
        self.point_graph_CM.hide()
        self.point_graph_CM_2.hide()
        if self.scanButton.isChecked:
            self.startSignal.emit(self.scan_laser.currentIndex())
            
    def get_scan_stop(self):  
        
        self.stopSignal.emit()

    def get_CM(self):
        if self.CMcheck.isChecked:
            self.CMSignal.emit()
            
    def get_CM_auto(self):
        if self.CMcheck_auto.isChecked():
            self.CMautoSignal.emit(True)
        else:
            self.CMautoSignal.emit(False)
            
    def get_CM_NP2(self):
        if self.CMcheck_NP2.isChecked:
            self.CMSignal_NP2.emit()
            
            
    def set_scan_mode(self):
        
        self.set_parameters()
        
        if self.scan_mode.currentText() == Scanmodes[0]:
            self.scan_modeSignal.emit(Scanmodes[0])
            
        elif self.scan_mode.currentText() == Scanmodes[1]:
            self.scan_modeSignal.emit(Scanmodes[1])
            
    def set_psf_mode(self):
        
        if self.PSF_mode.currentText() == PSFmodes[0]:
            self.psf_modeSignal.emit(PSFmodes[0])
            
        elif self.PSF_mode.currentText() == PSFmodes[1]:
            self.psf_modeSignal.emit(PSFmodes[1])
            
        elif self.PSF_mode.currentText() == PSFmodes[2]:
            self.psf_modeSignal.emit(PSFmodes[2])
            
        elif self.PSF_mode.currentText() == PSFmodes[3]:
            self.psf_modeSignal.emit(PSFmodes[3])
         

    def set_image_scan(self):
        
        if self.scan_image.currentText() == ScanImage[0]:
            self.image_scanSignal.emit(ScanImage[0])
            
        elif self.scan_image.currentText() == ScanImage[1]:
            self.image_scanSignal.emit(ScanImage[1])
            
        elif self.scan_image.currentText() == ScanImage[2]:
            self.image_scanSignal.emit(ScanImage[2])
            
        elif self.scan_image.currentText() == ScanImage[3]:
            self.image_scanSignal.emit(ScanImage[3])
            
            
    def set_method_center(self):
        
        if self.method_center.currentText() == MethodCenter[0]:
            self.method_centerSignal.emit(MethodCenter[0])
            
        elif self.method_center.currentText() == MethodCenter[1]:
            self.method_centerSignal.emit(MethodCenter[1])
            
        elif self.method_center.currentText() == MethodCenter[2]:
            self.method_centerSignal.emit(MethodCenter[2])
            
        elif self.method_center.currentText() == MethodCenter[3]:
            self.method_centerSignal.emit(MethodCenter[3])
            
    def set_filter_method_center(self):
        
        nfilter = float(self.nfilterEdit.text())

        self.filterSignal.emit(nfilter)
   
    def get_save_frame(self):
        if self.saveimageButton.isChecked:
            self.saveSignal.emit()
            
    def setUpGUI(self):
        
    
#  Buttons

    # Defino el laser
        self.scan_laser = QtGui.QComboBox()
        self.scan_laser.addItems(shutters)
        self.scan_laser.setCurrentIndex(0)
        self.scan_laser.setFixedWidth(80)
        self.scan_laser.activated.connect(
                                    lambda: self.color_menu(self.scan_laser))
        self.color_menu(self.scan_laser)
        
    # Button: defino el scan ramp o step
        self.scan_mode = QtGui.QComboBox()  
        self.scan_mode.addItems(Scanmodes)
        self.scan_mode.setCurrentIndex(0)
        self.scan_mode.setFixedWidth(80)
        self.scan_mode.currentIndexChanged.connect(self.set_scan_mode)
        
    # Button: defino el scan xy,xz,yz 
        self.PSF_mode = QtGui.QComboBox()  
        self.PSF_mode.addItems(PSFmodes)
        self.PSF_mode.setCurrentIndex(0)
        self.PSF_mode.setFixedWidth(80)
        self.PSF_mode.currentIndexChanged.connect(self.set_psf_mode)
        
        
    # scan
        self.scanButton = QtGui.QPushButton('Start Scan')
        self.scanButton.clicked.connect(self.get_scan)    
        
    # scan
        self.scanButtonstop = QtGui.QPushButton('Stop')
        self.scanButtonstop.clicked.connect(self.get_scan_stop)   
        
    # Scanning parameters
        self.scanrangeLabel = QtGui.QLabel('Range x or z (µm)')
        self.scanrangeEdit = QtGui.QLineEdit('2')

        self.NxLabel = QtGui.QLabel('Number of pixel x')
        self.NxEdit = QtGui.QLineEdit('34')
        self.NxEdit.setToolTip('Poner multiples de 16 por cada 1 µm')
        
        self.scanrangeLabel_y = QtGui.QLabel('Range y or z (µm)')        
        self.scanrangeEdit_y = QtGui.QLineEdit('2')
       
        self.NyLabel = QtGui.QLabel('Number of pixel y or z')
        self.NyEdit = QtGui.QLineEdit('34')
        self.NxEdit.setToolTip('Poner multiples de 16 por cada 1 µm')
        
        self.scanrangeEdit.textChanged.connect(self.set_parameters)
        self.scanrangeEdit_y.textChanged.connect(self.set_parameters) 
        self.NxEdit.textChanged.connect(self.set_parameters) 
        self.NyEdit.textChanged.connect(self.set_parameters) 
        
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
        subgrid.addWidget(self.scan_mode,              1, 2) 
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

        self.CMcheck = QtGui.QPushButton('go to NP1')
        self.CMcheck.clicked.connect(self.get_CM)
        
        self.CMcheck_auto = QtGui.QCheckBox('')
        self.CMcheck_auto.clicked.connect(self.get_CM_auto)
        
        self.CMcheck_NP2 = QtGui.QPushButton('go to NP2')
        self.CMcheck_NP2.clicked.connect(self.get_CM_NP2)
        
        # Button: defino si el scan es minimun o maximum, o choose
        self.scan_image = QtGui.QComboBox()
        self.scan_image.addItems(ScanImage)
        self.scan_image.setCurrentIndex(0)
        self.scan_image.setFixedWidth(80)
        self.scan_image.currentIndexChanged.connect(self.set_image_scan)
        
        # Button: defino si el metodo de encontrar el centro es center of mass, gauss, o hay dos NP con dos gauss
        self.method_center = QtGui.QComboBox()
        self.method_center.addItems(MethodCenter)
        self.method_center.setCurrentIndex(0)
        self.method_center.setFixedWidth(80)
        self.method_center.currentIndexChanged.connect(self.set_method_center)
        
        #Defino el filtro para para encontrar el centro
        nfilterLabel = QtGui.QLabel('Filter:')
        self.nfilterEdit = QtGui.QLineEdit('0.3')
        self.nfilterEdit.setToolTip('Aumentar por presencia de flags de grafeno a 0.7. Ojo que lo vuelve más exacto, pero menos preciso a la centro.')
        self.nfilterEdit.textChanged.connect(self.set_filter_method_center) 
        
        NPLabel_1 = QtGui.QLabel('NP 1:')
        NPLabel_2 = QtGui.QLabel('NP 2:')
        
        CxLabel = QtGui.QLabel('Center X:')
        CyLabel = QtGui.QLabel('Center Y:')
        
        self.CxValue_1 = QtGui.QLabel('NaN')
        self.CyValue_1 = QtGui.QLabel('NaN')
        self.CxValue_2 = QtGui.QLabel('NaN')
        self.CyValue_2 = QtGui.QLabel('NaN')

        layout3.addWidget(self.CMcheck,        1,1)
        layout3.addWidget(self.CMcheck_auto,   1,2)
        layout3.addWidget(self.CMcheck_NP2,    1,3)
        layout3.addWidget(self.scan_image,     2,1)
        layout3.addWidget(self.method_center,  2,2)
        
        layout3.addWidget(nfilterLabel,          3, 1)
        layout3.addWidget(self.nfilterEdit,      3, 2)
        layout3.addWidget(NPLabel_1,      4, 2)
        layout3.addWidget(NPLabel_2,      4, 3)
        layout3.addWidget(CxLabel,        5, 1)
        layout3.addWidget(CyLabel,        6, 1)
        
        layout3.addWidget(self.CxValue_1, 5, 2)
        layout3.addWidget(self.CxValue_2, 5, 3)
        
        layout3.addWidget(self.CyValue_1, 6, 2)
        layout3.addWidget(self.CyValue_2, 6, 3)
        
        #drift

        self.driftWidget = QtGui.QWidget()
        layout4 = QtGui.QGridLayout()
        self.driftWidget.setLayout(layout4) 

        self.driftButton = QtGui.QPushButton('DRIFT measurment/stop')
        self.driftButton.setCheckable(True)
        self.driftButton.clicked.connect(self.get_drift)
        self.driftButton.setToolTip('With on scan mode: ramp, psf: x/y')
        
        total_time = QtGui.QLabel('Total time (min):')
        refresh_time = QtGui.QLabel('Refresh time (s):')
        
        self.drift_totaltime = QtGui.QLineEdit('20')
        self.drift_refreshtime = QtGui.QLineEdit('40')

        layout4.addWidget(self.driftButton,        1,1)
        layout4.addWidget(total_time,              2,1)
        layout4.addWidget(self.drift_totaltime,    2,2)
        layout4.addWidget(refresh_time,            3,1)
        layout4.addWidget(self.drift_refreshtime,  3,2)
        
        self.drift_widget = pg.GraphicsLayoutWidget()
        
        #image scan
        
        imageWidget = pg.GraphicsLayoutWidget()
        imageWidget.setAspectLocked(True)
        #imageWidget.setMinimumHeight(50)
        #imageWidget.setMinimumWidth(50)
        
        self.img = pg.ImageItem()
        self.point_graph_CM = pg.ScatterPlotItem(size=10,
                                                 symbol='+', color='m')
        
        self.point_graph_CM_2 = pg.ScatterPlotItem(size=5,
                                                 symbol='+', color='b') 
      #   self.vb = imageWidget.addViewBox(row=1, col=1)
     #   self.vb.setMouseMode(pg.ViewBox.RectMode)
     
        self.xlabel = pg.AxisItem(orientation = 'left')
        labelStyle = {'color': '#FFF', 'font-size': '8pt'}
        self.xlabel.setLabel('X', units = 'um',**labelStyle)
        self.ylabel = pg.AxisItem(orientation = 'bottom')
        self.ylabel.setLabel('Y', units = 'um',**labelStyle)
        
        pixel_initial = round(2/34, 3)
        self.get_view_scale(pixel_initial, pixel_initial)
        
        self.vb = imageWidget.addPlot(axisItems={'bottom': self.ylabel, 'left': self.xlabel} )
        self.vb.addItem(self.img)
        self.vb.invertY()
        self.vb.setAspectLocked(True)

        self.hist = pg.HistogramLUTItem(image=self.img)
        self.hist.gradient.loadPreset('thermal')
# 'thermal', 'flame', 'yellowy', 'bipolar', 'spectrum',
# 'cyclic', 'greyclip', 'grey' # Solo son estos
        #self.hist.vb.setLimits(yMin=0, yMax=66000)

        for tick in self.hist.gradient.ticks:
            tick.hide()
            
        imageWidget.addItem(self.hist, row=0, col=1)
        
        dockArea = DockArea()
        hbox = QtGui.QHBoxLayout(self)

        viewDock = Dock('Viewbox',size=(100,100))
        viewDock.addWidget(imageWidget)
        viewDock.hideTitleBar()
        dockArea.addDock(viewDock)

        scanDock = Dock('Confocal parameters')
        scanDock.addWidget(self.paramWidget)
        dockArea.addDock(scanDock, 'right', viewDock)

        goCMDock = Dock('CM')
        goCMDock.addWidget(self.goCMWidget)
        dockArea.addDock(goCMDock, 'right', scanDock)

        driftDock = Dock('Drift measurment')
        driftDock.addWidget(self.driftWidget)
        dockArea.addDock(driftDock, 'bottom', goCMDock)
        
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
        elif QComboBox .currentText() == shutters[4]: # orange
            QComboBox.setStyleSheet("QComboBox{color: rgb(190,100,0);}\n")

    @pyqtSlot(float, float)
    def get_view_scale(self, px, py):
        
     #  print('scala nueva', px, py)
    
       self.xlabel.setScale(scale=px)
       self.ylabel.setScale(scale=py)
        
    @pyqtSlot(np.ndarray)
    def get_img(self, data_img):
        self.img.setImage(data_img)
       
    @pyqtSlot(list)
    def get_CMValues(self, data_cm):
        self.CxValue_1.setText(format(data_cm[0]))
        self.CyValue_1.setText(format(data_cm[1]))
        self.point_graph_CM.setData([data_cm[3]], [data_cm[2]])
        self.point_graph_CM.show()
        self.vb.addItem(self.point_graph_CM)
        
    @pyqtSlot(list)
    def get_CMValues_NP2(self, data_cm):
        self.CxValue_2.setText(format(data_cm[0]))
        self.CyValue_2.setText(format(data_cm[1]))
        self.point_graph_CM_2.setData([data_cm[3]], [data_cm[2]])
        self.point_graph_CM_2.show()
        self.vb.addItem(self.point_graph_CM_2)
        
    def get_drift(self):
        total_time = float(self.drift_totaltime.text())*60
        refresh_time = float(self.drift_refreshtime.text())
        color_laser = self.scan_laser.currentIndex()
        if self.driftButton.isChecked():
           self.driftSignal.emit(True, color_laser, total_time, refresh_time)
        else:
           self.driftSignal.emit(False, color_laser, total_time, refresh_time)
            

    @pyqtSlot(list)
    def plot_drift(self, drift):

        time = drift[0]
        xdrift = drift[1]
        ydrift = drift[2]

        subgrid = QtGui.QGridLayout()
        subgrid.addWidget(self.drift_widget)
        
        plotdrift = self.drift_widget.addPlot(row=2, col=2, title="Drift x, y")
        plotdrift.showGrid(x=True, y=True)
        plotdrift.setLabel('left', "Position CM")
        plotdrift.setLabel('bottom', "Time (s)")
        
        curve_x = plotdrift.plot(open='y')
        curve_y = plotdrift.plot(open='y')
        curve_x.setData(time, xdrift, pen=pg.mkPen('r', width=1), symbol='o')
        curve_y.setData(time, ydrift, pen=pg.mkPen('b', width=1), symbol='o')
        
        self.drift_widget.show()
        
    def closeEvent(self, event):

        reply = QtGui.QMessageBox.question(self, 'Quit', 'Are you sure to quit Confocal?',
                                           QtGui.QMessageBox.No |
                                           QtGui.QMessageBox.Yes)
        if reply == QtGui.QMessageBox.Yes:
            print("Confocal Close")
            event.accept()
            self.closeSignal.emit()
            self.close()

        else:
            event.ignore()
  
    def make_connection(self, backend):
        backend.scaleSignal.connect(self.get_view_scale)
        backend.dataSignal.connect(self.get_img)
        backend.CMValuesSignal.connect(self.get_CMValues)
        backend.CMValuesSignal_NP2.connect(self.get_CMValues_NP2)
        backend.plotdriftSignal.connect(self.plot_drift)

class Backend(QtCore.QObject):
    
    scaleSignal = pyqtSignal(float, float)
    dataSignal = pyqtSignal(np.ndarray)
    CMValuesSignal = pyqtSignal(list)
    CMValuesSignal_NP2 = pyqtSignal(list)
    scandoneSignal = pyqtSignal()
    plotdriftSignal = pyqtSignal(list)
    
    scanfinishSignal = pyqtSignal(np.ndarray, list, np.ndarray, np.ndarray)
    scanfinishSignal_dimers_center = pyqtSignal(np.ndarray, list, np.ndarray, np.ndarray)
    scanfinishSignal_dimers_pree = pyqtSignal(np.ndarray, np.ndarray, np.ndarray)
    scanfinishSignal_dimers_post = pyqtSignal(np.ndarray, np.ndarray, np.ndarray)
    
    def __init__(self, pi_device, task_nidaqmx,*args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.shuttertask = task_nidaqmx[0]
        
        self.pi_device = pi_device
        
        self.file_path = os.path.abspath("C:\Julian\Data_PyPrinting")
        
        self.PDtimer_stepxy = QtCore.QTimer()
        self.PDtimer_rampxy = QtCore.QTimer()
        self.PDtimer_rampxz = QtCore.QTimer()
        self.PDtimer_rampyx = QtCore.QTimer()
        self.PDtimer_rampyz = QtCore.QTimer()
        self.drifttimer = QtCore.QTimer()

   #     self.PDtimer_stepxy.timeout.connect(self.scan_step_xy)
        
   #     self.PDtimer_rampxy.timeout.connect(self.scan_ramp_xy)
   #     self.PDtimer_rampxz.timeout.connect(self.scan_ramp_xz)
        
   #     self.PDtimer_rampyx.timeout.connect(self.scan_ramp_yx)
   #     self.PDtimer_rampyz.timeout.connect(self.scan_ramp_yz)
        
   #     self.drifttimer.timeout.connect(self.drift)
        
        self.scan_mode_option  = Scanmodes[0]
        self.psf_mode_option  = PSFmodes[0]
        self.scan_ramp_parameters([2,2,34,34])
        
        self.cm_auto = False
        self.image_scan_option  = ScanImage[0]
        self.method_center_option  = MethodCenter[0]
        self.n_filter = 0.3  #numero para filtrar la imagem
        
        self.mode_printing = 'none'
        

    def x_create(self): 
        pos = self.pi_device.qPOS()
        x_pos = pos['A']
        y_pos = pos['B']
        z_pos = pos['C']
 
        return x_pos, y_pos, z_pos
    
    @pyqtSlot(str)
    def scan_mode(self, scan_mode_option):
        
        if scan_mode_option == Scanmodes[0]:
            
           self.scan_mode_option = Scanmodes[0]
           
        elif scan_mode_option == Scanmodes[1]:
            
           self.scan_mode_option = Scanmodes[1]
           
    @pyqtSlot(str)
    def psf_mode(self, psf_mode_option):
        
        if psf_mode_option == PSFmodes[0]:
            
           self.psf_mode_option = PSFmodes[0]
           
        elif psf_mode_option == PSFmodes[1]:
            
           self.psf_mode_option = PSFmodes[1]
           
        elif psf_mode_option == PSFmodes[2]:
            
           self.psf_mode_option = PSFmodes[2]
           
        elif psf_mode_option == PSFmodes[3]:
            
           self.psf_mode_option = PSFmodes[3]
           
    @pyqtSlot(str, str, str)        
    def start_scan_routines(self, laser, mode_printing, number_scan):
        
        self.mode_printing = mode_printing
        self.number_scan = number_scan
        self.laser = laser
        
        self.start_scan(self.laser)
        
    @pyqtSlot(int)     
    def start_scan_button(self, color_laser):    
                #this is for the routines Printing or Dimers:
        self.mode_printing = 'none'
        self.number_scan = 'none'
        self.laser = shutters[color_laser]
    
        self.start_scan(self.laser)
              
    def start_scan(self, laser):  
        print("start scan")

        self.signal_scan_stop = False
        
        self.image = np.zeros((self.Ny, self.Nx))
        self.image_gone = np.zeros((self.Ny, self.Nx)) 
        self.image_back = np.zeros((self.Ny, self.Nx)) 
        
        if self.scan_mode_option == Scanmodes[0]:
            print('Modo Rampa')
            if self.psf_mode_option  == PSFmodes[0]:
                self.start_scan_ramp_xy(self.laser)
            elif self.psf_mode_option  == PSFmodes[1]:
                self.start_scan_ramp_xz(self.laser)
            elif self.psf_mode_option  == PSFmodes[2]:
                self.start_scan_ramp_yx(self.laser)   
            elif self.psf_mode_option  == PSFmodes[3]:
                self.start_scan_ramp_yz(self.laser)   
        elif self.scan_mode_option == Scanmodes[1]:
            print('Modo Step')
            if self.psf_mode_option  == PSFmodes[0]:
                self.start_scan_step(self.laser) 
            else:
                print('Modo no programado')
     
    @pyqtSlot()   
    def stop_scan(self):
        
        if not self.signal_scan_stop: 
          print("stop scan")
          closeShutter(self.laser, self.shuttertask)

        if self.mode_printing == 'none':
          
            if self.scan_mode_option == Scanmodes[0]:
                if self.psf_mode_option == PSFmodes[0]:
                    self.PDtimer_rampxy.stop()
                    self.pi_device.MOV(['A','B'], [self.x_pos, self.y_pos])
                elif self.psf_mode_option == PSFmodes[1]:
                    self.PDtimer_rampxz.stop()   
                    self.pi_device.MOV(['A','C'], [self.x_pos, self.z_pos])
                elif self.psf_mode_option == PSFmodes[2]:
                    self.PDtimer_rampyx.stop()   
                    self.pi_device.MOV(['B','A'], [self.y_pos, self.x_pos])
                elif self.psf_mode_option == PSFmodes[3]:
                    self.PDtimer_rampyz.stop()   
                    self.pi_device.MOV(['B','C'], [self.y_pos, self.z_pos])
                     
            elif self.scan_mode_option == Scanmodes[1]:
                if self.psf_mode_option == PSFmodes[0]:
                    self.PDtimer_stepxy.stop()
                    self.pi_device.MOV(['A','B'], [self.x_pos, self.y_pos])
                else:
                    print('Modo no programado')
                 
            
    def start_scan_step(self, laser):
        
        self.tic = ptime.time()  
        self.i = 0  
        self.j = 0
        self.x_pos, self.y_pos, self.z_pos = self.x_create()

       # dy = self.range_y/self.Ny
       # dx = self.range_x/self.Nx

      #  matrix_scan_step_x = np.linspace(self.x_pos - self.range_x/2, self.x_pos + self.range_x/2, self.Nx)
      #  matrix_scan_step_y = np.linspace(self.y_pos - self.range_y/2, self.y_pos + self.range_y/2, self.Ny)
        
        dy = self.range_y/self.Ny
        dx = self.range_x/self.Nx

        matrix_scan_step_x = np.arange(self.x_pos - self.range_x/2 + dx/2, self.x_pos + self.range_x/2, dx)
        matrix_scan_step_y = np.arange(self.y_pos - self.range_y/2 + dy/2, self.y_pos + self.range_y/2, dy)

        self.matrix_scan_step = [matrix_scan_step_x, matrix_scan_step_y]
        
        self.matrix_scan_spiral = to_spiral(self.matrix_scan_step, 'cw')
        
       # print('matrix step by step',self.matrix_scan_step)
       # print('matrix spiral',self.matrix_scan_spiral)

        openShutter(laser, self.shuttertask)
        time.sleep(0.05)
        self.PDtimer_stepxy.start(0)
    
    @pyqtSlot(str)
    def start_scan_ramp_xy(self, laser):
        
        self.tic = ptime.time()  
        self.i = 0  
        self.x_pos, self.y_pos, self.z_pos = self.x_create()
        self.scan_ramp_x_lin_configuration(self.x_pos)

        openShutter(laser, self.shuttertask)
        #time.sleep(0.15)
        #self.PDtimer_rampxy.start(2*self.tau*10**3) 
        self.PDtimer_rampxy.start(0) 
        
    def start_scan_ramp_xz(self, laser):

        self.tic = ptime.time()  
        self.i = 0  
        self.x_pos, self.y_pos, self.z_pos = self.x_create()
        self.scan_ramp_x_lin_configuration(self.x_pos)

        openShutter(laser, self.shuttertask)
       # time.sleep(0.15)
        #self.PDtimer_rampxz.start(2*self.tau*10**3)  
        self.PDtimer_rampxz.start(0) 
        
    def start_scan_ramp_yx(self, laser):

        self.tic = ptime.time()  
        self.i = 0  
        self.x_pos, self.y_pos, self.z_pos = self.x_create()
        self.scan_ramp_y_lin_configuration(self.y_pos)

        openShutter(laser, self.shuttertask)
       # time.sleep(0.15)
        #self.PDtimer_rampxz.start(2*self.tau*10**3)  
        self.PDtimer_rampyx.start(0) 
        
    def start_scan_ramp_yz(self, laser):

        self.tic = ptime.time()  
        self.i = 0  
        self.x_pos, self.y_pos, self.z_pos = self.x_create()
        self.scan_ramp_y_lin_configuration(self.y_pos)

        openShutter(laser, self.shuttertask)
       # time.sleep(0.15)
        #self.PDtimer_rampxz.start(2*self.tau*10**3)  
        self.PDtimer_rampyz.start(0) 
        
    @pyqtSlot(list)            
    def scan_step_parameters(self, parameters): 
        
        self.range_x = parameters[0]
        self.range_y = parameters[1]
        self.Nx  = parameters[2]
        self.Ny = parameters[3]
        
        self.Nph = 10 #cantidad de puntos que lee el photodiodo por pixel
        self.rate = rateNI/10  #frecuencia de sampleo por canal del photodiodo
        self.time_step_x_lin = (self.Nph/self.rate + 0.01)*self.Nx #aprox. segundos para hacer una linea en x   

        px = round(self.range_x/self.Nx, 3)
        py = round(self.range_y/self.Ny, 3)
        self.scaleSignal.emit(px, py)

    @pyqtSlot(list)       
    def scan_ramp_parameters(self, parameters): 
        
        self.range_x = parameters[0]
        self.range_y = parameters[1]
        self.Nx  = parameters[2]
        self.Ny = parameters[3]
        
        self.extra = self.range_x/6
        self.range_total = self.range_x + 2*self.extra
        
        self.extra_y = self.range_y/6
        self.range_total_y = self.range_y + 2*self.extra_y

        self.frequency = rateNI/100  #frecuencia de sampleo por canal del photodiodo
        factor_ramp = 1/1200  
        #Hay problemas a partir de factor_ramp = 1/1000 con reconocer solo 2 puntos del trigger
        
        self.frequency_ramp = factor_ramp*rateNI/100 #frecuencia de rampa total en ida
        self.tau = 1/self.frequency_ramp
        
        Ntotal = int(self.frequency/self.frequency_ramp)  
        self.Nramp = 2*Ntotal #puntos de interes de lectura
        
        px = round(self.range_x/self.Nx, 3)
        py = round(self.range_y/self.Ny, 3)
        self.scaleSignal.emit(px, py)

     
    def scan_step_xy(self):   
        
        if self.j < self.Ny:
            if self.i < self.Nx :
                self.pi_device.MOV(['A', 'B'], [self.matrix_scan_step[0][self.i], self.matrix_scan_step[1][self.j]])    
                step_profile  = self.scan_step()     
                self.image[self.j, self.i] = step_profile
                self.dataSignal.emit(self.image)
                self.i = self.i + 1 
                
            else:
                self.i = 0
                self.j = self.j + 1       
           
        else:
            
             self.PDtimer_stepxy.stop()
             #self.dataSignal.emit(self.image)
             self.signal_scan_stop = True
             closeShutter(self.laser, self.shuttertask)
             
             x_o, y_o = self.CMmeasure() 
             center_mass = [x_o, y_o]
             
             print(round(ptime.time()-self.tic, 3), "Time scan ramp x/y")
             
            # self.pi_device.MOV(['A','B'], [self.x_pos, self.y_pos])
            # print(ptime.time()-self.tic, "Time scan ramp x/y")
           #  self.scandoneSignal.emit()
           
             time.sleep(0.1)
             
             if self.mode_printing == 'none':
                self.saveFrame()
                if self.cm_auto:
                    self.moveto(x_o, y_o)
                    self.scandoneSignal.emit()
                else:
                    self.pi_device.MOV(['A','B'], [self.x_pos, self.y_pos])
                    self.scandoneSignal.emit()
                            
             if self.mode_printing == 'printing':
                self.scanfinishSignal.emit(self.image, center_mass, self.image_gone, self.image_back)
                
             if self.mode_printing == 'dimers':
                 if self.number_scan == 'center_scan':
                     self.scanfinishSignal_dimers_center.emit(self.image, center_mass, self.image_gone, self.image_back)
                 elif self.number_scan == 'pree_scan':
                     self.scanfinishSignal_dimers_pree.emit(self.image, self.image_gone, self.image_back)
                 elif self.number_scan == 'post_scan':
                     self.scanfinishSignal_dimers_post.emit(self.image, self.image_gone, self.image_back)
                     
             if self.mode_printing == 'drift':
                self.saveFrame_drift()
                self.x_cm_drift.append(x_o)
                self.y_cm_drift.append(y_o)
                self.pi_device.MOV(['A','B'], [self.x_pos, self.y_pos])
                self.scandoneSignal.emit()
            
        
    def scan_step(self):
        
        PDtask = channels_photodiodos(nidaqmx, self.rate, self.Nph) 
        PDstep = PDtask.read(self.Nph)  
        PDtask.wait_until_done()
        PDtask.close() 
        
        step_profile = np.mean(PDstep[PD_channels[self.laser]])
       
        return step_profile
        
    def scan_ramp_xy(self):
         
        dy = self.range_y/self.Ny
                        
        if self.i < self.Ny: 
            
           self.pi_device.MOV('B', self.y_pos - self.range_y/2 + dy/2 + self.i*dy) 
           
          # while any(self.pi_device.IsGeneratorRunning().values()):
           #   time.sleep(0.01)          
           
           imagen_lin_gone, imagen_lin_back = self.scan_ramp_x_lin()
        
           imagen_lin_mean_gone = average(imagen_lin_gone, self.Nx)
           imagen_lin_mean_back = average(imagen_lin_back, self.Nx)
    
           self.image_gone[self.i, :] = imagen_lin_mean_gone
           self.image_back[self.i, :] = imagen_lin_mean_back
           
           self.image = self.image_gone + np.fliplr(self.image_back)
           
           self.dataSignal.emit(self.image)
           
           self.i = self.i + 1
           
        else: 
             self.PDtimer_rampxy.stop()
             #self.dataSignal.emit(self.image)
             self.signal_scan_stop = True
             closeShutter(self.laser, self.shuttertask)
             
             self.image_back = np.fliplr(self.image_back)
             self.image = self.image_gone + self.image_back
             
             x_o, y_o = self.CMmeasure() 
             center_mass = [x_o, y_o]
             
             print(round(ptime.time()-self.tic, 3), "Time scan ramp x/y")
             
            # self.pi_device.MOV(['A','B'], [self.x_pos, self.y_pos])
            # print(ptime.time()-self.tic, "Time scan ramp x/y")
           #  self.scandoneSignal.emit()
           
             time.sleep(0.1)
             
             if self.mode_printing == 'none':
                self.saveFrame()
                if self.cm_auto:
                    self.moveto(x_o, y_o)
                    self.scandoneSignal.emit()
                else:
                    self.pi_device.MOV(['A','B'], [self.x_pos, self.y_pos])
                    self.scandoneSignal.emit()
                            
             if self.mode_printing == 'printing':
                self.scanfinishSignal.emit(self.image, center_mass, self.image_gone, self.image_back)
                
             if self.mode_printing == 'dimers':
                 if self.number_scan == 'center_scan':
                     self.scanfinishSignal_dimers_center.emit(self.image, center_mass, self.image_gone, self.image_back)
                 elif self.number_scan == 'pree_scan':
                     self.scanfinishSignal_dimers_pree.emit(self.image, self.image_gone, self.image_back)
                 elif self.number_scan == 'post_scan':
                     self.scanfinishSignal_dimers_post.emit(self.image, self.image_gone, self.image_back)
                     
             if self.mode_printing == 'drift':
                self.saveFrame_drift()
                self.x_cm_drift.append(x_o)
                self.y_cm_drift.append(y_o)
                self.pi_device.MOV(['A','B'], [self.x_pos, self.y_pos])
                self.scandoneSignal.emit()
                     
    def scan_ramp_xz(self):
        
        dz = self.range_y/self.Ny
        
        if self.i < self.Ny: 
            
           self.pi_device.MOV('C', self.z_pos - self.range_y/2 + dz/2 + self.i*dz) 
           
           imagen_lin_gone, imagen_lin_back = self.scan_ramp_x_lin()
        
           imagen_lin_mean_gone = average(imagen_lin_gone, self.Nx)
           imagen_lin_mean_back = average(imagen_lin_back, self.Nx)
    
           self.image_gone[self.i, :] = imagen_lin_mean_gone
           self.image_back[self.i, :] = imagen_lin_mean_back
        
           self.image = self.image_gone +  np.fliplr(self.image_back)
           
           self.dataSignal.emit(self.image)
           
           self.i = self.i + 1
           
        else: 
            self.PDtimer_rampxz.stop()
            self.signal_scan_stop = True
            closeShutter(self.laser, self.shuttertask)
            time.sleep(0.1)
            
            self.image_back = np.fliplr(self.image_back)
            self.image = self.image_gone + self.image_back
            
            self.pi_device.MOV(['A','C'], [self.x_pos, self.z_pos])
            print(round(ptime.time()-self.tic, 3), "Time scan ramp x/z")
            self.saveFrame()
            self.scandoneSignal.emit()
            
            
    def scan_ramp_yx(self):
        
        dx = self.range_x/self.Nx
        
        if self.i < self.Nx: 
            
           self.pi_device.MOV('A', self.x_pos - self.range_x/2 + dx/2 + self.i*dx) 
           
           imagen_lin_gone, imagen_lin_back = self.scan_ramp_y_lin()
        
           imagen_lin_mean_gone = average(imagen_lin_gone, self.Ny)
           imagen_lin_mean_back = average(imagen_lin_back, self.Ny)
    
           self.image_gone[:, self.i] = imagen_lin_mean_gone
           self.image_back[:, self.i] = imagen_lin_mean_back
           
           self.image = self.image_gone + np.flipud(self.image_back) 
           
           self.dataSignal.emit(self.image)
           
           self.i = self.i + 1
           
        else: 
            
            self.PDtimer_rampyx.stop()
            self.signal_scan_stop = True
            closeShutter(self.laser, self.shuttertask)
            time.sleep(0.1)
            
            self.image_back = np.flipud(self.image_back)
            self.image = self.image_gone + self.image_back
            
            x_o, y_o = self.CMmeasure()
            center_mass = [x_o, y_o]
            
            print(round(ptime.time()-self.tic, 3), "Time scan ramp y/x")
            
            if self.mode_printing == 'none':
                self.saveFrame()
                if self.cm_auto:
                    self.moveto(x_o, y_o)
                    self.scandoneSignal.emit()
                else:
                    self.pi_device.MOV(['A','B'], [self.x_pos, self.y_pos])
                    self.scandoneSignal.emit()
                    
                if self.mode_printing == 'printing':
                    self.scanfinishSignal.emit(self.image, center_mass, self.image_gone, self.image_back)

                if self.mode_printing == 'dimers':
                    if self.number_scan == 'center_scan':
                        self.scanfinishSignal_dimers_center.emit(self.image, center_mass, self.image_gone, self.image_back)
                    elif self.number_scan == 'pree_scan':
                        self.scanfinishSignal_dimers_pree.emit(self.image, self.image_gone, self.image_back)
                    elif self.number_scan == 'post_scan':
                        self.scanfinishSignal_dimers_post.emit(self.image, self.image_gone, self.image_back)
                 
                if self.mode_printing == 'drift':
                    self.saveFrame_drift()
                    self.x_cm_drift.append(x_o)
                    self.y_cm_drift.append(y_o)
                    self.pi_device.MOV(['A','B'], [self.x_pos, self.y_pos])
                    self.scandoneSignal.emit()
                
                
    def scan_ramp_yz(self):
        
        dz = self.range_x/self.Nx
        
        if self.i < self.Nx: 
            
           self.pi_device.MOV('C', self.z_pos - self.range_x/2 + dz/2 + self.i*dz) 
           
           imagen_lin_gone, imagen_lin_back = self.scan_ramp_y_lin()
        
           imagen_lin_mean_gone = average(imagen_lin_gone, self.Ny)
           imagen_lin_mean_back = average(imagen_lin_back, self.Ny)
    
           self.image_gone[self.i, :] = imagen_lin_mean_gone
           self.image_back[self.i, :] = imagen_lin_mean_back
        
           self.image = self.image_gone + np.fliplr(self.image_back) 
           
           self.dataSignal.emit(self.image)
           
           self.i = self.i + 1
           
        else: 
            self.PDtimer_rampyz.stop()
            self.signal_scan_stop = True
            closeShutter(self.laser, self.shuttertask)
            time.sleep(0.1)
            
            self.image_back = np.fliplr(self.image_back)
            self.image = self.image_gone + self.image_back
            
            self.pi_device.MOV(['B','C'], [self.y_pos, self.z_pos])
            print(round(ptime.time()-self.tic, 3), "Time scan ramp y/z")
            self.saveFrame()
            self.scandoneSignal.emit()
            
    def scan_ramp_x_lin_configuration(self, x_pos):
        
        size_points = (self.range_x/self.Nx)
        Npoints = int(self.range_total/size_points)*20
        Nspeed = int(Npoints/4)  #antes 12/07 era int(Npoints/16)
        
        WTRtime = int(1/(self.frequency_ramp*servo_time*Npoints))
        self.pi_device.WTR(1, WTRtime, 0)
        
        #opcion 2 lineales ida y vuelta:
        self.pi_device.WAV_LIN(1, 0, Npoints, "X", Nspeed, self.range_total, 0, Npoints)
        self.pi_device.WAV_LIN(1, 0, Npoints, "&", Nspeed, -self.range_total, self.range_total, Npoints)
        
        #opcion 1 rampa ida y vuelta:
        #self.pi_device.WAV_RAMP(1, 0, Npoints*2, "X", Npoints, Nspeed,  self.range, 0, Npoints*2)
              
        nciclos = 1
        self.pi_device.WGC(1, nciclos)

        xo = x_pos - self.range_total/2

        self.pi_device.MOV('A', xo)
        self.pi_device.WOS(1, xo)
        
        self.pi_device.TWC() 
        self.pi_device.CTO(1, 3, 3)
        self.pi_device.CTO(1, 5, xo + self.extra)
        self.pi_device.CTO(1, 6, xo + self.range_total - self.extra)
        
    def scan_ramp_x_lin(self):

        PDtask = channels_photodiodos(nidaqmx, self.frequency, self.Nramp)
        channels_triggers(PDtask, 'X')

        self.pi_device.WGO(1, True) 
        data_read = PDtask.read(self.Nramp)
        PDtask.close()

        data_ph = np.array(data_read[PDchans.index(PD_channels[self.laser])])
        
        data_trigger = np.array(data_read[len(PDchans)])  #los fotodiodos son los primeros  (0, 1, 2, 6), el 4 es el trigger

        x_profile_gone, x_profile_back = self.x_profiles(data_ph, data_trigger)

        return x_profile_gone, x_profile_back

    def x_profiles(self, data_ph, data_trigger):
        
       # data_trigger = average(data_trigger, int(self.Nramp/10))
       # data_ph = average(data_ph, int(self.Nramp/10))
        
       # print('data trigger x', data_trigger)

        derivative = np.diff(data_trigger)
        index_dt_pos = np.where(derivative >= 1.5)[0]
        index_dt_neg = np.where(derivative <= -1.5)[0]
        
        #print('index de trigger flanco ascendete', index_dt_pos)
        #print('index de trigger flanco desscendete', index_dt_neg)
        
        L = len(data_trigger)
        first_element_pos_asc = index_dt_pos[0]
        dt_pos_asc = np.where(index_dt_pos > first_element_pos_asc + L/3)[0]
        second_element_pos_asc  = index_dt_pos[dt_pos_asc[0]]
        
        dt_neg_dsc_first = np.where(index_dt_neg > first_element_pos_asc + L/6)[0]
        first_element_pos_dsc = index_dt_neg[dt_neg_dsc_first[0]]
        dt_pos_dsc = np.where(index_dt_neg > first_element_pos_dsc + L/3)[0]
        second_element_pos_dsc  = index_dt_neg[dt_pos_dsc[0]]
        
       # print('flanco ascendetes select', first_element_pos_asc, second_element_pos_asc)
      #  print('flanco desscendete select', first_element_pos_dsc, second_element_pos_dsc)
        
        x_profile_gone = data_ph[first_element_pos_asc:first_element_pos_dsc]
        x_profile_back  = data_ph[second_element_pos_asc:second_element_pos_dsc]

        return x_profile_gone, x_profile_back
    
    def scan_ramp_y_lin_configuration(self, x_pos):
        
        size_points = (self.range_y/self.Ny)
        Npoints = int(self.range_total/size_points)*20
        Nspeed = int(Npoints/4)  #antes 12/07 era int(Npoints/16)
        
        WTRtime = int(1/(self.frequency_ramp*servo_time*Npoints))
        self.pi_device.WTR(2, WTRtime, 0)
        
        #opcion 2 lineales ida y vuelta:
        self.pi_device.WAV_LIN(2, 0, Npoints, "X", Nspeed, self.range_total_y, 0, Npoints)
        self.pi_device.WAV_LIN(2, 0, Npoints, "&", Nspeed, -self.range_total_y, self.range_total_y, Npoints)
        
        #opcion 1 rampa ida y vuelta:
        #pi_device.WAV_RAMP(1, 0, Npoints*2, "X", Npoints, Nspeed,  self.range, 0, Npoints*2)
              
        nciclos = 1
        self.pi_device.WGC(2, nciclos)

        xo = x_pos - self.range_total_y/2

        self.pi_device.MOV('B', xo)
        self.pi_device.WOS(2, xo)
        
        self.pi_device.TWC() 
        self.pi_device.CTO(2, 3, 3)
        self.pi_device.CTO(2, 5, xo + self.extra_y)
        self.pi_device.CTO(2, 6, xo + self.range_total_y - self.extra_y)
        
    def scan_ramp_y_lin(self):

        PDtask = channels_photodiodos(self.frequency, self.Nramp)
        channels_triggers(PDtask, 'Y')

        self.pi_device.WGO(2, True) 
        data_read = PDtask.read(self.Nramp)
        PDtask.close()

        data_ph = np.array(data_read[PDchans.index(PD_channels[self.laser])])
        data_trigger = np.array(data_read[len(PDchans)])  #los fotodiodos son los primeros  (0, 1, 2, 6), el 4 es el trigger

        x_profile_gone, x_profile_back = self.x_profiles(data_ph, data_trigger)

        return x_profile_gone, x_profile_back
    
    @pyqtSlot(str)
    def image_scan(self, image_scan_option):
        
        if image_scan_option == ScanImage[0]:
            
           self.image_scan_option = ScanImage[0]
           
        elif image_scan_option == ScanImage[1]:
            
           self.image_scan_option = ScanImage[1]
           
        elif image_scan_option == ScanImage[2]:
            
           self.image_scan_option = ScanImage[2]
        
        elif image_scan_option == ScanImage[3]:
            
           self.image_scan_option = ScanImage[3]
               
           
    @pyqtSlot(str)
    def method_center(self, method_center_option):
        
        if method_center_option == MethodCenter[0]:
            
           self.method_center_option = MethodCenter[0]
           
        elif method_center_option == MethodCenter[1]:
            
           self.method_center_option = MethodCenter[1]
           
        elif method_center_option == MethodCenter[2]:
            
           self.method_center_option = MethodCenter[2]
           
        elif method_center_option == MethodCenter[3]:
            
           self.method_center_option = MethodCenter[3]
           
    @pyqtSlot(float)
    def filter_method_center(self, nfilter):
        
        self.n_filter = nfilter
    
    def norm_image(self, Z):
        
        Zmin = np.min(Z)
        Zmax = np.max(Z)
        Zn = (Z-Zmin)/(Zmax- Zmin)  #lleva a ceros y unos
        
        if self.image_scan_option == ScanImage[0]: #caso NPs maximos
            Zn = Zn #queda NP = 1, bkg = 0
            print('go to CM de un maximo')  
                    
        elif self.image_scan_option == ScanImage[1]: #caso NPs minimos
            print('go to CM de un minimo')  
            Zn = Zn - 1 #queda NP = -1, bkg = 0
            Zn = np.abs(Zn)  #queda NP = 1, bkg = 0
                        
        elif self.image_scan_option == ScanImage[2]: #caso NPs puede ser maximos o minimos y no sabemos
            bkg = np.mean(Z)
            choose_umbral = 0.3
            
            if bkg > choose_umbral*Zmax:   
                print('choose: go to CM de un minimo')
                Zn = Zn - 1
                Zn = np.abs(Zn)  
            else:
                print('choose: go to CM de un maximo')
                Zn = Zn
                
        elif self.image_scan_option == ScanImage[4]:  #para caso de 2 NP, una minima y la otra maxima
            bkg = np.mean(Z)
            Zn = (Z-bkg)/(Zmax- bkg)  #lleva a ceros el bkg, 1 NP maxima, <0 NP minima
            Zn = np.abs(Zn)  #lleva a ceros el bkg, 1 NP maxima, >0 NP minima            
                
        return Zn
    
    def filter_image(self, image, image_bin, n_filter):
        
        for i in range(len(image[:,1])):
            for j in range (len(image[1,:])):
                if image_bin[i,j] < n_filter:
                    image_bin[i,j] = 0
                    
        return image_bin
    
        
    def filter_image_2(self, image_bin):
        
        bkg = np.mean(image_bin)
    
        n_filter = bkg/np.max(image_bin)
        
        for i in range(len(image_bin[:,1])):
            for j in range (len(image_bin[1,:])):
                if image_bin[i,j] < n_filter:
                    image_bin[i,j] = bkg
                    
        return image_bin
    
    
    def coordinates_position(self, xo, yo):
        
        dy = self.range_y/self.Ny
        dx = self.range_x/self.Nx

        xo_um = np.round(self.x_pos - self.range_x/2 + dx/2 + (xo*dx), 3)
        yo_um = np.round(self.y_pos - self.range_y/2 + dy/2 + (yo*dy), 3)
        
        return xo_um, yo_um
           
    #  CMmeasure
    def CMmeasure(self):

        Z = self.image #ida y vuelta
        
        Zn = self.norm_image(Z)  #normalizo la imagen para que quede con 1
        
        if self.method_center_option == MethodCenter[0]:
            
            Zfilter = self.filter_image(Z, Zn, self.n_filter)
            xo, yo = center_of_mass(Zfilter)  #ycm, xcm = ndimage.measurements.center_of_mass(Zn)
            xo_um, yo_um = self.coordinates_position(xo, yo)
            self.CMValuesSignal.emit([xo_um, yo_um, xo, yo])

        elif self.method_center_option == MethodCenter[1]:
        
            Zfilter = self.filter_image(Z, Zn, self.n_filter)
            x_cm, y_cm = center_of_mass(Zfilter)
            xo, yo = center_of_gauss2D(Zn, x_cm, y_cm)
            xo_um, yo_um = self.coordinates_position(xo, yo)
            self.CMValuesSignal.emit([xo_um, yo_um, xo, yo])
            
        elif self.method_center_option == MethodCenter[2]:
            
            Zfilter = self.filter_image(Z, Zn, self.n_filter)
            xo_1, yo_1, xo_2, yo_2 = find_two_centers(Zfilter)
            xo, yo, xo2, yo2 = two_centers_of_gauss2D(Zn, xo_1, yo_1, xo_2, yo_2)
            
            xo_um, yo_um = self.coordinates_position(xo, yo)
            xo2_um, yo2_um = self.coordinates_position(xo2, yo2)
            
            self.xo2_um = xo2_um
            self.yo2_um = yo2_um
            
            self.CMValuesSignal.emit([xo_um, yo_um, xo, yo])
            self.CMValuesSignal_NP2.emit([xo2_um, yo2_um, xo2, yo2])
            
        elif self.method_center_option == MethodCenter[3]:
        
            Zfilter = self.filter_image_2(Zn)
            Z =rvt.rvt(Zfilter,rmin=1,rmax=10)
    
            Zmin = np.min(Z)
            Zmax = np.max(Z)
            Zn = (Z-Zmin)/(Zmax- Zmin)
        
            x_cm, y_cm = center_of_mass(Zn)
            xo, yo = center_of_gauss2D(Zn, x_cm, y_cm)
            
        return xo_um, yo_um

    @pyqtSlot()  
    def goCM(self):
        
        xo, yo = self.CMmeasure()

        self.moveto(xo, yo)
        self.scandoneSignal.emit()
        
    @pyqtSlot(bool)  
    def goCM_auto(self, cm_auto):
        
        self.cm_auto = cm_auto
        
    @pyqtSlot()  
    def goCM_NP2(self):
        
        xo, yo = self.CMmeasure()

        self.moveto(self.xo2_um, self.yo2_um)
        self.scandoneSignal.emit()

    def moveto(self, x, y):
        """moves the position along the axis to a specified point.
        Cambie todo paraque ande con la PI"""
        axis = ['A', 'B']
        targets = [x, y]
        self.pi_device.MOV(axis, targets)
        while not all(self.pi_device.qONT(axis).values()):
            time.sleep(0.01)
        
    @pyqtSlot(str)        
    def direction(self, file_name):
        self.file_path = file_name

    @pyqtSlot()
    def saveFrame(self):
        """ Config the path and name of the file to save, and save it"""   
        
        filepath = self.file_path
        timestr = time.strftime("%Y%m%d-%H%M%S")
        
        name = str(filepath + "/" + "scan_" + timestr + ".tiff")
        guardado = Image.fromarray(np.transpose(self.image))
        guardado.save(name)
        
        name_gone = str(filepath + "/" + "image_gone_" + timestr + ".tiff")
        guardado_gone = Image.fromarray(np.transpose(self.image_gone))
        guardado_gone.save(name_gone)
        
        name_back = str(filepath + "/" + "image_back_" + timestr + ".tiff")
       # guardado_back = Image.fromarray((np.fliplr(np.transpose( np.flip(self.image_back) ))))
       
        guardado_back = Image.fromarray(np.transpose(self.image_back))
        guardado_back.save(name_back)
        
        print("\n Scan saved\n")

            
    @pyqtSlot(bool, int, float, float)
    def measurment_drift(self, play_stop_bool, color_laser, time_total, time_refresh):
        
        self.laser = shutters[color_laser]
        
        if play_stop_bool:
            
           self.play_drift(time_total, time_refresh)
             
        else:
            
            self.stop_drift()
        
        
    def play_drift(self, time_total, time_refresh):
        
        print('Start measurment Drift. Wait 30s to first scan')
        
        folder = os.path.join(self.file_path, 'Drift')
        
        if not os.path.exists(folder):
            os.makedirs(folder)
        
        self.time_inicial = ptime.time()
        self.n_drift = 0
        
       # time_refresh = 40 #s
       # time_total = 60*20 #min
        
        self.N = int(time_total/time_refresh)
        #self.time = np.arange(0, time_total, time_refresh)

        self.x_cm_drift = []
        self.y_cm_drift = []
        self.time = []
        
        self.start_scan_routines(self.laser, mode_printing = 'drift', number_scan = 'none')
        step_time = np.around(ptime.time() - self.time_inicial, 2)
        self.time.append(step_time)
        
       # x_cm, y_cm = self.CMmeasure()
       # self.x_cm_drift[self.n_drift] = x_cm
       # self.y_cm_drift[self.n_drift] = y_cm
        
       # self.plotdriftSignal.emit([self.time, self.x_cm_drift, self.y_cm_drift])
        
        self.drifttimer.start(time_refresh*10**3)
        
    def stop_drift(self):
        
        self.drifttimer.stop()
        self.plotdriftSignal.emit([self.time, self.x_cm_drift, self.y_cm_drift])
        file_name = os.path.join(self.file_path, 'Drift', time.strftime("%Y%m%d-%H%M%S") + '_Drift.txt')
        np.savetxt(file_name, np.transpose([self.time, self.x_cm_drift, self.y_cm_drift]))
        print('Finish measurment Drift')
        self.mode_printing = 'none'
        
    def drift(self):
        
        if self.n_drift < self.N - 1:
            
            self.n_drift = self.n_drift + 1
            
            self.start_scan_routines(self.laser, mode_printing = 'drift', number_scan = 'none')
            step_time = np.around(ptime.time() - self.time_inicial, 2)
            self.time.append(step_time)
            self.plotdriftSignal.emit([self.time, self.x_cm_drift, self.y_cm_drift])
            
        else:
            
            self.stop_drift()
            
            
    @pyqtSlot()
    def saveFrame_drift(self):
        """ Config the path and name of the file to save, and save it"""   
        
        filepath = os.path.join(self.file_path, 'Drift')
        timestr = str(round(float(time.strftime("%M")) + float(time.strftime("%S"))/60,2))
        
        name = str(filepath + "/" + "scan_" + "_minute_" + timestr + ".tiff")
        guardado = Image.fromarray(np.transpose(self.image))
        guardado.save(name)
        
        name_gone = str(filepath + "/" + "image_gone_" + "_minute_" + timestr + ".tiff")
        guardado_gone = Image.fromarray(np.transpose(self.image_gone))
        guardado_gone.save(name_gone)
        
        name_back = str(filepath + "/" + "image_back_" + timestr + ".tiff")
       # guardado_back = Image.fromarray((np.fliplr(np.transpose( np.flip(self.image_back) ))))
       
        guardado_back = Image.fromarray(np.transpose(self.image_back))
        guardado_back.save(name_back)
        
        print("\n Scan saved\n")

           
    @pyqtSlot()
    def close(self):
        self.pi_device.CloseConnection()
        #PDtask.close()
        #shuttertask.close()
           

    def make_connection(self, frontend):
        
        frontend.scan_modeSignal.connect(self.scan_mode)
        frontend.psf_modeSignal.connect(self.psf_mode)
        
        frontend.startSignal.connect(self.start_scan_button)
        frontend.stopSignal.connect(self.stop_scan)

        frontend.parametersrampSignal.connect(self.scan_ramp_parameters) 
        frontend.parametersstepSignal.connect(self.scan_step_parameters)
        
        frontend.image_scanSignal.connect(self.image_scan)
        frontend.method_centerSignal.connect(self.method_center)
        frontend.filterSignal.connect(self.filter_method_center)
        frontend.CMSignal.connect(self.goCM)
        frontend.CMautoSignal.connect(self.goCM_auto)
        frontend.CMSignal_NP2.connect(self.goCM_NP2)
        
        frontend.driftSignal.connect(self.measurment_drift)

        frontend.saveSignal.connect(self.saveFrame)
        
        frontend.closeSignal.connect(self.close)


# %% Otras Funciones
def gaussian(height, center_x, center_y, width_x, width_y):
    """Returns a gaussian function with the given parameters"""
    width_x = float(width_x)
    width_y = float(width_y)
    return lambda x, y: height*np.exp(
                -(((center_x-x)/width_x)**2+((center_y-y)/width_y)**2)/2)

def moments(data):
    """Returns (height, x, y, width_x, width_y)
    the gaussian parameters of a 2D distribution by calculating its
    moments """
    total = data.sum()
    X, Y = np.indices(data.shape)
    x = (X*data).sum()/total
    y = (Y*data).sum()/total
    col = data[:, int(y)]
    width_x = np.sqrt(np.abs((np.arange(col.size)-y)**2*col).sum()/col.sum())
    row = data[int(x), :]
    width_y = np.sqrt(np.abs((np.arange(row.size)-x)**2*row).sum()/row.sum())
    height = data.max()
    return height, x, y, width_x, width_y

def fitgaussian(data):
    """Returns (height, x, y, width_x, width_y)
    the gaussian parameters of a 2D distribution found by a fit"""
    params = moments(data)
    errorfunction = lambda p: np.ravel(gaussian(*p)(*np.indices(data.shape)) -
                                       data)
    p, success = optimize.leastsq(errorfunction, params)
    return p


def find_nearest(array, value):
    idx = (np.abs(array-value)).argmin()
    return array[idx]

def average(arr, n):
    
    resto = len(arr)//n
    end = resto*n
    arr_new = np.mean(arr[:end].reshape(-1,resto),1)

    return arr_new
    
#%%
        
if __name__ == '__main__':

       #app = QtGui.QApplication([])
    
    if not QtGui.QApplication.instance():
        app = QtGui.QApplication([])
    else:
        app = QtGui.QApplication.instance() 

    gui = Frontend()   
    
    pi_device= GCSDevice()
    Instrument_PI.initial_pi_device(pi_device)
    
    task_nidaqmx = initial_nidaqmx(nidaqmx)
    
    worker = Backend(pi_device, task_nidaqmx)

    worker.make_connection(gui)
    gui.make_connection(worker)

    ## Confocal Photodiode Thread
    
    confocalThread = QtCore.QThread()
    worker.moveToThread(confocalThread)
    worker.PDtimer_stepxy.moveToThread(confocalThread)
    worker.PDtimer_rampxy.moveToThread(confocalThread)
    worker.PDtimer_rampxz.moveToThread(confocalThread)
    worker.drifttimer.moveToThread(confocalThread)
    worker.PDtimer_stepxy.timeout.connect(worker.scan_step_xy)
    worker.PDtimer_rampxy.timeout.connect(worker.scan_ramp_xy)
    worker.PDtimer_rampxz.timeout.connect(worker.scan_ramp_xz)
    worker.PDtimer_rampyx.timeout.connect(worker.scan_ramp_yx)
    worker.PDtimer_rampyz.timeout.connect(worker.scan_ramp_yz)
    worker.drifttimer.timeout.connect(worker.drift)
    confocalThread.start()

    gui.show()
    app.exec_()


