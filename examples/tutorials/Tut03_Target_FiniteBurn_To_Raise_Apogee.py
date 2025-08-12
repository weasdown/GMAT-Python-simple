# Tutorial 03: Target FiniteBurn to raise apoapsis.
# Iterate a FiniteBurn's duration to achieve a desired final apoapsis altitude
# Written by William Easdown Babb

from __future__ import annotations
from load_gmat import gmat
import gmat_py_simple as gpy
import os

# # Uncomment to enable logging
# log_path = os.path.normpath(f'{os.getcwd()}/examples/logs/GMAT-Tut03-Log.txt')
# gmat.UseLogFile(log_path)
# gmat.EchoLogFile(False)  # set to True to view log output in console (e.g. live iteration results)

sat_params = {
    'Name': 'DefaultSC',
    'Hardware': {
        'ChemicalTanks': [{'Name': 'ChemicalTank1'}, ],
        'ChemicalThrusters': [{'Name': 'ChemicalThruster1', 'Tanks': 'ChemicalTank1'}, ],
    }
}
sat = gpy.Spacecraft.from_dict(sat_params)

# Set parameters of thruster that will be used for FiniteBurn
thruster_to_fire = sat.chem_thrusters[0]  # select which thruster on the Spacecraft will be fired
thruster_to_fire.SetField('DecrementMass', True)  # reduce the mass of fuel in ChemicalTank1 as it's burned
thruster_to_fire.SetField('MixRatio', [1])  # all draining from one tank (ChemicalTank1, only one assigned to thruster)
thruster_to_fire.SetField('C1', 1000)  # 1000 N thrust

prop = gpy.PropSetup('DefaultProp', gator=gpy.PropSetup.Propagator('RungeKutta89'),
                     accuracy=9.999999999999999e-12)

burn_dur = gpy.Variable('BurnDuration')

fb1 = gpy.FiniteBurn('FiniteBurn1', thruster_to_fire)

dc1 = gpy.DifferentialCorrector('DC1')

print(f'Sat state before running: {sat.GetState()}')
print(f"Epoch before running: {sat.GetField('Epoch')}")

# Mission Command Sequence
mcs = [
    gpy.Propagate('Prop To Periapsis', sat, prop, f'{sat.name}.Earth.Periapsis'),
    # Targeting sequence to adjust burn duration to achieve desired final orbit
    gpy.Target('Raise Apoapsis', dc1, exit_mode='SaveAndContinue', command_sequence=[
        # Vary the FiniteBurn duration to achieve an apoapsis with RMAG = 12000 km
        gpy.Vary('Vary Burn Duration', dc1, burn_dur.name, initial_value=200, upper=10000, max_step=100),
        gpy.BeginFiniteBurn(fb1, sat, 'Turn Thruster On'),
        gpy.Propagate('Prop BurnDuration', sat, prop, (f'{sat.name}.ElapsedSecs', burn_dur.name)),
        gpy.EndFiniteBurn(fb1, 'Turn Thruster Off'),
        gpy.Propagate('Prop To Apoapsis', sat, prop, f'{sat.name}.Earth.Apoapsis'),
        gpy.Achieve('Achieve Apoapsis Radius = 12000', dc1, f'{sat.name}.Earth.RMAG', 12000)
    ])
]

gpy.RunMission(mcs)  # Run the mission

print(f'Sat state after running: {sat.GetState()}')
print(f'Epoch after running: {sat.GetField("Epoch")}')

script_path = os.path.normpath(f'{os.getcwd()}/examples/scripts/Tut03_Target_FiniteBurn_To_Raise_Apogee.script')
gmat.SaveScript(script_path)
