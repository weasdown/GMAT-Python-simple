# Tutorial 02: Simple Orbit Transfer. Perform a Hohmann Transfer from Low Earth Orbit (LEO) to Geostationary orbit (GEO)
# Written by William Easdown Babb

from __future__ import annotations
from load_gmat import gmat
import gmat_py_simple as gpy
import os

log_path = os.path.normpath(f'{os.getcwd()}/examples/logs/GMAT-Tut02-Log.txt')
gmat.UseLogFile(log_path)
gmat.EchoLogFile(False)  # set to True to view log output in console (e.g. live iteration results)

sat = gpy.Spacecraft('DefaultSC')

# sat_params = {
#     'Name': 'DefaultSC',
#     'Orbit': {
#         'CoordSys': 'EarthMJ2000Eq',
#         'Epoch': '21545',
#         'StateType': 'Keplerian',
#         'SMA': 7200
#     },
#     'DryMass': 100,  # kg
#     'Hardware': {'Tanks': {'Chemical': [{'Name': 'ChemicalTank1'}],
#                            'Electric': [{'Name': 'ElectricTank1'}]},
#                  'Thrusters': {'Chemical': [{'Name': 'ChemicalThruster1', 'Tanks': 'ChemicalTank1'}],
#                                'Electric': [{'Name': 'ElectricThruster1', 'Tanks': 'ElectricTank1'}]}
#                  }
# }
# test_sat = gpy.Spacecraft.from_dict(sat_params)

prop = gpy.PropSetup('DefaultProp', gator=gpy.PropSetup.Propagator('RungeKutta89'),
                     accuracy=9.999999999999999e-12)

toi = gpy.ImpulsiveBurn('TOI')
goi = gpy.ImpulsiveBurn('GOI')

dc1 = gpy.DifferentialCorrector('DC1')

print(f'Sat state before running: {sat.GetState()}')
print(f"Epoch before running: {sat.GetField('Epoch')}")

# Targeting sequence to adjust parameters of the two burns (TOI and GOI) to achieve desired final orbit
tg1 = gpy.Target('Hohmann Transfer', dc1, exit_mode='SaveAndContinue', command_sequence=[
        # Vary the velocity of the TOI burn to achieve an apoapsis with RMAG = 42165 km
        gpy.Vary('Vary TOI', dc1, f'{toi.name}.Element1'),
        gpy.Maneuver('Perform TOI', toi, sat),
        gpy.Propagate('Prop To Apoapsis', sat, prop, f'{sat.name}.Earth.Apoapsis'),
        gpy.Achieve('Achieve RMAG = 42165', dc1, f'{sat.name}.Earth.RMAG', 42164.169, 0.1),

        # Vary the velocity of the GOI burn to achieve an eccentricity of 0.005
        gpy.Vary('Vary GOI', dc1, f'{goi.name}.Element1', max_step=0.2),
        gpy.Maneuver('Perform GOI', goi, sat),
        gpy.Achieve('Achieve ECC = 0.005', dc1, f'{sat.name}.Earth.ECC', 0.005, 0.0001)
    ])

# Mission Command Sequence
mcs = [
    gpy.Propagate('Prop To Periapsis', sat, prop, f'{sat.name}.Earth.Periapsis'),
    tg1,  # Target command and its command sequence
    gpy.Propagate('Prop One Day', sat, prop, (f'{sat.name}.ElapsedDays', 1))
]

gpy.RunMission(mcs)  # Run the mission

print(f'Sat state after running: {sat.GetState()}')
print(f'Epoch after running: {sat.GetField("Epoch")}')

script_path = os.path.normpath(f'{os.getcwd()}/examples/scripts/Tut02-SimpleOrbitTransfer.script')
gmat.SaveScript(script_path)

# print(test_sat.thrusters)
# fb1 = gpy.FiniteBurn('FB1', test_sat.thrusters.Electric[0])
# fb1.Help()
