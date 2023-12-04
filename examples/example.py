from load_gmat import gmat

import gmat_py_simple as gpy

sat_params = {
    'Name': 'DefaultSC',
    'Orbit': {
        'coord_sys': 'EarthMJ2000Eq',
        'StateType': 'Keplerian',
    },
    'DryMass': 100,  # kg
    'Hardware': {'Tanks': {'Chemical': [{'Name': 'ChemicalTank1'}],
                           'Electric': [{'Name': 'ElectricTank1'}]},
                 'Thrusters': {'Chemical': [{'Name': 'ChemicalThruster1', 'Tanks': 'ChemicalTank1'}],
                               'Electric': [{'Name': 'ElectricThruster1', 'Tanks': 'ElectricTank1'}]}
                 }
}
sat = gpy.Spacecraft.from_dict(sat_params)

default_prop = gpy.PropSetup('DefaultProp', gator=gpy.PropSetup.Propagator('RungeKutta89'))
gpy.Propagate(default_prop, sat, 'ElapsedSecs', 12000)

sat.Help()
gmat.ShowObjects('Spacecraft')
