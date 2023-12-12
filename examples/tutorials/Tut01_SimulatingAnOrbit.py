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

# gmat.ShowObjects()
# prop.Help()

# print(f'Starting state: {state}')


# bms = gmat.BeginMissionSequence()
# print(f'BeginMissionSequence return: {bms.Execute()}')


def CustomHelp(obj):
    print(f'CustomHelp for {obj.GetName()}:')
    if 'gmat_py_simple' in str(type(obj)):
        param_count = obj.gmat_obj.GetParameterCount()
    else:
        param_count = obj.GetParameterCount()

    for i in range(param_count):
        try:
            param_name = obj.GetParameterText(i)
            param_type = obj.GetParameterTypeString(i)
            print(f'Parameter: {param_name}')
            print(f'- Type: {param_type}')
            if param_type == 'String':
                val = obj.GetStringParameter(i)
            elif param_type == 'Object':
                val = obj.GetName()
            elif (param_type == 'Real') or (param_type == 'UnsignedInt') or (param_name == 'InitialEpoch'):
                val = obj.GetRealParameter(i)
            elif param_type == 'Rmatrix':
                val = obj.GetRmatrixParameter(i)
            else:
                try:
                    val = obj.GetField(param_name)
                except Exception:
                    raise TypeError(f'Getting value of {param_type} failed')

            print(f'- Value: {val}\n')

        except Exception as exc:
            print(exc, '\n')
            # raise


# # stop_cond fields: ['Covariance', 'BaseEpoch', 'Epoch', 'EpochVar', 'StopVar', 'Goal', 'Repeat']
# stop_cond = gmat.Construct('StopCondition', 'StopCond')  # , 'Sat.ElapsedSecs=8640')  # , 8640.0)
# print(f'Set LHS: {stop_cond.SetLhsString(f"{sat_name}.ElapsedSecs =")}')
# print(f'Set RHS: {stop_cond.SetRhsString("8640.0")}')
# print(f'Get LHS: {stop_cond.GetLhsString()}')
# print(f'Get RHS: {stop_cond.GetRhsString()}')
# print(f'\nSetField StopVar: {stop_cond.SetField("StopVar", stop_cond.GetLhsString())}')
# print(f'SetField Goal: {stop_cond.SetField("Goal", stop_cond.GetRhsString())}')
# print(f'GetField StopVar: {stop_cond.GetField("StopVar")}')
# print(f'GetField Goal: {stop_cond.GetField("Goal")}\n')
#
# print(f'Generating string:\n{stop_cond.GetGeneratingString()}')
#
# # gmat.Initialize()
#
# # epoch_param = gmat.Construct('Parameter', 'EpochUser', 'UserParam')
#
# # sat_epoch = sat.GetState().GetEpoch()
# # print(f'sat current epoch: {sat_epoch}')
# # print(f'SetStopEpoch: {stop_cond.SetEpochParameter(sat_epoch+8640)}')
# # print(f'GetStopEpoch: {stop_cond.GetStopEpoch()}')
#
# print(f'GetStopValue: {stop_cond.GetStopValue()}, type: {type(stop_cond.GetStopValue())}')
# # print(f'GetStopEpoch: {stop_cond.GetStopEpoch()}')
# print(f'GetStopParameter: {stop_cond.GetStopParameter()}')
#
# print(gmat.Update())
#
# print(f'stop_cond fields: {gpy.utils.gmat_obj_field_list(stop_cond)}')
# stop_cond.Help()
#

gmat.BeginMissionSequence()

pgate = gmat.Construct('Propagate')
pgate.SetSolarSystem(gmat.GetSolarSystem())
pgate.SetGlobalObjectMap(gmat.Sandbox.GetGlobalObjectMap(gmat.Sandbox()))
pgate.SetObjectMap(gmat.Sandbox.GetObjectMap(gmat.Sandbox()))
# pgate_valid = pgate.CheckStopConditions()

stop_cond = gmat.Construct('StopCondition', 'StopForSatDays')
print(stop_cond)
stop_param_str = f'{sat.GetName()}.ElapsedSecs'
stop_cond.SetLhsString(stop_param_str)
goal_param_str = '8640.0'
stop_cond.SetRhsString(goal_param_str)
stop_cond.SetSpacecrafts([sat], [sat])

# craft_param = gmat.Construct('Variable', 'SatParam')
# craft_param.SetField('InitialValue', stop_param_str)
# ela = gmat.Construct('ElapsedSecs', 'Sat.ElapsedSecs')
# ela.SetField('Object', sat_name)
# ela.SetRefObject(sat, gmat.SPACECRAFT, sat.GetName())
# ela.Initialize()
# ela_param = gmat.ConfigManager.Instance().GetParameter(ela.GetName())

# stop_param_default = stop_cond.GetStopParameter()
# stop_cond.SetStopParameter(ela_param)
# craft_param = gmat.ConfigManager.Instance().GetParameter(ela.GetName())

# mod = gmat.Moderator.Instance()
# craft_param = mod.CreateParameter('String', stop_param_str)

# stop_param = sat.GetGmatTimeParameter(f'{sat.GetName()}.ElapsedSecs')
stop_param = gmat.Construct('ElapsedSecs', f'{sat.GetName()}.ElapsedSecs')
# gmat.Initialize()
print(f'\nstop_param fields: {gpy.gmat_obj_field_list(stop_param)}')
stop_param.SetField('Object', sat.GetName())
stop_param.SetRefObject(sat, gmat.SPACECRAFT, sat.GetName())
stop_param.SetField('InitialValue', stop_param_str)
stop_param.SetField('Expression', stop_param_str)
stop_param.SetField('Description', stop_param_str)
stop_param.SetField('InitialEpoch', sat.GetState().GetEpoch())
# print(gmat.GetTypeName(116))
# gmat.Initialize()
# stop_param.SetReference(sat)
stop_param.Initialize()
# stop_param = gmat.Moderator.Instance().GetInternalObject('Sat.ElapsedSecs')
stop_param = gmat.ConfigManager.Instance().GetParameter('Sat.ElapsedSecs')
stop_cond.SetStopParameter(stop_param)
stop_cond.GetStopParameter()
stop_cond.Validate()
stop_cond.Initialize()

pgate.SetObject(stop_cond, gmat.STOP_CONDITION)

# pgate.Initialize()
# stop_cond_fields = gpy.gmat_obj_field_list(stop_cond)
# stop_cond.AddToBuffer(True)
# stop_cond.Help()
# stop_cond.SetRefObject(gmat.SPACECRAFT, sat.GetName())
# stop_cond.Validate()

# ela = gmat.Construct('ElapsedSecs', f'{sat.GetName()}.ElapsedSecs', f'{sat.GetName()}')
# # ela.SetField('Object', sat_name)
# ela.SetField('InitialValue', stop_param_str)
# ela.SetField('Expression', stop_param_str)
# # ela.SetField('DepObject', sat.GetName())
# # ela.SetField('InitialEpoch', [0])
# ela_param = gmat.ConfigManager.Instance().GetParameter(ela.GetName())
# stop_cond.SetStopParameter(ela_param)
# stop_cond.Initialize()
# stop_param = ela.GetName()

# stop_cond.SetField('StopParameter', str(stop_param))
# ela.SetRefObject(sat, gmat.SPACECRAFT, sat.GetName())

# CustomHelp(ela)
# ela.Validate()

goal_val = 8640.0

# stop_cond_fields = gmat_py_simple.gmat_obj_field_list(stop_cond)
# ela_fields = gmat_py_simple.gmat_obj_field_list(ela)
# pgate_fields = gmat_py_simple.gmat_obj_field_list(pgate)

# stop_cond.SetField('Goal', str(goal_val))
# goal = gmat.Construct('Variable', 'Goal')
# gpy.gmat_obj_field_list(goal)
# goal.SetField('InitialValue', str(goal_val))
# goal.SetField('Unit', 's')

# goal_param = gmat.ConfigManager.Instance().GetParameter(goal.GetName())
# print(f'Setting stop_cond Goal param: {stop_cond.SetGoalParameter(goal_param)}')
# print(f'stop_cond Goal param: {stop_cond.GetGoalParameter()}')

# stop_cond.SetLhsString(ela.GetName())
# stop_cond.SetRhsString('8640.0')
# stop_cond.SetSpacecrafts([sat], [sat])
# stop_con_valid = stop_cond.Validate()

# goal_param = stop_cond.GetGoalParameter()
# print(f'goal_param value: {goal_param}, type: {type(goal_param)}')
# # goal_param = gmat.ConfigManager.Instance().GetParameter()
# # goal_param.SetReal(8640.0)
# print(f'goal_param value: {goal_param}, type: {type(goal_param)}')
# stop_cond.SetGoalParameter(goal_param)
# print(f'stop_cond StopParameter: {stop_cond.GetStopParameter()}')

# ela's fields: ['Covariance', 'Object', 'InitialValue', 'Expression', 'Description', 'Unit', 'DepObject', 'Color',
#                'InitialEpoch']
# ela.SetField('Object', sat.GetName())
# print(ela.GetField('Object'))
# print(f'ela Set InitialEpoch: {ela.GetRealParameter(8)}')
# print(f'ela InitialEpoch: {ela.GetRealParameter(8)}')

#
# print(f'ela Set InitialEpoch: {ela.SetRealParameter(8, 0)}')
# print(f'ela InitialEpoch: {ela.GetRealParameter(8)}')
#
# print(f'ela type: {ela.GetType()}')
# # print(f'ela as LHS wrapper: {stop_cond.SetLhsWrapper(ela)}')
# print(f'stop_cond set ref object ela: {stop_cond.SetRefObject(gmat.PARAMETER, ela.GetName())}')
#
# print(f'Setting Stop Parameter: {stop_cond.SetStopParameter(gmat.GetGmatTimeParameter(ela))}')
# # print(f'GetStopParameter again: {stop_cond.GetStopParameter()}')
#
# # print(f'Update Buffer: {stop_cond.UpdateBuffer()}')
# # print('Buffer update complete')
#
# print(stop_cond.SetSpacecrafts([sat], [sat]))
# stop_cond.Help()
# # print(f'Initializing: {stop_cond.Initialize()}')
#
# # gmatpy._py39.gmat_py.APIException: Currently GMAT expects a Parameter of propagating Spacecraft to be on the LHS of
# # stopping condition (stop Parameter is NULL)
# print(f'StopCondition Validate: {stop_cond.Validate()}')

# pgate.SetRefObject(stop_cond, gmat.STOP_CONDITION, stop_cond.GetName(), 5)

# print(pgate.GetParameterTypeString(10))
# pgate.SetRefObject(stop_cond, gmat.STOP_CONDITION, stop_cond.GetName(), 10)
pgate.SetObject(prop.GetName(), gmat.PROP_SETUP)
pgate.SetObject(sat.GetName(), gmat.SPACECRAFT)
pgate.SetField('StopCondition', [stop_cond.GetName()])
pgate.SetObject(stop_cond.GetName(), gmat.STOP_CONDITION)

print(pgate.GetObjectList())

# bms = gmat.BeginMissionSequence()
# print(bms)

print(f'pgate Validate: {pgate.Validate()}')
# pgate.Initialize()
# CustomHelp(pgate)
print('\n', pgate.GetGeneratingString())

# print(pgate.TakeAction('CheckStopConditions'))
# print(pgate.TakeAction('PrepareToPropagate'))
print(f'\npgate fields: {gpy.gmat_obj_field_list(pgate)}')
print(f'\nstop_cond fields: {gpy.gmat_obj_field_list(stop_cond)}')

# pgate.Help()

CustomHelp(pgate)
# print(pgate.Initialize())

# pgate.Help()

# print(f'pgate Initialize: {pgate.Initialize()}')

# gmat.Update(stop_cond.GetName())

# TODO: set Lhs and Rhs wrappers for stop_cond
# stop_cond.SetLhsWrapper(stop_cond.GetLhsString())
# stop_cond.SetRhsWrapper(stop_cond.GetRhsString())
# print(stop_cond.GetWrapperObjectNameArray())

# obj_map = gmat.ConfigManager.Instance().GetObjectMap()
# print(obj_map)
# print(f'Global object map: {gmat.Sandbox.GetGlobalObjectMap(gmat.Sandbox())}')
# gmat.Update()

# print(f'Setting StopCond with SetObject: {pgate.SetObject("StopCond", gmat.STOP_CONDITION)}')
# print(f'Setting StopCondition with SetField{pgate.SetField("StopCondition", ela.GetName())}')
# print(f'StopCondition: {pgate.GetStringArrayParameter(10)}')
# print(f'Setting Propagator: {pgate.SetField("Propagator", "Prop")}')
# print(f'Setting Sat: {pgate.SetObject("Sat", gmat.SPACECRAFT)}')

# bf = gmat.FiniteThrust("Thrust")
# bf.SetRefObjectName(gmat.SPACECRAFT, s.GetName())
# bf.SetReference(b)
# gmat.ConfigManager.Instance().AddPhysicalModel(bf)

# print(pgate.GetWrapperObjectNameArray())
# print(pgate.SetElementWrapper(ela, 'name'))
# gmat.ConfigManager.Instance().GetElementWrapper(ela.GetName())

# gmat.Initialize()

# print(pgate.GetRefObjectTypeArray())  # (134 - PROP_SETUP, 101 - Spacecraft, 122 - Parameter)
# print(f'Setting objects:\n'
#       f'- Propagator: {pgate.SetObject(prop.GetName(), gmat.PROP_SETUP)},\n'
#       f'- Stop Condition: {pgate.SetObject(stop_cond.GetName(), gmat.STOP_CONDITION)}\n'
#       f'- Sat: {pgate.SetObject(sat.GetName(), gmat.SPACECRAFT)}\n')

# bf.SetReference(b)
# gmat.ConfigManager.Instance().AddPhysicalModel(bf)

# print(ela.GetObjectTypeString(116))

# gmat.Initialize()  # 116: SpacePoint

# print(f'pgate Initialize: {pgate.Initialize()}')

# STOP_CONDITION: 126, PROPAGATOR: 110

# gmatpy._py39.gmat_py.APIException: Command Exception: Object map has not been initialized for Propagate

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

# print(stop_cond.GetStopParameter())
# print(stop_cond.GetGoalParameter())

# print(f'pgate Propagator: {pgate.GetField("Propagator")}')

# goal_param = gmat.Moderator.Instance().CreateParameter('UserParam', 'Goal', stop_cond.GetName())
# gmat.ConfigManager.Instance().AddParameter(goal_param)
# stop_cond.SetGoalParameter()

# om = gmat.ConfigManager.Instance().GetObjectMap()
# print(pgate.SetGlobalObjectMap(om))

# CustomHelp(pgate)

# pgate.Initialize()
# print(pgate.Execute())

# print(f'ela fields: {gpy.gmat_obj_field_list(ela)}\n')

# pgate.Help()

# psm = prop.GetPropStateManager()
# psm.BuildState()
# sat_ele = psm.ElementMapForSat()
# print(sat_ele)

# sb = gmat.Sandbox()
# bms = gmat.BeginMissionSequence()
# bms.Help()
# sb.AddCommand(bms)
# sb.AddCommand(pgate)
# sb.AddSolarSystem(gmat.GetSolarSystem())
# cs = gmat.ConfigManager.Instance().GetCoordinateSystem(sat.GetField('CoordinateSystem'))
# sb.SetInternalCoordSystem(cs)
# sb.Initialize()

# pgate.TakeAction('PrepareToPropagate')

# print(f'\npgate fields: {gpy.gmat_obj_field_list(pgate)}')

# pgate.Initialize()
# print(pgate.GetObjectList())

# print(pgate.GetParameterTypeString('StopTolerance'))
