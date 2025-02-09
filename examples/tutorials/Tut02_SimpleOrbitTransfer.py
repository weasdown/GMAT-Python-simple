# Tutorial 02: Simple Orbit Transfer. Perform a Hohmann Transfer from Low Earth Orbit (LEO) to Geostationary orbit (GEO)
# Written by William Easdown Babb

from __future__ import annotations

# Assumes there is a config.py file in the same folder as this tutorial (see README.md).
# This is only needed if not using PyCharm's "Add content roots to PYTHONPATH" option in your run configuration.
from config import gmat

import gmat_py_simple as gpy
import os

log_path = os.path.normpath(f'{os.getcwd()}/examples/logs/GMAT-Tut02-Log.txt')
gmat.UseLogFile(log_path)
gmat.EchoLogFile(False)  # set to True to view log output in console (e.g. live iteration results)

sat = gpy.Spacecraft('DefaultSC')

prop = gpy.PropSetup('NonDefaultProp', gator=gpy.PropSetup.Propagator('RungeKutta89'),
                     accuracy=9.999999999999999e-12)

toi = gpy.ImpulsiveBurn('TOI')
goi = gpy.ImpulsiveBurn('GOI')

dc1 = gpy.DifferentialCorrector('DC1')

print(f'Sat state before running: {sat.GetState()}')
print(f"Epoch before running: {sat.GetField('Epoch')}")

# Targeting sequence to adjust parameters of the two burns (TOI and GOI) to achieve desired final orbit
tg1 = gpy.Target('Hohmann Transfer', dc1, exit_mode='SaveAndContinue', command_sequence=[
        # Vary the velocity of the TOI burn to achieve an apoapsis with RMAG = 42165 km
        gpy.Vary('Vary TOI', dc1, f'{toi.name}.Element1'),
        gpy.Maneuver('Perform TOI', toi, sat),
        gpy.Propagate('Prop To Apoapsis', sat, prop, f'{sat.name}.Earth.Apoapsis'),
        gpy.Achieve('Achieve RMAG = 42165', dc1, f'{sat.name}.Earth.RMAG', 42164.169, 0.1),

        # Vary the velocity of the GOI burn to achieve an eccentricity of 0.005
        gpy.Vary('Vary GOI', dc1, f'{goi.name}.Element1', max_step=0.2),
        gpy.Maneuver('Perform GOI', goi, sat),
        gpy.Achieve('Achieve ECC = 0.005', dc1, f'{sat.name}.Earth.ECC', 0.005, 0.0001)
    ])

# Mission Command Sequence
mcs = [
    gpy.Propagate('Prop To Periapsis', sat, prop, f'{sat.name}.Earth.Periapsis'),
    tg1,  # Target command and its command sequence
    gpy.Propagate('Prop One Day', sat, prop, (f'{sat.name}.ElapsedDays', 1))
]

gpy.RunMission(mcs)  # Run the mission

print(f'Sat state after running: {sat.GetState()}')
print(f'Epoch after running: {sat.GetField("Epoch")}')

script_path = os.path.normpath(f'{os.getcwd()}/examples/scripts/Tut02-SimpleOrbitTransfer.script')
gmat.SaveScript(script_path)
