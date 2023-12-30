# Tutorial 02: Simple Orbit Transfer. Perform a Hohmann Transfer from Low Earth Orbit (LEO) to Geostationary orbit (GEO)

from __future__ import annotations

from datetime import datetime

from load_gmat import gmat
import gmat_py_simple as gpy
import os

log_path = os.path.normpath(f'{os.getcwd()}/GMAT-Log.txt')
script_path = os.path.normpath(f'{os.getcwd()}/Tut01.script')
gmat.UseLogFile(log_path)

# TODO: change parameters and commands from Tut01 to Tut02
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
# sat = gpy.Spacecraft('Sat')
# sat.SetField('DateFormat', 'A1Gregorian')
# sat.SetField('Epoch', '01 Jan 2000 12:00:00.000')

# fm = gpy.ForceModel(name='LowEarthProp_ForceModel', point_masses=['Luna', 'Sun'], drag=gpy.ForceModel.DragForce(),
#                     srp=True, gravity_field=gpy.ForceModel.GravityField(degree=10, order=10))
# prop = gpy.PropSetup('LowEarthProp', accuracy=9.999999999999999e-12,
#                      gator=gpy.PropSetup.Propagator(name='LowEarthProp', integrator='RungeKutta89'))
prop = gpy.PropSetup('LowEarthProp')

toi = gpy.ImpulsiveBurn('IB1', sat.GetCoordinateSystem(), [0.2, 0, 0])

print(f'Sat state before running: {sat.GetState()}')

start_epoch = sat.GetEpoch()
print(f'Epoch before running: {start_epoch}')
start_epoch_datetime = sat.GetEpoch(as_datetime=True)

prop1 = gpy.Propagate('Prop One Day', prop, sat, ('Sat.ElapsedSecs', 60))

# TODO bugfix: Maneuver command causing crash in RunMission/for loop/mod.AppendCommand()
# man1 = gpy.Maneuver('Maneuver1', toi, sat)

# TODO bugfix: crash with second Propagate - StopCondition name being double-used?
#  Note: LoadScript shows single Sat.ElapsedSecs even if multiple ElapsedSecs Propagate commands in script
prop2 = gpy.Propagate('Prop Another Day', prop, sat, ('Sat.ElapsedSecs', 120))

# Mission Command Sequence
mcs = [
    prop1,
    # man1,
    prop2
]

gpy.RunMission(mcs)  # Run the mission

print(f'Sat state after running: {sat.GetState()}')
end_epoch = sat.GetEpoch()
print(f'Epoch after running: {end_epoch}')
end_epoch_datetime = sat.GetEpoch(as_datetime=True)

prop1_stop_goal = prop1.stop_cond.GetStopGoal()
prop2_stop_goal = prop2.stop_cond.GetStopGoal()
print(f'prop1 stop goal: {prop1_stop_goal}s')
print(f'prop2 stop goal: {prop2_stop_goal}s')

epoch_delta = end_epoch_datetime - start_epoch_datetime
print(f'Epoch difference: {epoch_delta}')
stop_goal_total = prop1_stop_goal + prop2_stop_goal

print(f'Match? {epoch_delta.total_seconds()} epoch_delta vs {stop_goal_total} stop_goal_total')

gmat.SaveScript(script_path)
