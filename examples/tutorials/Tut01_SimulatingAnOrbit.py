from __future__ import annotations

from load_gmat import gmat
import load_gmat

import gmat_py_simple as gpy
# import gmat_py_simple.utils
# from gmat_py_simple import orbit as o
# from gmat_py_simple.orbit import PropSetup
# from gmat_py_simple.commands import Propagate

import os

log_path = os.path.normpath(f'{os.getcwd()}/GMAT-Log.txt')
gmat.UseLogFile(log_path)

script_path = os.path.normpath(f'{os.getcwd()}/Tut01.script')

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

sat = gpy.Spacecraft.from_dict(sat_params)

mod = gpy.Moderator()
sb = mod.GetSandbox()

vdator = gmat.Validator.Instance()
vdator.SetSolarSystem(gmat.GetSolarSystem())
vdator.SetObjectMap(mod.GetConfiguredObjectMap())

# Create a BeginMissionSequence command
bms = mod.CreateDefaultCommand('BeginMissionSequence')
sb.AddCommand(bms)
bms.SetObjectMap(sb.GetObjectMap())
bms.SetGlobalObjectMap(sb.GetGlobalObjectMap())
bms.SetSolarSystem(gmat.GetSolarSystem())

# Create a Propagator and Propagate Command
prop = gpy.PropSetup('DefaultProp')
pgate = gpy.Propagate('PropagateCommand', prop, sat)

# Commands must be validated before running, for some reason (TODO: determine why)
gmat.Moderator.Instance().ValidateCommand(bms)
gmat.Moderator.Instance().AppendCommand(bms)  # add BeginMissionSequence to Mission Command Sequence
pgate.TakeAction('PrepareToPropagate')

print(f'Sat state before running: {sat.GetState()}')
print(f"Epoch before running: {sat.GetField('Epoch')}")

# RUN MISSION #
run_mission_return_code = int(mod.RunMission())  # Run the mission
if run_mission_return_code != 1:
    raise Exception(f'RunMission did not complete successfully - returned code {run_mission_return_code}')
else:
    print(f'\nRunMission succeeded!\n')
    sat.was_propagated = True  # mark sat as propagated so GetState gets runtime values

print(f'Sat state after running: {sat.GetState()}')
print(f'Epoch after running: {sat.GetField("Epoch")}')

gmat.SaveScript(script_path)
