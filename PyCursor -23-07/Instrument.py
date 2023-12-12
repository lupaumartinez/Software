""" Placa"""

import nidaqmx
from pipython import GCSDevice
import numpy as np
import time

device = nidaqmx.system.System.local().devices['Dev1']

shutters = ['532 nm (green)', '642 nm (red)', '405 nm (blue)', '808 nm (NIR)']  
shutterschan = [9, 10, 11, 7]  # digital output (do) of shutters

PDchans = [0, 1, 2]  #  analog input (ai) of photodiodos

rateNI_single_channel =  1.25*10**6  # rate = 1.25 MS/s Analog input NI 6353 Single channel maximum
rateNI = 1*10**6 # rate = 1 MS/s Analog input NI 6353 Multichannel maximum (aggregate)

PD_channels = {shutters[0]: 0, shutters[1]: 2, shutters[2]: 1, shutters[3]: 2}  #si rojo e infrarrojo comparten fotodiodo en el set up

pi_device = GCSDevice ()  # Load PI Python Libraries

try:
    pi_device.ConnectUSB ('0111176619')  # Connect to the controller via USB with serial number 0111176619
    print(pi_device.qIDN()) #Out[]: 'Physik Instrumente, E-517, 0111176619, V01.243'
    axes = ['A','B','C']
    allTrue = [True, True, True]
    allFalse = [False, False, False]
    pi_device.ONL([1,2,3],[1,1,1])  # Turn on the Online config (PC master)
    pi_device.DCO(axes, allTrue)  # Turn on the drift compensation mode
    pi_device.SVO (axes, allTrue)  # Turn on servo control
    pi_device.VCO(axes, allFalse)  # Turn off Velocity control. Can't move if ON
    
    pi_device.MOV(axes, [100, 100, 50])  # move away from origin (0,0,0)
    
except IOError as e:
    print("I/O error({0}): {1}".format(e.errno, e.strerror))
    print("Can't connect to the platine.")

servo_time = 0.000040  # seconds  # tiempo del servo: 40­µs. lo dice qGWD()

#%% para abrir y cerrar shutters 

shuttersignal = [True,True,False,True] # blue is different for the modulation mode 
shuttertask = nidaqmx.Task("shutter")
                 
for n in range(len(shutters)):
    shuttertask.do_channels.add_do_chan(
        lines="Dev1/port0/line{}".format(shutterschan[n]),
        line_grouping=nidaqmx.constants.LineGrouping.CHAN_PER_LINE)

def openShutter(p):
     if p == shutters[2]:
         shuttersignal[2] = True
         shuttertask.write(shuttersignal, auto_start=True)
     if p == shutters[3]:
         shuttersignal[3] = True
         shuttertask.write(shuttersignal, auto_start=True)
         time.sleep(0.003)  
         shuttersignal[3] = False
         shuttertask.write(shuttersignal, auto_start=True)
     else:
         for i in np.array([0,1]):    # for i in range(len(shutters)):
            if p == shutters[i]: 
                shuttersignal[i] = False
                shuttertask.write(shuttersignal, auto_start=True)
                
def closeShutter(p):
     if p == shutters[2]:
         shuttersignal[2] = False
         shuttertask.write(shuttersignal, auto_start=True)
     if p == shutters[3]:
         shuttersignal[3] = True
         shuttertask.write(shuttersignal, auto_start=True)
         time.sleep(0.003)  
         shuttersignal[3] = False
         shuttertask.write(shuttersignal, auto_start=True)
     else:
         for i in np.array([0,1]):
                if p == shutters[i]:
                    shuttersignal[i] = True
                    shuttertask.write(shuttersignal, auto_start=True)
                      
def closeAllShutter():
    for i in range(len(shutters)):
        p = shutters[i]
        closeShutter(p)
                
#%% Flipper         
        
flippertask1 = nidaqmx.Task("flipper1")
flippertask1.ao_channels.add_ao_voltage_chan('Dev1/ao0')
         
flippertask0 = nidaqmx.Task("flipper0")
flippertask0.ao_channels.add_ao_voltage_chan('Dev1/ao1')

def upFlipper():
        flippertask1.write(5)
        time.sleep(0.003)                
        flippertask1.write(0)
          
def downFlipper(): 
        flippertask0.write(5)
        time.sleep(0.003)
        flippertask0.write(0)

        