import time

# test "manually"
print('main SC:', gxsm.get('script-control'))
gxsm.set('script-control', '3')

print('py-sc01: ', gxsm.get('py-sc01'))
gxsm.set('py-sc01', '1.01')

print('py-sc02: ', gxsm.get('py-sc02'))
gxsm.set('py-sc02', '2.02')

gxsm.set_sc_label('py-sc02', 'SuperSC')

gxsm.set_sc_label('py-sc04', 'Molecule#')

# Test via little helper dict
# Up to 10
#sc = dict(Points=330,  Molecule=123,  Iref=40, Zdown=-0.6, Zstart=-0.1)
sc = dict(STM_Range=70, AFM_Range=45,  Molecule=1,  I_ref=40, CZ_Level=0.1,  Z_down=-0.6, Z_start=-0.1)

print(sc)

# Setup SCs
def SetupSC():
	for i, e in enumerate(sc.items()):
		id='py-sc{:02d}'.format(i+1)
		print (id, e[0], e[1])
		gxsm.set_sc_label(id, e[0])
		gxsm.set(id, '{:.4f}'.format(e[1]))

SetupSC()
time.sleep(5)
print ('5s Zzzz')

# Read / Update dict
def GetSC():
	for i, e in enumerate(sc.items()):
		id='py-sc{:02d}'.format(i+1)
		print (id, ' => ', e[0], e[1])
		sc[e[0]] = float(gxsm.get(id))
		print (id, '<=', sc[e[0]])

GetSC()
print (sc)

time.sleep(5)
print ('5s Zzzz')
sc['Points']=400

# Update SCs
def SetSC():
	for i, e in enumerate(sc.items()):
		id='py-sc{:02d}'.format(i+1)
		gxsm.set(id, '{:.4f}'.format(e[1]))

SetSC()


# Reset
sc = dict(SC1=0, SC2=0,SC3=0, SC4=0,SC5=0, SC6=0,SC7=0, SC8=0)
SetupSC()


