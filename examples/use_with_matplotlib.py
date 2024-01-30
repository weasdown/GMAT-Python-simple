# Example showing how the gmat_py_simple wrapper can be used with matplotlib
# Written by William Easdown Babb

from __future__ import annotations

from load_gmat import gmat
import gmat_py_simple as gpy
import os

gmat.Clear()

# Debug options - TODO remove
gmat_global = gmat.GmatGlobal.Instance()
# gmat_global.SetMissionTreeDebug(True)

# writes param info to log
# e.g. "18  ECC                        Spacecraft     Origin                                Y  Y  Y  Eccentricity"
gmat_global.SetWriteParameterInfo(True)
gmat_global.SetWriteFilePathInfo(False)
gmat_global.SetCommandEchoMode(True)  # enables "CurrentCommand: [command generating string]" print out in log

# Set log and script options
log_path = os.path.normpath(f'{os.getcwd()}/GMAT-Log.txt')
script_path = os.path.normpath(f'{os.getcwd()}/matplotlib_example.script')
gmat.UseLogFile(log_path)
echo_log = False
if echo_log:
    gmat.EchoLogFile()
    print('Echoing GMAT log file to terminal\n')

sat_params = {
    'Name': 'Sat',
    'Orbit': {
        # TODO: uncomment defaults and remove debugging values once working
        # 'Epoch': '22 Jul 2014 11:29:10.811',
        # 'DateFormat': 'UTCGregorian',
        'Epoch': '01 Jan 2000 12:00:00.000',  # debugging
        'DateFormat': 'A1Gregorian',  # debugging

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

# toi = gpy.ImpulsiveBurn('IB1', sat.GetCoordinateSystem(), [0.2, 0, 0])

# Mission commands
# # prop1 = gpy.Propagate('Prop 60 s', prop, sat, ('Sat.ElapsedSecs', 60))
# man1 = gpy.Maneuver('Maneuver1', toi, sat)
# # prop2 = gpy.Propagate('Prop One Day', prop, sat, ('Sat.ElapsedDays', 1))
# # prop3 = gpy.Propagate('Prop To Apoapsis', prop, sat, 'Sat.Earth.Apoapsis')

# gmat.ShowObjects()

for t in range(10, 120, 10):
    print(f'Sat state before running: {sat.GetState()}')
    print(f'Epoch before running: {sat.GetEpoch()}')

    # Mission Command Sequence
    mcs = [
        gpy.Propagate('Prop 60 s', prop, sat, ('Sat.ElapsedSecs', t)),
        # gpy.Maneuver('Maneuver1', toi, sat),
        # gpy.Propagate('Prop One Day', prop, sat, ('Sat.ElapsedDays', 1)),
        # gpy.Propagate('Prop To Apoapsis', prop, sat, 'Sat.Earth.Apoapsis'),

        # # prop1,  # propagate by 60 seconds
        # man1,  # 0.2 km/s maneuver
        # # prop2,  # propagate by one day (TODO make comment accurate)
        # # prop3  # propagate to periapsis
    ]

    gpy.RunMission(mcs)  # Run the mission

    new_state = sat.GetState()
    new_epoch = sat.GetEpoch()
    print(f'Sat state after running for {t} s: {new_state}')
    print(f'Epoch after running for {t} s: {new_epoch}')

# gmat.SaveScript(script_path)
