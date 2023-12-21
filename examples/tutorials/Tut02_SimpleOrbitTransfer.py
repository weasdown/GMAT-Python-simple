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

toi = gpy.ImpulsiveBurn()

print(f'Sat state before running: {sat.GetState()}')
print(f"Epoch before running: {sat.GetField('Epoch')}")

# Mission Command Sequence
mcs = [gpy.BeginMissionSequence(),
       gpy.Propagate('Prop To Periapsis', prop, sat, 'Sat.Earth.Periapsis'),
       gpy.Target('', 'DC1', command_sequence=[
           gpy.Vary('Vary TOI'),
           gpy.Maneuver('Perform TOI'),
           gpy.Propagate('Prop To Apoapsis', prop, sat, 'Sat.Earth.Apoapsis'),
           gpy.Achieve('Achieve RMAG = 42165'),
           gpy.Vary('Vary GOI'),
           gpy.Maneuver('Perform GOI'),
           gpy.Achieve('Achieve ECC = 0.05'),
           gpy.EndTarget('End Hohmann Transfer')
       ]),
       gpy.Propagate('Prop One Day', prop, sat, ('Sat.ElapsedSecs', 86400)),
       ]

gpy.RunMission(mcs)  # Run the mission

print(f'Sat state after running: {sat.GetState()}')
print(f'Epoch after running: {sat.GetField("Epoch")}')

gmat.SaveScript(script_path)
