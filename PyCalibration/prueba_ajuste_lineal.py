import matplotlib.pyplot as plt
import numpy as np

from scipy.optimize import curve_fit

# Ajustamos

def ajuste_lineal(x, y, ey):
	f = lambda xl, A, B: A*xl+B # la función modelo, con la que ajustamos
	popt, pcov = curve_fit(f, x, y, sigma = ey, absolute_sigma=True)
	sigmas = np.sqrt([pcov[0,0],pcov[1,1]])

	pendiente = round(popt[0], 3)
	error_pendiente = round(sigmas[0],3)

	ordenada = round(popt[1], 3)
	error_ordenada = round(sigmas[1],3)

	ajuste = [pendiente, ordenada]
	error_ajuste = [error_pendiente, error_ordenada]

	return ajuste, error_ajuste

x = np.array([1, 2, 3,6,7])
y = np.array([2, 4, 6,12,14])
ey = np.ones(len(y))*0.5

ajuste, error_ajuste = ajuste_lineal(x,y,ey)
print(ajuste, error_ajuste)