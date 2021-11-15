from odbAccess import *
import numpy as np

nside = [2,2,2]
lside = 10
structureType=3

Z_list = [1.0, 1.1, 1.2, 1.3]
# Z_list = [1.0]
OutList = []
for z_scale in Z_list:
    odbname = 'data/wire-compress-Type{:d}-H{:d}.odb'.format(structureType,int(z_scale*10))
    odb = openOdb(path=odbname,readOnly=True)
    step1 = odb.steps['Step-1']
    key = ''
    for k in step1.historyRegions.keys():
        if k.startswith("Node BOTTOM"):
            key = k
            break
    region = step1.historyRegions[key]
    times = np.array(region.historyOutputs['U3'].data)[:,0].astype(object)
    U3 = -np.array(region.historyOutputs['U3'].data)[:,1].astype(object)
    F3 = -np.array(region.historyOutputs['RF3'].data)[:,1].astype(object)
    out = np.vstack((times,U3,F3)).T
    head = np.array([['Type3-H{:d}'.format(int(z_scale*10)),'',''],['T','U','F']])
    out = np.vstack((head,out))
    OutList.append(out)
    print "Max F: ",F3[-1]

Info = OutList[0]
for value in OutList[1:]:
    Info = np.hstack((Info,value))

np.savetxt("data/H_info.csv",Info,fmt="%s",delimiter =',') 

