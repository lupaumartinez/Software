
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

from Instrument import shutters, openShutter, closeShutter, pi_device
from Camera import myAndor
from Spectrum import mySpectrometer, DEVICE,  NumberofPixel

PSFmodes = ['x/y', 'x/z'] 

class Frontend(QtGui.QFrame):

    scanmodeSignal = pyqtSignal(int, bool)
    stopSignal = pyqtSignal(int, bool)
    parametersstepSignal = pyqtSignal(list)
    spectrum_parametersSignal = pyqtSignal(float)
    spectrum_parameters_filterSignal = pyqtSignal(list)
    show_filterSignal = pyqtSignal(bool, list)
    CMSignal = pyqtSignal()
    saveSignal = pyqtSignal()
    
    gotomaximum_Signal = pyqtSignal(int)
    parameters_gotomaximum_Signal = pyqtSignal(list)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setUpGUI()

 
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
        self.time_Edit = QtGui.QLineEdit('0.5')
    
        self.time_Edit.textChanged.connect(self.spectrum_parameters)
        
        self.parameters_spectrum = QtGui.QWidget()
        parameters_layout = QtGui.QGridLayout()
        self.parameters_spectrum.setLayout(parameters_layout)

        parameters_layout.addWidget(time_Label,                         0, 0)
        parameters_layout.addWidget(self.time_Edit,                     0, 1)
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

        self.center_column_sl = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.center_column_sl.setMinimum( int(self.size_spot_Edit.text()) )
        self.center_column_sl.setMaximum(1002 - int(self.size_spot_Edit.text()) )
        self.center_column_sl.setValue(501)
        self.center_column_sl.setTickPosition(QtGui.QSlider.TicksBelow)
        self.center_column_sl.setTickInterval(1)
        self.center_column_sl.valueChanged.connect(self.spectrum_parameters_filter)

        center_column_Label = QtGui.QLabel('Center column (pixel):')
        self.center_column_Label = QtGui.QLabel('0')
        self.center_column_Label.setText(format(int(self.center_column_sl.value())))

        self.show_filter_button = QtGui.QPushButton('Show ROI selected')
        self.show_filter_button.setCheckable(True)
        self.show_filter_button.clicked.connect(self.show_spectrum_parameters_filter)

        self.parameters_filter = QtGui.QWidget()
        parameters_filter_layout = QtGui.QGridLayout()
        self.parameters_filter.setLayout(parameters_filter_layout)
        
        parameters_filter_layout.addWidget(center_row_Label,                   2, 0)
        parameters_filter_layout.addWidget(self.center_row_Label,              2, 1)
        parameters_filter_layout.addWidget(self.center_row_sl,                 3, 0)

        parameters_filter_layout.addWidget(center_column_Label,                4, 0)
        parameters_filter_layout.addWidget(self.center_column_Label,           4, 1)
        parameters_filter_layout.addWidget(self.center_column_sl,              5, 0)

        parameters_filter_layout.addWidget(size_spot_Label,                    6, 0)
        parameters_filter_layout.addWidget(self.size_spot_Edit,                6, 1)

        parameters_filter_layout.addWidget(self.show_filter_button,            7, 0)
         
        
        #Go to maximum:
        
        self.scanrangeLabel_z = QtGui.QLabel('Range z (µm)')        
        self.scanrangeEdit_z = QtGui.QLineEdit('2')
       
        self.NzLabel = QtGui.QLabel('Number of pixel z')
        self.NzEdit = QtGui.QLineEdit('8')
        
        self.gotomaximumButton = QtGui.QPushButton('Go to maximum')
        self.gotomaximumButton.clicked.connect(self.set_go_to_maximum)
        
        self.graph_focus = pg.GraphicsLayoutWidget()
        subgrid = QtGui.QGridLayout()
        subgrid.addWidget(self.graph_focus)
        
        plotfocus = self.graph_focus.addPlot(row=2, col=1, title="Go to maximum")
        plotfocus.showGrid(x=True, y=True)
        plotfocus.setLabel('left', "Counts on ROI")
        plotfocus.setLabel('bottom', "z position (µm)")
               
        self.curve_z = plotfocus.plot(open='y')
        self.curve_z_max = plotfocus.plot(open='y')    
        
        self.gotomaximumWidget = QtGui.QWidget()
        parameters_gotomaximum_layout = QtGui.QGridLayout()
        self.gotomaximumWidget.setLayout(parameters_gotomaximum_layout)
        
        parameters_gotomaximum_layout.addWidget(self.scanrangeLabel_z,       0, 0)
        parameters_gotomaximum_layout.addWidget(self.scanrangeEdit_z,        0, 1) 
        parameters_gotomaximum_layout.addWidget(self.NzLabel,                1, 0)
        parameters_gotomaximum_layout.addWidget(self.NzEdit,                 1, 1) 
        parameters_gotomaximum_layout.addWidget(self.gotomaximumButton,      2, 1)
        
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
        
        gotomaximumDock = Dock('Go to maximum Z')
        gotomaximumDock.addWidget(self.gotomaximumWidget)
        dockArea.addDock(gotomaximumDock, 'bottom', goCMDock)
        
        hbox.addWidget(dockArea)
        self.setLayout(hbox)

  #  algunas cosas que ejecutan una vez antes de empezar

        self.vb.setMouseMode(pg.ViewBox.RectMode)
        self.img = pg.ImageItem()
        self.vb.addItem(self.img)

        self.hist = pg.HistogramLUTItem(image=self.img)
        self.hist.gradient.loadPreset('grey')
# 'thermal', 'flame', 'yellowy', 'bipolar', 'spectrum',
# 'cyclic', 'greyclip', 'grey' # Solo son estos

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
        
    def spectrum_parameters(self):

        exposure_time = float(self.time_Edit.text())            
        
        self.spectrum_parametersSignal.emit(exposure_time)
   
    def spectrum_parameters_filter(self):

        self.center_row_Label.setText(format(int(self.center_row_sl.value())))
        self.center_column_Label.setText(format(int(self.center_column_sl.value())))

        spot_size = int(self.size_spot_Edit.text())
        center_row = int(self.center_row_Label.text())
        center_column = int(self.center_column_Label.text()) 
        
        filter_ROI = [spot_size, center_row, center_column]

        self.spectrum_parameters_filterSignal.emit(filter_ROI)
        
        self.show_spectrum_parameters_filter()

    def show_spectrum_parameters_filter(self):

        spot_size = int(self.size_spot_Edit.text())
        center_row = int(self.center_row_Label.text())
        center_column = int(self.center_column_Label.text()) 
        
        filter_ROI = [spot_size, center_row, center_column]

        if self.show_filter_button.isChecked():

            self.show_filterSignal.emit(True, filter_ROI)

        else:

            self.show_filterSignal.emit(False, filter_ROI)
   
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
            
    def set_go_to_maximum(self):
        
        if self.gotomaximumButton.isChecked:
            
            self.graph_focus.show()
        
            parameters_z = self.set_parameters_go_to_maximum()   
            self.parameters_gotomaximum_Signal.emit(parameters_z)
            
            self.gotomaximum_Signal.emit(self.scan_laser.currentIndex())
        
    def set_parameters_go_to_maximum(self):
        
        parameters_z = [float(self.scanrangeEdit_z.text()), int(self.NzEdit.text())]
        
        return parameters_z
    

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
        
    @pyqtSlot(np.ndarray, np.ndarray)
    def plot_data_maximum(self, z_step, z_profile):
        
        self.curve_z.setData(z_step, z_profile,pen = None, symbol = 'o') 
        

    @pyqtSlot(np.ndarray, np.ndarray)
    def plot_go_to_maximum(self, z_step, z_max):
        
        self.curve_z_max.setData(z_step, z_max,
                           pen=pg.mkPen('k', width=1),
                           shadowPen=pg.mkPen('m', width=3)) 
 
    def make_connection(self, backend):
        backend.aspectSignal.connect(self.get_view_aspect)
        backend.dataSignal.connect(self.get_img)
        backend.CMValuesSignal.connect(self.get_CMValues)
        
        backend.data_gotomaximumSignal.connect(self.plot_data_maximum)
        backend.plot_gotomaximumSignal.connect(self.plot_go_to_maximum)

class Backend(QtCore.QObject):
    
    aspectSignal = pyqtSignal(int)
    dataSignal = pyqtSignal(np.ndarray)
    CMValuesSignal = pyqtSignal(list)

    scandoneSignal = pyqtSignal()  #para módulo Nanopositioning
    imageSignal = pyqtSignal(np.ndarray) #para view de módulo Cámara
    
    data_gotomaximumSignal = pyqtSignal(np.ndarray, np.ndarray)
    plot_gotomaximumSignal = pyqtSignal(np.ndarray, np.ndarray)
    gotomaximum_doneSignal = pyqtSignal()
    
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.file_path = os.path.abspath("C:\Julian\Data_PySpectrum") 

        self.PDtimer_stepxy = QtCore.QTimer()
        self.PDtimer_stepxy.timeout.connect(self.scan_step_xy)
        
        self.PDtimer_stepZ = QtCore.QTimer()
        self.PDtimer_stepZ.timeout.connect(self.scan_step_Z)

        self.exposure_time = 0.5 
        self.shape = (NumberofPixel, NumberofPixel)
          
        self.center_row = 438
        self.center_column = 501
        self.spot_size = 25

        self.set_scan_filter([self.spot_size, self.center_row, self.center_column])
        
    @pyqtSlot(list)
    def set_scan_filter(self, filter_roi):
        
        self.spot_size = filter_roi[0]
        self.center_row = filter_roi[1]
        self.center_column = filter_roi[2]
        
        down_row = self.center_row - int((self.spot_size-1)/2)
        up_row = self.center_row + int((self.spot_size-1)/2) + 1  
        self.roi_rows = range(down_row, up_row)

        down_column = self.center_column - int((self.spot_size-1)/2)
        up_column = self.center_column + int((self.spot_size-1)/2) + 1  
        self.roi_columns = range(down_column, up_column)


    def x_create(self): 
        pos = pi_device.qPOS()
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
        
        self.create_folder()

        self.laser = shutters[color_laser]
        
        self.signal_scan_stop = False
        self.mode_printing = 'none'

        self.set_scan_spectrum(self.exposure_time)
        self.set_zero_order()

        if psfbool:
            self.start_scan_step_xy(self.laser, self.mode_printing) 
        else:
             print('Modo no programado')
             
    
     
    @pyqtSlot(int, bool)   
    def stop_scan(self, color_laser, psfbool):
        
        if not self.signal_scan_stop: 
           
           laser = shutters[color_laser]
           closeShutter(laser)
          
           myAndor.shutter(1, 2, 0, 0, 2)
           print("stop scan: close instrument")
           
           if psfbool:
               
               self.PDtimer_stepxy.stop()
               
               print('timer stop')
              
               pi_device.MOV(['A','B'], [self.x_pos, self.y_pos])
           else:
               print('Modo no programado')

    @pyqtSlot(str, str)             
    def start_scan_step_xy(self, laser, mode_printing):  

        self.laser = laser
        self.mode_printing = mode_printing
        
        myAndor.shutter(1, 1 , 0, 0, 1) # opens both shutter, mode liveview
        self.tic = ptime.time()  
        self.j = 0  
        self.i = 0
        self.x_pos, self.y_pos, self.z_pos = self.x_create()
        openShutter(laser)
        #self.PDtimer_stepxy.start(self.time_step_x_lin*10**3)   
        self.PDtimer_stepxy.start(0)  
        
    def scan_step_xy(self):   
 
        dy = self.range_y/self.Ny
        dx = self.range_x/self.Nx
        
        if self.j < self.Ny:
            
            if self.i < self.Nx :
        
                pi_device.MOV(['A', 'B'], [self.x_pos - self.range_x/2 + self.i*dx, self.y_pos - self.range_y/2 + self.j*dy]) 
                step_profile  = self.scan_step()
                self.image_scan[self.j, self.i] = step_profile
                self.dataSignal.emit(self.image_scan)
                self.i = self.i + 1 
        
            else:
                self.i = 0
                self.j = self.j + 1       
           
        else:
            # myAndor.shutter(1, 1 , 0, 0, 0) # mode pictures
             myAndor.shutter(1, 2, 0, 0, 2)
             self.PDtimer_stepxy.stop()
             self.dataSignal.emit(self.image_scan)
             self.signal_scan_stop = True
             closeShutter(self.laser)
             #time.sleep(self.time_step_x_lin) #TODO  
             self.CMmeasure() 
             pi_device.MOV(['A','B'], [self.x_pos, self.y_pos])
             print(ptime.time()-self.tic, "Time scan step x/y")
             self.saveFrame()
             self.scandoneSignal.emit()
        
    def scan_step(self):
        """ a pesar de ser Step, hago toda una linea y despues la dibujo"""

        image = self.taking_picture()
      #  self.save_picture(self.i, self.j, image)

        #array_profile = np.sum(image[self.roi_rows,:], axis=0)
        array_profile = np.sum(image[:,self.roi_rows], axis=1)
        step_profile = np.sum(array_profile[self.roi_columns])
       
        return step_profile

    @pyqtSlot(float)
    def set_scan_spectrum(self, exposure_time):
        
        self.exposure_time = exposure_time

        myAndor.set_exposure_time(exposure_time)
        print('[Camera] Exposure time = {} s'.format(exposure_time))


    def set_zero_order(self):

        mySpectrometer.ShamrockSetWavelength(DEVICE, 0)
        print(datetime.now(), '[Shamrock] Wavelength = ', mySpectrometer.ShamrockGetWavelength(DEVICE))

    def taking_picture(self):
        
        # set shutters configuration
       # myAndor.shutter(1, 1, 0, 0, 0) # standard mode for us
       
        myAndor.acquisition_mode = 'Single Scan'
       # myAndor.acquisition_mode = 'Run till Abort'
       
        myAndor.start_acquisition()    
        myAndor.wait_for_acquisition()  
        myAndor.abort_acquisition()
        
        image = np.transpose(myAndor.most_recent_image16(self.shape))
        self.imageSignal.emit(image)

        return image

    #  CMmeasure
    def CMmeasure(self):

        Z = self.image_scan  #solo ida
      
        Zn = (Z-min(map(min,Z)))/(max(map(max,Z))-min(map(min,Z)))  #filtro de %70
        for i in range(len(Z[:,1])):
            for j in range (len(Z[1,:])):
                if Zn[i,j] < 0.7:
                    Zn[i,j] = 0
                    
        ycm, xcm = ndimage.measurements.center_of_mass(Zn)
        
        Normal_y = self.range_y/self.Ny
        Normal_x = self.range_x/self.Nx

        self.x_cm = np.round(self.x_pos - self.range_x/2 + (xcm*Normal_x), 3)
        self.y_cm = np.round(self.y_pos - self.range_y/2 + (ycm*Normal_y), 3)
        
        self.CMValuesSignal.emit([self.x_cm, self.y_cm, xcm, ycm])
        
        return self.x_cm, self.y_cm

    @pyqtSlot()  
    def goCM(self):
        self.moveto(self.x_cm, self.y_cm)

    def moveto(self, x, y):
        """moves the position along the axis to a specified point.
        Cambie todo paraque ande con la PI"""
        axis = ['A', 'B']
        targets = [x, y]
        pi_device.MOV(axis, targets)
        while not all(pi_device.qONT(axis).values()):
            time.sleep(0.01)
            
    @pyqtSlot(int)           
    def start_go_to_maximum(self, color_laser):  
        print("go to maximum on Z")
        
        self.laser = shutters[color_laser]
       #self.mode_printing = 'none'

        self.set_scan_spectrum(self.exposure_time)
        self.set_zero_order()

        myAndor.shutter(1, 1 , 0, 0, 1) # opens both shutter, mode liveview
        self.tic = ptime.time()  
    
        self.x_pos, self.y_pos, self.z_pos = self.x_create()
        
        openShutter(self.laser)

        self.k = 0
        self.PDtimer_stepZ.start(0)  
        
    @pyqtSlot(list)
    def parameters_go_to_maximum(self, parameters_z):
        
        self.range_z = parameters_z[0]
        self.Nz = parameters_z[1]
        
        self.z_profile = np.zeros(self.Nz)
        self.z_step = np.zeros(self.Nz)
    
    def scan_step_Z(self):   
 
        dz = self.range_z/self.Nz
        
        if self.k < self.Nz:

            pi_device.MOV('C', self.z_pos - self.range_z/2 + self.k*dz) 
            step_profile  = self.step_Z()
            
            self.z_profile[self.k] = step_profile
            self.z_step[self.k] = self.z_pos - self.range_z/2 + self.k*dz
            
            self.data_gotomaximumSignal.emit(self.z_step, self.z_profile)
            self.k = self.k + 1 
           
        else:
             myAndor.shutter(1, 2, 0, 0, 2)
             self.PDtimer_stepZ.stop()
             self.data_gotomaximumSignal.emit(self.z_step, self.z_profile)
             closeShutter(self.laser)

             self.go_to_maximum_Z(self.z_step, self.z_profile)
             #pi_device.MOV('C', self.z_pos)
             
             print(ptime.time()-self.tic, "Time go to maximum Z")
             self.gotomaximum_doneSignal.emit()     
   
    def step_Z(self):
        """ a pesar de ser Step, hago toda una linea y despues la dibujo"""

        image = self.taking_picture()
        array_profile = np.sum(image[:,self.roi_rows], axis=1)

        print(array_profile.shape)

        step_profile = np.sum(array_profile[self.roi_columns])
        print(step_profile)
       
        return step_profile
    
    def go_to_maximum_Z(self, z_step, z_profile):
        
        index_z_step_max = np.argmax(z_profile)
        z_max_position = round(z_step[index_z_step_max], 3) 
        
        pi_device.MOV('C', z_max_position)
        print(datetime.now(), 'Go to maximum on Z:', z_max_position)   
        
        z_max = np.zeros(self.Nz)
        z_max[index_z_step_max] = np.max(z_profile)
        
       # self.plot_gotomaximumSignal(z_step, z_max)
        
    def create_folder(self):
        """ Crea una carpeta para este archivo particular.
        Si es una grilla, puede tener esa data en el nombre (ej: 10x15)"""

        timestr = time.strftime("%Y%m%d-%H%M%S")
        
        self.old_folder = self.file_path
        new_folder = os.path.join(self.old_folder,  timestr + "_" + "Confocal_Zero")       
        
        print(new_folder)
        self.new_folder = new_folder

        os.makedirs(new_folder)
        

    def save_picture(self, i, j, image):
        
        filepath = self.new_folder
        filename = "Picture_Andor_Zero_Order_i%04d_j%04d.tiff" % (int(i), int(j))
        
        full_filename = os.path.join(filepath,filename)
        
        guardado = Image.fromarray(np.transpose(image))
        guardado.save(full_filename)

        #print(datetime.now(), '[PySpectrum]', 'Save Image spectrum')           
    
        
    @pyqtSlot(str)        
    def get_direction(self, file_name):
        self.file_path = file_name

    @pyqtSlot()
    def saveFrame(self):
        """ Config the path and name of the file to save, and save it"""   
        
        filepath = self.new_folder
        timestr = time.strftime("%Y%m%d-%H%M%S")
        name = str(filepath + "/" + "Confocal_Zero" + timestr + ".tiff")
        guardado = Image.fromarray(np.transpose(self.image_scan))
        guardado.save(name)
        
        print("\n Image saved\n")
    
    
    def make_connection(self, frontend):
        
        frontend.scanmodeSignal.connect(self.start_scan)
        frontend.stopSignal.connect(self.stop_scan)
        frontend.parametersstepSignal.connect(self.scan_step_parameters)
        frontend.spectrum_parametersSignal.connect(self.set_scan_spectrum)
        frontend.spectrum_parameters_filterSignal.connect(self.set_scan_filter)
 
        frontend.CMSignal.connect(self.goCM)
        frontend.saveSignal.connect(self.saveFrame)
        
        frontend.gotomaximum_Signal.connect(self.start_go_to_maximum)
        frontend.parameters_gotomaximum_Signal.connect(self.parameters_go_to_maximum)

#%%
        
if __name__ == '__main__':

    app = QtGui.QApplication([])

    gui = Frontend()   
    worker = Backend()

    worker.make_connection(gui)
    gui.make_connection(worker)

    confocalThread = QtCore.QThread()
    worker.moveToThread(confocalThread)
    worker.PDtimer_stepxy.moveToThread(confocalThread)
    worker.PDtimer_stepZ.moveToThread(confocalThread)
    confocalThread.start()

    gui.show()
    app.exec_()


