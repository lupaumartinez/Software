
import numpy as np
import tkinter as tk
from tkinter import filedialog

import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from pyqtgraph.dockarea import Dock, DockArea
from PIL import Image

pixel_size_canon = 0.058 #um

class Frontend(QtGui.QFrame):

    setimgSignal = pyqtSignal()
    moveSignal = pyqtSignal(float, float, float, float)
    setreferenceSignal = pyqtSignal(float, float)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setUpGUI()
            
    def setUpGUI(self):
        
        imageWidget = pg.GraphicsLayoutWidget()
        self.vb = imageWidget.addViewBox(row=1, col=1)
        self.vb.setMouseMode(pg.ViewBox.RectMode)
        self.vb.setAspectLocked(True, ratio= 1)
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

        #reference_x_Label = QtGui.QLabel('Initial X')
        #self.reference_x = QtGui.QLabel('NaN')
        #reference_y_Label = QtGui.QLabel('Initial Y')
        #self.reference_y = QtGui.QLabel('NaN')

        self.move_distance_x = QtGui.QPushButton('mov x')
        self.move_distance_x.clicked.connect(self.set_mov_x)

        self.move_distance_y = QtGui.QPushButton('mov y')
        self.move_distance_y.clicked.connect(self.set_mov_y)
        
        distancex_Label = QtGui.QLabel('real distance x (µm)')
        self.distancex_Edit = QtGui.QLineEdit('10')
        
        distancey_Label = QtGui.QLabel('real distance y (µm)')
        self.distancey_Edit = QtGui.QLineEdit('10')
        
        pixel_size_Label = QtGui.QLabel('pixel size canon (µm)')
        self.pixel_size = QtGui.QLabel(str(pixel_size_canon))
        
        self.distance_Edit = QtGui.QLineEdit('1')

        cursor_x_Label = QtGui.QLabel('Cursor X')
        self.cursor_x = QtGui.QLabel('NaN')
        cursor_y_Label = QtGui.QLabel('Cursor Y')
        self.cursor_y = QtGui.QLabel('NaN')

        layout.addWidget(self.set_img_button, 0,0)

        layout.addWidget(self.set_reference_button, 0,1)

        layout.addWidget(self.move_distance_x, 3, 2)
        layout.addWidget(self.move_distance_y, 4, 2)
        
        layout.addWidget(distancex_Label,        5, 1)
        layout.addWidget(self.distancex_Edit,    5, 2)
        layout.addWidget(distancey_Label,        6, 1)
        layout.addWidget(self.distancey_Edit,    6, 2)
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
           self.move_distance_x.setEnabled(False)
           self.move_distance_y.setEnabled(False)
        else:
           self.move_distance_x.setEnabled(True)
           self.move_distance_y.setEnabled(True)
           
    @pyqtSlot(np.ndarray)
    def get_img(self, image):
        self.img.setImage(image)

    def set_mov_y(self):

        x_cursor = float(self.cursor_x.text())
        y_cursor = float(self.cursor_y.text())
        
        pixel_y = np.round(float(self.distancey_Edit.text())/pixel_size_canon, 3)

        self.moveSignal.emit(x_cursor, y_cursor, 0, pixel_y)

    def set_mov_x(self):

        x_cursor = float(self.cursor_x.text())
        y_cursor = float(self.cursor_y.text()) 

        pixel_x = np.round(float(self.distancex_Edit.text())/pixel_size_canon, 3)
        
        self.moveSignal.emit(x_cursor, y_cursor, pixel_x, 0)
    
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.referencebool = False

    @pyqtSlot()
    def send_image(self):

        root = tk.Tk()
        root.withdraw()

        name = filedialog.askopenfilename()  
        im = Image.open(name)
        im_t = im.transpose(Image.ROTATE_270)
        data_image = np.array(im_t) 

        print(im.width, im.height)

        self.total_pixel_x = im.height
        self.total_pixel_y = im.width

        self.imgSignal.emit(data_image)

        self.go_initial_cursor()

    def go_initial_cursor(self):
        
        x_cursor_initial = self.total_pixel_x/2
        y_cursor_initial = self.total_pixel_y/2
        
        self.datacursorSignal.emit([x_cursor_initial , y_cursor_initial])


    @pyqtSlot(float, float, float, float)    
    def cursor(self, x_cursor, y_cursor, pixel_x, pixel_y):

        x_new_cursor = np.round(x_cursor - pixel_x, 3)
        y_new_cursor = np.round(y_cursor + pixel_y, 3)
        
        self.datacursorSignal.emit([x_new_cursor, y_new_cursor])

    @pyqtSlot(float, float)
    def set_cursor_reference(self, x_cursor_reference, y_cursor_reference):

        #pos = pi_device.qPOS()
        
        #self.x_pos_reference = pos['A']
        #self.y_pos_reference = pos['B']

        self.x_cursor_reference = x_cursor_reference 
        self.y_cursor_reference = y_cursor_reference
        
        self.referencebool = True

    @pyqtSlot(list)    #espera señal que viene de Nanpositioning
    def real_cursor(self, pos):

        x_new_pos = pos[0]
        y_new_pos = pos[1]

        distance_x = (x_new_pos - self.x_pos_reference)/pixel_size_canon
        distance_y = (y_new_pos - self.x_pos_reference)/pixel_size_canon

        x_new_cursor = self.x_cursor_reference - distance_x
        y_new_cursor = self.y_cursor_reference + distance_y

        if self.referencebool: 
           self.datacursorSignal.emit([x_new_cursor, y_new_cursor])
  
    def make_connection(self, frontend): 

        frontend.setimgSignal.connect(self.send_image) 
        frontend.moveSignal.connect(self.cursor)
        frontend.setreferenceSignal.connect(self.set_cursor_reference)
                
if __name__ == '__main__':

    app = QtGui.QApplication([])

    gui = Frontend()   
    worker = Backend()

    worker.make_connection(gui)
    gui.make_connection(worker)

    cursorThread = QtCore.QThread()
    worker.moveToThread(cursorThread)
    cursorThread.start()

    gui.show()
    app.exec_()


