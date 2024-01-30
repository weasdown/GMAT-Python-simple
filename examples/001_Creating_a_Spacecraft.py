import gmat_py_simple as gpy

sat_params = {
    'Name': 'DefaultSC',
    'Orbit': {
        'CoordSys': 'EarthMJ2000Eq',
        'Epoch': '21545',
        'DisplayStateType': 'Keplerian',
        'SMA': 7200
    },
    'DryMass': 100,  # kg
    'Hardware': {'ChemicalTanks': [{'Name': 'ChemicalTank1'}],
                 'ElectricTanks': [{'Name': 'ElectricTank1'}],
                 'ChemicalThrusters': [{'Name': 'ChemicalThruster1', 'Tanks': 'ChemicalTank1'}],
                 'ElectricThrusters': [{'Name': 'ElectricThruster1', 'Tanks': 'ElectricTank1'}]
                 }
}

sat = gpy.Spacecraft.from_dict(sat_params)

sat.Help()
