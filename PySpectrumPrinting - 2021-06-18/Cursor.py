
import numpy as np
import tkinter as tk
from tkinter import filedialog

import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from pyqtgraph.dockarea import Dock, DockArea
from PIL import Image

from pipython import GCSDevice
import Instrument_PI 

pixel_size_canon = 0.059 #um

class Frontend(QtGui.QFrame):

    setimgSignal = pyqtSignal()
    moveSignal = pyqtSignal(float, float, float, float)
    setreferenceSignal = pyqtSignal(float, float)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setUpGUI()
            
    def setUpGUI(self):
        
        imageWidget = pg.GraphicsLayoutWidget()
        self.vb = imageWidget.addPlot()
       # self.vb.invertY()
        self.img = pg.ImageItem()
        self.vb.addItem(self.img)
        
        self.point_graph_cursor = pg.ScatterPlotItem(size=25,
                                                 symbol='+', color='b')      

        self.cursorWidget = QtGui.QWidget()
        layout = QtGui.QGridLayout()
        self.cursorWidget.setLayout(layout) 

        self.set_img_button = QtGui.QPushButton('Set image')
        self.set_img_button.clicked.connect(self.set_img)

        self.set_reference_button = QtGui.QPushButton('Set reference')
        self.set_reference_button.setCheckable(True)
        self.set_reference_button.clicked.connect(self.set_reference)
        
        pixel_size_Label = QtGui.QLabel('pixel size canon (µm)')
        self.pixel_size = QtGui.QLabel(str(pixel_size_canon))

        self.mov_x_sl = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.mov_x_sl.setMinimum(1)
        self.mov_x_sl.setMaximum(3168)
        self.mov_x_sl.setValue(1584)
        self.mov_x_sl.setTickPosition(QtGui.QSlider.TicksBelow)
        self.mov_x_sl.setTickInterval(1)
        self.mov_x_sl.valueChanged.connect(self.set_mov_x)

        self.mov_y_sl = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.mov_y_sl.setMinimum(1)
        self.mov_y_sl.setMaximum(4752)
        self.mov_y_sl.setValue(2376)
        self.mov_y_sl.setTickPosition(QtGui.QSlider.TicksBelow)
        self.mov_y_sl.setTickInterval(1)
        self.mov_y_sl.valueChanged.connect(self.set_mov_y)

        cursor_x_Label = QtGui.QLabel('Cursor X')
        self.cursor_x = QtGui.QLabel('NaN')
        cursor_y_Label = QtGui.QLabel('Cursor Y')
        self.cursor_y = QtGui.QLabel('NaN')

        self.cursor_x.setText(format(int(self.mov_x_sl.value())))
        self.cursor_y.setText(format(int(self.mov_y_sl.value())))

        self.x_cursor = float(self.cursor_x.text())
        self.y_cursor = float(self.cursor_y.text())

        layout.addWidget(self.set_img_button, 0,0)

        layout.addWidget(self.set_reference_button, 0,1)

        layout.addWidget(self.mov_x_sl, 3, 2)
        layout.addWidget(self.mov_y_sl, 4, 2)
        layout.addWidget(pixel_size_Label ,      7, 1)
        layout.addWidget(self.pixel_size,        7, 2)

        layout.addWidget(cursor_x_Label, 3, 0)
        layout.addWidget(self.cursor_x,  3, 1)
        layout.addWidget(cursor_y_Label, 4, 0)
        layout.addWidget(self.cursor_y,  4, 1)

        dockArea = DockArea()
        hbox = QtGui.QHBoxLayout(self)

        viewDock = Dock('Viewbox',size=(100,400))
        viewDock.addWidget(imageWidget)
        viewDock.hideTitleBar()
        dockArea.addDock(viewDock)

        cursorDock = Dock('Cursor')
        cursorDock.addWidget(self.cursorWidget)
        dockArea.addDock(cursorDock, 'right', viewDock)
        
        hbox.addWidget(dockArea)
        self.setLayout(hbox)

    def set_img(self):
        if self.set_img_button.isChecked:
           self.setimgSignal.emit()

    def set_reference(self):
        if self.set_reference_button.isChecked():
           x_cursor_reference = float(self.cursor_x.text())
           y_cursor_reference = float(self.cursor_y.text())
           self.setreferenceSignal.emit(x_cursor_reference, y_cursor_reference)
           self.mov_x_sl.setEnabled(False)
           self.mov_y_sl.setEnabled(False)
        else:
           self.mov_x_sl.setEnabled(True)
           self.mov_y_sl.setEnabled(True)
           
    @pyqtSlot(np.ndarray)
    def get_img(self, image):
        self.img.setImage(image)

    def set_mov_y(self):

        self.cursor_y.setText(format(int(self.mov_y_sl.value())))
        self.y_cursor = float(self.cursor_y.text())
        pixel_y = pixel_size_canon

        self.moveSignal.emit(self.x_cursor, self.y_cursor, 0, pixel_y)

    def set_mov_x(self):

        self.cursor_x.setText(format(int(self.mov_x_sl.value())))
        self.x_cursor = float(self.cursor_x.text())
        pixel_x = pixel_size_canon
        
        self.moveSignal.emit(self.x_cursor, self.y_cursor, pixel_x, 0)
    
    @pyqtSlot(list)
    def get_cursor_values(self, data_cursor):

        point_cursor_x = data_cursor[0]
        point_cursor_y = data_cursor[1]

        self.cursor_x.setText(format(point_cursor_x))
        self.cursor_y.setText(format(point_cursor_y))

        self.point_graph_cursor.setData([point_cursor_y], [point_cursor_x])
        self.vb.addItem(self.point_graph_cursor)

  
    def make_connection(self, backend):
        backend.imgSignal.connect(self.get_img)
        backend.datacursorSignal.connect(self.get_cursor_values)

class Backend(QtCore.QObject):

    imgSignal = pyqtSignal(np.ndarray)
    datacursorSignal = pyqtSignal(list)

    def __init__(self, pi_device, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.pi_device = pi_device
        
        self.referencebool = False
        self.x_pos_reference = 0
        self.y_pos_reference = 0
        self.x_cursor_reference = 0
        self.y_cursor_reference = 0
        
    @pyqtSlot()
    def send_image(self):

        root = tk.Tk()
        root.withdraw()

        name = filedialog.askopenfilename()  
        im = Image.open(name)
        
        im_t = im.transpose(Image.ROTATE_270)
        data_image = np.array(im_t) 

        self.total_pixel_x = 3168
        self.total_pixel_y = 4752

        self.imgSignal.emit(data_image)

        self.go_initial_cursor()

    def go_initial_cursor(self):
        
        x_cursor_initial = self.total_pixel_x/2
        y_cursor_initial = self.total_pixel_y/2
        
        self.datacursorSignal.emit([x_cursor_initial , y_cursor_initial])


    @pyqtSlot(float, float, float, float)    
    def cursor(self, x_cursor, y_cursor, pixel_x, pixel_y):

        x_new_cursor = x_cursor
        y_new_cursor = y_cursor
        
        self.datacursorSignal.emit([x_new_cursor, y_new_cursor])

    @pyqtSlot(float, float)
    def set_cursor_reference(self, x_cursor_reference, y_cursor_reference):

        pos = self.pi_device.qPOS()
        
        self.x_pos_reference = pos['A']
        self.y_pos_reference = pos['B']

        self.x_cursor_reference = x_cursor_reference 
        self.y_cursor_reference = y_cursor_reference
        
        self.referencebool = True

    @pyqtSlot(list)    #espera señal que viene de Nanpositioning
    def real_cursor(self, pos):

        x_new_pos = pos[0]
        y_new_pos = pos[1]

        distance_x = (x_new_pos - self.x_pos_reference)/pixel_size_canon
        distance_y = (y_new_pos - self.y_pos_reference)/pixel_size_canon

        x_new_cursor = round(self.x_cursor_reference - distance_x, 2)
        y_new_cursor = round(self.y_cursor_reference + distance_y, 2)

        if self.referencebool: 
           self.datacursorSignal.emit([x_new_cursor, y_new_cursor])
  
    def make_connection(self, frontend): 

        frontend.setimgSignal.connect(self.send_image) 
        frontend.moveSignal.connect(self.cursor)
        frontend.setreferenceSignal.connect(self.set_cursor_reference)
                
if __name__ == '__main__':

    app = QtGui.QApplication([])

    gui = Frontend()   
    
    pi_device= GCSDevice()
    Instrument_PI.initial_pi_device(pi_device)
    worker = Backend(pi_device)

    worker.make_connection(gui)
    gui.make_connection(worker)

    gui.show()
   # app.exec_()


