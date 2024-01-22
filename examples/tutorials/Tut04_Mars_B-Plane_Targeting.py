# Tutorial 04: Mars B-Plane Targeting
# Achieve orbit around Mars with the MAVEN spacecraft by targeting Mars' B-plane on approach
# Written by William Easdown Babb

from __future__ import annotations
from load_gmat import gmat
import gmat_py_simple as gpy
import os

log_path = os.path.normpath(f'{os.getcwd()}/examples/logs/GMAT-Tut03-Log.txt')
gmat.UseLogFile(log_path)
gmat.EchoLogFile(False)  # set to True to view log output in console (e.g. live iteration results)

sat_params = {
    'Name': 'MAVEN',
    'Hardware': {'Tanks': {'chemical': [{'Name': 'MainTank'}], },
                 'Thrusters': {'chemical': [{'Name': 'ChemicalThruster1', 'Tanks': 'MainTank'}]},
                 }
}
sat = gpy.Spacecraft.from_dict(sat_params)
main_tank = gpy.ChemicalTank('TestTank', fuel_mass=1718, allow_negative_fuel_mass=False, fuel_density=1000, temperature=20, ref_temp=20, pressure=5000, volume=2, pressure_model='PressureRegulated')
main_tank.Help()

# Set parameters of thruster that will be used for FiniteBurn
thruster_to_fire = sat.thrusters.chemical[0]  # select which thruster on the Spacecraft will be fired
thruster_to_fire.SetField('DecrementMass', True)  # reduce the mass of fuel in ChemicalTank1 as it's burned
thruster_to_fire.SetField('MixRatio', [1])  # all draining from one tank (ChemicalTank1, only one assigned to thruster)
thruster_to_fire.SetField('C1', 1000)  # 1000 N thrust

prop = gpy.PropSetup('DefaultProp', gator=gpy.PropSetup.Propagator('RungeKutta89'),
                     accuracy=9.999999999999999e-12)

# tcm = gpy.ImpulsiveBurn('TCM', decrement_mass=True, tanks=sat.tanks.chemical[0])

dc1 = gpy.DifferentialCorrector('DC1')

print(f'Sat state before running: {sat.GetState()}')
print(f"Epoch before running: {sat.GetField('Epoch')}")

# Mission Command Sequence
mcs = [
    # Target Mars' B-plane
    gpy.Target('Target desire B-plane coordinates', dc1, exit_mode='SaveAndContinue', command_sequence=[
        # TODO set correct propagator
        gpy.Propagate('Prop 3 days', sat, prop, (f'{sat.name}.ElapsedDays', 3)),
        gpy.Propagate('Prop 12 days to TCM', sat, prop, (f'{sat.name}.ElapsedDays', 12)),
        # Vary the Trajectory Correction Maneuver (TCM) elements
        # TODO set correct values
        gpy.Vary('Vary TCM.V', dc1, variable='TCM.Element1', initial_value=200, upper=10000, max_step=100),
        gpy.Vary('Vary TCM.N', dc1, variable='TCM.Element2', initial_value=200, upper=10000, max_step=100),
        gpy.Vary('Vary TCM.B', dc1, variable='TCM.Element3', initial_value=200, upper=10000, max_step=100),
        gpy.Maneuver('Apply TCM', tcm, sat),
        # TODO set correct propagator
        gpy.Propagate('Prop 280 days', sat, prop, (f'{sat.name}.ElapsedDays', 280)),
        gpy.Propagate('Prop to Mars Periapsis', sat, prop, f'{sat.name}.Earth.Periapsis'),
        gpy.Achieve('Achieve BdotT', dc1, f'{sat.name}.{mars_inertial.name}.BdotT', 0),
        gpy.Achieve('Achieve BdotR', dc1, f'{sat.name}.{mars_inertial.name}.BdotR', -7000)
    ]),
    # Capture into Mars orbit
    # TODO set correct sub-commands
    gpy.Target('Mars capture', dc1, exit_mode='SaveAndContinue', command_sequence=[
        # Vary the burn duration to achieve an altitutde of 12000 km
        # TODO set correct values
        gpy.Vary('Vary MOI.V', dc1, variable=f'{moi.name}.Element1', initial_value=200, upper=10000, max_step=100),
        gpy.Maneuver('Apply MOI', moi, sat),
        gpy.Propagate('Prop to Mars Apoapsis', sat, prop, f'{sat.name}.Mars.Apoapsis'),
        gpy.Achieve('Achieve RMAG', dc1, f'{sat.name}.Mars.RMAG', 12000, tolerance=0.1),
    ]),
    gpy.Propagate('Prop for 1 day', sat, prop, (f'{sat.name}.ElapsedDays', 1)),
]

gpy.RunMission(mcs)  # Run the mission

print(f'Sat state after running: {sat.GetState()}')
print(f'Epoch after running: {sat.GetField("Epoch")}')

script_path = os.path.normpath(f'{os.getcwd()}/examples/scripts/Tut03_Target_FiniteBurn_To_Raise_Apogee.script')
gmat.SaveScript(script_path)
