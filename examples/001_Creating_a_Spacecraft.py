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
    'Hardware': {'Tanks': {'Chemical': [{'Name': 'ChemicalTank1'}],
                           'Electric': [{'Name': 'ElectricTank1'}]},
                 'Thrusters': {'Chemical': [{'Name': 'ChemicalThruster1', 'Tanks': 'ChemicalTank1'}],
                               'Electric': [{'Name': 'ElectricThruster1', 'Tanks': 'ElectricTank1'}]}
                 }
}

sat = gpy.Spacecraft.from_dict(sat_params)

sat.Help()
