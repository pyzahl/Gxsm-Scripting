#!/usr/bin/python3
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter, freqz, ellip
import math
import time

vpfile = 'data-da/test.vpdata'
columns = np.transpose(np.loadtxt (vpfile))
labels  = ["Idx","Time-Mon (ms)","Current (nA)"," 09-LockIn-X (V)", "14-LockIn-Mag-pass (V)", "15-LockIn-Mag-BQ1 (V)", "08-LockIn-Mag-BQ2 (V)", "Time-Mon (ms)"]

columns[4] = 256*columns[4]
FS = columns[0][-1] / (1e-3*columns[1][-1])
print ('NS = ',columns[0][-1], '  T=',columns[1][-1], ' ms  FS=', FS, 'Hz')


def plot_vpdata(cols=[1,2,4]):
    plt.figure(figsize=(8, 4))
    yl = ''
    for c in cols[1:]:
            plt.plot(columns[cols[0]], columns[c], label=labels[c])
            if yl != '':
                    yl = yl + ', ' + labels[c]
            else:
                    yl = labels[c]
    plt.title('VPDATA  FS={:.2f} Hz'.format(FS))
    plt.xlabel(labels[cols[0]])
    plt.ylabel(yl)
    plt.legend()
    plt.grid()
    plt.show()


def dds_phaseinc (freq):
	fclk = 125e6
	return (1<<44)*freq/fclk

def Fs():
	freq = 1000. #float(gxsm.get("dsp-SPMC-LCK-FREQ"))
	print ('Lck Freq: {} Hz'.format(freq))
	n2 = round (math.log2(dds_phaseinc (freq)))
	lck_decimation_factor = (1 << (44 - 10 - n2)) - 1.
	return 125e6 / (lck_decimation_factor)  # pre-deciamtion to 1024 samples per lockin ref period

print ('Fs is ', Fs (), ' Hz')

def run_sosfilt(sos, x):
    n_samples = x.shape[0]
    n_sections = sos.shape[0]
    zx = np.zeros(n_sections)
    zy = np.zeros(n_sections)

    print (n_samples, n_sections)
    print (sos.shape)

    y = np.zeros(n_samples)

    z0 = np.zeros((n_sections,n_samples))
    z1 = np.zeros((n_sections,n_samples))
    
    zi_slice = np.zeros((n_sections,2))
    for n in range(0,n_samples):
        x_cur=x[n]
        for s in range(n_sections):
            x_new          = sos[s, 0] * x_cur                     + zi_slice[s, 0]
            zi_slice[s, 0] = sos[s, 1] * x_cur - sos[s, 4] * x_new + zi_slice[s, 1]
            zi_slice[s, 1] = sos[s, 2] * x_cur - sos[s, 5] * x_new
            x_cur = x_new
            z0[s,n] = zi_slice[s, 0]
            z1[s,n] = zi_slice[s, 1]
        y[n]=x_cur
    return y, z0, z1


def run_sosfilt_Q24(sos, x):
    Q24 = 1<<24
    Q28 = 1<<28
    n_samples = x.shape[0]
    n_sections = sos.shape[0]
    zx = np.zeros(n_sections)
    zy = np.zeros(n_sections)

    print (n_samples, n_sections)
    print (sos.shape)

    sos = sos*Q28
    sos = sos.astype(np.int64)

    print ('SOS_Q28:', sos)
    
    xi = (x*Q24).astype(np.int64)

    print ('xQ24:', xi)
    
    y = np.zeros(n_samples, type(np.int64))
    
    zi_slice = np.zeros((n_sections,2), type(np.int64))
    for n in range(0,n_samples):
        x_cur=xi[n]
        for s in range(n_sections):
            x_new          = int(sos[s, 0] * x_cur                  + zi_slice[s, 0]) >> 28
            zi_slice[s, 0] =  sos[s, 1] * x_cur - sos[s, 4] * x_new + zi_slice[s, 1]
            zi_slice[s, 1] =  sos[s, 2] * x_cur - sos[s, 5] * x_new
            x_cur = x_new
        y[n]=x_cur

    print (y)
    return y.astype(float)/Q24



# Design a lowpass elliptic filter
# rp: Passband ripple in dB
# sa: Stopband attenuation in dB
def ellipt_filter(order=4, cutoff=0.2, sa=50, rp=0.5, filter_type='lowpass', fs=1.0):
    nyquist = 0.5 * fs  # Nyquist frequency
    normal_cutoff = cutoff / nyquist
    sos = ellip(order, rp, sa, cutoff, btype=filter_type, output='sos')
    sos = np.atleast_2d(sos)
    b ,a = ellip(order, rp, sa, cutoff, btype=filter_type, output='ba')
    return sos, b, a


# Design a Butterworth IIR filter
def butterworth_filter(order=2, cutoff=0.3, filter_type='low', fs=1.0):
    nyquist = 0.5 * fs  # Nyquist frequency
    normal_cutoff = cutoff / nyquist
    b, a = butter(order, normal_cutoff, btype=filter_type, analog=False)
    return b, a

# Compute and plot the frequency response
def plot_frequency_response(b, a, cutoff):
    w, h = freqz(b, a, worN=1024)
    plt.figure(figsize=(8, 4))
    plt.plot(w / np.pi, 20 * np.log10(abs(h)), 'b')
    plt.plot([cutoff, cutoff], [0, -20], 'r')
    plt.title('Frequency Response of the IIR Filter, low {} ({} Hz)'.format(cutoff, cutoff*Fs()))
    plt.xlabel('Normalized Frequency (×π rad/sample)')
    plt.ylabel('Magnitude (dB)')
    plt.grid()
    plt.show()

# test with
fc = 10000
fc_norm = fc/Fs()

#b, a = butterworth_filter(order=1, cutoff=fc_norm)
#print (b.size)

sos, b, a = ellipt_filter(order=4, cutoff=fc_norm, sa=40, rp=0.5)

print ('fCut_norm=', fc_norm, ' fc=', fc, ' Hz')
print (' b=',b,' a=',a)
print (' sos=',sos)


if 0: # AB type
	gxsm.set("dsp-SPMC-LCK-BQ-COEF-BA00", str(b[0]))
	gxsm.set("dsp-SPMC-LCK-BQ-COEF-BA01", str(b[1]))
	if b.size>2:
		gxsm.set("dsp-SPMC-LCK-BQ-COEF-BA02", str(b[2]))

	gxsm.set("dsp-SPMC-LCK-BQ-COEF-BA03", str(a[0]))
	gxsm.set("dsp-SPMC-LCK-BQ-COEF-BA04", str(a[1]))
	if a.size>2:
		gxsm.set("dsp-SPMC-LCK-BQ-COEF-BA05", str(a[2]))

if 0: # SOS ellipt cascaded BiQ type
	for s in range (0,2):
		for i in range (0,6):
			gxsm.set("dsp-SPMC-LCK-BQ{}-COEF-BA0{}".format(s+1,i), '0.1234')
			gxsm.set("dsp-SPMC-LCK-BQ{}-COEF-BA0{}".format(s+1,i), '0')
			gxsm.set("dsp-SPMC-LCK-BQ{}-COEF-BA0{}".format(s+1,i), str(sos[s][i]))

#plot_frequency_response(b, a, fc_norm)

#filteredS = sosfilt(sos, sig)

columns[0], z0, z1 = run_sosfilt(sos, columns[4])
labels[0]  = 'SOS[4] Flt'
columns[5] = run_sosfilt_Q24(sos, columns[4])
labels[5]  = 'SOS[4] Q24'

plot_vpdata([1,2,4,0,5])

