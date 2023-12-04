from load_gmat import gmat

import gmat_py_simple as gpy

sat_params = {
    'Name': 'Servicer',
    'Orbit': {
        'coord_sys': 'EarthMJ2000Eq',
        'StateType': 'Keplerian',
    },
    'DryMass': 100,  # kg
    'Hardware': {}
}
sat = gpy.Spacecraft.from_dict(sat_params)

default_prop = gpy.PropSetup('DefaultProp', gator=gpy.PropSetup.Propagator('RungeKutta89'))
gpy.Propagate(sat, 'ElapsedSecs', 12000, propagator=default_prop)
