import os
from typing import Union

from load_gmat import gmat
import gmat_api_simple as api
import sys

# TODO consider making enum that defines valid fields so they can be used in sat_params
#  e.g. {DRYMASS = 100}

# TODO add parameter parsing to Spacecraft class
sat_params = {
    'Name': 'Servicer',
    'Orbit': {  # TODO: add other orbit params. Cartesian by default
        'coord_sys': 'EarthMJ2000Eq',
        'state_type': 'Cartesian',
    },
    'DryMass': 100,  # kg
    'Hardware': {'Tanks': {'Chemical': [{'Name': 'ChemicalTank1'}],
                           'Electric': [{'Name': 'ElectricTank1'}]},
                 'Thrusters': {'Chemical': [{'Name': 'ChemicalThruster1', 'Tanks': 'ChemicalTank1'}],
                               'Electric': [{'Name': 'ElectricThruster1', 'Tanks': 'ElectricTank1'}]}
                 }
}

# sat = api.Spacecraft.from_dict(sat_params)
# sat = api.Spacecraft(sat_params['name'])
# sat = Spacecraft.from_dict(sat_params)
# print(f'sat specs:\n{json.dumps(sat.specs, indent=4)}')
# print(f'sat orbit specs: {sat.specs["orbit"]}')
# gmat.Initialize()
# sat.Help()

# ep_tank = api.ElectricTank('EP_Tank', sat)
# print(ep_tank)

# ep_thruster = api.ElectricThruster('EP_Thruster', sat, ep_tank)
# print(ep_thruster)

# gmat.ShowObjects()
# sat.Help()

# gmat.Initialize()
# ep_thruster.IsInitialized()
#
# ep_thruster.mix_ratio = [1]
#
# burn = api.FiniteBurn('FiniteBurn1', sat, ep_thruster)
# finite_thrust = api.FiniteThrust('FiniteThrust1', sat, burn)

# burn.BeginFiniteBurn(finite_thrust)

# print(f'Spacecraft fields: {api.get_object_gmat_fields(sat.gmat_object)}')

# classes = api.get_gmat_classes()
# class_fields = {}
# for cls in classes:
# api.get_gmat_class_fields(sat.gmat_object)

# api.fields_for_gmat_base_gmat_command()

# sat.Help()
# sat.gmat_object.GetRefObjectTypeArray(): (150, 149, 117, 176, 179, 105)
# 150 = EarthMJ2000Eq, 149 = Error, 117 = Error, 176 = Blank, 179 = Error, 105 = Error
# print(sat.gmat_object.GetRefObject(150, 'EarthMJ2000Eq')): Object of type CoordinateSystem named EarthMJ2000Eq
# print(sat.gmat_object.GetRefObjectTypeArray())
# print(sat.gmat_object.GetRefObjectArray()

# sat_coord_sys = sat.gmat_object.GetRefObject(150, 'EarthMJ2000Eq')

# sat_coord_sys.Help()
# sat_coord_sys.GetRefObjectTypeArray(): (116,) (PropertyObjectType 675)
# print(sat_coord_sys.CanAssignStringToObjectProperty(116))

# sat.Help()

# print(f'sat.Thrusters: {sat.Thrusters}')
# burn = api.FiniteBurn('FB1', sat, sat.thrusters[0])
# burn.Help()

# gmat.Help('Commands')

# type(prop) == PropSetup
# type(gator) == Propagator


# sat = gmat.Construct('Spacecraft', 'DefaultSC')
#
# hardware_obj = api.SpacecraftHardware(sat_params['Hardware'])
# print(hardware_obj)

# class Thruster(api.HardwareItem):
#     def __init__(self, thruster_type: str, name: str):
#         self.thruster_type = thruster_type  # 'ChemicalThruster' or 'ElectricThruster'
#         self.name = name
#         super().__init__(self.thruster_type, self.name)

# ep_thruster = api.ElectricThruster.from_dict({'Name': 'EP_Thruster1', 'ConstantThrust': 15})

# ep_thruster.Help()

# cp_thruster = api.ChemicalThruster.from_dict({'Name': 'CP_Thruster1', 'C1': 15})
# cp_thruster.Help()
# gmat.Clear()

sat = api.Spacecraft.from_dict(sat_params)
# sat.Help()

# print(f"sat's thrusters: {sat.Thrusters}")

# sat.SetField('Epoch', '21550')
# sat.SetField('StateType', 'Keplerian')

# sat.Help()

fred = gmat.Construct('CoordinateSystem', 'Fred', 'Earth', 'MJ2000Eq')
# gmat.ShowObjects('CoordinateSystem')
# gmat.ShowObjects()

# fred.Help()

bob = api.OrbitState.CoordinateSystem('Bob', 'MJ2000Eq')
# bob.Help()

orbit_state = api.OrbitState(state_type='Keplerian')
orbit_state.apply_to_spacecraft(sat)

# sat.Help()

print(api.GetCelestialBodies())

# gmat.Help('SolarSystemBarycenter')
