import numpy as np

def gen_lattice_regular(nside,lside,structurepath,Type=0):
    '''
    General lattice by regularization
    '''
    nx,ny,nz = int(nside[0]),int(nside[1]),int(nside[2])
    Vertex_file = os.path.join(structurepath,"Type" + str(Type),"Type" + str(Type)+"_Lattice_Vertex.txt")
    Bar_file = os.path.join(structurepath,"Type" + str(Type),"Type" + str(Type)+"_Lattice_BarList.txt")
    if not os.path.exists(Vertex_file) or not os.path.exists(Bar_file):
        print("Type{} Vertex file or BarList file does not exist!!!\nCheck the structurepath:{} ".format(Type,os.path.abspath(structurepath)))
        os._exit(0)
    Vertex = lside * np.loadtxt(Vertex_file, dtype=float)
    Bar = np.loadtxt(Bar_file, dtype=int)
    nblock = nx*ny*nz
    nbar = Bar.shape[0]
    nvertex = Vertex.shape[0]
    Nodes = np.zeros((nvertex*nblock,3),dtype=float)
    Elements = np.zeros((nbar*nblock,Bar.shape[1]),dtype=int)
    bid = 0
    # general in each block and numbering X-Y-Z
    for k in range(nz):
        for j in range(ny):
            for i in range(nx):
                dxyz = lside * np.tile(np.array([i,j,k]),(nvertex,1))
                Nodes[bid*nvertex:(bid+1)*nvertex,:] = Vertex + dxyz
                Elements[bid*nbar:(bid+1)*nbar,:] = Bar + bid*nvertex
                bid += 1
    # Assembly 
    return Nodes, Elements

from abaqus import *
from abaqusConstants import *
from caeModules import *
from driverUtils import executeOnCaeStartup
from material import createMaterialFromDataString

nside = [2,2,2]
lside = 10
structurepath = ""
structureType=3

Z_list = [1.0, 1.1, 1.2, 1.3, 1.4, 1.5]
R_list = [0.838, 0.863, 0.888, 0.907, 0.924, 0.939] # 25%

for z_scale, rc in zip(Z_list,R_list):
    Node, Element = gen_lattice_regular(nside, lside, structurepath,Type=structureType)
    Node[:,2] = z_scale*Node[:,2]
    part1 = mdb.models['Model-1'].Part(name='Part-{:d}'.format(int(z_scale*10)),dimensionality=THREE_D,type=DEFORMABLE_BODY)
    points = [(Node[e[0]-1],Node[e[1]-1]) for e in Element]
    part1.WirePolyLine(points=points, mergeType=MERGE, meshable=ON)
    part1.Set(edges=part1.edges, name='Set-1')
    mdb.models['Model-1'].CircularProfile(name='Profile-{:d}'.format(int(z_scale*10)), r=rc)
    mdb.models['Model-1'].BeamSection(name='Section-{:d}'.format(int(z_scale*10)), 
        integration=DURING_ANALYSIS, poissonRatio=0.0, profile='Profile-{:d}'.format(int(z_scale*10)), 
        material='Material-1', temperatureVar=LINEAR, consistentMassMatrix=False)
    part1.SectionAssignment(region=part1.sets['Set-1'], sectionName='Section-{:d}'.format(int(z_scale*10)), offset=0.0, 
        offsetType=MIDDLE_SURFACE, offsetField='', 
        thicknessAssignment=FROM_SECTION)
    part1.assignBeamSectionOrientation(region=part1.sets['Set-1'], method=N1_COSINES, n1=(0.0, 0.0, -1.0))
    part1.seedPart(size=0.5, deviationFactor=0.1, minSizeFactor=0.1)
    part1.generateMesh()
    elemType = mesh.ElemType(elemCode=B31)
    part1.setElementType(regions=part1.sets['Set-1'], elemTypes=(elemType, ))

for z_scale in Z_list:
    a = mdb.models['Model-1'].rootAssembly
    a.suppressFeatures(('Part-10-1', 'Part-11-1', 'Part-12-1', 'Part-13-1', 
        'Part-14-1', 'Part-15-1', ))
    a.features['Part-{:d}-1'.format(int(z_scale*10))].resume()
    U3 = -0.5*z_scale*lside*nside[2]
    dZ = (z_scale-1.0)*lside*nside[2]
    mdb.models['Model-1'].boundaryConditions['BC-2'].setValuesInStep(
        stepName='Step-1', u3=U3)
    a.translate(instanceList=('Bottom-2', ), vector=(0.0, 0.0, dZ))
    jobname = 'wire-compress-Type{:d}-H{:d}'.format(structureType,int(z_scale*10))
    mdb.Job(name=jobname, model='Model-1', 
        numCpus=4, numDomains=4)
    mdb.jobs[jobname].writeInput(consistencyChecking=OFF)
    a.translate(instanceList=('Bottom-2', ), vector=(0.0, 0.0, -dZ))

