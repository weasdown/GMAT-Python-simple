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

stco = gmat.Construct('StopCondition', 'StCo1')
# stco_fields = ['Covariance', 'BaseEpoch', 'Epoch', 'EpochVar', 'StopVar', 'Goal', 'Repeat']

# stco.SetField('Epoch', 21550)
# stco.SetField('EpochVar', '21550')
stco.SetLhsString('ElapsedSecs')
stco.SetRhsString('12000')

print(stco.GetStopParameter())
# stco.SetField('Goal', '12000')

# gmat.Initialize()
stco.Help()

pdprop = gmat.Construct('Propagator', 'PDPROP')  # PropSetup
pdprop.Help()
