import math
import numpy as np
import time as time
import datetime as datetime

### EXAMPLE AUTO APP via SCRIPT

### Inst-SPM Settings:
### ========================
### Instrument/X-Piezo-AV = 10
### Instrument/Y-Piezo-AV = 10
### Instrument/Z-Piezo-AV = 10
### Instrument/Bias-Gain = 1
### Instrument/Bias-Offset = 0
### Instrument/nAmpere2Volt = 1
### ========================
### Set  VX=VY=VZ = 5
### ========================
### Dummy Loop Back: Bias-Out  to Current-In    (OUT6 -> IN0)

ZRANGE = 500    # +/- 500A is max full scale Z servo range at this setting
TIMEOUT= datetime.timedelta(seconds=5)    # 5s time out/max wait

print (ZRANGE)
print (TIMEOUT)

# setup default scan (not required)
gxsm.set ("RangeX", "500")
gxsm.set ("PointsX", "400") 


# general purpose "script control" value
sc=gxsm.get ("script-control")
gxsm.set ("script-control","1")

# store current bias, cp, ci as reference for sensing/approach
bias=gxsm.get ("dsp-fbs-bias")
current=gxsm.get ("dsp-fbs-mx0-current-set")
cp=gxsm.get ("dsp-fbs-cp")
ci=gxsm.get ("dsp-fbs-ci")
print ("CP=", cp, ", CI=",ci, ", current-setpoint=", current)



# RT-Query of DSP statemachine status vector
# via  gxsm.rtquery("z")

# Real-Time Query of DSP signals/values, auto buffered
# Propertiy hash:      return val1, val2, val3:
# "z" :                ZS, XS, YS  with offset!! -- in volts after piezo amplifier
# "o" :                Z0, X0, Y0  offset -- in volts after piezo amplifier
# "R" :                expected Z, X, Y -- in Angstroem/base unit
# "f" :                dFreq, I-avg, I-RMS
# "s","S" :            DSP Statemachine Status Bits, DSP load, DSP load peak
# "Z" :                probe Z Position
# "i" :                GPIO (high level speudo monitor)
# "A" :                Mover/Wave axis counts 0,1,2 (X/Y/Z)
# "p" :                X,Y Scan/Probe Coords in Pixel, 0,0 is center, DSP Scan Coords
# "P" :                X,Y Scan/Probe Coords in Pixel, 0,0 is top left [indices]
# "M" :                Mix-IN1, 2, 3
# "mNN" :              MonitorSignal[NN] -- Monitor Singals at index SigMon[NN]: [Scaled Signal in Unit, raw signal, scale, ret=unit-string] (NN = 00 ... 22), 99: reload signal mapping


def RTQ_info():
	svec=gxsm.rtquery ("s")
	s = int(svec[0])
	print ("FB:", s&1, " Scan:", s&(2+4), " VP: ", s&8, " Mov:", s&16, " PLL:", s&32, " Script Ctrl=", sc)
	z=gxsm.rtquery ("R")
	print("ZXY (Ang) = ", z)
	fi=gxsm.rtquery ("f")
	print("dFreq, I-avg ,I-RMS = ", fi)

def get_z():
	spm_rvec = gxsm.rtquery ("R")
	return float(spm_rvec[0])

def get_current():
	fvec = gxsm.rtquery ("f")
	return float(fvec[1])

# utility functions
def goto_refpoint (x=0.0, y=0.0):
    gxsm.set ("ScanX","{}".format(x))
    gxsm.set ("ScanY","{}".format(y))
    print ("Zzzz@ ", x, ", ", y)
    gxsm.sleep (15) # sleep 15/10 sec.

def watch_mixin():
        mixer_vec = gxsm.rtquery ("M")
        print ('Mixer IN1,2,3 = [{} V, {} V, {} V] '.format(mixer_vec[0], mixer_vec[1], mixer_vec[2] ))


def freeze_Z ():
    gxsm.set ("DSP_CP","0")
    gxsm.set ("DSP_CI","0")

def release_Z ():
    gxsm.set ("DSP_CP","{}".format(cp))
    gxsm.set ("DSP_CI","{}".format(ci))
    gxsm.sleep (20)


def check_for_tunneling ():
	gxsm.set ("dsp-fbs-mx0-current-set","{}".format(current))
	ti = datetime.datetime.now()
	print ('Checking for tunneling...')
	print ('Zi=', get_z())
	while ti+TIMEOUT > datetime.datetime.now() and get_z() > -ZRANGE*0.9:
		print ('Z=', get_z(), 'Ang    Current=', get_current(), 'nA')
		#watch_mixin()
		time.sleep(0.5)

def retract_Z_servo ():
	gxsm.set ("dsp-fbs-mx0-current-set","0")
	ti = datetime.datetime.now()
	print ('Retracting Z Piezo...', ti)
	print ('Zi=', get_z())
	while ti+TIMEOUT > datetime.datetime.now() and get_z() < +ZRANGE*0.9:
		print ('Z=', get_z(), datetime.datetime.now() -ti)
		time.sleep(0.5)

def execute_coarse_steps ():
	print ("Executing Coarse Motion Steps")
	gxsm.action("DSP_CMD_MOV-ZM_Auto")
	#gxsm.action("DSP_CMD_MOV-XP_Rot")
	time.sleep(1)



RTQ_info()

print ('Z=', get_z())
starttime = datetime.datetime.now()
print (starttime)

check_for_tunneling ()

count = 0
while get_z() < -ZRANGE/2 and sc > 0:
	count = count+1
	print (count)
	retract_Z_servo ()
	execute_coarse_steps()
	check_for_tunneling ()
	sc=gxsm.get ("script-control")

if get_z() > -ZRANGE/2:
	print ("Ready: Z in range")
else:
	print ("Time out reached or user abort.")

fintime = datetime.datetime.now()
print (fintime)



