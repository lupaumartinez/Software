"""
	Tomar foto con Python y opencv
	@date 20-03-2018
	@author parzibyte
	@see https://www.parzibyte.me/blog
"""
#pip install opencv-python

import cv2
import matplotlib.pyplot as plt

"""
	En este caso, 0 quiere decir que queremos acceder
	a la cámara 0. Si hay más cámaras, puedes ir probando
	con 1, 2, 3...
"""

camera_port = 0

cap = cv2.VideoCapture(camera_port)
leido, frame = cap.read()
gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

print(frame, gray)

if leido == True:
	foto = cv2.imwrite("foto.png", gray)
	print("Foto tomada correctamente")
else:
	print("Error al acceder a la cámara")

"""
	Finalmente liberamos o soltamos la cámara
"""
cap.release()
cv2.destroyAllWindows()

#cv2.imshow('Webcam', frame)