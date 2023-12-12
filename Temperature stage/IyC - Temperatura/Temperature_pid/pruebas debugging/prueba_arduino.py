import serial, time
arduino = serial.Serial('COM3', 9600)
time.sleep(2)

arduino.write(b'2')

value = arduino.readline().strip()
value_dc = float(str(value).split(":")[3].split("\'")[0])
value_temp = float(str(value).split(":")[1])

print(value)

arduino.close()