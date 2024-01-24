# Tutorial 04: Mars B-Plane Targeting
# Achieve orbit around Mars with the MAVEN spacecraft by targeting Mars' B-plane on approach
# Written by William Easdown Babb

# TODO: THIS EXAMPLE IS CURRENTLY A WORK IN PROGRESS (WIP)

from __future__ import annotations
from load_gmat import gmat
import gmat_py_simple as gpy
import os

log_path = os.path.normpath(f'{os.getcwd()}/examples/logs/GMAT-Tut04-Log.txt')
gmat.UseLogFile(log_path)
gmat.EchoLogFile(False)  # set to True to view log output in console (e.g. live iteration results)

sat = gpy.Spacecraft('MAVEN')
main_tank = gpy.ChemicalTank('TestTank', fuel_mass=1718, allow_negative_fuel_mass=False, fuel_density=1000,
                             temperature=20, ref_temp=20, pressure=5000, volume=2, pressure_model='PressureRegulated')
sat.add_tanks(main_tank)

# Setup ForceModels and Propagators
near_earth_fm = gpy.ForceModel('NearEarthFM', primary_body='Earth',
                               gravity_field=gpy.ForceModel.GravityField(degree=8, order=8),
                               point_masses=['Luna', 'Sun'],
                               srp=True)
near_earth = gpy.PropSetup('NearEarth',
                           gator=gpy.PropSetup.Propagator('RungeKutta89'), fm=near_earth_fm,
                           initial_step_size=600, accuracy=1e-13, min_step=0, max_step=600, max_step_attempts=50)

deep_space_fm = gpy.ForceModel('DeepSpaceFM', central_body='Sun', primary_body='Sun',
                               point_masses=['Earth', 'Jupiter', 'Luna', 'Mars',
                                             'Neptune', 'Saturn', 'Sun', 'Uranus',
                                             'Venus'], srp=True)
deep_space = gpy.PropSetup('DeepSpace',
                           gator=gpy.PropSetup.Propagator('PrinceDormand78'), fm=deep_space_fm,
                           initial_step_size=600, accuracy=1e-12, min_step=0, max_step=864000, max_step_attempts=50)

mars_gravity_file = f'{gmat.FileManager.Instance().GetRootPath()}data\\gravity\\mars\\Mars50c.cof'
near_mars_fm = gpy.ForceModel('NearMarsFM', central_body='Mars', primary_body='Mars',
                              gravity_field=gpy.ForceModel.GravityField(body='Mars', model='Mars-50C', degree=8,
                                                                        order=8, gravity_file=mars_gravity_file),
                              point_masses=['Sun'], srp=True)
near_mars = gpy.PropSetup('NearMars',
                          gator=gpy.PropSetup.Propagator('PrinceDormand78'), fm=near_mars_fm,
                          initial_step_size=600, accuracy=1e-12, min_step=0, max_step=86400, max_step_attempts=50)

# Setup CoordinateSystems
mars_inertial = gpy.OrbitState.CoordinateSystem('MarsInertial', 'Mars', 'BodyInertial')

# Setup ImpulsiveBurns
tcm = gpy.ImpulsiveBurn('TCM', coord_sys={'CoordinateSystem': 'Local', 'Origin': 'Mars', 'Axes': 'VNB'},
                        decrement_mass=True, tanks=main_tank)
moi = gpy.ImpulsiveBurn('MOI', coord_sys={'CoordinateSystem': 'Local', 'Origin': 'Mars', 'Axes': 'VNB'},
                        decrement_mass=True, tanks=main_tank)

dc1 = gpy.DifferentialCorrector('DC1')

print(f'Sat state before running: {sat.GetState()}')
print(f"Epoch before running: {sat.GetField('Epoch')}")

# Mission Command Sequence
mcs = [
    # Target Mars' B-plane
    gpy.Target('Target desire B-plane coordinates', dc1, exit_mode='SaveAndContinue', command_sequence=[
        # TODO set correct propagator
        gpy.Propagate('Prop 3 days', sat, near_earth, (f'{sat.name}.ElapsedDays', 3)),
        gpy.Propagate('Prop 12 days to TCM', sat, deep_space, (f'{sat.name}.ElapsedDays', 12)),
        # Vary the Trajectory Correction Maneuver (TCM) elements
        # TODO set correct values
        gpy.Vary('Vary TCM.V', dc1, variable='TCM.Element1', initial_value=200, upper=10000, max_step=100),
        gpy.Vary('Vary TCM.N', dc1, variable='TCM.Element2', initial_value=200, upper=10000, max_step=100),
        gpy.Vary('Vary TCM.B', dc1, variable='TCM.Element3', initial_value=200, upper=10000, max_step=100),
        gpy.Maneuver('Apply TCM', tcm, sat),
        # TODO set correct propagator
        gpy.Propagate('Prop 280 days', sat, deep_space, (f'{sat.name}.ElapsedDays', 280)),
        gpy.Propagate('Prop to Mars Periapsis', sat, near_mars, f'{sat.name}.Earth.Periapsis'),
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
        gpy.Propagate('Prop to Mars Apoapsis', sat, near_mars, f'{sat.name}.Mars.Apoapsis'),
        gpy.Achieve('Achieve RMAG', dc1, f'{sat.name}.Mars.RMAG', 12000, tolerance=0.1),
    ]),
    gpy.Propagate('Prop for 1 day', sat, near_mars, (f'{sat.name}.ElapsedDays', 1)),
]

# FIXME: MAVEN.MarsInertial.BdotT/BdotR params not being created but unnecessary ones are - check StopCondition init
gmat.ShowObjects()

gpy.RunMission(mcs)  # Run the mission

print(f'Sat state after running: {sat.GetState()}')
print(f'Epoch after running: {sat.GetField("Epoch")}')

script_path = os.path.normpath(f'{os.getcwd()}/examples/scripts/Tut04_Mars_B-Plane_Targeting.script')
gmat.SaveScript(script_path)
