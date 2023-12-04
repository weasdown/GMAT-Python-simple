from load_gmat import gmat

import gmat_py_simple as gpy

# TODO !!! this currently simulates the default mission rather than the relevant tutorial

sat_params = {
    'Name': 'DefaultSat',
    'Orbit': {
        'Epoch': '22 Jul 2014 11:29:10.811',
        'DateFormat': 'UTCGregorian',
        'CoordSys': 'EarthMJ2000Eq',
        'StateType': 'Keplerian',
        'SMA': 83474.31800000001,
        'ECC': 0.89652,
        'INC': 12.4606,
        'RAAN': 292.8362,
        'AOP': 218.9805,
        'TA': 180,
    },
}
sat = gpy.Spacecraft.from_dict(sat_params)

sat.Help()

default_prop = gpy.PropSetup('DefaultProp', gator=gpy.PropSetup.Propagator('RungeKutta89'))
gpy.Propagate(default_prop, sat, 'ElapsedSecs', 12000)

# sat.Help()
