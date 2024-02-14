
import numpy as np

def spiral_cw(A):
    A = np.array(A)
    out = []
    while(A.size):
        out.append(A[0])        # take first row
        A = A[1:].T[::-1]       # cut off first row and rotate counterclockwise
    return np.concatenate(out)

def spiral_ccw(A):
    A = np.array(A)
    out = []
    while(A.size):
        out.append(A[0][::-1])    # first row reversed
        A = A[1:][::-1].T         # cut off first row and rotate clockwise
    return np.concatenate(out)

def base_spiral(nrow, ncol, clock_type):

    if clock_type == 'cw':

        spiral = spiral_cw(np.arange(nrow*ncol).reshape(nrow,ncol))[::-1]

    elif  clock_type == 'ccw':

        spiral = spiral_ccw(np.arange(nrow*ncol).reshape(nrow,ncol))[::-1]
   
    return spiral

def to_spiral(A, clock_type):
    A = np.array(A)
    B = np.empty_like(A)
    B.flat[base_spiral(*A.shape, clock_type)] = A.flat
    return B

def from_spiral(A, clock_type):
    A = np.array(A)
    return A.flat[base_spiral(*A.shape, clock_type)].reshape(A.shape)

def matrix_index(number_pixel):

    x = number_pixel
    y = number_pixel
    matrix_pixel_index = np.arange(x*y).reshape(x,y) 

    return matrix_pixel_index


def matrix_index_2(number_pixel):

    x = np.arange(0, number_pixel)
    y = np.arange(0, number_pixel)
    matrix_pixel_index = [x, y]

    return matrix_pixel_index

def matrix_xy(xo, yo, rango, n):
    
    x = np.linspace(xo-rango/2, xo + rango/2, n)
    y = np.linspace(yo-rango/2, yo + rango/2, n)
    
    matrix = [x, y]
    
    return matrix

                       
#%%

matrix_pixel_index = matrix_index_2(34)

matrix = matrix_xy(100, 150, 2, 34)  

matrix_index_spiral = to_spiral(matrix_pixel_index, 'ccw')

#%%

matrix_x_spiral = matrix[0][matrix_index_spiral[0][:]]

matrix_y_spiral = matrix[1][matrix_index_spiral[1][:]]

matrix_spiral = [matrix_x_spiral, matrix_y_spiral]