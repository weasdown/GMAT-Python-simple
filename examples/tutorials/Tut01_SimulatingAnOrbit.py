from __future__ import annotations
from load_gmat import gmat
import gmat_py_simple as gpy
import os

log_path = os.path.normpath(f'{os.getcwd()}/GMAT-Log.txt')
script_path = os.path.normpath(f'{os.getcwd()}/Tut01.script')
gmat.UseLogFile(log_path)

# TODO complete modelling the tutorial mission (inc. add drag, prop to Periapsis)

sat_params = {
    'Name': 'Sat',
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

sat = gpy.Spacecraft.from_dict(sat_params)
fm = gpy.ForceModel(name='LowEarthProp_ForceModel', point_masses=['Luna', 'Sun'], drag=gpy.ForceModel.DragForce(),
                    srp=True, gravity_field=gpy.ForceModel.GravityField(degree=10, order=10))
prop = gpy.PropSetup('DefaultProp', fm=fm)

print(f'Sat state before running: {sat.GetState()}')
print(f"Epoch before running: {sat.GetField('Epoch')}")

# Mission Command Sequence
mcs = [gpy.BeginMissionSequence(),
       gpy.Propagate('PropagateCommand', prop, sat)]

gpy.RunMission(mcs)  # Run the mission

print(f'Sat state after running: {sat.GetState()}')
print(f'Epoch after running: {sat.GetField("Epoch")}')

gmat.SaveScript(script_path)
