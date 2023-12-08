import gmat_py_simple.utils
from load_gmat import gmat

import gmat_py_simple as gpy
from gmat_py_simple import orbit as o
from gmat_py_simple.orbit import PropSetup
from gmat_py_simple.commands import Propagate

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

# sat = gpy.Spacecraft.from_dict(sat_params)

# sat.Help()

# lep_fm = o.ForceModel(name='LowEarthProp_ForceModel',
#                       gravity_field=o.ForceModel.GravityField(
#                           degree=10,
#                           order=10,
#                       ),
#                       point_masses=['Luna', 'Sun'],
#                       drag=True,
#                       srp=True
#                       )

# lep_fm.Help()

# start_state = sat.GetKeplerianState()
# print(f'Start state: {start_state}')
#
# prop = PropSetup('Propagator', fm=lep_fm)
#
# gmat.Initialize()
#
# Propagate(prop, sat, ('ElapsedSecs', 60))
#
# end_state = sat.GetKeplerianState()
# print(f'End state: {end_state}')

# sat.Help()
# gator = prop.GetPropagator()
# print(f'gator: {gator}')
# print('gator Help:')
# gator.Help()

# propagate = gmat.Construct('Propagate')
# print(f'Propagate Generating String: {propagate.GetGeneratingString()}')

sc = gmat.Construct('Spacecraft', 'DefaultSC')

fm = gmat.Construct('ODEModel', 'GF&Sun')
pm_sun = gmat.Construct('PointMassForce')
fm.AddForce(pm_sun)

prop = gmat.Construct('Propagator', 'Prop')
gator = gmat.Construct("PrinceDormand78", "Gator")
prop.SetReference(gator)
prop.SetReference(fm)

gmat.Initialize()
prop.AddPropObject(sc)
prop.PrepareInternals()

gator = prop.GetPropagator()

# gmat.Initialize()

# gator = prop.GetPropagator()
# psm = prop.GetPropStateManager()
# psm.SetObject(sc)

# gmat.Initialize()
#
# fm = prop.GetODEModel()
# gator = prop.GetPropagator()
# psm.BuildState()
# fm.SetPropStateManager(psm)
# fm.SetState(psm.GetState())
# fm.Initialize()
# fm.BuildModelFromMap()
# fm.UpdateInitialData()
# prop.Initialize()
# gator.Initialize()

gmat.Initialize()

# bms = gmat.BeginMissionSequence()
# print(f'BeginMissionSequence return: {bms.Execute()}')


def CustomHelp(obj):
    if 'gmat_py_simple' in str(type(obj)):
        param_count = obj.gmat_obj.GetParameterCount()
    else:
        param_count = obj.GetParameterCount()

    for i in range(param_count):
        try:
            print(f'Parameter: {obj.GetParameterText(i)}\n'
                  f'param type str: {obj.GetParameterTypeString(i)}\n')
                  # f'Type and value: {obj.GetTypeAndValue(i)}\n')
        except Exception as ex:
            print(ex, '\n')


sat = gmat.Construct('Spacecraft', 'Sat')

fm = gpy.orbit.ForceModel()
fm.Help()

prop = gmat.Construct('Propagator', 'DefaultProp')
# fm = prop.GetODEModel()
# fm.Help()
# prop.Help()

stop_cond = gmat.Construct('StopCondition', 'StopCond')  # , 'Sat.ElapsedSecs=8640')  # , 8640.0)

# stop_cond.SetGoalParameter(8640.0)

# stop_cond.SetDescription('Propagate until Sat.ElapsedSecs = 8640')
# stop_cond.SetLhsString('Sat.ElapsedSecs =')
#
# propagate = gmat.Construct('Propagate')
# propagate.SetObject('StopCondition', gmat.STOP_CONDITION)
#
# # stop_cond.Validate()
# # stop_cond.SetRhsString('8640.0')
# # stop_cond.SetSpacecrafts(sat, [sat])
# stop_cond.Help()

# propagate.SetField('StopCondition', 'StopCond')
# propagate.SetReference(stop_cond)

# print(propagate.GetRefObjectTypeArray())  # (134, 101, 122)
# print(propagate.GetRefObjectName(134))  # (134, 101, 122)

# propagate.Help()

# print(propagate.GetRefObjectNameArray(122))  # (), (), ()
# print(propagate.GetRefObjectArray(101))  # <gmat_py.ObjectArray; proxy of <Swig Object of type 'std::vector...
#
# propagate.SetObject(prop.GetName(), gmat.PROP_SETUP)  # src/base/Propagate.cpp/Propagate.SetObject()
# # print(propagate.GetField('Propagator'))  # API Exception caught: Cannot get string parameter with ID 9: "Propagator"
# # on Propagate named ""
#
# propagate.SetStringParameter(9, prop.GetName())
# # print(propagate.GetStringParameter(9))
# propagate.SetField('Spacecraft', sc.GetName())
#
# CustomHelp(propagate)
#
# # print(propagate.AcceptsObjectType(gmat.STOP_CONDITION))
# print(propagate.GetFirstSpaceObjectName())
# print(propagate.Initialize())

# propagate.SetField('Propagator', gator.GetName())


# propagate.SetField('StopCondition', 'DefaultSC.ElapsedSecs = 8640.0')
# propagate.SetField('Spacecraft', sc.GetName())

# propagate.SetObject(gator.GetName(), gmat.PROPAGATOR)
# propagate.SetObject(sc.GetName(), gmat.SPACECRAFT)
# propagate.SetObject(prop.GetName(), gmat.PROP_SETUP)

# propagate.Help()

# print(f'Prop status: {propagate.GetPropStatus()}')
# print(propagate.RunComplete())

# propagate.Initialize()
# propagate.Execute()
# propagate.Help()

# print(gpy.utils.gmat_obj_field_list(propagate))

# print(propagate.GetParameterCount())  # 16
# print(propagate.GetTypeAndValue(3))


# CustomHelp(propagate)

# bob = gpy.orbit.OrbitState.CoordinateSystem('Bob')
# bob.Help()

# cs = gmat.Construct('CoordinateSystem', 'CS', 'Earth')
# cs.Help()

# propagate = gmat.Construct('Propagate', 'Pgate', 'DefaultSC.ElapsedSecs = 8640.0')
# propagate.Help()
