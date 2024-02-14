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

def calc_r2(observed, fitted):
    # Calculate coefficient of determination
    avg_y = observed.mean()
    ssres = ((observed - fitted)**2).sum()
    sstot = ((observed - avg_y)**2).sum()
    return 1.0 - ssres/sstot

def fit_polynomial(spectrum, wavelength, npol):
    
    wavelength_fitted = np.linspace(wavelength[0], wavelength[-1], 1000)
    spectrum_inter = np.interp(wavelength_fitted, wavelength, spectrum)
    
    poly = np.polyfit(wavelength_fitted, spectrum_inter, npol)
    
    spectrum_fitted = np.polyval(poly, wavelength_fitted)
    
    r2_coef_pearson = calc_r2(spectrum_inter, spectrum_fitted)
    
    max_wavelength =  wavelength_fitted[np.argmax(spectrum_fitted)]

    return spectrum_fitted, wavelength_fitted, max_wavelength, r2_coef_pearson

def stokes_signal(wavelength, spectrum, ends_notch, final_wave):
    
    desired_range_stokes = np.where((wavelength > ends_notch) & (wavelength <= final_wave))
    wavelength_S = wavelength[desired_range_stokes]
    spectrum_S = spectrum[desired_range_stokes]
    
    return wavelength_S, spectrum_S

def fit_signal_polynomial(wavelength_NP, signal_NP, ends_notch, final_wave, npol):
    
    specs_NP = [spectrum_all for _,spectrum_all in sorted(zip(wavelength_NP, signal_NP))]
    wavelength_NP = np.sort(wavelength_NP)
    specs_NP = np.array(specs_NP)
    
   # specs_NP = smooth_Signal(specs_NP, window, deg, repetitions)
    
    wavelength_NP_S, spectrum_NP_S = stokes_signal(wavelength_NP, specs_NP, ends_notch, final_wave)
   
    spectrum_fitted, wavelength_fitted, max_wavelength, r2_coef_pearson = fit_polynomial(spectrum_NP_S, wavelength_NP_S, npol)  
    
    print('r-squared fit polynomial:', r2_coef_pearson)
    
    return wavelength_fitted, spectrum_fitted, max_wavelength