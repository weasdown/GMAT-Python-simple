# Tutorial 02: Simple Orbit Transfer. Perform a Hohmann Transfer from Low Earth Orbit (LEO) to Geostationary orbit (GEO)
# Written by William Easdown Babb

from __future__ import annotations
from load_gmat import gmat
import gmat_py_simple as gpy
import os

log_path = os.path.normpath(f'{os.getcwd()}/examples/logs/GMAT-Tut02-Log.txt')
gmat.UseLogFile(log_path)
gmat.EchoLogFile(False)  # set to True to view log output in console (e.g. live iteration results)

sat_params = {
    'Name': 'DefaultSC',
    'DisplayStateType': 'Keplerian',
    'DateFormat': 'UTCGregorian',
    'Hardware': {'Tanks': {'chemical': [{'Name': 'ChemicalTank1'}],
                           'electric': [{'Name': 'ElectricTank1'}]},
                 'Thrusters': {'chemical': [{'Name': 'ChemicalThruster1', 'Tanks': 'ChemicalTank1'}],
                               'electric': [{'Name': 'ElectricThruster1', 'Tanks': 'ElectricTank1'}]},
                 'SolarPowerSystem': {'Name': 'SolarPowerSystem1'},
                 }
}
sat = gpy.Spacecraft.from_dict(sat_params)

prop = gpy.PropSetup('DefaultProp', gator=gpy.PropSetup.Propagator('RungeKutta89'),
                     accuracy=9.999999999999999e-12)

fb1 = gpy.FiniteBurn('FiniteBurn1', sat.thrusters.electric[0])

print(f'Sat state before running: {sat.GetState()}')
print(f"Epoch before running: {sat.GetEpoch()}")

# Mission Command Sequence
mcs = [
    gpy.BeginFiniteBurn(fb1, sat, 'Turn Thruster On'),
    gpy.Propagate('Prop 10 days', sat, prop, (f'{sat.name}.ElapsedDays', 10)),
    gpy.EndFiniteBurn(fb1, 'Turn Thruster Off'),
]

gpy.RunMission(mcs)  # Run the mission

print(f'Sat state after running: {sat.GetState()}')
print(f'Epoch after running: {sat.GetField("Epoch")}')

script_path = os.path.normpath(f'{os.getcwd()}/examples/scripts/Tut02-SimpleOrbitTransfer.script')
gmat.SaveScript(script_path)
