# Minimum Propagate example, written by William Easdown Babb.
# Note this does not work with apoapsis/periapsis - these will be demonstrated in separate examples

from __future__ import annotations
from load_gmat import gmat
import gmat_py_simple as gpy
import os

# Set log and script options
log_path = os.path.normpath(f'{os.getcwd()}/GMAT-Log.txt')
gmat.UseLogFile(log_path)

ss = gmat.GetSolarSystem()
mod = gmat.Moderator.Instance()
sb = gmat.Sandbox()


# Custom function to give state for any Spacecraft object (from gmat.GetObject() or gmat.GetRuntimeObject())
def GetState(spacecraft) -> list[float]:
    state: list[float | None] = [None] * 6
    for i in range(13, 19):
        state[i - 13] = float(spacecraft.GetField(i))  # int field refs used to be state type agnostic
    return state


internal_coord_sys = mod.CreateCoordinateSystem('InternalEarthMJ2000Eq', True, True)  # create coord sys for use in sat
sat = mod.CreateSpacecraft('Spacecraft', 'DefaultSC')  # create Spacecraft object
# sat = gmat.Spacecraft('DefaultSC')  # create Spacecraft object
sat.SetInternalCoordSystem(internal_coord_sys)  # attach internal coordinate system to sat
sat.SetRefObject(mod.GetCoordinateSystem('EarthMJ2000Eq'), gmat.COORDINATE_SYSTEM, 'EarthMJ2000Eq')  # attach CS to sat

print(f'Before running mission: {GetState(sat)}')

fm = mod.CreateODEModel('ForceModel', 'NonDefaultPropSetup_ForceModel')  # create a ForceModel/ODEModel
fm.SetSolarSystem(ss)
fm.Initialize()
prop = mod.CreateDefaultPropSetup('DefaultPropSetup')  # Propagator object
prop.SetODEModel(fm)  # attach the ForceModel to the Propagator
prop.Initialize()

gmat.Initialize()

epoch_var = f'{sat.GetName()}.A1ModJulian'  # create an epoch variable
stop_var = f'{sat.GetName()}.ElapsedSecs'  # create a stop variable
stop_cond_name = f'StopOn{stop_var}'
stop_cond = gmat.StopCondition(f'StopOn{stop_var}')  # create StopCondition object

# Setup Validator for use during Parameter creation
vdator = gmat.Validator.Instance()
vdator.SetSolarSystem(ss)
vdator.SetObjectMap(mod.GetConfiguredObjectMap())

if not mod.GetParameter(epoch_var):
    mod.CreateParameter('A1ModJulian', epoch_var)  # returns <class 'SwigPyObject'>
    # SetRefObjectName() doesn't work with params from mod.CreateParameter(), so use Validator to convert
    param = gmat.Validator.Instance().FindObject(epoch_var)  # returns <class 'gmat_py.GmatBase'>
    param.SetRefObjectName(gmat.SPACECRAFT, sat.GetName())  # attach Spacecraft to Parameter

if not mod.GetParameter(stop_var):
    mod.CreateParameter('ElapsedSecs', stop_var)  # returns <class 'SwigPyObject'>
    # SetRefObjectName() doesn't work with params from mod.CreateParameter(), so use Validator to convert
    param = gmat.Validator.Instance().FindObject(stop_var)  # returns <class 'gmat_py.GmatBase'>
    param.SetRefObjectName(gmat.SPACECRAFT, sat.GetName())  # attach Spacecraft to Parameter

# Set stop parameters
stop_cond.SetStringParameter('EpochVar', epoch_var)  # A1ModJulian
stop_cond.SetStringParameter('StopVar', stop_var)  # ElapsedSecs
stop_cond.SetStringParameter('Goal', str(86400))  # 12000.0 seconds

# add the StopCondition to the ConfigManager, so it can later be used as a ref object by Propagate
gmat.ConfigManager.Instance().AddObject(gmat.STOP_CONDITION, stop_cond)

# gmat.Initialize()

# Create and setup Propagate command
# pgate = gmat.Propagate()
# noop = mod.GetFirstCommand()
# default_pgate_name = 'Propagate'
pgate_name = 'DefaultPropagateCommand'
# pgate = mod.CreateDefaultCommand('Propagate')
pgate = gpy.Propagate(pgate_name, prop, sat)
print(f'\nCM list before creating Propagate: {gmat.ConfigManager.Instance().GetListOfAllItems()}\n')
# pgate = gmat.Propagate()
# pgate = gpy.GmatCommand.ClearDefaultObjects(pgate)
# pgate.SetName(pgate_name)
# pgate = gmat.Propagate()
# pgate.ClearObject()
# pgate = gmat.Validator.Instance().FindObject(pgate_name)  # returns <class 'gmat_py.GmatBase'>
# pgate = gmat.FindObject(noop, gmat.COMMAND, pgate_name)
# print(f'\nCM list before pgate.Init, Init(pgate): {gmat.ConfigManager.Instance().GetListOfAllItems()}\n')
# gmat.GmatCommand().Append(pgate)
# commands = gmat.GetCommands('')
# print(f'\n{*commands}, {type(*commands)}')
# print('\n'.join([f'Name: {command.GetName()}, type: {command.GetTypeName()}' for command in commands]))
# pgate.SetSolarSystem(gmat.GetSolarSystem())
# pgate.SetObjectMap(mod.GetConfiguredObjectMap())
# pgate.SetGlobalObjectMap(gmat.Sandbox().GetGlobalObjectMap())
print(f'pgate type: {type(pgate)}')

# pgate.SetRefObject(stop_cond, gmat.STOP_CONDITION, stop_cond_name, 0)  # attach StopCondition to Propagate command

# pgate.Initialize()
print(f'prop IsInitialized? {prop.IsInitialized()}')
# gmat.Initialize()
# print(pgate.SetObject(prop.GetName(), gmat.PROP_SETUP))
# pgate.SetObject(sat.GetName(), gmat.SPACECRAFT)

# Create and setup StopCondition object
# stop_cond_name = f'StopOn{sat.GetName()}.ElapsedSecs'
# stop_cond = mod.CreateStopCondition('StopCondition', stop_cond_name)  # create StopCondition object
# stop_cond = pgate.GetRefObject(gmat.STOP_CONDITION, f'StopOn{sat.GetName()}.ElapsedSecs', 0)

# propagate.SetSolarSystem(gmat.GetSolarSystem())
# propagate.SetObjectMap(mod.GetConfiguredObjectMap())
# propagate.SetGlobalObjectMap(gmat.Sandbox().GetGlobalObjectMap())
# propagate.Initialize()

# stop_var_str = stop_cond.GetStringParameter('StopVar')
# goal_str = stop_cond.GetStringParameter('Goal')

# gmat.Initialize()
# pgate = gmat.Validator.Instance().FindObject(pgate.GetName())  # returns <class 'gmat_py.GmatBase'>
# print(f'{pgate}, {type(pgate)}')
# print(f'CM list of all: {gmat.ConfigManager.Instance().GetListOfAllItems()}')
# print(f'Command list: {gmat.GetCommands("Propagate")}')

# print(sb.AddCommand(pgate))
gmat.Initialize()

# Mission Command Sequence
mcs = [gmat.BeginMissionSequence(),  # BeginMissionSequence command (required at start of sequence)
       pgate]  # Propagate to Sat.ElapsedSecs = 12000.0

for command in mcs:
    command.SetSolarSystem(gmat.GetSolarSystem())
    command.SetObjectMap(mod.GetConfiguredObjectMap())
    command.SetGlobalObjectMap(gmat.Sandbox().GetGlobalObjectMap())

    valid = gmat.Validator.Instance().ValidateCommand(command)
    command.Initialize()

    mod.AppendCommand(command)
    command_list = gmat.GetCommands()
    print(command_list)
    # print(f'Command list: {[f"{command.GetTypeName()} named \"{command.GetName()}\"" for command in command_list]}\n')
    print('\nCommand list:')
    print(''.join([f'Name: {command.GetName()}, type: {command.GetTypeName()}\n' for command in command_list]))

mod.RunMission()
sat = gmat.GetRuntimeObject(sat.GetName())  # update Spacecraft object now it's been propagated

print(f'After running mission: {GetState(sat)}')
