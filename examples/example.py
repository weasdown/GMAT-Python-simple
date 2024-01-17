# General wrapper example. Written by William Easdown Babb

from __future__ import annotations
import os

from load_gmat import gmat
import gmat_py_simple as gpy

# Set log and script options
log_path = os.path.normpath(f'{os.getcwd()}/GMAT-Log-example.txt')
gmat.UseLogFile(log_path)  # tell GMAT to log to the path previously declared
echo_log = False
if echo_log:
    gmat.EchoLogFile()
    print('Echoing GMAT log file to terminal\n')

# Build a Spacecraft from a dictionary of parameters
sat_params = {
    'Name': 'ExampleSat',
    'Orbit': {
        'Epoch': '01 Jan 2000 12:00:00.000',
        'DateFormat': 'UTCGregorian',
        'CoordSys': 'EarthMJ2000Eq',
        'DisplayStateType': 'Keplerian',
        'SMA': 83474.318,
        'ECC': 0.89652,
        'INC': 12.4606,
        'RAAN': 292.8362,
        'AOP': 218.9805,
        'TA': 181,
    },
}
sat = gpy.Spacecraft.from_dict(sat_params)

# Build a ForceModel and Propagator that will be used within Propagate commands
fm = gpy.ForceModel(name='LowEarthProp_ForceModel', point_masses=['Luna', 'Sun'], drag=gpy.ForceModel.DragForce(),
                    srp=True, gravity_field=gpy.ForceModel.GravityField(degree=10, order=10))
prop = gpy.PropSetup('LowEarthProp', fm=fm, accuracy=9.999999999999999e-12,
                     gator=gpy.PropSetup.Propagator(name='LowEarthProp', integrator='RungeKutta89'))

# Build an ImpulsiveBurn that will be used in the Maneuver command
toi = gpy.ImpulsiveBurn('IB1', sat.GetCoordinateSystem(), [0.2, 0, 0])

# StopConditions for use in Propagate commands
secs_60 = (f'{sat.name}.ElapsedSecs', 60)
days_1 = (f'{sat.name}.ElapsedDays', 1)
earth_apo = f'{sat.name}.Earth.Apoapsis'
earth_peri = f'{sat.name}.Earth.Periapsis'

print(f'Sat state before running: {sat.GetState()}')
print(f'Epoch before running: {sat.GetEpoch()}')

# Mission Command Sequence
mcs = [
    gpy.Propagate('Prop One Day', sat, prop, days_1),
    gpy.Propagate('Prop 60 s', sat, prop, secs_60),
    gpy.Maneuver('0.2km/s Maneuver', toi, sat),
    gpy.Propagate('Prop Another One Day', sat, prop, days_1),
    gpy.Propagate('Prop To Apoapsis', sat, prop, earth_apo),
]

gpy.RunMission(mcs)  # Run the mission

print(f'Sat state after running: {sat.GetState()}')
print(f'Epoch after running: {sat.GetEpoch()}')

script_path = os.path.normpath(f'{os.getcwd()}/examples/scripts/example.script')  # path for saved script
gmat.SaveScript(script_path)
