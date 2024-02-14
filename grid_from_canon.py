# -*- coding: utf-8 -*-
"""
Created on Sun Apr  3 18:13:11 2022

@author: lupau
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 27 16:40:42 2021

@author: luciana
"""

import numpy as np
import matplotlib.pyplot as plt
import skimage
from skimage.feature import peak_local_max
from skimage import data, img_as_float
from skimage import io
import os

def bin_image(image, sigma):
    
    blur = skimage.filters.gaussian(image, sigma=sigma)
    
    return blur

def bin_image_2(image, filter_value):
    
    bin_image = np.zeros((image.shape[0], image.shape[1]))
    
    for i in range(image.shape[0]):
        for j in range(image.shape[1]):
            
            if image[i, j] > filter_value:

                bin_image[i, j] = 1
                
    return bin_image


def make_sorted_2(coordinates, list_N):
    
    coordinate_x = coordinates[:, 1]
    coordinate_y = coordinates[:, 0]
    
    print(coordinate_x, coordinate_y)
    
    new_coordinate_x = np.zeros(len(coordinate_x))
    new_coordinate_y = np.zeros(len(coordinate_y))
    
    a = 0
    
    for i in range(len(list_N)):
        
        b = list_N[i] + a
        
        zipped_lists = zip(coordinate_y[a:b], coordinate_x[a:b])    
        sorted_pairs = sorted(zipped_lists)
        tuples = zip(*sorted_pairs)
        new_coordinate_y[a:b], new_coordinate_x[a:b] = [list(tuple) for tuple in tuples]
        
        a = b
    
    print(new_coordinate_x , new_coordinate_y)
    
    new_coordinates = np.zeros(coordinates.shape)
    new_coordinates[:, 1] = new_coordinate_x
    new_coordinates[:, 0] = new_coordinate_y
    
    return new_coordinates

def make_sorted(coordinates):
    
    new_coordinates = np.zeros(coordinates.shape)
    new_coordinates2 = np.zeros(coordinates.shape)
    
    new_coordinate_x = []
    new_coordinate_y = []
    
    coordinates = sorted(coordinates, key=lambda x:x[0])
    
    for (a,b) in coordinates:
        
        new_coordinate_x.append(b)
        new_coordinate_y.append(a)
        
    new_coordinates[:, 1] = new_coordinate_x
    new_coordinates[:, 0] = new_coordinate_y
    
    new_coordinate_x2 = []
    new_coordinate_y2 = []
    
    new_coordinates = sorted(new_coordinates, key=lambda x:x[1])
    
    for (a,b) in new_coordinates:
        
        new_coordinate_x2.append(b)
        new_coordinate_y2.append(a)
        
    new_coordinates2[:, 1] = new_coordinate_x2
    new_coordinates2[:, 0] = new_coordinate_y2
    
    return new_coordinates2
    
def delete_coordinates(pree_coordinates, index_delete):
    
    if index_delete == []:
        
        coordinates = pree_coordinates
        
    else:
        
        x = pree_coordinates[:, 1]
        y = pree_coordinates[:, 0]
        i = 0
        for e in index_delete:
            
            x = np.delete(x, e - i)
            y = np.delete(y, e - i)
            i = i + 1
        
        N = len(x)
        
        coordinates = np.zeros((N, N))
        coordinates[:, 1] = x
        coordinates[:, 0] = y
        
        print(N)
        
    return coordinates

def make_grid(coordinates, pixel_size):
    
    N = coordinates.shape[0]
    
    grid = np.zeros((N, 3))
    
    for i in range(N):
    
        y = round((coordinates[i, 0] - coordinates[0, 0])*pixel_size,3)
        x = round((coordinates[i, 1]- coordinates[0, 1])*pixel_size,3)
        
        grid[i, 1] = x
        grid[i, 0] = y
    
    return grid

def grid_plot(datos):
    """hace un plot de la grilla cargada para estar seguro que es lo que
    se quiere imprimir"""
    
    grid_x = datos[:, 1]
    grid_y = datos[:, 0]
    
    plt.figure()
    
    plt.ylabel( "x (µm)")
    plt.xlabel( "y (µm)")
    
    plt.plot(grid_y, grid_x, 'o')
    
    plt.show()
    
    return

##aca se inserta el archivo del dia:
folder = 'C:/Julian/Destino Camara/2022_09_07'
file = '2022_09_07_IMG_2772_crop.jpg'

#---------------------------------------

file = os.path.join(folder, file)

image_RGB = io.imread(file)
im = skimage.color.rgb2gray(image_RGB)
im = im
#im1 = bin_image(im1, sigma = 0.5)
#im2 = bin_image_2(im1, 0.59)

coordinates_1 = peak_local_max(im, min_distance=3, threshold_abs = 0.1)

fig, axes = plt.subplots(1, 3, figsize=(8, 3), sharex=True, sharey=True)

ax = axes.ravel()
ax[0].imshow(im, cmap=plt.cm.gray)
ax[0].axis('off')
ax[0].set_title('Filter Gausssian')

ax[1].imshow(im, cmap=plt.cm.gray)
ax[1].axis('off')
ax[1].set_title('Bin')

ax[2].imshow(im, cmap=plt.cm.gray)
ax[2].plot(coordinates_1[:, 1], coordinates_1[:, 0], 'r.')

for i in range(coordinates_1.shape[0]):
    ax[2].text(coordinates_1[i, 1], coordinates_1[i, 0], '%d'%i, color = 'white')
ax[2].axis('off')
ax[2].set_title('Peak local max')

fig.tight_layout()
plt.show()

#index_delete = []
#coordinates = delete_coordinates(coordinates_2, index_delete)

coordinates = make_sorted(coordinates_1)

plt.figure()
plt.imshow(im, cmap=plt.cm.gray)
plt.plot(coordinates[:, 1], coordinates[:, 0], 'r.')
for i in range(coordinates.shape[0]):
    plt.text(coordinates[i, 1], coordinates[i, 0], '%d'%i, color = 'white')
plt.axis('off')
plt.show()

#list_N_col = [3,3,3]   #cantidad de NP por columna, foto original
#coordinates = make_sorted_2(coordinates, list_N_col)

plt.figure()
plt.imshow(im, cmap=plt.cm.gray)
plt.plot(coordinates[:, 1], coordinates[:, 0], 'r.')
for i in range(coordinates.shape[0]):
    plt.text(coordinates[i, 1], coordinates[i, 0], '%d'%i, color = 'white')
plt.axis('off')
plt.savefig(os.path.join(folder, "Grid_canon.jpg"))

grid = make_grid(coordinates, pixel_size = 0.059)
Npart = grid.shape[0]
print(Npart)

save_folder = folder
grid_name = "Grid_canon.txt"
name = os.path.join(save_folder, grid_name)
np.savetxt(name, grid, fmt='%1.3f')

grid_plot(grid)