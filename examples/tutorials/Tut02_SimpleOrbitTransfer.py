# Tutorial 02: Simple Orbit Transfer. Perform a Hohmann Transfer from Low Earth Orbit (LEO) to Geostationary orbit (GEO)

from __future__ import annotations
from load_gmat import gmat
import gmat_py_simple as gpy
import os

log_path = os.path.normpath(f'{os.getcwd()}/GMAT-Log.txt')
script_path = os.path.normpath(f'{os.getcwd()}/Tut01.script')
gmat.UseLogFile(log_path)

# TODO: change parameters and commands from Tut01 to Tut02

sat = gpy.Spacecraft('DefaultSC')
prop = gpy.PropSetup('DefaultProp')
toi = gpy.ImpulsiveBurn('TOI', sat.GetCoordinateSystem(), [0, 0, 0])
dc1 = gpy.DifferentialCorrector('DC1')
goi = gpy.ImpulsiveBurn('GOI', sat.GetCoordinateSystem(), [0, 0, 0])

# gmat.Initialize()  # initialize GMAT so objects are in place for use in command sequence

print(f'Sat state before running: {sat.GetState()}')
print(f"Epoch before running: {sat.GetField('Epoch')}")

# Mission Command Sequence
mcs = [gpy.BeginMissionSequence(),
       gpy.Propagate('Prop To Periapsis', prop, sat, 'Sat.Earth.Periapsis'),
       gpy.Target('', 'DC1', command_sequence=[
           gpy.Vary('Vary TOI', 'DC1', 'TOI.Element1'),
           gpy.Maneuver('Perform TOI', toi, sat),
           gpy.Propagate('Prop To Apoapsis', prop, sat, 'Sat.Earth.Apoapsis'),
           gpy.Achieve('Achieve RMAG = 42165', dc1, 'Sat.Earth.RMAG', 42164.169, 0.1),
           gpy.Vary('Vary GOI', 'DC1', 'GOI.Element1'),  # TODO
           gpy.Maneuver('Perform GOI', goi, sat),
           gpy.Achieve('Achieve ECC = 0.005', dc1, 'Sat.Earth.ECC', 0.005, 0.0001),
           gpy.EndTarget('End Hohmann Transfer')
       ]),
       gpy.Propagate('Prop One Day', prop, sat, ('Sat.ElapsedSecs', 86400)),
       ]

gpy.RunMission(mcs)  # Run the mission

print(f'Sat state after running: {sat.GetState()}')
print(f'Epoch after running: {sat.GetField("Epoch")}')

gmat.SaveScript(script_path)
