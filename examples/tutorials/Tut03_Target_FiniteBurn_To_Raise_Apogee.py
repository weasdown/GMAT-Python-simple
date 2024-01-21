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
    'Hardware': {'Tanks': {'chemical': [{'Name': 'ChemicalTank1'}], },
                 'Thrusters': {'chemical': [{'Name': 'ChemicalThruster1', 'Tanks': 'ChemicalTank1'}]}
                 }
}
sat = gpy.Spacecraft.from_dict(sat_params)

prop = gpy.PropSetup('DefaultProp', gator=gpy.PropSetup.Propagator('RungeKutta89'),
                     accuracy=9.999999999999999e-12)

burn_dur = gpy.Variable('BurnDuration')

fb1 = gpy.FiniteBurn('FiniteBurn1', sat.thrusters.chemical[0])

# ib = gpy.ImpulsiveBurn('DefaultIB')

dc1 = gpy.DifferentialCorrector('DC1')

print(f'Sat state before running: {sat.GetState()}')
print(f"Epoch before running: {sat.GetField('Epoch')}")

# Mission Command Sequence
mcs = [
    gpy.Propagate('Prop To Periapsis', sat, prop, f'{sat.name}.Earth.Periapsis'),
    # Targeting sequence to adjust burn duration to achieve desired final orbit
    gpy.Target('Raise Apoapsis', dc1, exit_mode='SaveAndContinue', command_sequence=[
        # Vary the FiniteBurn duration to achieve an apoapsis with RMAG = 12000 km
        gpy.Vary('Vary Burn Duration', dc1, burn_dur.name),
        gpy.BeginFiniteBurn(fb1, sat, 'Turn Thruster On'),
        gpy.Propagate('Prop BurnDuration', sat, prop, (f'{sat.name}.ElapsedSecs', burn_dur.name)),
        gpy.EndFiniteBurn(fb1, 'Turn Thruster Off'),
        gpy.Propagate('Prop To Apogee', sat, prop, f'{sat.name}.Earth.Apoapsis'),
        gpy.Achieve('Achieve Apogee Radius = 12000', dc1, f'{sat.name}.Earth.RMAG', 12000)
    ])
]

gmat.ShowObjects()

gpy.RunMission(mcs)  # Run the mission

print(f'Sat state after running: {sat.GetState()}')
print(f'Epoch after running: {sat.GetField("Epoch")}')

script_path = os.path.normpath(f'{os.getcwd()}/examples/scripts/Tut02-SimpleOrbitTransfer.script')
gmat.SaveScript(script_path)
