
import time
from datetime import datetime
import numpy as np

from pyqtgraph.Qt import QtCore, QtGui
from pyqtgraph.dockarea import DockArea, Dock
from PyQt5.QtCore import pyqtSignal, pyqtSlot

class Frontend(QtGui.QFrame):

    read_pos_button_signal = pyqtSignal()
    move_signal = pyqtSignal(str, float)
    go_to_pos_signal = pyqtSignal(list)
    set_reference_signal = pyqtSignal()

    closeSignal = pyqtSignal()

    def __init__(self, *args, **kwargs):  
        super().__init__(*args, **kwargs)

        self.setUpGUI()
           
# Possitioner - Buttons

    @pyqtSlot(list)
    def read_pos_list(self, positions):
        list_pos = positions
        self.xLabel.setText(str(list_pos[0]))
        self.yLabel.setText(str(list_pos[1]))
        self.zLabel.setText(str(list_pos[2]))

    def get_read_pos(self):
        if self.read_pos_button.isChecked:
           self.read_pos_button_signal.emit()
          # self.read_pos_list()

    def xUp(self):
        if self.xUpButton.isChecked:
            self.move_signal.emit('x', float(self.StepEdit.text()))
   
    def xUp2(self):
        if self.xUp2Button.isChecked:
            self.move_signal.emit('x', 10*float(self.StepEdit.text()))

    def xDown(self):
        if self.xDownButton.isChecked:
            self.move_signal.emit('x', -float(self.StepEdit.text()))

    def xDown2(self):
        if self.xDown2Button.isChecked:
            self.move_signal.emit('x', -10*float(self.StepEdit.text()))

    def yUp(self):
        if self.yUpButton.isChecked:
            self.move_signal.emit('y', float(self.StepEdit.text()))

    def yUp2(self):
        if self.xUp2Button.isChecked:
            self.move_signal.emit('y', 10*float(self.StepEdit.text()))

    def yDown(self):
        if self.yDownButton.isChecked:
            self.move_signal.emit('y', -float(self.StepEdit.text()))

    def yDown2(self):
        if self.yDown2Button.isChecked:
            self.move_signal.emit('y', -10*float(self.StepEdit.text()))

    def zUp(self):
        if self.zUpButton.isChecked:
            self.move_signal.emit('z', float(self.zStepEdit.text()))
   
    def zUp2(self):
        if self.zUp2Button.isChecked:
            self.move_signal.emit('z', 10*float(self.zStepEdit.text()))

    def zDown(self):
        if self.zDownButton.isChecked:
            self.move_signal.emit('z', -float(self.zStepEdit.text()))

    def zDown2(self):
        if self.zDown2Button.isChecked:
            self.move_signal.emit('z', -10*float(self.zStepEdit.text()))
            
    def set_reference(self):
        if self.set_ref_button.isChecked:
            self.set_reference_signal.emit()
            
    @pyqtSlot(list)        
    def get_go_to_reference(self, positions):
        list_pos = positions
        self.xgotoLabel.setText(str(list_pos[0]))
        self.ygotoLabel.setText(str(list_pos[1]))
        self.zgotoLabel.setText(str(list_pos[2]))

    def go_to_action(self):
        go_to_pos = [float(self.xgotoLabel.text()), float(self.ygotoLabel.text()), float(self.zgotoLabel.text())]
           
        if self.gotoButton.isChecked:
           self.go_to_pos_signal.emit(go_to_pos)
   
    def setUpGUI(self):

        # # Positioner - Read position
        self.read_pos_button = QtGui.QPushButton("Read position")
        self.read_pos_button.clicked.connect(self.get_read_pos)
        self.read_pos_button.setToolTip('The actual position')
        self.read_pos_Label = QtGui.QLabel('Position')
        
        # # Positioner - Set reference
        self.set_ref_button = QtGui.QPushButton("Set reference")
        self.set_ref_button.clicked.connect(self.set_reference)
        self.set_ref_button.setToolTip('The actual position')
        
        # # Positioner - Axes control
        self.StepEdit = QtGui.QLineEdit("1")

        self.xLabel = QtGui.QLabel('Nan')
        self.xLabel.setTextFormat(QtCore.Qt.RichText)
        self.xname = QtGui.QLabel("<strong>x =")
        self.xname.setTextFormat(QtCore.Qt.RichText)
        self.xUpButton = QtGui.QPushButton("x ►")
        self.xDownButton = QtGui.QPushButton("◄ x")
        self.xUp2Button = QtGui.QPushButton("x ►►")  
        self.xDown2Button = QtGui.QPushButton("◄◄ x")
        self.xUpButton.pressed.connect(self.xUp)
        self.xUp2Button.pressed.connect(self.xUp2)
        self.xDownButton.pressed.connect(self.xDown)
        self.xDown2Button.pressed.connect(self.xDown2)

        self.yLabel = QtGui.QLabel('Nan')
        self.yLabel.setTextFormat(QtCore.Qt.RichText)
        self.yname = QtGui.QLabel("<strong>y =")
        self.yname.setTextFormat(QtCore.Qt.RichText)
        self.yUpButton = QtGui.QPushButton("y ▲")  # ↑
        self.yDownButton = QtGui.QPushButton("y ▼")  # ↓
        self.yUp2Button = QtGui.QPushButton("y ▲▲")  # ↑
        self.yDown2Button = QtGui.QPushButton("y ▼▼")  # ↓
        self.yUpButton.pressed.connect(self.yUp)
        self.yUp2Button.pressed.connect(self.yUp2)
        self.yDownButton.pressed.connect(self.yDown)
        self.yDown2Button.pressed.connect(self.yDown2)

        self.zLabel = QtGui.QLabel('Nan')  
        self.zLabel.setTextFormat(QtCore.Qt.RichText)
        self.zname = QtGui.QLabel("<strong>z =")
        self.zname.setTextFormat(QtCore.Qt.RichText)
        self.zUpButton = QtGui.QPushButton("z ▲")
        self.zDownButton = QtGui.QPushButton("z ▼")
        self.zUp2Button = QtGui.QPushButton("z ▲▲")
        self.zDown2Button = QtGui.QPushButton("z ▼▼")
        self.zUpButton.pressed.connect(self.zUp)
        self.zUp2Button.pressed.connect(self.zUp2)
        self.zDownButton.pressed.connect(self.zDown)
        self.zDown2Button.pressed.connect(self.zDown2)
        self.zStepEdit = QtGui.QLineEdit("0.2")

        tamaño = 30
        self.xLabel.setFixedWidth(tamaño)
        self.yLabel.setFixedWidth(tamaño)
        self.zLabel.setFixedWidth(tamaño)
        
        tamaño = 50
        self.xUp2Button.setFixedWidth(tamaño)
        self.xDown2Button.setFixedWidth(tamaño)
        self.xUpButton.setFixedWidth(tamaño)
        self.xDownButton.setFixedWidth(tamaño)
        self.yUp2Button.setFixedWidth(tamaño)
        self.yDown2Button.setFixedWidth(tamaño)
        self.yUpButton.setFixedWidth(tamaño)
        self.yDownButton.setFixedWidth(tamaño)
        
# Positioner - Interface

        self.positioner = QtGui.QWidget()
        layout = QtGui.QGridLayout()
        self.positioner.setLayout(layout)
        
        layout.addWidget(self.xname,        1, 0)
        layout.addWidget(self.xLabel,       1, 1)
        layout.addWidget(self.xUpButton,    2, 6, 2, 1)
        layout.addWidget(self.xDownButton,  2, 4, 2, 1)
        layout.addWidget(self.xUp2Button,   2, 7, 2, 1)
        layout.addWidget(self.xDown2Button, 2, 3, 2, 1)

        layout.addWidget(self.yname,       2, 0)
        layout.addWidget(self.yLabel,      2, 1)
        layout.addWidget(self.yUpButton,   1, 5, 3, 1)
        layout.addWidget(self.yDownButton, 3, 5, 2, 1)
        layout.addWidget(QtGui.QLabel("step x/y [µm]"), 4, 6, 1, 2)
        layout.addWidget(self.StepEdit,   5, 6)
        layout.addWidget(self.yUp2Button,   0, 5, 2, 1)
        layout.addWidget(self.yDown2Button, 4, 5, 2, 1)

        layout.addWidget(self.zname,       4, 0)
        layout.addWidget(self.zLabel,      4, 1)
        layout.addWidget(self.zUp2Button,   0, 9, 2, 1)
        layout.addWidget(self.zUpButton,   1, 9, 3, 1)
        layout.addWidget(self.zDownButton, 3, 9, 2, 1)
        layout.addWidget(self.zDown2Button, 4, 9, 2, 1)
        layout.addWidget(QtGui.QLabel("step z [µm]"), 4, 10)
        layout.addWidget(self.zStepEdit,   5, 10)

        layout.addWidget(self.read_pos_button, 0, 0, 1, 2)
        layout.addWidget(self.set_ref_button,  5,0)
        
        tamaño = 40
        self.StepEdit.setFixedWidth(tamaño)
        self.zStepEdit.setFixedWidth(tamaño)

        
 #%% Go to - Interface and buttons

        self.gotoWidget = QtGui.QWidget()
        layout2 = QtGui.QGridLayout()
        self.gotoWidget.setLayout(layout2)
        
        layout2.addWidget(QtGui.QLabel("X [µm]"), 1, 1)
        layout2.addWidget(QtGui.QLabel("Y [µm]"), 2, 1)
        layout2.addWidget(QtGui.QLabel("Z [µm]"), 3, 1)
        
        self.xgotoLabel = QtGui.QLineEdit("100")
        self.ygotoLabel = QtGui.QLineEdit("100")
        self.zgotoLabel = QtGui.QLineEdit("50")
        self.gotoButton = QtGui.QPushButton("Go to")
        self.gotoButton.pressed.connect(self.go_to_action)
        
        layout2.addWidget(self.gotoButton, 1, 5, 2, 2)
        layout2.addWidget(self.xgotoLabel, 1, 2)
        layout2.addWidget(self.ygotoLabel, 2, 2)
        layout2.addWidget(self.zgotoLabel, 3, 2)
 
        tamaño = 50
        self.xgotoLabel.setFixedWidth(tamaño)
        self.ygotoLabel.setFixedWidth(tamaño)
        self.zgotoLabel.setFixedWidth(tamaño)
        
  #o docks       
        
        hbox = QtGui.QHBoxLayout(self)
        dockArea = DockArea()

             # Positioner
        posDock = Dock('Positioners', size=(1, 1))
        posDock.addWidget(self.positioner)
        dockArea.addDock(posDock)

             # Go to  
        gotoDock = Dock('Go to', size=(1, 1))
        gotoDock.addWidget(self.gotoWidget)
        dockArea.addDock(gotoDock, 'left', posDock)
        
        hbox.addWidget(dockArea)
        self.setLayout(hbox)

    def closeEvent(self, *args, **kwargs):
        
        self.closeSignal.emit()
        
        super().closeEvent(*args, **kwargs)
        
    def make_connection(self, backend):
        backend.read_pos_signal.connect(self.read_pos_list)
        backend.reference_signal.connect(self.get_go_to_reference)
        
#%%
class Backend(QtCore.QObject):

    read_pos_signal = pyqtSignal(list)
    reference_signal = pyqtSignal(list)

    def __init__(self, pi_device, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.pi_device = pi_device

        self.read_pos()

    @pyqtSlot()
    def read_pos(self):
        """lee las entradas analogicas que manda la platina y se donde estoy""" 
        pos = self.pi_device.qPOS()
        x_pos = pos['A']
        y_pos = pos['B']
        z_pos = pos['C']

        self.read_pos_signal.emit([x_pos, y_pos, z_pos])

        return x_pos, y_pos, z_pos
        
    @pyqtSlot()
    def set_reference(self): 
        
        x_pos, y_pos, z_pos = self.read_pos()
        self.reference_signal.emit([x_pos, y_pos, z_pos])
        
    @pyqtSlot(str, float)
    def move(self, axis, dist):
        """moves the position along the axis specified a distance dist."""
        x_pos, y_pos, z_pos = self.read_pos()
        inicial = 0
        if axis == 'x':
            axes = 'A'
            inicial = x_pos
        elif axis == 'y':
            axes = 'B'
            inicial = y_pos
        elif axis == 'z':
            axes = 'C'
            inicial = z_pos
        else:
            print("Pone un eje conocido! (x,y,z)")
        target = dist + inicial

        self.pi_device.MOV(axes, target)
        while not all(self.pi_device.qONT(axes).values()):
            time.sleep(0.01)
        self.read_pos()

    @pyqtSlot(list)
    def goto(self, go_to_pos):
        x_o, y_o, z_o = self.read_pos()
        if go_to_pos[2] < 0:
            print("Z can't be negative!")
        else:
            print("arranco en", x_o, y_o, z_o)
            self.moveto(go_to_pos)
            x_f, y_f, z_f = self.read_pos()
            print("termino en", x_f, y_f, z_f)

    def moveto(self, move_pos):
        """moves the position along the axis to a specified point.
        Cambie todo paraque ande con la PI"""

        axis = ['A', 'B', 'C']
        targets = [move_pos[0], move_pos[1], move_pos[2]]

        self.pi_device.MOV(axis, targets)
        while not all(self.pi_device.qONT(axis).values()):
            time.sleep(0.01)


    @pyqtSlot()
    def close(self):
        
        x_pos, y_pos, z_pos = self.read_pos()
        
        last_position = [x_pos, y_pos, z_pos]
        
        filepath = "C:/Users/CibionPC/Desktop/PyPrinting/"
        name = str(filepath  + "/" + "Last_position.txt")
        
        f = open(name, "w")
        np.savetxt(name, last_position)
        f.close()
        
        print("\n Save Last position on x, y, z:", last_position)
        
        self.pi_device.MOV(['A','B','C'], [0, 0, 0])
        self.pi_device.CloseConnection()

        print(datetime.now(), '[Nanopositioning] Close')

    def make_connection(self, frontend):
        frontend.read_pos_button_signal.connect(self.read_pos)
        frontend.move_signal.connect(self.move)
        frontend.go_to_pos_signal.connect(self.goto)
        frontend.set_reference_signal.connect(self.set_reference)
        frontend.closeSignal.connect(self.close)


#%%
if __name__ == '__main__':
    
    app = QtGui.QApplication([])
    gui = Frontend()
    
    from pipython import GCSDevice
    from Instrument_PI import initial_pi_device
    
    pi_device= GCSDevice()
    initial_pi_device(pi_device)
    worker = Backend(pi_device)

    worker.make_connection(gui)
    gui.make_connection(worker)

    nanopositioningThread = QtCore.QThread()
    worker.moveToThread(nanopositioningThread)
    nanopositioningThread.start()

    gui.show()
    app.exec_()