from load_gmat import gmat

import gmat_py_simple as gpy
# import gmat_py_simple.utils
# from gmat_py_simple import orbit as o
# from gmat_py_simple.orbit import PropSetup
# from gmat_py_simple.commands import Propagate

import os

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

# gmat.ShowClasses()

log_path = os.path.normpath(f'{os.getcwd()}/GMAT-Log.txt')
gmat.UseLogFile(log_path)

blank_path = ''
script_path = os.path.normpath(f'{os.getcwd()}/Tut01.script')  # {os.getcwd()}/Tut01.script
# gmat.LoadScript(blank_path)
# gmat.Clear()


# sat = gmat.Construct('Spacecraft', 'Sat')
# sat.SetField('Epoch', '21545')
# sat_name = sat.GetName()

# fm = gmat.Construct("ForceModel", "FM")
# epm = gmat.Construct("PointMassForce", "EPM")
# fm.AddForce(epm)

# prop = gmat.Construct("Propagator", "Prop")
# gator = gmat.Construct("PrinceDormand78", "Gator")
# prop.SetReference(gator)
# prop.SetReference(fm)
#
# gmat.Initialize()
# prop.AddPropObject(sat)
# prop.PrepareInternals()
#
# gator = prop.GetPropagator()
#
# state = gator.GetState()

# gmat.Initialize()

def CustomHelp(obj):
    print(f'\nCustomHelp for {obj.GetName()}:')
    if 'gmat_py_simple' in str(type(obj)):
        param_count = obj.gmat_obj.GetParameterCount()
    else:
        param_count = obj.GetParameterCount()

    for i in range(param_count - 1):
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


# pgate = gmat.Construct('Propagate')
# # gmat.ShowObjects()
#
# print(gmat.GetCommands())
#
# pgate.SetSolarSystem(gmat.GetSolarSystem())
# pgate.SetGlobalObjectMap(gmat.Sandbox.GetGlobalObjectMap(gmat.Sandbox()))
# pgate.SetObjectMap(gmat.Sandbox.GetObjectMap(gmat.Sandbox()))
#
# stop_cond = gmat.Construct('StopCondition', 'StopForSatSecs')
# stop_param_str = f'{sat.GetName()}.ElapsedSecs ='
# stop_param_str_no_eq = stop_param_str[:-2]
# stop_cond.SetLhsString(stop_param_str_no_eq)
# goal_param_str = '8640.0'
# stop_cond.SetRhsString(goal_param_str)
# stop_cond.SetSpacecrafts([sat], [sat])
#
# # craft_param = gmat.Construct('Variable', 'SatParam')
# # craft_param.SetField('InitialValue', stop_param_str)
# # ela = gmat.Construct('ElapsedSecs', 'Sat.ElapsedSecs')
# # ela.SetField('Object', sat_name)
# # ela.SetRefObject(sat, gmat.SPACECRAFT, sat.GetName())
# # ela.Initialize()
# # ela_param = gmat.ConfigManager.Instance().GetParameter(ela.GetName())
#
# # stop_param_default = stop_cond.GetStopParameter()
# # stop_cond.SetStopParameter(ela_param)
# # craft_param = gmat.ConfigManager.Instance().GetParameter(ela.GetName())
#
# # mod = gmat.Moderator.Instance()
# # craft_param = mod.CreateParameter('String', stop_param_str)
#
# # stop_param = sat.GetGmatTimeParameter(f'{sat.GetName()}.ElapsedSecs')
# stop_param = gmat.Construct('ElapsedSecs', stop_param_str_no_eq)
# stop_param.SetField('Object', sat.GetName())
# stop_param.SetRefObject(sat, gmat.SPACECRAFT, sat.GetName())
# stop_param.SetField('InitialValue', stop_param_str)
# stop_param.SetField('Expression', str(0))
# stop_param.SetField('Description', 'Elapsed Secs')
# stop_param.SetField('Unit', 's')
# stop_param.SetField('InitialEpoch', sat.GetState().GetEpoch())
# stop_param.SetReference(sat)
# stop_param.Initialize()
# # stop_param = gmat.Moderator.Instance().GetInternalObject('Sat.ElapsedSecs')
# stop_param = gmat.ConfigManager.Instance().GetParameter(stop_param.GetName())
# # stop_param = gmat.GetObject(stop_param_str)
# # print(f'stop_param:\n{stop_param}, type: {type(stop_param)}')
# stop_cond.SetStopParameter(stop_param)
# # print(f'stop param: {stop_cond.GetStopParameter()}')
# stop_cond.Validate()
# stop_cond.Initialize()
#
# # pgate.SetField('StopCondition', [stop_cond.GetName()])
# pgate.SetObject(stop_cond.GetName(), gmat.STOP_CONDITION)  # adds stop_cond name to output of pgate.GetObjectList()
# pgate.SetObject(stop_cond, gmat.STOP_CONDITION)  # adds stop_cond to output of pgate.GetGeneratingString()
# pgate.SetObject(prop.GetName(), gmat.PROP_SETUP)
# pgate.SetObject(sat.GetName(), gmat.SPACECRAFT)
#
# print(gmat.Update('Propagate'))
# print(gmat.Exists('Propagate'))
#
# print(f'pgate Validate: {pgate.Validate()}')
# # pgate.Initialize()
# # CustomHelp(pgate)
#
# print(f'Check stop conditions: {pgate.TakeAction("CheckStopConditions")}')
# # print(pgate.TakeAction('PrepareToPropagate'))
# # print(f'\npgate fields: {gpy.gmat_obj_field_list(pgate)}')
# # print(f'\nstop_cond fields: {gpy.gmat_obj_field_list(stop_cond)}')
# # print(f'\nstop_param fields: {gpy.gmat_obj_field_list(stop_param)}')
#
# # print(f'\npgate:\n{pgate}, type: {type(pgate)}\n\n'
# #       f'stop_cond:\n{stop_cond}, type: {type(stop_cond)}\n\n'
# #       f'stop_param:\n{stop_param}, type: {type(stop_param)}')
#
# print(f'pgate object list: {pgate.GetObjectList()}')
#
# # bms = gmat.BeginMissionSequence()
#
# print('\n', pgate.GetGeneratingString())

# We can use CreateDefaultCommand to make a default version of a Propagate command, that we'll then modify

sb = gmat.Moderator.Instance().GetSandbox()
cm = gmat.ConfigManager.Instance()
ss = gmat.GetSolarSystem()

# sb.AddSolarSystem(gmat.GetSolarSystem())

bms = gmat.Moderator.Instance().CreateDefaultCommand('BeginMissionSequence')
sb.AddCommand(bms)
bms.SetObjectMap(sb.GetObjectMap())
bms.SetGlobalObjectMap(sb.GetGlobalObjectMap())
bms.SetSolarSystem(gmat.GetSolarSystem())
bms.Initialize()
print(f'bmsIsI: {bms.IsInitialized()}')
gmat.Initialize()

pgate = gmat.Moderator.Instance().CreateDefaultCommand('Propagate', 'Elapsed')
sb.AddObject(pgate)
pgate.SetSolarSystem(gmat.GetSolarSystem())

# NOT YET IN SANDBOX
sat = gmat.GetObject(pgate.GetRefObjectName(gmat.SPACECRAFT))
sb.AddObject(sat)
pgate.SetObject(sat.GetName(), gmat.SPACECRAFT)

prop = gmat.GetObject(pgate.GetRefObjectName(gmat.PROP_SETUP))
sb.AddObject(prop)
pgate.SetObject(prop.GetName(), gmat.PROP_SETUP)

# # fm = prop.GetRefObjectName(gmat.ODE_MODEL)
# # fm = gmat.GetObject()
# prop.Help()
# fm = gmat.GetObject(prop.GetField('FM'))
# fm.SetSolarSystem(ss)
# prop.SetReference(fm)
#
# gator = prop.GetPropagator()
# prop.SetReference(fm)

prop.AddPropObject(sat)
gmat.Initialize()
# prop.SetReference(gmat.GetObject(prop.GetField('FM')).SetSolarSystem(ss))
# prop.PrepareInternals()

# gmat.Initialize()

# prop.Initialize()

pgate.SetObjectMap(gmat.ConfigManager.Instance().GetObjectMap())
pgate.SetGlobalObjectMap(sb.GetGlobalObjectMap())
pgate.Initialize()

# gmat.Initialize()
# gmat.ShowObjects()
# pgate = gmat.Moderator.Instance().AppendCommand('Propagate', 'NameNotUsed', True, 1)
# CreateDefaultCommand('Propagate', 'Pgate') has also created a default ForceModel and default Propagator, so get those

# gmat.Moderator.Instance().Initialize()
# gmat.Moderator.Instance().UpdateDataFiles()
# prop.Help()
# pgate.SetName('Pgate')
# pgate.SetGlobalObjectMap(gmat.Sandbox().GetGlobalObjectMap())
# pgate.SetObjectMap(gmat.ConfigManager.Instance().GetObjectMap())
# pgate.SetSolarSystem(gmat.GetSolarSystem())
# print(f'pgI:')
# # CustomHelp(pgate)
# print(pgate.Initialize())

# sat = gmat.GetObject('DefaultSC')
# mj = gmat.GetObject('DefaultSC.A1ModJulian')
# el = gmat.GetObject('DefaultSC.ElapsedSecs')
#
# mj.Help()
# el.Help()

# fm = gmat.GetObject('DefaultProp_ForceModel')
# prop = gmat.GetObject('DefaultProp')
# prop_name = prop.GetName()
# gmat.Initialize()

# pgate.SetObject(stop_cond.GetName(), gmat.STOP_CONDITION)  # adds stop_cond name to output of pgate.GetObjectList()
# pgate.SetObject(stop_cond, gmat.STOP_CONDITION)  # adds stop_cond to output of pgate.GetGeneratingString()
# pgate.SetField('Propagator', prop_name)
# pgate.SetObject(prop_name, gmat.PROP_SETUP)
# pgate.SetObject(sat.GetName(), gmat.SPACECRAFT)

# pgate.Help()
# gmat.Update()

# pgate.Initialize()  # 'Command Exception: Propagate command cannot find Propagator Setup "Prop"'

# def_stop_cond = gmat.GetObject('Sat.A1ModJulian')

# print(f'state: {sat.GetState().GetState()}')

print(f'Generating string for default Propagate command:\n{pgate.GetGeneratingString()}\n')
# print(f'\nGenerating string for default stop condition:\n{def_stop_cond.GetGeneratingString()}')

# pgate.Execute()

sat_name_from_pgate_field = pgate.GetField('Spacecraft')[1:-1]
coord_sys_name = gmat.GetObject(sat.GetName()).GetField('CoordinateSystem')
coord_sys = gmat.GetObject(coord_sys_name)
sb.SetInternalCoordSystem(coord_sys)

# print(f'pgate valid: {pgate.Validate()}')
# print(f'pgate Init: {pgate.Initialize()}')
# print(pgate.TakeAction('PrepareToPropagate'))

sb.AddCommand(bms)
sb.AddCommand(pgate)
sb.Initialize()

# print(sb.GetObjectMap())
# print(sb.GetGlobalObjectMap())

# pgate.SetGlobalObjectMap(sb.GetGlobalObjectMap())
# pgate.SetObjectMap(sb.GetObjectMap())

# **** ERROR **** Sandbox Exception: Errors were found in the mission control sequence; please correct the errors
# listed in the message window

print(f'CM item list: {gmat.ConfigManager.Instance().GetListOfAllItems()}')

mod = gmat.Moderator.Instance()



# print(mod.GetScript())

# print(mod.ShowObjectMap())
# mod.RunMission()

# sb.Initialize()
# bms = gmat.BeginMissionSequence()
# bms.Execute()

# print(pgate.TakeAction('PrepareToPropagate'))
# print(pgate.GetPropStatus())

# sb.Execute()

# print(f'state: {sat.GetState().GetState()}')

# gmat.SaveScript(script_path)
