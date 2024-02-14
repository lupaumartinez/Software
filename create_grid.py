# -*- coding: utf-8 -*-
"""
Created on Wed Mar 30 15:08:27 2022

@author: lupau
"""

from tkinter import filedialog
import numpy as np
import matplotlib.pyplot as plt
import os

def grid_create(save_folder, n, d_n, N, d_N): 

  #  n #particulas por columna
  #  N #cantidad de columnas
  #  d_n  #espaciado entre particulas um
  #  d_N #espaciado entre columnas um

    datos = np.zeros((3, n*N))

    i = 0
    k = 0

    for i in range(n):
       for k in range(N):
           datos[1, k*n+i]= k*d_N
           datos[0, k*n+i]= i*d_n

    grid_name = "{}x{}_{}umx{}um.txt".format(n, N, d_n, d_N)
    
    name = os.path.join(save_folder, grid_name)
    
    np.savetxt(name, datos.T)
    
    return datos

def grid_plot(datos):
    """hace un plot de la grilla cargada para estar seguro que es lo que
    se quiere imprimir"""
    
    grid_x = datos[0, :]
    grid_y = datos[1, :]
    
    plt.figure()
    
    plt.ylabel( "x (µm)")
    plt.xlabel( "y (µm)")
    
    plt.plot(grid_y, grid_x, 'o')
    
    plt.show()
    
    return


save_folder = 'C:/Julian/PyPrinting/PyPrinting - 02_06_ThreadsOK'
datos = grid_create(save_folder, n = 3, d_n = 4, N = 5, d_N = 4)
print(datos)
grid_plot(datos)


#%%

#root = tk.Tk()
#root.withdraw()

name = filedialog.askopenfilename()  

f = open(name, "r")
datos = np.loadtxt(name, unpack=True)
f.close()

grid_name = 'Load_grid'
grid_x = datos[0, :]
grid_y = datos[1, :]


print(datos)

grid_plot(datos)