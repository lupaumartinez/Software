# -*- coding: utf-8 -*-
"""
Created on Thu Jul 18 17:13:23 2019

@author: CibionPC
"""

import numpy as np

filepath = "C:/Users/CibionPC/Desktop/PySpectrum/"

lampara =  np.loadtxt( str(filepath  + "/" + 'lamp_IR_unpol.asc') )

wave_lampara = np.array(lampara[:, 0])
image_lampara = np.array(lampara[:, 1:])
rows = range(500, 600)
espectro_lampara = np.round(np.mean(image_lampara[:,rows], axis=1), 3)
lamp = [wave_lampara, espectro_lampara]

#import matplotlib.pyplot as plt
#plt.plot(wave_lampara, espectro_lampara)
#plt.show()