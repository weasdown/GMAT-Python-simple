import gmat_py_simple.utils
from load_gmat import gmat

import gmat_py_simple as gpy
from gmat_py_simple import orbit as o
from gmat_py_simple.orbit import PropSetup
from gmat_py_simple.commands import Propagate

# TODO complete modelling the tutorial mission rather than the default one

sat_params = {
    'Name': 'DefaultSat',
    'Orbit': {
        'Epoch': '22 Jul 2014 11:29:10.811',
        'DateFormat': 'UTCGregorian',
        'CoordSys': 'EarthMJ2000Eq',
        'StateType': 'Keplerian',
        'SMA': 83474.31800000001,
        'ECC': 0.89652,
        'INC': 12.4606,
        'RAAN': 292.8362,
        'AOP': 218.9805,
        'TA': 180,
    },
}

# sat = gpy.Spacecraft.from_dict(sat_params)

# sat.Help()

# lep_fm = o.ForceModel(name='LowEarthProp_ForceModel',
#                       gravity_field=o.ForceModel.GravityField(
#                           degree=10,
#                           order=10,
#                       ),
#                       point_masses=['Luna', 'Sun'],
#                       drag=True,
#                       srp=True
#                       )

# lep_fm.Help()

# start_state = sat.GetKeplerianState()
# print(f'Start state: {start_state}')
#
# prop = PropSetup('Propagator', fm=lep_fm)
#
# gmat.Initialize()
#
# Propagate(prop, sat, ('ElapsedSecs', 60))
#
# end_state = sat.GetKeplerianState()
# print(f'End state: {end_state}')

# sat.Help()
# gator = prop.GetPropagator()
# print(f'gator: {gator}')
# print('gator Help:')
# gator.Help()

# propagate = gmat.Construct('Propagate')
# print(f'Propagate Generating String: {propagate.GetGeneratingString()}')

sc = gmat.Construct('Spacecraft', 'DefaultSC')

fm = gmat.Construct('ODEModel', 'GF&Sun')
fm.SetSolarSystem(gmat.GetSolarSystem())
grav = gmat.Construct('GravityField')
grav.SetField('BodyName', 'Earth')
grav.SetField('PotentialFile', 'JGM2.cof')

pm_sun = gmat.Construct('PointMassForce')
pm_sun.SetField('BodyName', 'Sun')
fm.AddForce(grav)
fm.AddForce(pm_sun)
fm.Help()

prop = gmat.Construct('PropSetup', 'prop')
prop.AddPropObject(sc)
prop.SetReference(fm)
prop.Help()

prop.PrepareInternals()
gator = prop.GetPropagator()
gmat.Initialize()

# gator = prop.GetPropagator()
# psm = prop.GetPropStateManager()
# psm.SetObject(sc)

# gmat.Initialize()
#
# fm = prop.GetODEModel()
# gator = prop.GetPropagator()
# psm.BuildState()
# fm.SetPropStateManager(psm)
# fm.SetState(psm.GetState())
# fm.Initialize()
# fm.BuildModelFromMap()
# fm.UpdateInitialData()
# prop.Initialize()
# gator.Initialize()

propagate = gmat.Construct('Propagate')
propagate.SetField('Propagator', gator.GetName())
# propagate.SetField('Spacecraft', sc.GetName())

propagate.SetObject(gator.GetName(), gmat.PROPAGATOR)
propagate.SetObject(sc.GetName(), gmat.SPACECRAFT)
propagate.SetObject(prop.GetName(), gmat.PROP_SETUP)

gmat.Initialize()

propagate.Help()

print(f'Prop status: {propagate.GetPropStatus()}')
print(propagate.RunComplete())

# propagate.Initialize()
# propagate.Execute()
# propagate.Help()
