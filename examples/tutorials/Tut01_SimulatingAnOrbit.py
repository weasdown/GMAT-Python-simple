import gmat_py_simple.utils
from load_gmat import gmat

import gmat_py_simple as gpy
from gmat_py_simple import orbit as o

# TODO complete modelling the tutorial mission rather than the default one

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

lep_fm = o.ForceModel(name='LowEarthProp_ForceModel',
                      gravity_field=o.ForceModel.GravityField(
                          degree=10,
                          order=10,
                      ),
                      point_masses=['Luna', 'Sun'],
                      drag=True,
                      srp=True
                      )

lep_fm.Help()

start_state = sat.GetKeplerianState()
print(start_state)

prop = gpy.orbit.PropSetup('Propagator', fm=lep_fm)
gpy.commands.Propagate(prop, sat, 'ElapsedDays', 365)

end_state = sat.GetKeplerianState()
print(end_state)

# sat.Help()
