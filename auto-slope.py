import numpy as np
import time

ZAV = 8.0  ## need Z Ang/Volt

def auto_slope(dir='x'):

	print ('Auto slope compute', dir)
	nx = float(gxsm.get ("PointsX"))
	if nx < 600:
		print ('Please run scan with more than 600 Points. Stop.')
		return

	if gxsm.waitscan(False) < 1:
		print ('Please run a scan with more than 600 Points. Stop.')
		return
		
	if dir == 'y':
		print ('Rotating to -90...')
		gxsm.set ("Rotation", "-90")
	else:
		gxsm.set ("Rotation", "0")

	dzp=0.0
	for i in range (0,6):
		y =gxsm.waitscan(False)
		yn = y+2
		while y < yn:
			y =gxsm.waitscan(False)
			if y < 1:
				print ('Please run a scan with more than 600 Points. Stop.')
				return
			time.sleep (1)
		ms = gxsm.get_slice(0, 0,0, y,1) # ch, v, t, yi, yn  

		med_left = np.median(ms[0,:100])
		med_right = np.median(ms[0,-100:])

		xr = float(gxsm.get ("RangeX"))
		nx = float(gxsm.get ("PointsX"))-80

		slpx = float(gxsm.get ("dsp-adv-scan-slope-"+dir))
		
		dz = slpx + (med_right -  med_left)/ZAV*3276.8/nx/xr*2
		gxsm.set ("dsp-adv-scan-slope-"+dir, "{}".format(dz))
		if abs(dzp-dz) < 0.00005:
			print ('OK dzE=', abs(dzp-dz))
			break
		dzp=dz
		print (dir,'  Slope compute:', med_left, med_right, dz)

	gxsm.set ("Rotation", "0")


auto_slope('x')
auto_slope('y')
