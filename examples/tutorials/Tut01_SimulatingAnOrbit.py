from load_gmat import gmat

import gmat_py_simple as gpy

# TODO !!! this currently simulates the default mission rather than the relevant tutorial

sat_params = {
    'Name': 'DefaultSat',
    'Orbit': {
        'coord_sys': 'EarthMJ2000Eq',
        'StateType': 'Keplerian',
    },
    'Hardware': {}
}
sat = gpy.Spacecraft.from_dict(sat_params)

default_prop = gpy.PropSetup('DefaultProp', gator=gpy.PropSetup.Propagator('RungeKutta89'))
gpy.Propagate(sat, 'ElapsedSecs', 12000, propagator=default_prop)
