# Tutorial 02: Simple Orbit Transfer. Perform a Hohmann Transfer from Low Earth Orbit (LEO) to Geostationary orbit (GEO)

from __future__ import annotations
from load_gmat import gmat
import gmat_py_simple as gpy
import os

log_path = os.path.normpath(f'{os.getcwd()}/examples/logs/GMAT-Tut02-Log.txt')
gmat.UseLogFile(log_path)
gmat.EchoLogFile(True)
gmat_global = gmat.GmatGlobal.Instance()
gmat_global.EchoCommands()

# TODO: change parameters and commands from Tut01 to Tut02

sat = gpy.Spacecraft('TestSC')
prop = gpy.PropSetup('DefaultProp', gator=gpy.PropSetup.Propagator('RungeKutta89'))

local_coordsys = gpy.OrbitState.CoordinateSystem('Local', axes='VNB')  # FIXME
toi = gpy.ImpulsiveBurn('TOI', local_coordsys, [0, 0, 0])
goi = gpy.ImpulsiveBurn('GOI', local_coordsys, [0, 0, 0])

pgate_peri = gpy.Propagate('Prop To Periapsis', sat, prop, f'{sat.name}.Earth.Periapsis')
pgate_apo = gpy.Propagate('Prop To Apoapsis', sat, prop, f'{sat.name}.Earth.Apoapsis')
pgate_1d = gpy.Propagate('Prop One Day', sat, prop, (f'{sat.name}.ElapsedSecs', 86400))

# (TODO check whether still accurate) Creation of DifferentialCorrector objects *must* be after creation of Propagates
dc1 = gpy.DifferentialCorrector('TestDiffCorr')

print(f"\nVariables after DC1 creation: {dc1.GetStringArrayParameter('Variables')}")
print(f"Goals after DC1 creation: {dc1.GetStringArrayParameter('Goals')}\n")

targ1 = gpy.Target('Hohmann Transfer', dc1, command_sequence=[
    # TODO in Vary, if setting DC variables/goals, check whether Vary is first in Target sequence. If so,
    #  delete existing (placeholder) entries in DC Variables/Goals
    gpy.Vary('Vary TOI', dc1, f'{toi.name}.Element1'),
    gpy.Maneuver('Perform TOI', toi, sat),
    pgate_apo,
    gpy.Achieve('Achieve RMAG = 42165', dc1, f'{sat.name}.Earth.RMAG', 42164.169, 0.1),
    gpy.Vary('Vary GOI', dc1, f'{goi.name}.Element1'),
    gpy.Maneuver('Perform GOI', goi, sat),
    gpy.Achieve('Achieve ECC = 0.005', dc1, f'{sat.name}.Earth.ECC', 0.005, 0.0001),
    # gpy.EndTarget('End Hohmann Transfer')
])

print(f"\nVariables after Target (and subs) creation: {dc1.GetStringArrayParameter('Variables')}")
print(f"Goals after Target (and subs) creation: {dc1.GetStringArrayParameter('Goals')}\n")

print(f'Sat state before running: {sat.GetState()}')
print(f"Epoch before running: {sat.GetField('Epoch')}")

# Mission Command Sequence
mcs = [
    # gpy.BeginMissionSequence(),
    pgate_peri,
    targ1,
    # gpy.EndTarget(targ1),
    pgate_1d
]

# sat.Help()

gpy.RunMission(mcs)  # Run the mission

print('\nExited RunMission\n')

print(f'Sat state after running: {sat.GetState()}')
print(f'Epoch after running: {sat.GetField("Epoch")}')

script_path = os.path.normpath(f'{os.getcwd()}/examples/scripts/Tut02-SimpleOrbitTransfer.script')
gmat.SaveScript(script_path)

# toi.Help()
# goi.Help()
