from __future__ import annotations

from load_gmat import gmat

import gmat_py_simple as gpy
# import gmat_py_simple.utils
# from gmat_py_simple import orbit as o
# from gmat_py_simple.orbit import PropSetup
# from gmat_py_simple.commands import Propagate

import os

log_path = os.path.normpath(f'{os.getcwd()}/GMAT-Log.txt')
gmat.UseLogFile(log_path)

gmat.Clear()

script_path = os.path.normpath(f'{os.getcwd()}/Tut01.script')


# TODO complete modelling the tutorial mission (inc. add drag, prop to Periapsis)

def GetState(sc):
    state: list[None | float] = [None] * 6
    for i in range(13, 19):
        state[i - 13] = float(sat.GetField(i))
    return state


sat_params = {
    'Name': 'Sat',
    'Orbit': {
        'Epoch': '22 Jul 2014 11:29:10.811',
        'DateFormat': 'UTCGregorian',
        'CoordSys': 'EarthMJ2000Eq',
        'StateType': 'Keplerian',
        'SMA': 83474.31800000004,
        'ECC': 0.8965199999999998,
        'INC': 12.4606,
        'RAAN': 292.8362,
        'AOP': 218.9805,
        'TA': 180,
    },
}

sat = gpy.Spacecraft.from_dict(sat_params)

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

sb = gmat.Moderator.Instance().GetSandbox()
cm = gmat.ConfigManager.Instance()
ss = gmat.GetSolarSystem()
sb.AddSolarSystem(ss)

gmat.Initialize()

vdator = gmat.Validator.Instance()
vdator.SetSolarSystem(ss)
vdator.SetObjectMap(gmat.Moderator.Instance().GetConfiguredObjectMap())

# Create a BeginMissionSequence command
bms = gmat.Moderator.Instance().CreateDefaultCommand('BeginMissionSequence')
sb.AddCommand(bms)
bms.SetObjectMap(sb.GetObjectMap())
bms.SetGlobalObjectMap(sb.GetGlobalObjectMap())
bms.SetSolarSystem(gmat.GetSolarSystem())
bms.Initialize()

# Create a Propagate command
pgate = gmat.Moderator.Instance().CreateDefaultCommand('Propagate', 'Pgate')
sat_name_from_pgate_field = pgate.GetField('Spacecraft')[1:-1]
coord_sys_name = gmat.GetObject(sat_name_from_pgate_field).GetField('CoordinateSystem')
coord_sys = gmat.GetObject(coord_sys_name)
sb.SetInternalCoordSystem(coord_sys)

# We now need to get the Propagate command linked into the rest of the system
prop = gmat.GetObject('DefaultProp')
sat = gmat.GetObject(sat.GetName())

# Add the PropSetup and Spacecraft to the Sandbox
sb.AddObject(prop)
sb.AddObject(sat)

# Link the Propagate command to all the other objects
pgate.SetSolarSystem(gmat.GetSolarSystem())
pgate.SetObjectMap(gmat.Moderator.Instance().GetConfiguredObjectMap())
pgate.SetGlobalObjectMap(sb.GetGlobalObjectMap())

pgate.Initialize()

pgate.Initialize()

sb.Initialize()

pgate.SetObjectMap(gmat.ConfigManager.Instance().GetObjectMap())
pgate.SetGlobalObjectMap(sb.GetGlobalObjectMap())

# Add commands to the Mission Command Sequence
gmat.Moderator.Instance().AppendCommand(bms)
gmat.Moderator.Instance().AppendCommand(pgate)

print(f'Sat state before running: {sat.GetState().GetState()}')
print(f"Epoch before running: {sat.GetField('Epoch')}")

# Run the mission
run_mission_return_code = int(gmat.Moderator.Instance().RunMission())
if run_mission_return_code == 1:
    print(f'\nRunMission succeeded!\n')
else:
    raise Exception(f'RunMission did not complete successfully - returned code {run_mission_return_code}')

sat = gmat.GetRuntimeObject(sat.GetName())  # TODO: convert into a wrapper Spacecraft for easier handling
print(f'Sat state after running: {GetState(sat)}')
print(f'Sat epoch after running: {sat.GetField("Epoch")}')

gmat.SaveScript(script_path)
