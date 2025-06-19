import numpy as np
import time
import os

import matplotlib as mpl
mpl.use('Agg')

import matplotlib.pyplot as plt
from matplotlib import ticker

def jsquery_var(jvn):
	u,v,w = gxsm.rtquery('X *{}'.format(jvn))
	print ('{} = {}'.format(jvn, u))
	return u

def jsset_var(jvn):
	jps=''
	for jp in jvn:
		if jps > '':
			jps = jps+','
		jps = jps+'"'+ jp[0] +'":{"value":' + '{}'.format(jp[1]) + '}'
	json = '{ "parameters":{' + jps + '}}'
	print ('JSON=', json)
	u,v,w = gxsm.rtquery('X '+json)
	return u
	
jsquery_var ('SPMC_UPTIME_SECONDS')

print ('{:x}'.format(int(jsquery_var('RPSPMC_SERVER_VERSION'))))
print ('{:x}'.format(int(jsquery_var('RPSPMC_SERVER_DATE'))))
print ('{:x}'.format(int(jsquery_var('RPSPMC_FPGAIMPL_VERSION'))))
print ('{:x}'.format(int(jsquery_var('RPSPMC_FPGAIMPL_DATE'))))

jsquery_var('SPMC_AD5791_GLC_CH')
jsquery_var('SPMC_AD5791_GLC_BIT')
jsquery_var('SPMC_AD5791_GLC_VALPOS')
jsquery_var('SPMC_AD5791_GLC_VALNEG')

# adjust ADC to sync with DAC (if !=0)
jsset_var((['SPMC_AD463_POST_SYNC_DELAY', 0 ],))


jsset_var((['SPMC_AD5791_GLC_BIT', 0 ],  ['SPMC_AD5791_GLC_CH',2]))
jsset_var((['SPMC_AD5791_GLC_VALPOS', -40 ],['SPMC_AD5791_GLC_VALNEG',-126 ]))

time.sleep(0.5)

jsquery_var('SPMC_AD5791_GLC_BIT')
jsquery_var('SPMC_AD5791_GLC_CH')

jsquery_var('SPMC_AD5791_GLC_VALPOS')
jsquery_var('SPMC_AD5791_GLC_VALNEG')


jsset_var((['SPMC_AD5791_GLC_BIT', 1 ],  ['SPMC_AD5791_GLC_CH',2]))
jsset_var((['SPMC_AD5791_GLC_VALPOS', -120 ],['SPMC_AD5791_GLC_VALNEG',10 ]))
# -2.4746 ... -2.4736

time.sleep(0.5)

jsquery_var('SPMC_AD5791_GLC_BIT')
jsquery_var('SPMC_AD5791_GLC_CH')

jsquery_var('SPMC_AD5791_GLC_VALPOS')
jsquery_var('SPMC_AD5791_GLC_VALNEG')

jsset_var((['SPMC_AD5791_GLC_BIT', 2 ],  ['SPMC_AD5791_GLC_CH',2]))
jsset_var((['SPMC_AD5791_GLC_VALPOS', 0 ],['SPMC_AD5791_GLC_VALNEG',0 ]))


jsset_var((['SPMC_AD5791_GLC_BIT', 3 ],  ['SPMC_AD5791_GLC_CH',2]))
jsset_var((['SPMC_AD5791_GLC_VALPOS', 0 ], ['SPMC_AD5791_GLC_VALNEG',-100 ]))


def plot():
	print (gxsm.rtquery('X $SIGNAL_CH1'))
	x, n, dum, s1 = gxsm.rtquery('X $SIGNAL_CH1')
	t = np.arange(0, 1024, 1)

	fig=plt.figure(figsize=(8, 6))
	plt.plot(t, s1)
	plt.title('Signal Graph')
	plt.xlabel('index')
	plt.ylabel('s1')		
	#plt.legend()
	plt.grid()
	plt.show()
	plt.savefig('/tmp/glc.png')
	
	
	
def plot_gvp(sets,v):
    print ('Fig')
    fig=plt.figure(figsize=(8, 4))
    print ('Adj')
    plt.subplots_adjust(bottom=0.2)
    print ('Subs')
    fig0 = fig.subfigures(1)
    print ('Ax')
    ax0 = fig0.subplots()

    print ('Plot')
    for s in sets:
        for c in s[1:]:
            #plt.plot(s[0], c, marker = ',')
            plt.scatter(s[0], c, s=1)
    print ('Axis...')
    plt.title('DAC-Z around {}V'.format(v))
    plt.xlabel('DAC value in bin (dec)')
    plt.ylabel('DAC voltage in dev in DAC values')
    #plt.legend()
    ax0.tick_params("x", rotation=90)
    ax0.xaxis.set_major_formatter(lambda x, pos: '{:20b}\n({:d},{:.5}V)'.format(int(x),int(x),x*5/(1<<19)))
    #ax0.xaxis.set_major_formatter(ticker.StrMethodFormatter("{x:%.3f}"))
    plt.grid()
    print ('Show')
    plt.show()
    plt.savefig('/tmp/plot.png')

#GD = []

fig=plt.figure(figsize=(20, 6))

for sd in range(0, 2):
	print (sd)
	# adjust ADC to sync with DAC (if !=0)
	#jsset_var((['SPMC_AD463_POST_SYNC_DELAY', sd ],))

	gxsm.action("DSP_VP_VP_EXECUTE")
	time.sleep(1)

	#print ('#Events: ', gxsm.get_probe_event(0,-2)) # report
	gvp, labs, units = gxsm.get_probe_event(0,-1)  # get last
	print (labs)
	#print (labs, gvp)

	#GD.append(gvp)

	#plt.plot(gvp[1], 1000*gvp[0])
	plt.scatter(gvp[2], 1000*gvp[0],s=1)
	
	
plt.title('DAC-Z')
plt.xlabel('DAC-Z')
plt.ylabel('mVolts')		
#plt.legend()
plt.grid()
plt.show()
plt.savefig('/tmp/daczX.png')


#plot_gvp(([1,0],[1,0]),0)

for i in range(0, 8):
	dac = 1<<(19-i)
	print ('Bit MSB-{}  =>  {:.2f} mV  {:.2f}  {}  US:{}'.format(i, 5000 - dac*5000/(1<<19), dac*5000/(1<<19), (1<<19)-dac, dac))
