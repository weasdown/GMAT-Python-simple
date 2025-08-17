# Tutorial 01: Simulating an Orbit. # Propagate a spacecraft in Earth orbit to its periapsis
# Written by William Easdown Babb

from __future__ import annotations

import os

import gmat_py_simple as gpy
from gmat_py_simple import gmat

log_path = os.path.normpath(f'{os.getcwd()}/GMAT-Log.txt')
gmat.UseLogFile(log_path)
echo_log = False
if echo_log:
    gmat.EchoLogFile()
    print('Echoing GMAT log file to terminal\n')

sat_params = {
    'Name': 'Sat',
    'Orbit': {
        'Epoch': '22 Jul 2014 11:29:10.811',
        'DateFormat': 'UTCGregorian',
        'CoordSys': 'EarthMJ2000Eq',
        'DisplayStateType': 'Keplerian',
        'SMA': 83474.318,
        'ECC': 0.89652,
        'INC': 12.4606,
        'RAAN': 292.8362,
        'AOP': 218.9805,
        'TA': 180,
    },
}

sat = gpy.Spacecraft.from_dict(sat_params)

fm = gpy.ForceModel(name='LowEarthProp_ForceModel', point_masses=['Luna', 'Sun'], drag=gpy.ForceModel.DragForce(),
                    srp=True, gravity_field=gpy.ForceModel.GravityField(degree=10, order=10))
prop = gpy.PropSetup('LowEarthProp', fm=fm, accuracy=9.999999999999999e-12,
                     gator=gpy.PropSetup.Propagator(name='LowEarthProp', integrator='RungeKutta89'))

print(f'\nSat state before running: {sat.GetState()}')
print(f"Epoch before running: {sat.GetEpoch()}")

# Mission Command Sequence
mcs = [gpy.BeginMissionSequence(),
       gpy.Propagate('Prop To Periapsis', sat, prop, f'{sat.name}.Earth.Periapsis')]

gpy.RunMission(mcs)  # Run the mission

print(f'Sat state after running: {sat.GetState()}')
print(f'Epoch after running: {sat.GetEpoch()}')

script_path = os.path.normpath(f'{os.getcwd()}/Tut01.script')
gmat.SaveScript(script_path)
