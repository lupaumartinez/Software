# -*- coding: utf-8 -*-
"""
Created on Thu Jul 18 17:13:23 2019

@author: CibionPC
"""

import numpy as np
import os

base_folder = r"C:\Julian\PySpectrum\PySpectrum"
daily = 'PySpectrumPrinting - 2022-06-28/lamparaIR_450-950_overlap0.2/lamparaIR_grade_2.txt'
file_lamp = os.path.join(base_folder, daily)
data = np.loadtxt(file_lamp, comments = '#')
wave_lamp = data[:, 0]
spec_lamp = data[:, 1]

#filepath = r"C:/Users/CibionPC/Desktop/PySpectrum/"
#lampara =  np.loadtxt( str(filepath  + "/" + 'lamp_IR_unpol.asc') )
#wave_lamp = np.array(lampara[:, 0])
#image_lampara = np.array(lampara[:, 1:])
#rows = range(500, 600)
#spec_lamp = np.round(np.mean(image_lampara[:,rows], axis=1), 3)

lamp = [wave_lamp, spec_lamp]

def glue_steps(wave_PySpectrum, spectrum_py, number_pixel, grade):

    L = int(len(spectrum_py)/number_pixel) #cantidad de steps
    
    n_skip_points = 30
    n = int(n_skip_points/2)
    
    spec_steps = np.zeros((number_pixel-n_skip_points, L))
    wave_steps = np.zeros((number_pixel-n_skip_points, L))
    
    spec_steps_glue = np.zeros((number_pixel-n_skip_points, L))
    wave_steps_glue = np.zeros((number_pixel-n_skip_points, L))
    
    list_of_inf = np.zeros(L)
    list_of_sup = np.zeros(L)
    
    for i in range(L):
        
        spec = spectrum_py[i*number_pixel:number_pixel*(1+i)]
        wave = wave_PySpectrum[i*number_pixel:number_pixel*(i+1)]
        
        spec_steps[:, i] = spec[n:-n]
        wave_steps[:, i] = wave[n:-n]
        
        spec_steps_glue[:, i] = spec[n:-n]
        wave_steps_glue[:, i] = wave[n:-n]
        
        list_of_inf[i] = wave_steps[0, i] # wave[0]
        list_of_sup[i] = wave_steps[-1, i]
    
    for j in range(L-1):
        
        inf = list_of_inf[j+1]
       # sup = list_of_sup[i]
        
        wave_tail = wave_steps[:, j]   
        desired_range_tail = np.where(wave_tail >= inf)[0]
        
        m = int( len(desired_range_tail))
        
        weigth_h = np.linspace(0, 1, m)**grade
        weigth_t = np.flip(weigth_h)
        
        coef = weigth_h + weigth_t
        
        weigth_h =  weigth_h/coef
        weigth_t =  weigth_t/coef
        
        desired_range_tail = range(number_pixel-n_skip_points - m,  number_pixel-n_skip_points)
        spec_tail = spec_steps[desired_range_tail , j]
        wave_tail = wave_steps[desired_range_tail , j]
        
        desired_range_head = range(0,  m)
        spec_head = spec_steps[desired_range_head, j+1]
        wave_head = wave_steps[desired_range_head, j+1]
        
        spec_weigth = weigth_h*spec_head + weigth_t*spec_tail
        
       # spec_weigth = smooth_Signal(spec_weigth, window = 21, deg = 0, repetitions = 1)

        spec_steps_glue[desired_range_tail, j] = spec_weigth
        wave_steps_glue[desired_range_tail, j] = wave_tail
        
        spec_steps_glue[desired_range_head, j+1] = spec_weigth
        wave_steps_glue[desired_range_head, j+1] = wave_head
        
    wave_final = np.reshape(wave_steps_glue, [1,wave_steps_glue.size])[0]
    spectrum_final = np.reshape(spec_steps_glue, [1,wave_steps_glue.size])[0]
    
    spectrum_final = [spectrum_all for _,spectrum_all in sorted(zip(wave_final,spectrum_final))]
    wave_final = np.sort(wave_final)
    spectrum_final = np.array(spectrum_final)
    
    wave_final, spectrum_final = interpole_spectrum(wave_final, spectrum_final, number_pixel)

    return wave_final, spectrum_final


def interpole_spectrum(wavelength, spectrum, number_pixel):
    
   # factor = number_pixel/window_wavelength
    
  #  desired_points = round(factor*(wavelength[-1] - wavelength[0]))
    
    desired_points = number_pixel
    
    lower_lambda = wavelength[0]
    upper_lambda = wavelength[-1]
    
    wavelength_new = np.linspace(lower_lambda, upper_lambda, desired_points)

    spectrum_new = np.interp(wavelength_new, wavelength, spectrum)
    
    return wavelength_new, spectrum_new