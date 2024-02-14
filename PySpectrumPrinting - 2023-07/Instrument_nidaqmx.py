""" Placa"""

import numpy as np
import time

shutters = ['532 nm (green)', '642 nm (red)', '405 nm (blue)', '808 nm (NIR)', '592 nm (orange)']  
shutterschan = [9, 10, 11, 12]  # digital output (do) of shutters
shuttersignal = [False,True,False,True] # blue is different for the modulation mode 

flipper532chan = 7 # digital output (do) of flipper Notch 532 nm

PDchanBS = 6
PDchans = [0, 1, 2, PDchanBS] 

#PD_channels = {shutters[0]: PDchans[0], shutters[1]: PDchans[1], shutters[2]: PDchans[1], shutters[3]: PDchans[2], shutters[4]: PDchans[0], 'BS': PDchanBS}
PD_channels = {shutters[0]: 0,  shutters[1]: 1, shutters[2]: 2, shutters[3]: 2, shutters[4]: 0, 'BS': 6}  #azul y infrarrojo comparten en 1, rojo solo en 2

Triggerchans = [4, 5, 3] # analg input (ai) of trigger of pi_device X, Z
pi_trigger = ['X', 'Y', 'Z']
Trigger_channels = {pi_trigger[0]: 4, pi_trigger[1]: 5, pi_trigger[2]: 3}

rateNI_single_channel =  1.25*10**6  # rate = 1.25 MS/s Analog input NI 6353 Single channel maximum
rateNI = 1*10**6 # rate = 1 MS/s Analog input NI 6353 Multichannel maximum (aggregate)

def initial_nidaqmx(nidaqmx):
    
    nidaqmx.system.System.local().devices['Dev1']
    
    shuttertask = channels_shutters(nidaqmx, shutters, shutterschan)
    flippertask = channels_flipper(nidaqmx) 
    fliper532task = channels_flipper_notch532(nidaqmx, flipper532chan)
    
    task = shuttertask, flippertask, fliper532task

    return task

#%% para abrir y cerrar shutters 

def channels_shutters(nidaqmx, shutters, shutters_chan):
    
    shuttertask = nidaqmx.Task("shutter")
                 
    for n in range(len(shutterschan)):
        shuttertask.do_channels.add_do_chan(
            lines="Dev1/port0/line{}".format(shutterschan[n]),
            line_grouping=nidaqmx.constants.LineGrouping.CHAN_PER_LINE)
        
    return shuttertask

def openShutter(p, shuttertask):
    
     if p == shutters[2]:
         shuttersignal[2] = True
         shuttertask.write(shuttersignal, auto_start=True)
     if p == shutters[3]:
        shuttersignal[3] = False
        shuttertask.write(shuttersignal, auto_start=True)
        
     if p == shutters[0]:
        shuttersignal[0] = True
        shuttertask.write(shuttersignal, auto_start=True)
        
     if p == shutters[1] or p == shutters[4]:
        shuttersignal[1] = False
        shuttertask.write(shuttersignal, auto_start=True)
        
def closeShutter(p, shuttertask):
    
     if p == shutters[2]:
         shuttersignal[2] = False
         shuttertask.write(shuttersignal, auto_start=True)
     if p == shutters[3]:
        shuttersignal[3] = True
        shuttertask.write(shuttersignal, auto_start=True)
        
     if p == shutters[0]:
        shuttersignal[0] = False
        shuttertask.write(shuttersignal, auto_start=True)
        
     if p == shutters[1] or p == shutters[4]:
        shuttersignal[1] = True
        shuttertask.write(shuttersignal, auto_start=True)
                      
def closeAllShutter():
    for i in range(len(shutters)):
        p = shutters[i]
        closeShutter(p)
                
#%% Flipper

def channels_flipper(nidaqmx):         
        
    flippertask1 = nidaqmx.Task("flipper1")
    flippertask1.ao_channels.add_ao_voltage_chan('Dev1/ao0')
             
    flippertask0 = nidaqmx.Task("flipper0")
    flippertask0.ao_channels.add_ao_voltage_chan('Dev1/ao1')
    
    flipptertask = [flippertask0, flippertask1]
    
    return flipptertask

def upFlipper(flippertask):
        flippertask[1].write(5)
        time.sleep(0.003)                
        flippertask[1].write(0)
          
def downFlipper(flippertask): 
        flippertask[0].write(5)
        time.sleep(0.003)
        flippertask[0].write(0)   
        
 #%% Flipper Notch532      

def channels_flipper_notch532(nidaqmx, flipper532chan):         
        
    fliper532task = nidaqmx.Task("Flipper Notch 532 nm")
    fliper532task.do_channels.add_do_chan(
            lines="Dev1/port0/line{}".format(flipper532chan),
            line_grouping=nidaqmx.constants.LineGrouping.CHAN_PER_LINE)
    
    return fliper532task

def Flipper_notch532(fliper532task, desired_position):
    flipper_notch532_status = read_flipper_notch532_status()
    #print(' after reading inside function',flipper_notch532_status)
    if desired_position == 'up' and flipper_notch532_status:
        fliper532task.write(True)
        time.sleep(0.003)  
        fliper532task.write(False)
        flipper_notch532_status = 0
        write_flipper_notch532_status(flipper_notch532_status)
      #  print('Flipper status was changed, now its up (False)')
    elif desired_position == 'up' and not flipper_notch532_status:
        flipper_notch532_status = 0
      #  print('Flipper status was not changed (left in False)')
    elif desired_position == 'down' and flipper_notch532_status:
        flipper_notch532_status = 1
      #  print('Flipper status was not changed (left in True)')
    elif desired_position == 'down' and not flipper_notch532_status:
        fliper532task.write(True)
        time.sleep(0.003)
        fliper532task.write(False)
        flipper_notch532_status = 1
        write_flipper_notch532_status(flipper_notch532_status)
     #   print('Flipper status was changed, now its down (True)')
    else:
        raise ValueError('Desired flipper status does not exist')
    print('after flipper func',flipper_notch532_status)
    return

def read_flipper_notch532_status():
    f = open('flipper_notch532_status.txt','r')
    flipper_notch532_status = f.readlines(1)[0]
    f.close()
    return int(flipper_notch532_status)

def write_flipper_notch532_status(flipper_notch532_status):
    f = open('flipper_notch532_status.txt','w+')
    f.write(str(flipper_notch532_status))
    f.close()
    return 

#%% Photodiodos
        
def channels_photodiodos(nidaqmx, rate, samps_per_chan):
        
    PDtask = nidaqmx.Task('PDtask')
        
    for n in range(len(PDchans)):
            
            PDtask.ai_channels.add_ai_voltage_chan(
                physical_channel='Dev1/ai{}'.format(PDchans[n]),  
                name_to_assign_to_channel='chan_PD{}'.format(PDchans[n]))
    
            PDtask.timing.cfg_samp_clk_timing(
              rate = rate, sample_mode=nidaqmx.constants.AcquisitionType.FINITE,samps_per_chan= samps_per_chan)            
        
    return PDtask

def channels_triggers(task, axes):

    task.ai_channels.add_ai_voltage_chan(
                physical_channel='Dev1/ai{}'.format(Trigger_channels[axes]),  
                name_to_assign_to_channel='trigger_pi_{}'.format(Trigger_channels[axes]))
