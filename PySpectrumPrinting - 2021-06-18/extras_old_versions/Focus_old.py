
import numpy as np
import time
from scipy import signal

import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore
from PyQt5.QtCore import pyqtSignal, pyqtSlot

from Instrument_nidaqmx  import channels_photodiodos, channels_triggers, shutters, openShutter, closeShutter, PD_channels, PDchans, rateNI
from Instrument_PI import pi_device, servo_time

class Frontend(QtGui.QFrame):

    focus_gotomax_signal = pyqtSignal(int)
    focus_lock_signal = pyqtSignal(bool, int)
    focus_auto_signal = pyqtSignal()
    focus_autox2_signal = pyqtSignal(str)
    
   # plot_close_Signal = pyqtSignal()   #para cerrar las ventanas de ploteo luego de 2 segundos
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setUpGUI()
        
        #self.plot_close_Signal.connect(self.plot_close_window)
        
    def setUpGUI(self):
        
        
     #Shortcuts
        
        self.focus_maximum_action = QtGui.QAction(self)
        QtGui.QShortcut(
            QtGui.QKeySequence('F8'), self, self.get_focus_go_to_maximum)
            
        self.lock_focus_action = QtGui.QAction(self)
        QtGui.QShortcut(
            QtGui.QKeySequence('F9'), self, self.get_focus_lock_lin)
            
        self.focus_autocorr_action = QtGui.QAction(self)
        QtGui.QShortcut(
            QtGui.QKeySequence('F10'), self, self.get_focus_autocorr_lin)
            
     # Defino el laser
        self.focus_laser = QtGui.QComboBox()
        self.focus_laser.addItems(shutters)
        self.focus_laser.setCurrentIndex(0)
        self.focus_laser.setToolTip('Elijo el shutter')
        self.focus_laser.setFixedWidth(80)
        self.focus_laser.activated.connect(
                                    lambda: self.color_menu(self.focus_laser))
        self.color_menu(self.focus_laser)
            
    # Go to maximun
        self.focus_gotomax_button = QtGui.QPushButton('Go to maximum')
        self.focus_gotomax_button.setCheckable(True)
        self.focus_gotomax_button.clicked.connect(self.get_focus_go_to_maximum)
        self.focus_gotomax_button.setToolTip('va al z donde la señal es máxima')
        
    # Lockear el foco
        self.focus_lock_button = QtGui.QPushButton('Lock Focus')
        self.focus_lock_button.setCheckable(True)
        self.focus_lock_button.clicked.connect(self.get_focus_lock_lin)
        self.focus_lock_button.setToolTip('guarda el patron de intensidad en el z actual')
        self.focus_lock_button.setStyleSheet(
                "QPushButton { background-color: orange; }"
                "QPushButton:pressed { background-color: blue; }")

    # Autocorrelacion, con el foco ya lockeado
        self.focus_autocorr_button = QtGui.QPushButton('Autocorrelation')
        self.focus_autocorr_button.setCheckable(True)
        self.focus_autocorr_button.clicked.connect(self.get_focus_autocorr_lin)
        self.focus_autocorr_button.setToolTip('va al z lockeado')
        
        
    # Autocorrelacion, con el foco ya lockeado
        self.focus_autocorrx2_button = QtGui.QPushButton('Autocorrelation (x2)')
        self.focus_autocorrx2_button.setCheckable(True)
        self.focus_autocorrx2_button.clicked.connect(self.get_focus_autocorrx2_lin)
        self.focus_autocorrx2_button.setToolTip('va al z lockeado 2 veces')
        
    # Interface
        
        self.grid_focus = QtGui.QWidget()
        grid_focus_layout = QtGui.QGridLayout()
        self.grid_focus.setLayout(grid_focus_layout)
        grid_focus_layout.addWidget(self.focus_laser,             1, 1)
        grid_focus_layout.addWidget(self.focus_gotomax_button,    2, 1)
        grid_focus_layout.addWidget(self.focus_lock_button,       3, 1)
        #grid_focus_layout.addWidget(self.focus_autocorr_button,   4, 1)
        grid_focus_layout.addWidget(self.focus_autocorrx2_button,   4, 1)
        
        
      # GUI layout
        
        grid = QtGui.QGridLayout()
        self.setLayout(grid)
        
        grid.addWidget(self.grid_focus)
        
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
            
    def get_focus_go_to_maximum(self):
        if self.focus_gotomax_button.isChecked:
           self.focus_gotomax_signal.emit(self.focus_laser.currentIndex())

    def get_focus_lock_lin(self):
        if self.focus_lock_button.isChecked():
           self.focus_lock_signal.emit(True, self.focus_laser.currentIndex())
        else:
            self.focus_lock_signal.emit(False, self.focus_laser.currentIndex())
        
    def get_focus_autocorr_lin(self):
         if self.focus_autocorr_button.isChecked:
           self.focus_auto_signal.emit()
           
    def get_focus_autocorrx2_lin(self):
         mode_printing = 'none'
         if self.focus_autocorrx2_button.isChecked:
           self.focus_autox2_signal.emit(mode_printing)
                
    @pyqtSlot(np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray)
    def plot_focus(self, z_array_gone, z_profile_gone, z_profile_gone_filter, z_profile_gone_max, z_array_back, z_profile_back, z_profile_back_filter, z_profile_back_max):
       
        # Ventanas de ploteo
        
        self.graph_focus = pg.GraphicsLayoutWidget()
        self.graph_focus.show()
        
        plotfocus = self.graph_focus.addPlot(row=2, col=1, title="Go to maximum")
        plotfocus.showGrid(x=True, y=True)
        plotfocus.setLabel('left', "Photodiode (V)")
        plotfocus.setLabel('bottom', "z position (µm)")
               
        curve_gone = plotfocus.plot(open='y')
        curve_gone_filter = plotfocus.plot(open='y', name = "z profile gone")
        curve_back = plotfocus.plot(open='y')
        curve_back_filter = plotfocus.plot(open='y', name = "z profile back")
        point_max_gone = plotfocus.plot(open='y', name="max of z profile gone")
        point_max_back = plotfocus.plot(open='y', name="max of z profile back")

        curve_gone.setData(z_array_gone, z_profile_gone, pen=pg.mkPen('y', width=1),
                           shadowPen=pg.mkPen('w', width=3))

        curve_gone_filter.setData(z_array_gone, z_profile_gone_filter, pen=pg.mkPen('g', width=1),
                           shadowPen=pg.mkPen('w', width=3))
        
        point_max_gone.setData(z_array_gone, z_profile_gone_max, pen=pg.mkPen('g', width=3),
                           shadowPen=pg.mkPen('w', width=3))
        
        curve_back.setData(z_array_back, z_profile_back, pen=pg.mkPen('b', width=1),
                           shadowPen=pg.mkPen('w', width=3))

        curve_back_filter.setData(z_array_back, z_profile_back_filter, pen=pg.mkPen('m', width=1),
                           shadowPen=pg.mkPen('w', width=3))
        
        point_max_back.setData(z_array_back, z_profile_back_max, pen=pg.mkPen('m', width=3),
                           shadowPen=pg.mkPen('w', width=3))
        
       # time.sleep(5)
        
       # self.plot_close_Signal.emit()
        
    @pyqtSlot(np.ndarray, np.ndarray)       
    def plot_lock(self, z_profile_gone_lock, z_profile_lock_filter):
        
             # Ventanas de ploteo
        
        self.graph_focus = pg.GraphicsLayoutWidget()
        self.graph_focus.show()
        
        plotfocus = self.graph_focus.addPlot(row=2, col=1, title="Lock focus")
        plotfocus.showGrid(x=True, y=True)
        plotfocus.setLabel('left', "Photodiode (V)")
        
        curve = plotfocus.plot(open='y')
        curve_filter = plotfocus.plot(open='y', name="z profile gone")

        curve.setData(z_profile_gone_lock, pen=pg.mkPen('y', width=1),
                           shadowPen=pg.mkPen('w', width=3))

        curve_filter.setData(z_profile_lock_filter, pen=pg.mkPen('g', width=1),
                           shadowPen=pg.mkPen('w', width=3))
        
        
        #time.sleep(5)
       # self.plot_close_Signal.emit()
        
        
    @pyqtSlot(np.ndarray, np.ndarray, np.ndarray)       
    def plot_auto(self, new_profile_filter, z_profile_lock_filter, correlation):
        
        # Ventanas de ploteo  
        
        self.graph_focus = pg.GraphicsLayoutWidget()
        self.graph_focus.show()
        
        plotfocus = self.graph_focus.addPlot(row=2, col=1, title="Autocorrelation")
        
        plotfocus.showGrid(x=True, y=True)
        plotfocus.setLabel('left', "Photodiode (V)")
        
        curve = plotfocus.plot(open='y', name="new z profile gone")
        curve_filter = plotfocus.plot(open='y', name="lock z profile gone")
        curve_correlation = plotfocus.plot(open='y', name = "correlation" )

        curve.setData(new_profile_filter/max(new_profile_filter), pen=pg.mkPen('r', width=1),
                           shadowPen=pg.mkPen('w', width=3))

        curve_filter.setData(z_profile_lock_filter/max(z_profile_lock_filter), pen=pg.mkPen('g', width=1),
                           shadowPen=pg.mkPen('w', width=3))
        
        curve_correlation.setData(correlation/max(correlation), pen=pg.mkPen('b', width=1),
                           shadowPen=pg.mkPen('w', width=3))
        
        #time.sleep(5)
       # self.plot_close_Signal.emit()

   # @pyqtSlot()
   # def plot_close_window(self):
        #self.graph_focus.close()
        
    
    def make_connection(self,backend):
        backend.plot_focusSignal.connect(self.plot_focus)
        backend.plot_lockSignal.connect(self.plot_lock)
        backend.plot_autoSignal.connect(self.plot_auto)

class Backend(QtCore.QObject):
    
    gotomaxdoneSignal = pyqtSignal()
    lockdoneSignal = pyqtSignal()
    autodoneSignal = pyqtSignal()
    
    plot_focusSignal = pyqtSignal(np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray)
    plot_lockSignal = pyqtSignal(np.ndarray, np.ndarray)
    plot_autoSignal = pyqtSignal(np.ndarray, np.ndarray, np.ndarray)

    autofinishSignal_luminescence = pyqtSignal()
    autofinishSignal_growth = pyqtSignal()
    autofinishSignal_luminescence_steps = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.locked_focus = False
        self.ramp_lin_parameters()
        
    def ramp_lin_parameters(self):
        
        self.range = 16 #um  #recorrido de ida (o vuelta), zona de interés de leer con fotodiodo
        self.extra = self.range/8 #un recorrido extra para el trigger de la rampa
        self.range_total = self.range + 2*self.extra #recorrido que hará la platina (ida/vuelta)

        self.frequency = rateNI/100  #para lectura del fotodiodo, frecuencia de sampleo por canal anagógico

        self.frequency_ramp = (rateNI/100)/3000 #para movimiento de platina, frecuencia de rampa ida/vuelta

        Nramp = int(self.frequency/self.frequency_ramp) #puntos de ida que leera el fotodiodo
        self.Ntot_read = 2*Nramp #puntos de ida y vuelta

        self.Npoints = 2000 #movimiento para la rampa de la platina, puntos total de la rampa
        self.Nspeed = 10  #movimiento para la acecleración de la rampa, asegurarse estar antes del trigger
        
        tau = 1/self.frequency_ramp     
        self.WTRtime = int(tau/(servo_time*self.Npoints)) #cantidad de puntos de cada "step" de la rampa

        #Para vincular lo que lee el fotodiodo y el movimiento de la rampa:
        size_point_ramp = self.range_total/self.Npoints
        self.Nz = int(self.range/size_point_ramp) 
            
    @pyqtSlot(int)            
    def focus_go_to_maximum(self, color_laser):
         
        self.laser = shutters[color_laser]

        pos = pi_device.qPOS()
        z_pos = pos['C']
        self.zo = z_pos - self.range_total/2 

        self.move_z(self.zo)
        pi_device.WOS(3, self.zo)
        
        flag_not_found = True
        
        while flag_not_found:
            openShutter(self.laser)
            #time.sleep(0.15)
            z_profile_gone, z_profile_back, flag_not_found = self.ramp_lin(self.laser)
            closeShutter(self.laser)

        factor_gone = int(len(z_profile_gone)/self.Nz)
        z_profile_gone_mean = average(z_profile_gone, factor_gone)
        z_profile_gone_filter = filter_signal(z_profile_gone_mean)

        factor_back = int(len(z_profile_back)/self.Nz)
        z_profile_back_mean = average(z_profile_back, factor_back)
        z_profile_back_filter = filter_signal(z_profile_back_mean)

      #  z_array_gone = np.linspace(z_pos - self.range/2, z_pos + self.range/2, len(z_profile_gone_mean))
      #  z_array_back = np.linspace(z_pos + self.range/2, z_pos - self.range/2, len(z_profile_back_mean))
      
        dz = self.range/self.Nz
        
        z_array_gone = np.linspace(z_pos - self.range/2 + dz/2, z_pos + self.range/2 - dz/2, len(z_profile_gone_mean))
        z_array_back = np.linspace(z_pos + self.range/2 - dz/2, z_pos - self.range/2 + dz/2, len(z_profile_back_mean))
  
        z_gone_max = np.max(z_profile_gone_filter)
        z_profile_gone_max = np.zeros(len(z_profile_gone_filter))
        i_gone_max = np.argmax(z_profile_gone_filter)
        z_profile_gone_max[i_gone_max] = z_gone_max
        
        z_back_max = np.max(z_profile_back_filter)
        z_profile_back_max = np.zeros(len(z_profile_back_filter))
        i_back_max = np.argmax(z_profile_back_filter)
        z_profile_back_max[i_back_max] = z_back_max
        
        z_max_mean = np.around((z_array_gone[i_gone_max] + z_array_back[i_back_max])/2, 3)

        #self.move_z(z_array_gone[i_gone_max])
        
        self.move_z(z_max_mean)
        
        self.gotomaxdoneSignal.emit()   #para read_pos del método Nanopositioning

        self.plot_focusSignal.emit(z_array_gone, z_profile_gone_mean, z_profile_gone_filter,
                                   z_profile_gone_max, z_array_back, z_profile_back_mean, z_profile_back_filter, z_profile_back_max)
        
    def ramp_lin(self, laser):
        
        PDtask = channels_photodiodos(self.frequency, self.Ntot_read)

        channels_triggers(PDtask, 'Z')

        pi_device.TWC() 
        pi_device.CTO(3, 3, 3)
        pi_device.CTO(3, 5, self.zo + self.extra)
        pi_device.CTO(3, 6, self.zo + self.range_total - self.extra)

        nciclos = 1
        pi_device.WGC(3, nciclos)
        pi_device.WTR(3, self.WTRtime, 0)
             
        pi_device.WAV_LIN(3, 0, self.Npoints, "X", self.Nspeed, self.range_total, 0, self.Npoints)
        pi_device.WAV_LIN(3, 0, self.Npoints, "&", self.Nspeed, -self.range_total, self.range_total, self.Npoints)
        
        pi_device.WGO(3, True) 
        data_read = PDtask.read(self.Ntot_read)
        PDtask.close()

        data_ph = np.array(data_read[PDchans.index(PD_channels[self.laser])]) 
        data_trigger = np.array(data_read[len(PDchans)])  #los fotodiodos son los primeros  (0, 1, 2, 6), el 4 es el trigger

        z_profile_gone, z_profile_back, flag_not_found = self.z_profiles(data_ph, data_trigger)
        
        return z_profile_gone, z_profile_back, flag_not_found

    def z_profiles(self, data_ph, data_trigger):
        
        flag_not_found = False
        derivative = np.diff(data_trigger)
        index_dt_pos = np.where(derivative >= 1.5)[0]
        index_dt_neg = np.where(derivative <= -1.5)[0]
       # print('index de trigger flanco ascendete', index_dt_pos)
       # print('index de trigger flanco desscendete', index_dt_neg)
        
        L = len(data_trigger)
        first_element_pos_asc = index_dt_pos[0]
        dt_pos_asc = np.where(index_dt_pos > first_element_pos_asc + L/3)[0]
        try:
            second_element_pos_asc  = index_dt_pos[dt_pos_asc[0]]
            flag_not_found = False
        except IndexError:
            z_profile_gone = 0
            z_profile_back = 0
            flag_not_found = True
            return z_profile_gone, z_profile_back, flag_not_found    
        
        #first_element_pos_dsc = index_dt_neg[0]
        #dt_pos_dsc = np.where(index_dt_neg > first_element_pos_dsc + L/3)[0]
        #second_element_pos_dsc  = index_dt_neg[dt_pos_dsc[0]]
        
        dt_neg_dsc_first = np.where(index_dt_neg > first_element_pos_asc + L/4)[0]
        try:
            first_element_pos_dsc = index_dt_neg[dt_neg_dsc_first[0]]
            flag_not_found = False
        except IndexError:
            z_profile_gone = 0
            z_profile_back = 0
            flag_not_found = True  
            return z_profile_gone, z_profile_back, flag_not_found
        
        dt_pos_dsc = np.where(index_dt_neg > first_element_pos_dsc + L/3)[0]
        
        try:
            second_element_pos_dsc  = index_dt_neg[dt_pos_dsc[0]]
            flag_not_found = False
        except IndexError:
            z_profile_gone = 0
            z_profile_back = 0
            flag_not_found = True
            return z_profile_gone, z_profile_back, flag_not_found

        z_profile_gone = data_ph[first_element_pos_asc:first_element_pos_dsc]
        z_profile_back  = data_ph[second_element_pos_asc:second_element_pos_dsc]

        return z_profile_gone, z_profile_back, flag_not_found
    
    
    def move_z(self, dist):
        """moves the position along the Z axis a distance dist."""     

        pi_device.MOV('C', dist)
        #print("me muevo a z", dist)
        
        while not all(pi_device.qONT('C').values()):
            time.sleep(0.1)
    
    @pyqtSlot(bool, int)    
    def focus_lock_lin(self, lockbool, color_laser):
        """ guarda el patron de intensidades, barriendo z en el foco actual""" 
        
        self.laser = shutters[color_laser]
        
        if lockbool:
            
            pos = pi_device.qPOS()
            z_lock = pos['C']
            self.zo = z_lock - self.range_total/2     

            self.move_z(self.zo)       
            pi_device.WOS(3, self.zo)
            
            flag_not_found = True
        
            while flag_not_found:
                openShutter(self.laser)
                #time.sleep(0.15)
                z_profile_gone_lock, z_profile_back_lock, flag_not_found = self.ramp_lin(self.laser)
                closeShutter(self.laser)

            factor_gone = int(len(z_profile_gone_lock)/self.Nz)
            self.z_profile_gone_lock = average(z_profile_gone_lock, factor_gone)
            self.z_profile_lock_filter = filter_signal(self.z_profile_gone_lock)

            self.move_z(z_lock)
            
            self.lockdoneSignal.emit()
            self.plot_lockSignal.emit(self.z_profile_gone_lock, self.z_profile_lock_filter)
            
            self.locked_focus = True 
            print("¡Foco lockeado con el láser seleccionado!")
            
        else:
            self.locked_focus = False
            print("Hay que lockear el foco")
                      
    @pyqtSlot(str)        
    def focus_autocorr_lin_x2(self, mode_printing):
        
        if self.locked_focus:
        
            i = 0
            
            openShutter(self.laser)
           # time.sleep(0.15)

            for i in range(2):
                self.focus_autocorr_lin()
                
            closeShutter(self.laser)
                
            self.plot_autoSignal.emit(self.new_profile_filter, self.z_profile_lock_filter, self.correlation_filter)
            self.autodoneSignal.emit()
                          
        else:
            print("¡No esta lockeado el foco!")
        

        if mode_printing == 'luminescence':
           self.autofinishSignal_luminescence.emit()
           
        if mode_printing == 'growth':
           self.autofinishSignal_growth.emit()
           
        if mode_printing == 'luminescence_steps':
           self.autofinishSignal_luminescence_steps.emit()
             

    @pyqtSlot()
    def focus_autocorr_lin(self):
        """ correlaciona la medicion de intensidad moviendo z,
        respecto del que se lockeo con loc focus RAMPAS"""
            
        pos = pi_device.qPOS()
        z_before =  pos['C']
        self.zo = z_before - self.range_total/2        
        self.move_z(self.zo)
        pi_device.WOS(3, self.zo)

        flag_not_found = True
        
        while flag_not_found:
            newprofilegone, newprofileback, flag_not_found = self.ramp_lin(self.laser)
        
        factor_gone = int(len(newprofilegone)/self.Nz)
        new_profile = average(newprofilegone, factor_gone)
        new_profile_filter = filter_signal(new_profile)

        z_profile_lock_filter = self.z_profile_lock_filter
        
        correlation_filter = np.correlate(new_profile_filter, z_profile_lock_filter, "same")
        indexmax_filter = np.argmax(correlation_filter)
        
       # z_array_gone = np.linspace(z_before - self.range/2, z_before + self.range/2, len(new_profile_filter))
       
        dz = self.range/self.Nz
      #  z_array_gone = np.arange(z_before - self.range/2 + dz/2, z_before + self.range/2, dz)
        z_array_gone = np.linspace(z_before - self.range/2 + dz/2, z_before + self.range/2 - dz/2, len(new_profile_filter))
        
        self.move_z(z_array_gone[indexmax_filter])
        
        self.new_profile_filter = new_profile_filter
        self.correlation_filter = correlation_filter
        

    def make_connection(self, frontend):

        frontend.focus_gotomax_signal.connect(self.focus_go_to_maximum)
        frontend.focus_lock_signal.connect(self.focus_lock_lin)
        frontend.focus_auto_signal.connect(self.focus_autocorr_lin)
        frontend.focus_autox2_signal.connect(self.focus_autocorr_lin_x2)

def average(arr,n):
    end = n*int(len(arr)/n)
    return np.mean(arr[:end].reshape(-1,n),1)

def filter_signal(i):
    n = len(i)
    if n%2 == 0:
       i_filter = signal.savgol_filter(i, int(n/80), 1)
    else:
       i_filter = signal.savgol_filter(i, int((n-1)/80), 1)
       
    return i_filter


if __name__ == '__main__':

    app = QtGui.QApplication([])

    gui = Frontend()   
    worker = Backend()

    worker.make_connection(gui)
    gui.make_connection(worker)

    focusThread = QtCore.QThread()
    worker.moveToThread(focusThread)
    focusThread.start()

    gui.show()
    app.exec_()
 