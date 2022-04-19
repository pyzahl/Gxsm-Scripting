from string import *
import os
import time

#folder = '/home/pzahl/BNLBox/Data/Percy-P0/Exxon-Yunlong/20220401-Cu111-PP-TS-prev-warmup65C/'

full_original_name = gxsm.chfname(0).split()[0]

postfix='X'

print(full_original_name)

ncfname = os.path.basename(full_original_name)
print(ncfname)

folder = os.path.dirname(full_original_name)
print(folder)

name, ext = os.path.splitext(ncfname)
print(name)

dest_name = folder+'/'+name
print(dest_name)

gxsm.chmodea(0)
gxsm.chmodem(1)

print('Crop Original...')
gxsm.crop (0,1)
gxsm.autodisplay()
time.sleep(1)
print('crop-X exporty drawing')
gxsm.save_drawing(1, 0,0, dest_name+postfix+'.png')
gxsm.save_drawing(1, 0,0, dest_name+postfix+'.pdf')

print('Crop Edge...')

gxsm.chmodea(0)
gxsm.chmodem(1)

print('Edge action trigger')
gxsm.action ('MATH_FILTER2D_Edge')
print('Edge action wait')
time.sleep(1)
print('autodisplay')
gxsm.autodisplay()
print('crop-XLogr6  exporty drawing')
gxsm.save_drawing(1, 0,0, dest_name+postfix+'Logr6.png')
#gxsm.save_drawing(1, 0,0, dest_name+postfix+'Logr6.pdf')
gxsm.autodisplay()
gxsm.save_drawing(1, 0,0, dest_name+'XLogr6.png')
gxsm.save_drawing(1, 0,0, dest_name+'XLogr6.pdf')

gxsm.chmodea(0)
gxsm.chmodem(1)
