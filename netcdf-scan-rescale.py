import netCDF4 as nc
import numpy as np

## factors to rescale - - see below
x_rescale_by = 1.0
y_rescale_by = 1.0
z_rescale_by = 1.0

ch=0

print('------ Current Scan in CH --------', ch)
full_original_name = gxsm.chfname(0).split()[0]
diffs=gxsm.get_differentials(ch)
print ('Scan dx,dy,dz: ',diffs)

print('------ manipulating NC file -----------')

ncfile = gxsm.chfname(ch).split()[0]
print('Scan file name: ', ncfile)

print('------ initial geometry -----------')
sc = nc.Dataset(filename= ncfile, mode="r+")
print ('NCfile dx,dy,dz: ', sc['dx'][0], sc['dy'][0], sc['dz'][0])
print ('NCfile range x,y: ', sc['rangex'][0], sc['rangey'][0])

#print('NCfile dimx: ', sc['dimx'][:])
#print('NCfile dimx: ', sc['dimy'][:])

## rescale dx,dy

tmp = sc['dx'][0] *  x_rescale_by
sc['dx'][0] = tmp

tmp = sc['dy'][0] *  y_rescale_by
sc['dy'][0] = tmp


## dz similar
tmp = sc['dz'][0] *  z_rescale_by
sc['dz'][0] = tmp


## must also apply to ranges to match:
tmp = sc['rangex'][0] *  x_rescale_by
sc['rangex'][0] = tmp

tmp = sc['rangey'][0] *  y_rescale_by
sc['rangey'][0] = tmp

xlookup = sc['dimx'][:]
ylookup = sc['dimy'][:]
sc['dimx'][:] = xlookup*  x_rescale_by
sc['dimy'][:] = ylookup*  y_rescale_by
#print('NCfile dimx: ', sc['dimx'][:])
#print('NCfile dimx: ', sc['dimy'][:])


print('------ final geometry as updated -----------')

print ('NCfile dx,dy,dz: ', sc['dx'][0], sc['dy'][0], sc['dz'][0])
print ('NCfile range x,y: ', sc['rangex'][0], sc['rangey'][0])



sc.close ()

print('------ reloading NC file -----------')

# reload
gxsm.load (ch, ncfile)

