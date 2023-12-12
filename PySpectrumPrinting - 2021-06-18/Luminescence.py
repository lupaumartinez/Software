# -*- coing: utf-8 -*-
"""
Created on Thu Feb  7 18:44:18 2019

@author: Luciana

"""

import os
from pyqtgraph.Qt import QtGui, QtCore
import tkinter as tk
from tkinter import filedialog
import time

import pyqtgraph as pg
from pyqtgraph.dockarea import Dock, DockArea
from PyQt5.QtCore import pyqtSignal, pyqtSlot

import numpy as np
from PIL import Image

from Instrument_nidaqmx import shutters, Flipper_notch532

#%%

class Frontend(QtGui.QFrame):
    
    setreferenceSignal = pyqtSignal()
    goreferenceSignal = pyqtSignal()
    
    readgridSignal = pyqtSignal()
    gridcreateSignal = pyqtSignal(list)
    foldergridSignal = pyqtSignal()
    
    reference_refreshSignal = pyqtSignal(bool)
    gridSignal = pyqtSignal()
    pauseSignal = pyqtSignal()
    next_index_Signal = pyqtSignal()
    new_index_Signal = pyqtSignal(int)
    
    parametersSignal = pyqtSignal(int, list)

    gridinfoSignal = pyqtSignal(list)
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
      
        self.setUpGUI()
        self.get_grid_parameters()
      
    def setUpGUI(self):
        
        self.NameDirValue = QtGui.QLabel('')
        #self.NameDirValue.setText(self.file_path)
        self.NameDirValue.setStyleSheet(" background-color: red; ")

    # Defino el tipo de laser que quiero para imprimir
        self.grid_laser = QtGui.QComboBox()
        self.grid_laser.addItems(shutters)
        self.grid_laser.setCurrentIndex(0)
        self.grid_laser.setToolTip('Elijo con que láser imprimir.')
        self.grid_laser.setFixedWidth(80)
        self.grid_laser.activated.connect(
                                     lambda: self.color_menu(self.grid_laser))
        self.color_menu(self.grid_laser)
        grid_laser_label = QtGui.QLabel('<strong> Print Laser')

    # crea la carpeta vacía
        self.imprimir_button = QtGui.QPushButton('Luminescence folder')
        self.imprimir_button.setCheckable(True)
        self.imprimir_button.clicked.connect(self.get_grid_create_folder)
        self.imprimir_button.setStyleSheet(
                "QPushButton:pressed { background-color: blue; }")
        self.imprimir_button.setToolTip('Crea la carpeta con el nombre de la grilla creada o cargada.')
                                                                          
    # Print button
        self.play_button = QtGui.QPushButton('Play ►')
        self.play_button.clicked.connect(self.get_grid_measurment)
        self.play_button.setStyleSheet(
                "QPushButton:pressed { background-color: blue; }")
        
        self.pause_button = QtGui.QPushButton('Pause')
        self.pause_button.clicked.connect(self.get_grid_pause)
        
        self.next_button = QtGui.QPushButton('Next index ►')
        self.next_button.clicked.connect(self.get_grid_next)

    # go ref button.
        self.go_ref_button = QtGui.QPushButton('go reference')
        self.go_ref_button.setCheckable(True)
        self.go_ref_button.clicked.connect(self.get_goreference)
        self.go_ref_button.setStyleSheet(
                "QPushButton:pressed { background-color: blue; }")
        self.go_ref_button.setToolTip('Va a la referencia seteada.')
        self.go_ref_button.setFixedWidth(80)

    # set reference button.
        self.set_ref_button = QtGui.QPushButton('set reference')
        self.set_ref_button.setCheckable(True)
        self.set_ref_button.clicked.connect(self.get_setreference)
        self.set_ref_button.setStyleSheet(
                "QPushButton { background-color: orange; }"
                "QPushButton:pressed { background-color: blue; }")
        self.set_ref_button.setToolTip('Setea la referencia de la grilla.')
        self.set_ref_button.setFixedWidth(150)
        
     # reference option to refresh with center of mass everytime:
        refresh_reference_Label = QtGui.QLabel('Refresh reference?')
        self.refresh_reference_auto = QtGui.QCheckBox('')
        self.refresh_reference_auto.clicked.connect(self.get_grid_refresh_reference)
        self.refresh_reference_auto.setToolTip('Si esta marcado, refresca la posicion absoluta de referencia para hacer la grilla con los centros de masa del Slow Confocal Spectrum.')

     # particulas totales
        self.particulasLabel = QtGui.QLabel('Total targets')
        self.particulasEdit = QtGui.QLabel('0')
        self.particulasEdit.setFixedWidth(40)
        self.particulasEdit.setToolTip('Cantidad de particulas totales a imprimir.')
        self.particulasLabel.setToolTip('Cantidad de particulas totales')
        self.particulasEdit.setStyleSheet(
                                        " background-color: rgb(200,200,200)")
    # Indice actual
        self.indice_impresionLabel = QtGui.QLabel('Index printing')
        self.indice_impresionEdit = QtGui.QLineEdit('0')
        self.indice_impresionEdit.setFixedWidth(40)
        self.indice_impresionEdit.setStyleSheet(
                                        " background-color: rgb(200,200,200)")
        self.indice_impresionEdit.setToolTip('Cantidad de partículas que imprimió.')
        self.indice_impresionEdit.textChanged.connect(self.new_index_target)

        self.grid_print = QtGui.QWidget()
        grid_print_layout = QtGui.QGridLayout()
        self.grid_print.setLayout(grid_print_layout)

        grid_print_layout.addWidget(self.imprimir_button,         0, 0)
        grid_print_layout.addWidget(self.NameDirValue,            0, 1)

        grid_print_layout.addWidget(grid_laser_label,             1, 0)
        grid_print_layout.addWidget(self.grid_laser,              1, 1)
        
        grid_print_layout.addWidget(self.set_ref_button,          6, 0)
        grid_print_layout.addWidget(refresh_reference_Label,      7, 0)
        grid_print_layout.addWidget(self.refresh_reference_auto,  7, 1)
                
        grid_print_layout.addWidget(self.play_button,             7, 2)
        grid_print_layout.addWidget(self.pause_button,            8, 2)
        grid_print_layout.addWidget(self.next_button,             9, 2)
                    
        grid_print_layout.addWidget(self.particulasLabel,         4, 2)
        grid_print_layout.addWidget(self.particulasEdit,          4, 3)
        grid_print_layout.addWidget(self.indice_impresionLabel,   5, 2)
        grid_print_layout.addWidget(self.indice_impresionEdit,    5, 3) 
        grid_print_layout.addWidget(self.go_ref_button,           6, 2)

        # particles to autofocus
        self.autofocLabel = QtGui.QLabel('Autofocus')
        self.autofocEdit = QtGui.QLineEdit('2')
        self.autofocEdit.setFixedWidth(40)
        self.autofocEdit.setValidator(QtGui.QIntValidator(0, 5000))
        self.autofocEdit.setToolTip('Cada cuantas particulas hacer autofoco.')

        # shift x
        self.shifxLabel = QtGui.QLabel('focus shift x[µm]')
        self.shiftxEdit = QtGui.QLineEdit('0')
        self.shiftxEdit.setFixedWidth(40)
        self.shiftxEdit.setToolTip('Para que haga el autofoco corrido a tal distancia.')

        # shift y
        self.shiftyLabel = QtGui.QLabel('focus shift y[µm]')
        self.shiftyEdit = QtGui.QLineEdit('0')
        self.shiftyEdit.setFixedWidth(40)
        self.shiftyEdit.setToolTip('Para que haga el autofoco corrido a tal distancia.')

       
        self.grid_shift = QtGui.QWidget()
        grid_shift_layout = QtGui.QGridLayout()
        self.grid_shift.setLayout(grid_shift_layout)
        grid_shift_layout.addWidget(self.autofocLabel, 1, 0)
        grid_shift_layout.addWidget(self.autofocEdit,  2, 0)
        grid_shift_layout.addWidget(self.shifxLabel,   3, 0)
        grid_shift_layout.addWidget(self.shiftxEdit,   4, 0)
        grid_shift_layout.addWidget(self.shiftyLabel,  5, 0)
        grid_shift_layout.addWidget(self.shiftyEdit,   6, 0)


     # Crear grilla para imprimir
        self.number_files = QtGui.QLineEdit('4')
        self.number_columns = QtGui.QLineEdit('4')
        self.distance_files = QtGui.QLineEdit('3')
        self.distance_columns = QtGui.QLineEdit('3')

        self.grid_create_button = QtGui.QPushButton('Create grid')
        self.grid_create_button.setCheckable(True)
        self.grid_create_button.clicked.connect(self.get_grid_create)
        self.grid_create_button.setStyleSheet(
                "QPushButton { background-color: orange; }"
                "QPushButton:pressed { background-color: blue; }")
        self.grid_create_button.setToolTip('Setear la grilla a imprimir.')

    # Cargar la grilla de un .txt
        self.cargar_archivo_button = QtGui.QPushButton('or Load grid')
        self.cargar_archivo_button.setCheckable(True)
        self.cargar_archivo_button.clicked.connect(self.get_grid_read)
        self.cargar_archivo_button.setStyleSheet(
                "QPushButton { background-color: orange; }"
                "QPushButton:pressed { background-color: blue; }")
        self.cargar_archivo_button.setToolTip('Cargar el archivo .txt con la grilla, dibujo o letras, para imprimir.')

        self.grid_create_parameters = QtGui.QWidget()
        grid_create_parameters = QtGui.QGridLayout()
        self.grid_create_parameters.setLayout(grid_create_parameters)

        grid_create_parameters.addWidget(self.number_files,                       1, 1)
        grid_create_parameters.addWidget(self.number_columns,                     2, 1)
        grid_create_parameters.addWidget(self.distance_files,                     3, 1)
        grid_create_parameters.addWidget(self.distance_columns,                   4, 1)
        grid_create_parameters.addWidget(self.grid_create_button,                 5, 1)
        grid_create_parameters.addWidget(self.cargar_archivo_button,              6, 1)

        grid_create_parameters.addWidget(QtGui.QLabel('# NPs per column'),        1, 0)
        grid_create_parameters.addWidget(QtGui.QLabel('# columns'),               2, 0)
        grid_create_parameters.addWidget(QtGui.QLabel('distance NP (µm)'),        3, 0)
        grid_create_parameters.addWidget(QtGui.QLabel('distance column (µm)'),    4, 0)


    # Valores de refecencia
        self.xrefLabel = QtGui.QLabel('Nan')
        self.yrefLabel = QtGui.QLabel('Nan')
        self.zrefLabel = QtGui.QLabel('Nan')

        self.grid_reference = QtGui.QWidget()
        grid_reference = QtGui.QGridLayout()
        self.grid_reference.setLayout(grid_reference)
        grid_reference.addWidget(self.xrefLabel,            1, 1)
        grid_reference.addWidget(self.yrefLabel,            2, 1)
        grid_reference.addWidget(self.zrefLabel,            3, 1)
        grid_reference.addWidget(QtGui.QLabel('x ref'),     1, 0)
        grid_reference.addWidget(QtGui.QLabel('y ref'),     2, 0)
        grid_reference.addWidget(QtGui.QLabel('z ref'),     3, 0)

 #extra info:

        self.grid_save_info_button = QtGui.QPushButton('Save info')
        self.grid_save_info_button.setCheckable(True)
        self.grid_save_info_button.clicked.connect(self.get_grid_info)
        self.grid_save_info_button.setStyleSheet("QPushButton:pressed { background-color: blue; }")

        self.powerlaser = QtGui.QLineEdit('2.5')
        self.typeNP = QtGui.QLineEdit('AuNPz citrate (-) 60 nm')
        self.substrate = QtGui.QLineEdit('glass + PDDA + PSS')
        self.extra_info = QtGui.QLineEdit('Nan')

        self.grid_info = QtGui.QWidget()
        grid_info = QtGui.QGridLayout()
        self.grid_info.setLayout(grid_info)

        grid_info.addWidget(self.powerlaser,              1, 1)
        grid_info.addWidget(self.typeNP,                  2, 1)
        grid_info.addWidget(self.substrate,               3, 1)
        grid_info.addWidget(self.extra_info,              4, 1)
        grid_info.addWidget(self.grid_save_info_button,   5, 1)

        grid_info.addWidget(QtGui.QLabel('Power bfp (mW)'),               1, 0)
        grid_info.addWidget(QtGui.QLabel('NPs'),                          2, 0)
        grid_info.addWidget(QtGui.QLabel('Substrate'),                    3, 0)
        grid_info.addWidget(QtGui.QLabel('Extra comments'),               4, 0)

        dockArea = DockArea()
        hbox = QtGui.QHBoxLayout(self)
        hbox.addWidget(dockArea)
        self.setLayout(hbox)
        
        grid_reference_dock = Dock('Reference pos')
        grid_reference_dock.addWidget(self.grid_reference)
        dockArea.addDock(grid_reference_dock)
        
        grid_create_dock = Dock('Grid')
        grid_create_dock.addWidget(self.grid_create_parameters)
        dockArea.addDock(grid_create_dock, 'right', grid_reference_dock)
        
        grid_print_dock = Dock('Printing grids')
        grid_print_dock.addWidget(self.grid_print)
        dockArea.addDock(grid_print_dock, 'right', grid_create_dock)

        grid_shift_dock = Dock('Focus shift')
        grid_shift_dock.addWidget(self.grid_shift)
        dockArea.addDock(grid_shift_dock, 'right', grid_print_dock)  

        grid_info_dock = Dock('Extra printing info')
        grid_info_dock.addWidget(self.grid_info)
        dockArea.addDock(grid_info_dock, 'right', grid_shift_dock)

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
                 
    def get_grid_read(self):
        if self.cargar_archivo_button.isChecked:
           self.readgridSignal.emit() 

    def get_grid_create(self):

        grid = [int(self.number_files.text()), int(self.number_columns.text()), 
                float(self.distance_files.text()), float(self.distance_columns.text())]

        if self.grid_create_button.isChecked:
           self.gridcreateSignal.emit(grid)
           
    def get_grid_refresh_reference(self):
        if self.refresh_reference_auto.isChecked():
            self.reference_refreshSignal.emit(True)
        else:
            self.reference_refreshSignal.emit(False)
           
    @pyqtSlot(np.ndarray)       
    def grid_plot(self, datos):
        """hace un plot de la grilla cargada para estar seguro que es lo que
        se quiere imprimir"""
        
        grid_x = datos[0, :]
        grid_y = datos[1, :]
        
        self.gridplot = pg.GraphicsLayoutWidget()
        plotgrid = self.gridplot.addPlot(row=2, col=1, title="Grilla a imprimir")
        plotgrid.showGrid(x=True, y=True)
        plotgrid.setLabel('left', "x (µm)")
        plotgrid.setLabel('bottom', "y (µm)")
        
        subgrid = QtGui.QGridLayout()
        subgrid.addWidget(self.gridplot)
               
        data = plotgrid.plot(open='y')
        data.setData(grid_y, grid_x, pen=None, symbol='o')
        
        self.gridplot.show()
           
    @pyqtSlot(int)
    def particulas_edit(self, particulas):       
        self.particulasEdit.setText(str(particulas))
        
    def get_grid_create_folder(self):
        if self.imprimir_button.isChecked:
           self.foldergridSignal.emit() 
           
    @pyqtSlot(str)  
    def name_folder(self, folder):
        self.NameDirValue.setText(folder)
        self.NameDirValue.setStyleSheet(" background-color: green ; ")
        
    @pyqtSlot(int)      
    def index_target(self, i):
        self.indice_impresionEdit.setText(str(i))
        
    def new_index_target(self):
        new_index = int(self.indice_impresionEdit.text())
        self.new_index_Signal.emit(new_index)
                       
    def get_setreference(self):
        if self.set_ref_button.isChecked:
           self.setreferenceSignal.emit()
             
    @pyqtSlot(list)
    def reference_label(self, reference):
        list_pos = reference
        self.xrefLabel.setText(str(list_pos[0]))
        self.yrefLabel.setText(str(list_pos[1]))
        self.zrefLabel.setText(str(list_pos[2]))
        
    def get_goreference(self):
        if self.go_ref_button.isChecked:
           self.goreferenceSignal.emit()
           
    def get_grid_parameters(self):
        color_laser = self.grid_laser.currentIndex()
        
        grid_parameters = [float(self.autofocEdit.text()), float(self.shiftxEdit.text()),
                           float(self.shiftyEdit.text())]
           
        self.parametersSignal.emit(color_laser, grid_parameters)
           
    def get_grid_measurment(self):
        if self.play_button.isChecked:
           self.get_grid_parameters()
           self.gridSignal.emit()  
           
    def get_grid_pause(self):
        if self.pause_button.isChecked:
           self.get_grid_parameters()
           self.pauseSignal.emit()  
           
    def get_grid_next(self):      
         if self.next_button.isChecked:
             self.next_index_Signal.emit()  

    def get_grid_info(self):

        info = [["Laser:", str(self.grid_laser.currentText()) ], ["Power bfp (mW): ", str(self.powerlaser.text())], 
                ["NPs: ", str(self.typeNP.text())], ["Substrate: ", str(self.substrate.text())],
                  ["Extra comments: ", str(self.extra_info.text())]]

        if self.grid_save_info_button.isChecked:
           self.gridinfoSignal.emit(info) 

            
    def make_connection(self, backend):
        backend.referenceSignal.connect(self.reference_label)
        backend.particulasSignal.connect(self.particulas_edit)
        backend.gridplotSignal.connect(self.grid_plot)
        backend.namefolderSignal.connect(self.name_folder)
        backend.indexSignal.connect(self.index_target)   
        
class Backend(QtCore.QObject):
    
    referenceSignal = pyqtSignal(list)
    particulasSignal =  pyqtSignal(int)
    gridplotSignal = pyqtSignal(np.ndarray)
    
    namefolderSignal =  pyqtSignal(str)
    indexSignal = pyqtSignal(int)

    grid_move_finishSignal = pyqtSignal() 
    grid_autofocusSignal = pyqtSignal(str) 

    grid_scanSignal = pyqtSignal(str, str, str)
    
    grid_scan_stopSignal = pyqtSignal()
    
    grid_spectrumSignal = pyqtSignal(str, str, str)
    grid_spectrum_fast_Signal = pyqtSignal(str, str, str)
    grid_spectrum_stopSignal = pyqtSignal()
    
    grid_traceSignal = pyqtSignal(str, str, str)
    grid_trace_stopSignal = pyqtSignal()
    
    goSignal = pyqtSignal()  #para actualizar en Nanopositioning nueva posicion
    
    def __init__(self, pi_device, task_nidaqmx, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.pi_device = pi_device
        self.shuttertask = task_nidaqmx[0]
        self.flippertask = task_nidaqmx[1]
        self.flipper532task = task_nidaqmx[2]
        
        self.refresh_reference_option = False
        
# Reference           
    def read_pos(self):
        """lee las entradas analogicas que manda la platina y se donde estoy"""
        pos = self.pi_device.qPOS()
        x = pos['A']
        y = pos['B']
        z = pos['C']     
        return x, y, z
    
    @pyqtSlot()
    def set_reference(self):
        """ no lee la posicion, solo copia los numeros de uno al otro"""
        self.xref, self.yref, self.zref = self.read_pos()
        reference = [self.xref, self.yref, self.zref]
        self.referenceSignal.emit(reference)

    def moveto(self, x, y, z):
        """moves the position along the axis to a specified point.
        Cambie todo paraque ande con la PI"""
        axis = ['A', 'B', 'C']
        targets = [x, y, z]
        self.pi_device.MOV(axis, targets)
        while not all(self.pi_device.qONT(axis).values()):
            time.sleep(0.01)
            
    @pyqtSlot()     
    def go_reference(self):
        self.moveto(self.xref, self.yref, self.zref)
        self.goSignal.emit()

    @pyqtSlot()  
    def grid_read(self):
        """ select the file where the grid comes from"""
        root = tk.Tk()
        root.withdraw()

        name = filedialog.askopenfilename()  
        
        f = open(name, "r")
        datos = np.loadtxt(name, unpack=True)
        f.close()
        self.grid_name = 'Load_grid'
        self.grid_x = datos[0, :]
        self.grid_y = datos[1, :]
        
        self.particulas = len(self.grid_x)
        self.particulasSignal.emit(self.particulas)
        self.gridplotSignal.emit(datos)
        
        self.n = self.particulas #todas las particulas en esa columna...

    @pyqtSlot(list)
    def grid_create(self, grid):

        n = grid[0] #particulas por columna
        N = grid[1] #cantidad de columnas
        d_n = grid[2] #espaciado entre particulas
        d_N = grid[3] #espaciado entre columnas
    
        datos = np.zeros((3, n*N))
    
        i = 0
        k = 0

        for i in range(n):
           for k in range(N):
               datos[1, k*n+i]= k*d_N
               datos[0, k*n+i]= i*d_n

        self.grid_name = "{}x{}".format(n, N)
        self.grid_x = datos[0, :]
        self.grid_y = datos[1, :]

        self.particulas = len(self.grid_x)
        self.particulasSignal.emit(self.particulas) 
        self.gridplotSignal.emit(datos)
        
        self.n = n
            
    @pyqtSlot(str)        
    def grid_direction(self, file_name):
        self.file_path = file_name
        self.namefolderSignal.emit(self.file_path)
            
    @pyqtSlot()    
    def grid_create_folder(self):
        """ Crea una carpeta para este archivo particular.
        Si es una grilla, puede tener esa data en el nombre (ej: 10x15)"""

        timestr = time.strftime("%Y%m%d-%H%M%S")
        
        try:  
            self.old_folder = self.file_path
        except IOError as e:
            #print("Solución: crea el directorio del día.")
            print("I/O error({0}): {1}".format(e.errno, e.strerror))

        try:
            print("Grid load")
            new_folder = self.old_folder + "/" + timestr + "_Luminescence_" + self.grid_name
        except IOError as e:
           # print("Solución: carga archivo de grilla.")
            print("I/O error({0}): {1}".format(e.errno, e.strerror))

        self.new_folder = new_folder
        os.makedirs(new_folder)

        self.i_global = 1
        self.mode_printing = 'none'
        self.namefolderSignal.emit(new_folder)
        self.indexSignal.emit(self.i_global) 
    
    @pyqtSlot(int, list)     
    def grid_parameters(self, color_laser, grid_parameters):
        
        self.laser = shutters[color_laser]
        
        self.autofoc = grid_parameters[0]
        self.shiftx = grid_parameters[1]
        self.shifty = grid_parameters[2]
        
        
    @pyqtSlot()   
    def grid_measurment(self):
           
        if self.mode_printing == 'none':
              self.grid_start()
        else:
             self.indexSignal.emit(self.i_global)
             self.grid_move()
           
    def grid_start(self):
        """funcion que empieza el programa de imprimir una grilla"""

        self.mode_printing = 'luminescence'
           
        self.startX = self.xref
        self.startY = self.yref

        self.grid_move() 
        
    @pyqtSlot()    
    def grid_pause(self):     
        print('Pausa grilla')
        
        try: 
            self.grid_scan_stopSignal.emit()
        except:  pass

        try: 
            self.grid_spectrum_stopSignal.emit()
        except:  pass
    
        try: 
            self.grid_trace_stopSignal.emit()
        except:  pass
        
    
    @pyqtSlot()          
    def grid_next_index(self):
       # self.grid_pause()
        
        self.i_global += 1
        self.indexSignal.emit(self.i_global)
        self.grid_move() 
        
                
    @pyqtSlot(int)
    def grid_change_index(self, new_index):
        self.i_global = new_index
        
    @pyqtSlot(bool)    
    def grid_refresh_reference(self, refresh_bool):
        
        if refresh_bool:
            self.refresh_reference_option = True
        else:
            self.refresh_reference_option = False
    
    def grid_move(self):
        """ se mueve siguiendo las coordenadas que lee del archivo"""

        axes=['A', 'B']
        targets = [self.grid_x[self.i_global] + self.startX,
                   self.grid_y[self.i_global] + self.startY]
       
        self.pi_device.MOV(axes, targets)
        time.sleep(0.01)
        
        self.grid_move_finishSignal.emit()
        
        
    @pyqtSlot()
    def grid_autofoco(self):
        
        multifoco = np.arange(0, self.particulas -1, self.autofoc)
                              
        if self.i_global in multifoco:
            print("Estoy haciendo foco en la particula =", self.i_global)
            
            if self.shiftx != 0  or self.shifty != 0 :
                axes=['A', 'B']
                targets = [self.shiftx + self.grid_x[self.i_global] + self.startX, self.shifty + self.grid_y[self.i_global] + self.startY]
                self.pi_device.MOV(axes, targets)
                time.sleep(0.01)
            
            self.grid_autofocusSignal.emit(self.mode_printing)  

        else:

            self.grid_center_scan()
            
    @pyqtSlot() 
    def grid_finish_autofoco(self):
          
        if self.shiftx != 0  or self.shifty != 0 :
           axes=['A', 'B']
           targets_return = [self.grid_x[self.i_global] + self.startX, self.grid_y[self.i_global] + self.startY]
           self.pi_device.MOV(axes, targets_return)
           time.sleep(0.01)
      
        self.grid_center_scan()

    def grid_center_scan(self):
        
        self.number_scan = 'center_scan'
        self.grid_scanSignal.emit(self.laser, self.mode_printing, self.number_scan)
    
    @pyqtSlot(np.ndarray, list, np.ndarray, np.ndarray) 
    def grid_center_scan_detect(self, image, center_mass, image_gone, image_back):
        
        self.save_scan(image, image_gone, image_back)
        
        axes=['A', 'B']
        self.center_mass_x = center_mass[0]
        self.center_mass_y = center_mass[1]
        targets = [self.center_mass_x, self.center_mass_y]
        self.pi_device.MOV(axes, targets)
        time.sleep(0.01)

        Flipper_notch532(self.flipper532task, 'up')
        time.sleep(0.15)

        self.grid_confocal_spectrum_fast()

    def grid_confocal_spectrum_fast(self):

        NP = "NP_%03d"%(int(self.i_global))
        Col = "Col_%03d"%(int(self.i_global/self.n) + 1)

        print('Measuring Fast Spectral Confocal image on %s at %s' % (NP, Col))

        folder_NP_spectrum = os.path.join(self.new_folder, "Fast_Confocal_Spectrum_" + Col + "_" + NP)
        os.makedirs(folder_NP_spectrum)
        
        self.grid_spectrum_fast_Signal.emit(self.laser, self.mode_printing, folder_NP_spectrum) 

    @pyqtSlot(list)                
    def grid_confocal_spectrum_fast_detect(self, position):

        axes=['A', 'B']
        position_x = position[0]
        position_y = position[1]
        targets = [position_x, position_y]
        self.pi_device.MOV(axes, targets)
        time.sleep(0.01)

        self.grid_confocal_spectrum()

           
    def grid_confocal_spectrum(self):

        NP = "NP_%03d"%(int(self.i_global))
        Col = "Col_%03d"%(int(self.i_global/self.n) + 1)

        print('Measuring Slow Spectral Confocal image on %s at %s' % (NP, Col))

        folder_NP_spectrum = os.path.join(self.new_folder, "Slow_Confocal_Spectrum_" + Col + "_" + NP)
        os.makedirs(folder_NP_spectrum)
        
        self.grid_spectrumSignal.emit(self.laser, self.mode_printing, folder_NP_spectrum)
        self.grid_traceSignal.emit(self.laser, self.mode_printing, folder_NP_spectrum) 
            
    @pyqtSlot(list)                
    def grid_confocal_spectrum_detect(self, center_mass): 
        
        self.grid_trace_stopSignal.emit()

        Flipper_notch532(self.flipper532task,'down')
        time.sleep(0.15)
        
        last_center_mass_x = center_mass[0]
        last_center_mass_y = center_mass[1]
        
        if self.refresh_reference_option:
            self.startX = last_center_mass_x - self.grid_x[self.i_global]
            self.startY = last_center_mass_y - self.grid_y[self.i_global]

        self.grid_detect()
        
    def save_scan(self, image, image_gone, image_back):
        """ Config the path and name of the file to save, and save it"""
 
        filepath = self.new_folder
        timestr = "NPscan_%03d"%(int(self.i_global))
        
        name = str(filepath + "/" + timestr + ".tiff")
        guardado = Image.fromarray(np.transpose(image))
        guardado.save(name)  
        
        name_gone = str(filepath + "/" + "gone_" + timestr + ".tiff")
        guardado_gone = Image.fromarray(np.transpose(image_gone))
        guardado_gone.save(name_gone)
        
        name_back = str(filepath + "/" + "back_" + timestr + ".tiff")
        guardado_back = Image.fromarray(np.transpose(image_back))
        guardado_back.save(name_back)
        
        print("\n Sacans saved\n")
        
    def grid_detect(self):
        """ Cuando detecta un evento de impresion y la escanea (o no), entra aca.
        Esta funcion define el paso siguiente."""

        Nmax = self.particulas -1  # self.Nmax  cantidad total de particulas

        print(" i global ", self.i_global)

        if self.i_global >= Nmax:
            
            self.file_path = self.old_folder
            self.namefolderSignal.emit(self.old_folder)
            self.indexSignal.emit(self.i_global+1)
            print('Fin de grilla')
        else:
            self.i_global += 1
            self.indexSignal.emit(self.i_global)
            
            self.grid_move()

    @pyqtSlot(list)
    def grid_extra_info(self, info):
        
        filepath = self.new_folder
        timestr = str("Info")
        name = str(filepath + "/" + timestr + ".txt")
        
        f = open(name, "w")
        np.savetxt(name, info, fmt="%s")
        f.close()
        print("\n Save info.")

            
    def make_connection(self, frontend):
        
        frontend.setreferenceSignal.connect(self.set_reference)
        frontend.goreferenceSignal.connect(self.go_reference)
        
        frontend.readgridSignal.connect(self.grid_read)
        frontend.gridcreateSignal.connect(self.grid_create)
        frontend.foldergridSignal.connect(self.grid_create_folder)
        
        frontend.parametersSignal.connect(self.grid_parameters)
        frontend.gridSignal.connect(self.grid_measurment)
        frontend.pauseSignal.connect(self.grid_pause)
        frontend.next_index_Signal.connect(self.grid_next_index)
        frontend.new_index_Signal.connect(self.grid_change_index)
        
        frontend.reference_refreshSignal.connect(self.grid_refresh_reference)

        frontend.gridinfoSignal.connect(self.grid_extra_info)
        
        