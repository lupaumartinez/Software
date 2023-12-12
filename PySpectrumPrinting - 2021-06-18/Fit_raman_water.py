#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 27 17:13:26 2019

@author: luciana
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 30 12:11:59 2019

@author: luciana

"""

import numpy as np

from scipy.optimize import curve_fit
import scipy.signal as sig

def smooth_Signal(signal, window, deg, repetitions):
    
    k = 0
    while k < repetitions:
        signal = sig.savgol_filter(signal, window, deg, mode = 'mirror')
        k = k + 1
        
    return signal

    
def lorentz(x, *p):
    
    # Lorentz fitting function with an offset
    # gamma = FWHM
    # I = amplitude
    # x0 = center
    pi = np.pi
    I, gamma, x0, C = p
    
    return (1/pi) * I * (gamma/2)**2 / ((x - x0)**2 + (gamma/2)**2) + C

def fit_lorentz(p, x, y):
    return curve_fit(lorentz, x, y, p0 = p)


def fit_two_lorentz(p, x, y):
    return curve_fit(two_lorentz, x, y, p0 = p, bounds = (0, [2000, 500, 700, 2000, 500, 700, 500]))#, method = 'trf')

def fit_three_lorentz(p, bounds, x, y):
    
    return curve_fit(three_lorentz, x, y, p0 = p, bounds = bounds)

def two_lorentz(x, *p):

    pi = np.pi

    I, gamma, x0, I_2, gamma_2, x0_2, C = p
    return  (1/pi) * I * (gamma/2)**2 / ((x - x0)**2 + (gamma/2)**2) + (1/pi) * I_2 * (gamma_2/2)**2 / ((x - x0_2)**2 + (gamma_2/2)**2) + C

def three_lorentz(x, *p):

    pi = np.pi

    I, gamma, x0, I_2, I_3, C = p
    
    a = (1/pi) * I_2 * (15.5/2)**2 / ((x - 649)**2 + (15.2/2)**2) 
    b = (1/pi) * I_3 * (183/2)**2 / ((x - 702)**2 + (183/2)**2) 
    
    return  (1/pi) * I * (gamma/2)**2 / ((x - x0)**2 + (gamma/2)**2) + (1/pi) * I_2 * a + (1/pi) * I_3 * b + C

def calc_r2(observed, fitted):
    # Calculate coefficient of determination
    avg_y = observed.mean()
    ssres = ((observed - fitted)**2).sum()
    sstot = ((observed - avg_y)**2).sum()
    return 1.0 - ssres/sstot

def fit_lorentz_signal(spectrum_S, wavelength_S, init_params):

    best_lorentz, err = fit_two_lorentz(init_params,  wavelength_S, spectrum_S)

    lorentz_fitted = two_lorentz(wavelength_S, *best_lorentz)
    r2_coef_pearson = calc_r2(spectrum_S, lorentz_fitted)

    return lorentz_fitted, best_lorentz, r2_coef_pearson

def fit_lorentz_signal_NP(spectrum_S, wavelength_S, init_params, bounds):

    best_lorentz, err = fit_three_lorentz(init_params, bounds, wavelength_S, spectrum_S)
    
    wavelength_fitted = np.linspace(wavelength_S[0]-20,  wavelength_S[-1]+20, 1000)

    lorentz_fitted = three_lorentz(wavelength_fitted, *best_lorentz)
    
    lorentz_fit = three_lorentz(wavelength_S, *best_lorentz)
    r2_coef_pearson = calc_r2(spectrum_S, lorentz_fit)  #

    return lorentz_fitted, wavelength_fitted, best_lorentz, r2_coef_pearson

def stokes_signal(wavelength, spectrum, ends_notch, final_wave):
    
    desired_range_stokes = np.where((wavelength > ends_notch + 2) & (wavelength <= final_wave -2))
    wavelength_S = wavelength[desired_range_stokes]
    spectrum_S = spectrum[desired_range_stokes]
    
    return wavelength_S, spectrum_S

def fit_signal_raman(wavelength_NP, signal_NP, ends_notch, final_wave):
    
    specs_NP = [spectrum_all for _,spectrum_all in sorted(zip(wavelength_NP, signal_NP))]
    wavelength_NP = np.sort(wavelength_NP)
    specs_NP = np.array(specs_NP)
    
   # specs_NP = smooth_Signal(specs_NP, window, deg, repetitions)
    
    wavelength_NP_S, spectrum_NP_S = stokes_signal(wavelength_NP, specs_NP, ends_notch, final_wave)
    
    I = 2500#20000#6000
    init_londa = 550
    init_width = 50
    I2 = 100#2500#1000
    I3 = 100#0#0
    C = 450
    
    init_parameters_NP = np.array([I, init_width, init_londa, I2, I3, C], dtype=np.double)
    bounds = ([0, 0, 500, 0, 0, 0], [16500, 300, 1000, 16500, 16500, 700])
   
    lorentz_fitted_NP, wavelength_fitted, best_parameters, r2_coef_pearson = fit_lorentz_signal_NP(spectrum_NP_S, wavelength_NP_S, init_parameters_NP, bounds)  
    
    print('Fit Lorentz NP:', best_parameters, 'r:', r2_coef_pearson)
    
    return wavelength_fitted, lorentz_fitted_NP, best_parameters