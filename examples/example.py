# Tutorial 02: Simple Orbit Transfer. Perform a Hohmann Transfer from Low Earth Orbit (LEO) to Geostationary orbit (GEO)

from __future__ import annotations
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

# fm = gpy.ForceModel(name='LowEarthProp_ForceModel', point_masses=['Luna', 'Sun'], drag=gpy.ForceModel.DragForce(),
#                     srp=True, gravity_field=gpy.ForceModel.GravityField(degree=10, order=10))
# prop = gpy.PropSetup('LowEarthProp', accuracy=9.999999999999999e-12,
#                      gator=gpy.PropSetup.Propagator(name='LowEarthProp', integrator='RungeKutta89'))
prop = gpy.PropSetup('LowEarthProp')

toi = gpy.ImpulsiveBurn('IB1', sat.GetCoordinateSystem(), [0.2, 0, 0])

print(f'Sat state before running: {sat.GetState()}')
print(f"Epoch before running: {sat.GetField('Epoch')}")

# Mission Command Sequence
mcs = [
    # gpy.Propagate('Prop One Day', prop, sat, ('Sat.ElapsedSecs', 60)),
    # gpy.Maneuver('Maneuver1', toi, sat),  # TODO bugfix: Maneuver command causing infinite run
    # TODO bugfix: crash with second Propagate - StopCondition name being double-used?
    # gpy.Propagate('Prop Another Day', prop, sat, ('Sat.ElapsedSecs', 120))
]

stop_cond = gpy.Moderator().CreateDefaultStopCondition()
stop_cond.Help()
gmat.ShowObjects()

mj = gpy.GetObject('Sat.A1ModJulian')
es = gpy.GetObject('Sat.ElapsedSecs')

mod = gpy.Moderator()
sb = gpy.Sandbox()
sb.AddObject(mj)
sb.AddObject(es)

print(gpy.GetTypeNameFromID(116))

gmat.Initialize()

mj.Help()
es.Help()

sc60 = gpy.GetObject('Goal=60')
sc60.Help()

gpy.RunMission(mcs)  # Run the mission

print(f'Sat state after running: {sat.GetState()}')
print(f'Epoch after running: {sat.GetField("Epoch")}')

gmat.SaveScript(script_path)
