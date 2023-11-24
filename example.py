from load_gmat import gmat
import gmat_api_simple as api

# TODO add parameter parsing to Spacecraft class
sat_params = {
    'name': 'Servicer',
    'orbit': {  # TODO: add other orbit params. Cartesian by default
        'coord_sys': 'EarthMJ2000Eq',
        'state_type': 'Cartesian',
    },
    'dry_mass': 100,  # kg
    'hardware': {'prop_type': 'EP',  # or 'CP'
                 'tanks': [{'name': 'ElectricTank1', 'FuelMass': 0},
                           {'name': 'ElectricTank2', 'FuelMass': 10}],
                 'thrusters': {'num': 1}}
}

sat = api.Spacecraft(sat_params['name'])
# sat = Spacecraft.from_dict(sat_params)
# print(f'sat specs:\n{json.dumps(sat.specs, indent=4)}')
# print(f'sat orbit specs: {sat.specs["orbit"]}')
gmat.Initialize()
# sat.Help()

ep_tank = api.ElectricTank('EP_Tank', sat)
# print(ep_tank)

ep_thruster = api.ElectricThruster('EP_Thruster', sat, ep_tank)
# print(ep_thruster)

# gmat.ShowObjects()
# sat.Help()

gmat.Initialize()
ep_thruster.IsInitialized()

ep_thruster.mix_ratio = [1]

burn = api.FiniteBurn('FiniteBurn1', sat, ep_thruster)
finite_thrust = api.FiniteThrust('FiniteThrust1', sat, burn)

# burn.BeginFiniteBurn(finite_thrust)

api.get_object_gmat_fields(sat.gmat_object)
