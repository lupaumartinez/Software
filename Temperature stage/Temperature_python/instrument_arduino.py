import time
import serial
from datetime import datetime

#Conexión con Arduino
#arduino = serial.Serial('/dev/ttyACM0', 2000000)
arduino = serial.Serial('COM4', 2000000)
time.sleep(2)
print(datetime.now(), 'OK connection with Arduino')

def ask_output():
    arduino.write(b'0')
    arduino.flush()
    output = arduino.readline()
    output = output.decode('utf-8')
    output = output.strip()
    return output

def ask_temperature():
    arduino.write(b'0')
    arduino.flush()
    output = arduino.readline()
    output = output.decode('utf-8')
    output = output.strip()
    temp = float(output.split(':')[3])
    return temp

def ask_dutycycle():
    arduino.write(b'0')
    arduino.flush()
    output = arduino.readline()
    output = output.decode('utf-8')
    output = output.strip()
    duty = float(output.split(':')[5])
    error = float(output.split(':')[7])
    propTerm = float(output.split(':')[9])
    intTerm = float(output.split(':')[11])
    devTerm = float(output.split(':')[13])
    return duty, error, propTerm, intTerm, devTerm

def ask_setpoint():
    arduino.write(b'0')
    arduino.flush()
    output = arduino.readline()
    output = output.decode('utf-8')
    output = output.strip()
    setpoint = float(output.split(':')[1])
    return setpoint
    
def change_setpoint(setpoint_value):
    arduino.write(b'%.1f' % setpoint_value)
    arduino.flush()
    output = arduino.readline()
    return output

def iterate():
    f = open('C:\\Julian\\Data_PyPrinting\\2019-12-02\\log_temp_2.txt', 'w+')
    t0 = time.time()
    sec = 0
    while sec<1200*2:
        sec = time.time()-t0
        print('time', sec)
        print(ask_output())
        f.write('time:' + str(sec) + ':' + str(ask_output()) + '\n')
        time.sleep(1)
    f.close()
    
change_setpoint(20)
iterate()

ask_output()
f.close(), arduino.close()
