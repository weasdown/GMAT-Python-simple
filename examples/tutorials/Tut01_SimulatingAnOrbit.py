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

sat = gmat.Construct('Spacecraft', 'Sat')
sat.SetField('Epoch', '21545')
sat_name = sat.GetName()

fm = gmat.Construct("ForceModel", "FM")
epm = gmat.Construct("PointMassForce", "EPM")
fm.AddForce(epm)

prop = gmat.Construct("Propagator", "Prop")
gator = gmat.Construct("PrinceDormand78", "Gator")
prop.SetReference(gator)
prop.SetReference(fm)

gmat.Initialize()
prop.AddPropObject(sat)
prop.PrepareInternals()

gator = prop.GetPropagator()

state = gator.GetState()


# print(f'Starting state: {state}')


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


# stop_cond fields: ['Covariance', 'BaseEpoch', 'Epoch', 'EpochVar', 'StopVar', 'Goal', 'Repeat']
stop_cond = gmat.Construct('StopCondition', 'StopCond')  # , 'Sat.ElapsedSecs=8640')  # , 8640.0)
print(f'Set LHS: {stop_cond.SetLhsString(f"{sat_name}.ElapsedSecs")}')
print(f'Set RHS: {stop_cond.SetRhsString("8640.0")}')
print(f'Get LHS: {stop_cond.GetLhsString()}')
print(f'Get RHS: {stop_cond.GetRhsString()}')
print(f'\nSetField StopVar: {stop_cond.SetField("StopVar", stop_cond.GetLhsString())}')
print(f'SetField Goal: {stop_cond.SetField("Goal", stop_cond.GetRhsString())}')
print(f'GetField StopVar: {stop_cond.GetField("StopVar")}')
print(f'GetField Goal: {stop_cond.GetField("Goal")}\n')

print(f'Generating string:\n{stop_cond.GetGeneratingString()}')

# gmat.Initialize()

# epoch_param = gmat.Construct('Parameter', 'EpochUser', 'UserParam')

# sat_epoch = sat.GetState().GetEpoch()
# print(f'sat current epoch: {sat_epoch}')
# print(f'SetStopEpoch: {stop_cond.SetEpochParameter(sat_epoch+8640)}')
# print(f'GetStopEpoch: {stop_cond.GetStopEpoch()}')

print(f'GetStopValue: {stop_cond.GetStopValue()}, type: {type(stop_cond.GetStopValue())}')
print(f'GetStopParameter: {stop_cond.GetStopParameter()}')

ela = gmat.Construct('ElapsedSecs', stop_cond.GetLhsString())
# ela's fields: ['Covariance', 'Object', 'InitialValue', 'Expression', 'Description', 'Unit', 'DepObject', 'Color',
#                'InitialEpoch']
ela.SetField('Object', sat.GetName())
print(f'ela Set InitialValue: {ela.GetRealParameter(8)}')
print(f'ela InitialEpoch: {ela.GetRealParameter(8)}')


print(f'ela Set InitialEpoch: {ela.SetRealParameter(8, 0)}')
print(f'ela InitialEpoch: {ela.GetRealParameter(8)}')

print(f'Setting Stop Parameter: {stop_cond.SetStopParameter(ela)}')
# print(f'GetStopParameter again: {stop_cond.GetStopParameter()}')

# print(f'Update Buffer: {stop_cond.UpdateBuffer()}')
# print('Buffer update complete')

print(stop_cond.SetSpacecrafts([sat], [sat]))
stop_cond.Help()
# print(f'Initializing: {stop_cond.Initialize()}')

# gmatpy._py39.gmat_py.APIException: Currently GMAT expects a Parameter of propagating Spacecraft to be on the LHS of
# stopping condition (stop Parameter is NULL)
print(f'StopCondition Validate: {stop_cond.Validate()}')

print(gmat.ConfigManager.Instance().GetListOfAllItems())

obj_map = gmat.ConfigManager.Instance().GetObjectMap()
print(obj_map)
# print(f'Global object map: {gmat.Sandbox.GetGlobalObjectMap(gmat.Sandbox())}')

pgate = gmat.Construct('Propagate')

print(f'Setting StopCond with SetObject: {pgate.SetObject("StopCond", gmat.STOP_CONDITION)}')
# print(f'Setting StopCond: with SetField{pgate.SetField("StopCondition", stop_cond.GetName())}')
print(f'Setting Propagator: {pgate.SetField("Propagator", "Prop")}')
print(f'Setting Sat: {pgate.SetObject("Sat", gmat.SPACECRAFT)}')

# bf = gmat.FiniteThrust("Thrust")
# bf.SetRefObjectName(gmat.SPACECRAFT, s.GetName())
# bf.SetReference(b)
# gmat.ConfigManager.Instance().AddPhysicalModel(bf)

print(f'Setting objects:\n'
      f'Propagator: {pgate.SetRefObjectName(gmat.PROP_SETUP, prop.GetName())},\n'
      # f'Stop Condition: {pgate.SetRefObjectName(gmat.STOP_CONDITION, stop_cond.GetName())}\n'
      f'Stop Condition as Reference to Propagate: {stop_cond.SetReference(pgate)}'
      f'Sat: {pgate.SetRefObjectName(gmat.SPACECRAFT, sat.GetName())}')

# bf.SetReference(b)
# gmat.ConfigManager.Instance().AddPhysicalModel(bf)

print(f'Validating: {pgate.Validate()}')

print(pgate.GetRefObjectTypeArray())  # (134 - PROP_SETUP, 101 - Spacecraft, 122 - Parameter)
# STOP_CONDITION: 126, PROPAGATOR: 110

# gmatpy._py39.gmat_py.APIException: Command Exception: Object map has not been initialized for Propagate
print(f'Initializing pgate: {pgate.Initialize()}')

# pgate.Help()

# pgate.Initialize()

# gmat.ConfigManager.Instance().AddStopCondition(stop_cond)

# gmat.ShowObjects()

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
