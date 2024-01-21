import gmat_py_simple as gpy

sat_params = {
    'Name': 'DefaultSC',
    'Orbit': {
        'CoordSys': 'EarthMJ2000Eq',
        'Epoch': '21545',
        'StateType': 'Keplerian',
        'SMA': 7200
    },
    'DryMass': 100,  # kg
    'Hardware': {'Tanks': {'chemical': [{'Name': 'ChemicalTank1'}],
                           'electric': [{'Name': 'ElectricTank1'}]},
                 'Thrusters': {'chemical': [{'Name': 'ChemicalThruster1', 'Tanks': 'ChemicalTank1'}],
                               'electric': [{'Name': 'ElectricThruster1', 'Tanks': 'ElectricTank1'}]}
                 }
}

sat = gpy.Spacecraft.from_dict(sat_params)

sat.Help()
