import time
import serial
from datetime import datetime

#Conexión con Arduino
arduino = serial.Serial('COM3', 9600)
time.sleep(2)
print(datetime.now(), 'OK connection with Arduino')

arduino.write(b'23')