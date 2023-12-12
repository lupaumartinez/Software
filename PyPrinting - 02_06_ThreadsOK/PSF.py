#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 13 15:50:42 2019

@author: luciana
"""
import numpy as np
from scipy.optimize import curve_fit
from skimage.feature import peak_local_max
from scipy import ndimage


def center_of_mass(image):
    
    com = ndimage.measurements.center_of_mass(image)
    yo, xo = np.around(com, 3)
    
    print('center of mass ok:', xo, yo)
    
    return xo, yo


def gaussian2D(grid, amplitude, x0, y0, σ_x, σ_y, offset, theta=0):
    
    # TO DO (optional): change parametrization to this one
    # http://mathworld.wolfram.com/BivariateNormalDistribution.html  
    # supposed to be more robust for the numerical fit
    
    x, y = grid
    x0 = float(x0)
    y0 = float(y0)   
    a = (np.cos(theta)**2)/(2*σ_x**2) + (np.sin(theta)**2)/(2*σ_y**2)
    b = -(np.sin(2*theta))/(4*σ_x**2) + (np.sin(2*theta))/(4*σ_y**2)
    c = (np.sin(theta)**2)/(2*σ_x**2) + (np.cos(theta)**2)/(2*σ_y**2)
    G = offset + amplitude*np.exp( - (a*((x-x0)**2) + 2*b*(x-x0)*(y-y0) 
                            + c*((y-y0)**2)))

    return G.ravel()


def center_of_gauss2D(image, xo, yo):
    
    Nx = image.shape[0]
    Ny = image.shape[1]
    
    x = np.arange(-Nx/2 + 1/2, Nx/2)
    y = np.arange(-Ny/2 + 1/2, Ny/2) 
    
    [Mx, My] = np.meshgrid(x, y)
    
    dataG_2d = image
    dataG_ravel = dataG_2d.ravel()
    
    initial_sigma = [2, 2]   #unidad en pixel, en general trabajamos con 58 nm por pixel
    
    initial_guess_G = [1, xo + x[0],  yo + y[0], initial_sigma[0], initial_sigma[1], 0]
    bounds = ([0, x[0], y[0], 0, 0, 0], [1, x[-1], y[-1], 4*initial_sigma[0], 4*initial_sigma[0], 1])
    
    poptG, pcovG = curve_fit(gaussian2D, (Mx, My), dataG_ravel, p0= initial_guess_G, bounds = bounds)
        
    poptG = np.around(poptG, 3)
        
    xo_cg = poptG[1] - x[0]
    yo_cg = poptG[2] - y[0]
    
    print('center of gauss ok', xo_cg, yo_cg)
    
    return xo_cg, yo_cg

def two_gaussian2D(grid, amplitude, x0, y0, σ_x, σ_y, offset, amplitude1, x1, y1, theta=0):

    x, y = grid

    x0 = float(x0)
    y0 = float(y0) 

    x1 = float(x1)
    y1 = float(y1)   

    a = (np.cos(theta)**2)/(2*σ_x**2) + (np.sin(theta)**2)/(2*σ_y**2)
    b = -(np.sin(2*theta))/(4*σ_x**2) + (np.sin(2*theta))/(4*σ_y**2)
    c = (np.sin(theta)**2)/(2*σ_x**2) + (np.cos(theta)**2)/(2*σ_y**2)


    G0 = amplitude*np.exp( - (a*((x-x0)**2) + 2*b*(x-x0)*(y-y0) + c*((y-y0)**2)))

    G1 = amplitude1*np.exp( - (a*((x-x1)**2) + 2*b*(x-x1)*(y-y1) + c*((y-y1)**2)))

    G =  offset + G0 + G1

    return G.ravel()

def two_centers_of_gauss2D(image, x1, y1, x2, y2):

    Nx = image.shape[0]
    Ny = image.shape[1]
    
    x = np.arange(-Nx/2 + 1/2, Nx/2)
    y = np.arange(-Nx/2 + 1/2, Ny/2) 
    
    [Mx, My] = np.meshgrid(x, y)
    
    dataG_2d = image
    dataG_ravel = dataG_2d.ravel()
    
    initial_sigma = [2, 2]
    bounds = ([0, x[0], y[0], 0, 0, 0, 0, x[0], y[0]], [1, x[-1], y[-1], 4*initial_sigma[0], 4*initial_sigma[0], 1, 1,x[-1], y[-1]])
    
    initial_guess_G = [1, x1 + x[0], y1 + y[0], initial_sigma[0], initial_sigma[1], 0, 1, x2 + x[0],  y2 +  y[0]]
    
    poptG, pcovG = curve_fit(two_gaussian2D, (Mx, My), dataG_ravel, p0= initial_guess_G, bounds = bounds)
    
    poptG = np.around(poptG, 3)
    	#print('A = {}, (y0, x0) = ({}, {}), σ_y = {}, σ_x = {}, bkg = {}'.format(*poptG))
    
    x1_cg = poptG[1] - x[0]
    y1_cg = poptG[2] - y[0]
     
    x2_cg = poptG[7] - x[0]
    y2_cg = poptG[8] - y[0]
    
    print('center of two gauss ok', 'NP1', x1_cg, y1_cg, 'NP2', x2_cg, y2_cg)

    return x1_cg, y1_cg, x2_cg, y2_cg
    
def find_two_centers(image):
        
    axe_x, profile_x, axe_y, profile_y = curve_gauss(image)
    
    index_x, axe_x, profile_x_max = find_peaks(axe_x, profile_x, threshold_rel = 0.24, number = 2)
    index_y, axe_y, profile_y_max = find_peaks(axe_y, profile_y, threshold_rel = 0.24, number = 2)
    
    if len(index_x) == 2 and len(index_y) == 1:
    
        pos_NP_1 = index_x[1][0], index_y[0][0]
        pos_NP_2 = index_x[0][0], index_y[0][0]
    
    if len(index_x) == 1 and len(index_y) == 2:
    
        pos_NP_1 = index_x[0][0], index_y[1][0]
        pos_NP_2 = index_x[0][0], index_y[0][0]
    
    if len(index_x) == 2 and len(index_y) == 2:
        
        pos_NP_1 = index_x[1][0], index_y[0][0]
        pos_NP_2 = index_x[0][0], index_y[1][0]
    
    if len(index_x) == 1 and len(index_y) == 1:
    
        pos_NP_1 = index_x[0][0], index_y[0][0]
        pos_NP_2 = index_x[0][0], index_y[0][0]
    
    x1, y1 = pos_NP_1
    x2, y2 = pos_NP_2
    
    print('center of two local peak ok', 'NP1', x1, y1, 'NP2', x2, y2)

    return x1, y1, x2, y2

def curve_gauss(image):
    
    profile_x = np.mean(image, axis = 0)
    profile_y = np.mean(image, axis = 1)
    
    Nx = image.shape[0]
    axe_x = np.arange(-Nx/2 + 1/2, Nx/2, 1)
    
    Ny = image.shape[1]
    axe_y = np.arange(-Ny/2 + 1/2, Ny/2, 1)
    
    return axe_x, profile_x, axe_y, profile_y

def find_peaks(x, y, threshold_rel, number):

	index = peak_local_max(y, min_distance=1, threshold_rel = threshold_rel, num_peaks = number, indices=True)

	return index, x[index], y[index]
    
    
    
    

        
        
        