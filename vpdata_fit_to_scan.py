from string import *
import math
import array
import numpy as np
from scipy.optimize import curve_fit

###############################################
### Reference Image in
ch=0
geo=gxsm.get_geometry(ch)
dims=gxsm.get_dimensions(ch)
print (dims)

# put results in
ch=1
m=np.zeros((dims[0],dims[1]))

# related VPDATA files are here:
#fname = '/home/pzahl/BNLBox/Data/Udo-P310640/20220509-Ag111PC/MapKP1282/Ag111C1283-VP001-VP.vpdata'
fpath = '/home/pzahl/BNLBox/Data/Udo-P310640/20220509-Ag111PC/MapKP1282'
fname =  fpath + '/Ag111C1283-VP'
#C Index	"Umon (V)"	"ADC0-I (pA)"	"Zmon (Å)"	"Umon (V)"	"McBSP Freq (Hz)"	"In 1 (V)"	"Time (ms)"	Block-Start-Index

import numpy as np


def fit_func(x, a, b, c):
    return -a*(x-b)*(x-b) + c

f0  =30212.74
fset=30210.60
foff=f0-fset
z0=0

for j in range(0, dims[1]):
	for i in range(0, dims[0]):
		fi = j * dims[0] + i + 1
		f = '{}{:03d}-VP.vpdata'.format(fname, fi)
		print (f)
		columns = np.transpose(np.loadtxt (f))

		#print (columns)
		print (columns.shape)
		#sec23 = columns[0:8,100:7099]
		sec23 = columns
		#print (sec23.shape)

		x = sec23[1]
		y = sec23[5]-foff
		params = curve_fit(fit_func, x, y)
		[a, b, c] = params[0]

		fit = -a*(x-b)*(x-b) + c
		
		m[j,i] = b*1000 # data in mV
	
# put resutl into Gxms scan as image!

# convert 2d array into single memory2d block
n = np.ravel(m) # make 1-d
mem2d = array.array('f', n.astype(float)) 

# CH2 : activate ch 2 and create scan with resulting image data from memory2d
gxsm.chmodea (ch)
gxsm.createscanf (ch, dims[0],dims[1],1,  geo[0], geo[1], mem2d, 0)
#gxsm.add_layerinformation ("@ "+str(flv)+" Hz",10)

# be nice and auto update/autodisp
gxsm.set_scan_unit (ch, 'V')
gxsm.chmodea (ch)
gxsm.direct ()
gxsm.autodisplay ()

