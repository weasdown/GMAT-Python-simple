# import sys
#
from load_gmat import gmat

import gmat_py_simple as gpy

# sat_params = {
#     'Name': 'DefaultSC',
#     'Orbit': {
#         'CoordSys': 'EarthMJ2000Eq',
#         'Epoch': '21545',
#         'StateType': 'Keplerian',
#         'SMA': 7178
#     },
#     'DryMass': 100,  # kg
#     'Hardware': {'Tanks': {'Chemical': [{'Name': 'ChemicalTank1'}],
#                            'Electric': [{'Name': 'ElectricTank1'}]},
#                  'Thrusters': {'Chemical': [{'Name': 'ChemicalThruster1', 'Tanks': 'ChemicalTank1'}],
#                                'Electric': [{'Name': 'ElectricThruster1', 'Tanks': 'ElectricTank1'}]}
#                  }
# }
#
# sat = gpy.Spacecraft.from_dict(sat_params)
# default_prop = gpy.PropSetup('DefaultProp', gator=gpy.PropSetup.Propagator('RungeKutta89'))
#
# sat.Help()
#
# print(f'sat start state: {sat.GetKeplerianState()}')
#
# gpy.Propagate(default_prop, sat, 'ElapsedSecs', 12000)
#
# print(f'sat end state: {sat.GetKeplerianState()}')

# stco = gmat.Construct('StopCondition', 'StCo1')
# # stco_fields = ['Covariance', 'BaseEpoch', 'Epoch', 'EpochVar', 'StopVar', 'Goal', 'Repeat']
#
# # stco.SetField('Epoch', 21550)
# # stco.SetField('EpochVar', '21550')
# stco.SetLhsString('ElapsedSecs')
# stco.SetRhsString('12000')
#
# print(stco.GetStopParameter())
# # stco.SetField('Goal', '12000')
#
# # gmat.Initialize()
# stco.Help()
#
# pdprop = gmat.Construct('Propagator', 'PDPROP')  # PropSetup
# pdprop.Help()
#
# print(gpy.utils.gmat_obj_field_list(stco))
# print(f'stco field: {stco.GetField("StopVar")}')
#
# cs = gpy.orbit.OrbitState.CoordinateSystem('CS')
# cs.Help()

sat = gmat.Construct('Spacecraft', 'Sat')

fm = gmat.Construct('ODEModel', 'FM')
earthgrav = gmat.Construct('GravityField')
earthgrav.SetField('BodyName', 'Earth')
earthgrav.SetField('Degree', 8)
earthgrav.SetField('Order', 8)
earthgrav.SetField('PotentialFile', 'JGM2.cof')
fm.AddForce(earthgrav)

prop = gmat.Construct('Propagator', 'Prop')
gator = gmat.Construct('PrinceDormand78', 'Gator')
prop.SetReference(gator)
prop.SetReference(fm)
psm = prop.GetPropStateManager()
psm.SetObject(sat)

gmat.Initialize()

fm = prop.GetODEModel()
gator = prop.GetPropagator()

psm.BuildState()

fm.SetPropStateManager(psm)
fm.SetState(psm.GetState())

fm.Initialize()

fm.BuildModelFromMap()
fm.UpdateInitialData()

prop.Initialize()
gator.Initialize()

gmat.Initialize()

prop.AddPropObject(sat)
prop.PrepareInternals()

fm = prop.GetODEModel()
gator = prop.GetPropagator()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# gmat.BeginMissionSequence()

stop_cond = gmat.Construct('StopCondition', 'StopCond')
stop_cond.SetLhsString('Sat.ElapsedSecs')
stop_cond.SetRhsString('8640.0')

propagate = gmat.Construct('Propagate')
propagate.SetField('Propagator', 'Prop')
# propagate.SetField('Spacecraft', 'Sat')

print(propagate.SetObject('Sat', gmat.SPACECRAFT))
print(propagate.SetObject('Prop', gmat.PROP_SETUP))
print(propagate.SetObject('StopCond', gmat.STOP_CONDITION))

# propagate.SetObjectMap(())

propagate.Validate()

propagate.Initialize()

# print(propagate.GetObjectMap())
# print(propagate.GetObjectList())
# print(propagate.SetCondition('Sat.ElapsedSecs', '=', '8640.0'))

# print(propagate.GetCurrentFunction())

# propagate.SetObject(gmat.SPACECRAFT, sat.GetName())

# propagate.Initialize()

propagate.Help()

# propagate.Execute()
