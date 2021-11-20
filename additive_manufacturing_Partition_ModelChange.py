from abaqus import *
from abaqusConstants import *
from caeModules import *
from driverUtils import executeOnCaeStartup
from material import createMaterialFromDataString

# configs values
nlayer = 50
lx,ly,lz = 50., 50., 40.
dy = ly/nlayer
initTemperature = 25.
envTemperature = 20.

# define Absolute Zero Temperature and Stefan-Boltzmann Constants (Unit: SIMM)
mdb.models['Model-1'].setValues(absoluteZero=-273.15, stefanBoltzmann=5.67E-11)

# define Materials Properties and Section
mdb.models['Model-1'].Material(name='Material-1')
material = mdb.models['Model-1'].materials['Material-1']
material.Conductivity(table=((0.9, ), ))
material.Density(table=((1e-09, ), ))
material.Elastic(table=((1.0, 0.3, 20.0), (0.8, 0.3, 60.0), (0.6, 0.4, 100.0), (0.5, 0.4, 150.0), (0.25, 0.4, 200.0)), temperatureDependency=ON)
material.Expansion(table=((1e-05, 20.0), (3e-05, 150.0)), temperatureDependency=ON)
material.SpecificHeat(table=((1200000000.0, ), ))
mdb.models['Model-1'].HomogeneousSolidSection(name='Section-1', material='Material-1', thickness=None)

# create Part-1
s = mdb.models['Model-1'].ConstrainedSketch(name='__profile__',sheetSize=200.0)
s.setPrimaryObject(option=STANDALONE)
s.rectangle(point1=(0.0, 0.0), point2=(lx, ly))
mdb.models['Model-1'].Part(name='Part-1', dimensionality=THREE_D, type=DEFORMABLE_BODY)
part1 = mdb.models['Model-1'].parts['Part-1']
part1.BaseSolidExtrude(sketch=s, depth=lz)
s.unsetPrimaryObject()

# Create Datum Plane for Partition
for i in range(1,nlayer):
    part1.DatumPlaneByPrincipalPlane(principalPlane=XZPLANE, offset=dy*i)
#  Create PartitionCell with datums plane
for i in range(1,nlayer):
    part1.PartitionCellByDatumPlane(datumPlane=part1.datums[i+1], cells=part1.cells[:])

session.viewports['Viewport: 1'].setValues(displayedObject=part1)


# create Set on each layer
part1.Set(cells=part1.cells, name='Set-all')
for i in range(nlayer):
    cell = part1.cells.getByBoundingBox(xMin=0.0, xMax=lx, yMin=(i-0.5)*dy,yMax=(i+1.5)*dy,zMin=0,zMax=lz)
    part1.Set(cells=cell, name='Set-{:d}'.format(i+1))


part1.seedPart(size=2.0, deviationFactor=0.1, minSizeFactor=0.1)
part1.generateMesh()
elemType1 = mesh.ElemType(elemCode=C3D8T)
elemType2 = mesh.ElemType(elemCode=C3D6T)
elemType3 = mesh.ElemType(elemCode=C3D4T)
part1.setElementType(regions=(part1.cells[:],), elemTypes=(elemType1, elemType2, elemType3))
side1Faces = part1.faces.getByBoundingBox(xMin=0.0, xMax=lx, yMin=-0.5*dy,yMax=0.5*dy,zMin=0,zMax=lz)
part1.Surface(side1Faces=side1Faces, name='Surf-1')


part1.SectionAssignment(region=part1.sets['Set-all'], sectionName='Section-1', offset=0.0, 
    offsetType=MIDDLE_SURFACE, offsetField='', thicknessAssignment=FROM_SECTION)

# Create Coupled-Temp-Displacement Steps
mdb.models['Model-1'].CoupledTempDisplacementStep(name='Step-kill', 
    previous='Initial', timePeriod=1e-08, initialInc=1e-08, minInc=1e-13, 
    maxInc=1e-08, deltmx=200.0, nlgeom=ON)
for i in range(nlayer):
    step_name='Step-{:d}'.format(nlayer-i)
    mdb.models['Model-1'].CoupledTempDisplacementStep(name=step_name, 
        previous='Step-kill',  timePeriod=2, 
        initialInc=0.2, minInc=5e-04, maxInc=0.2, deltmx=200.0)
mdb.models['Model-1'].CoupledTempDisplacementStep(name='Step-cool', 
    previous='Step-{:d}'.format(nlayer), timePeriod=20, 
    initialInc=1, minInc=0.1, maxInc=1, deltmx=200.0)


assembly = mdb.models['Model-1'].rootAssembly
assembly.Instance(name='Part-1-1', part=part1, dependent=ON)
assembly.ReferencePoint(point=(lx/2, 0.0, lz/2))
assembly.Set(referencePoints=(assembly.referencePoints[assembly.referencePoints.keys()[0]],), name='Set-1')
# Coupling
region1=assembly.sets['Set-1']
region2=assembly.instances['Part-1-1'].surfaces['Surf-1']
mdb.models['Model-1'].Coupling(name='Constraint-1', controlPoint=region1, 
    surface=region2, influenceRadius=WHOLE_SURFACE, couplingType=KINEMATIC, 
    localCsys=None, u1=ON, u2=ON, u3=ON, ur1=ON, ur2=ON, ur3=ON)
mdb.models['Model-1'].FieldOutputRequest(name='F-Output-1', 
    createStepName='Step-1',  numIntervals=10, variables=('HFL', 'LE', 'NT',  'RF', 'RFL', 'S', 'U'))
mdb.models['Model-1'].HistoryOutputRequest(name='H-Output-1', 
    createStepName='Step-1', variables=('RF2', 'RM1', 'RM3'), numIntervals=10, 
    region=assembly.sets['Set-1'])

# Create load and interactions
for i in range(nlayer):
    step_name='Step-{:d}'.format(i+1)
    int_name='Int-{:d}'.format(i+1)
    region = assembly.instances['Part-1-1'].sets['Set-{:d}'.format(i+1)]
    # ModelChange ELEMENT type
    mdb.models['Model-1'].ModelChange(name=int_name, createStepName='Step-kill', 
        region=region, regionType=GEOMETRY, activeInStep=False, includeStrain=False)
    mdb.models['Model-1'].interactions[int_name].setValuesInStep(stepName=step_name, 
        activeInStep=True, includeStrain=True)

mdb.models['Model-1'].TabularAmplitude(name='Amp-1', timeSpan=STEP, 
    smooth=SOLVER_DEFAULT, data=((0.0, 0.0), (0.5, 1.0), (0.6, 0.0)))
mdb.models['Model-1'].TabularAmplitude(name='Amp-2', timeSpan=STEP, 
    smooth=SOLVER_DEFAULT, data=((0.6, 0.0), (1.0, 1.0), (1.2, 0.0)))
mdb.models['Model-1'].EncastreBC(name='BC-1', createStepName='Step-1', region=assembly.sets['Set-1'])
mdb.models['Model-1'].Gravity(name='gavity', createStepName='Step-1', 
    comp2=9800.0, distributionType=UNIFORM, field='')
# Heat Flux
for i in range(nlayer):
    mdb.models['Model-1'].BodyHeatFlux(name='heatflux-{:d}'.format(i+1), createStepName='Step-{:d}'.format(i+1), 
        region=assembly.instances['Part-1-1'].sets['Set-{:d}'.format(i+1)], magnitude=100.0, amplitude='Amp-1')

#  Create FilmCondition and Radiation interactions

assembly.Surface(side1Faces=assembly.instances['Part-1-1'].faces, name='Surf-film')
assembly.Surface(side1Faces=assembly.instances['Part-1-1'].faces, name='Surf-radiation')
region=assembly.surfaces['Surf-film']
mdb.models['Model-1'].FilmCondition(name='Int-film', createStepName='Step-1', 
    surface=region, definition=EMBEDDED_COEFF, filmCoeff=2000, 
    filmCoeffAmplitude='', sinkTemperature=envTemperature, sinkAmplitude='', 
    sinkDistributionType=UNIFORM, sinkFieldName='')
region=assembly.surfaces['Surf-radiation']
mdb.models['Model-1'].RadiationToAmbient(name='Int-radiation', 
    createStepName='Step-1', surface=region, radiationType=AMBIENT, 
    distributionType=UNIFORM, field='', emissivity=0.85, 
    ambientTemperature=envTemperature, ambientTemperatureAmp='')
mdb.models['Model-1'].Temperature(name='temperature', createStepName='Initial', 
    region=assembly.sets['Set-1'], distributionType=UNIFORM, 
    crossSectionDistribution=CONSTANT_THROUGH_THICKNESS, magnitudes=(initTemperature, ))

# Body Force
for i in range(nlayer):
    mdb.models['Model-1'].BodyForce(name='pressure-t{:d}'.format(i+1), createStepName='Step-{:d}'.format(i+1), 
        region=assembly.instances['Part-1-1'].sets['Set-{:d}'.format(i+1)], comp2=0.1/dy, amplitude='Amp-2')

# Write Inputs
jobname = 'Job-AM-ModelChange-03'
mdb.Job(name=jobname, model='Model-1',  numCpus=4, numDomains=4, numGPUs=1000)
mdb.jobs[jobname].writeInput(consistencyChecking=OFF)

# mdb.saveAs( pathName='additive_manufacturing_Partition')