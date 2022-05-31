from string import *
import os

import time
import random as rng
import cv2
#import netCDF4 as nc
import struct
import array
import math
import numpy as np
from skimage.color import rgb2gray
import itertools

###############################################
## INSTRUMENT
ZAV=8.0 # 8 Ang/Volt in V



def get_gxsm_img(ch,v=0,t=0):
	dims=gxsm.get_dimensions(ch)
	gxsm.set_view_indices (ch, t,v)
	return gxsm.get_slice(ch, v,t, 0,dims[1]) # ch, v, t, yi, yn


def get_gxsm_img_cm(ch):
	# fetch dimensions
	dims=gxsm.get_dimensions(ch)
	print (dims)
	geo=gxsm.get_geometry(ch)
	print (geo)
	diffs=gxsm.get_differentials(ch)
	print (diffs)
	m = np.zeros((dims[1],dims[0]), dtype=float)

	for y in range (0,dims[1]):
		for x in range (0, dims[0]):
			v=0
			m[y][x]=gxsm.get_data_pkt (ch, x, y, v, 0)*diffs[2] # Z value in Ang now

	cmx = 0
	cmy = 0
	csum = 0
	cmed = np.median(m)
	print ('Z base: ', cmed)
	b=2
	for y in range (b,dims[1]-b):
		for x in range (b, dims[0]-b):
			v=0
			m[y][x]=m[y][x] - cmed # Z value in Ang now
			if m[y][x] > 0.5:
				cmx = cmx+x*m[y][x]
				cmy = cmy+y*m[y][x]
				csum = csum + m[y][x]
	if csum > 0:
		cmx = cmx/csum
		cmy = cmy/csum
	else:
		cmx = dims[0]/2
		cmy = dims[1]/2
	gxsm.add_marker_object(ch, 'PointCM',1, int(round(cmx)), int(round(cmy)), 1.0)
	export_drawing(ch, '-CM')
	return m, cmx, cmy


ch=8
geo=gxsm.get_geometry(ch)
dims=gxsm.get_dimensions(ch)
print (dims)

m = get_gxsm_img(ch,0,0)
for t in range(1,dims[3]):
	print (t)
	m = m + get_gxsm_img(ch,0,t)
	print(m)

m = m/dims[3]

ch=9

# convert 2d array into single memory2d block
n = np.ravel(m) # make 1-d
mem2d = array.array('f', n.astype(float)) 

# CH2 : activate ch 2 and create scan with resulting image data from memory2d
gxsm.chmodea (ch)
gxsm.createscanf (ch, dims[0],dims[1],1,  geo[0], geo[1], mem2d, 0)
#gxsm.add_layerinformation ("@ "+str(flv)+" Hz",10)

# be nice and auto update/autodisp
gxsm.chmodea (ch)
gxsm.direct ()
gxsm.autodisplay ()

