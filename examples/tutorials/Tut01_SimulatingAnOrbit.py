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
        'SMA': 83474.31800000004,
        'ECC': 0.8965199999999998,
        'INC': 12.4606,
        'RAAN': 292.8362,
        'AOP': 218.9805,
        'TA': 180,
    },
}

# sat = gpy.Spacecraft.from_dict(sat_params)
sat = gpy.Spacecraft('Sat')

mod = gpy.Moderator()
sb = gpy.Sandbox()

bms = gpy.BeginMissionSequence()
# Create a Propagator and Propagate Command
prop = gpy.PropSetup('DefaultProp')
pgate = gpy.Propagate('PropagateCommand', prop, sat)

print(f'Sat state before running: {sat.GetState()}')
print(f"Epoch before running: {sat.GetField('Epoch')}")

# RUN MISSION #
mcs = [gpy.BeginMissionSequence(), pgate]  # Mission Command Sequence
run_mission_return_code = int(mod.RunMission(mcs))  # Run the mission
if run_mission_return_code != 1:
    raise Exception(f'RunMission did not complete successfully - returned code {run_mission_return_code}')
else:
    print(f'\nRunMission succeeded!\n')
    sat.was_propagated = True  # mark sat as propagated so GetState gets runtime values

print(f'Sat state after running: {sat.GetState()}')
print(f'Epoch after running: {sat.GetField("Epoch")}')

gmat.SaveScript(script_path)
