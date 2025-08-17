# Minimum Propagate example, written by William Easdown Babb.
# Note this only works with ElapsedSecs/ElapsedDays. Other stop conditions will be demonstrated in separate examples

from __future__ import annotations
from load_gmat import gmat
import os

# Set log and script options
log_path = os.path.normpath(f'{os.getcwd()}/GMAT-Log.txt')
gmat.UseLogFile(log_path)
gmat.GmatGlobal.Instance().SetCommandEchoMode(
    True)  # enables "CurrentCommand: [command generating string]" print out in log
gmat.EchoLogFile(False)  # set to True to have the log also print to the console as it's written

# Shortcuts for later
ss = gmat.GetSolarSystem()
mod = gmat.Moderator.Instance()
sb = gmat.Sandbox()


# Custom function to give state for any Spacecraft object (from gmat.GetObject() or gmat.GetRuntimeObject())
def GetState(spacecraft) -> list[float]:
    state: list[float | None] = [None] * 6
    for i in range(13, 19):
        state[i - 13] = float(spacecraft.GetField(i))  # int field refs used to be state type agnostic
    return state


# sat = mod.CreateSpacecraft('Spacecraft', 'TestSC')  # create Spacecraft object
sat = gmat.Construct('Spacecraft', 'TestSC')  # create Spacecraft object
sat.SetField('DisplayStateType', 'Keplerian')  # to make periapsis/apoapsis stop conditions easier to verify
gmat.Initialize()  # needed for correct initial state

print(f'\nState before running mission: {GetState(sat)}')
print(f'Epoch before running mission: {sat.GetField("Epoch")}\n')

# # Setup Validator for use during Propagate creation - if not set, exceptions thrown in log (set EchoLogFile(True))
# vdator = gmat.Validator.Instance()
# vdator.SetSolarSystem(ss)
# vdator.SetObjectMap(mod.GetConfiguredObjectMap())

# Use default Propagate as basis then extract its ref objects and modify as needed
pgate_name = 'DefaultPropagateCommand'
pgate = mod.CreateDefaultCommand('Propagate')  # create Propagate object
pgate.SetName(pgate_name)  # CreateDefaultCommand() doesn't implement name, so set it manually
pgate.SetObjectMap(mod.GetConfiguredObjectMap())
pgate.SetGlobalObjectMap(gmat.Sandbox().GetGlobalObjectMap())
pgate.SetSolarSystem(gmat.GetSolarSystem())

# Initialize completes the attaching of PropSetup (and others?) to pgate, so required before we can access them
gmat.Initialize()
pgate.Initialize()

# Get names of Propagate's ref objects and extract the objects
sat_ref_name = pgate.GetRefObjectName(gmat.SPACECRAFT)
prop_ref_name = pgate.GetRefObjectName(gmat.PROP_SETUP)
prop_ref = pgate.GetRefObject(gmat.PROP_SETUP, prop_ref_name, 0)
sat_ref = gmat.GetObject(sat_ref_name)  # GetRefObject() throws an exception for Spacecraft so get from gmat.GetObject()
stop_cond_ref = pgate.GetGmatObject(gmat.STOP_CONDITION)

# Set custom stop condition parameters
# For epoch variable
epoch_var_type = 'A1ModJulian'
epoch_var = f'{sat_ref_name}.{epoch_var_type}'

# For stop variable (uncomment two lines for desired stop condition)
# For elapsed seconds = 60
# stop_var_type = 'ElapsedSecs'
# stop_var = f'{sat_ref_name}.{stop_var_type}'

# # For stop variable for Earth periapsis
stop_var_type = 'Periapsis'  # change to 'Apoapsis' for propagate to Earth apoapsis
stop_var = f'{sat_ref_name}.Earth.{stop_var_type}'

# For goal (uncomment desired line)
goal = 60.0  # elapsed secs = 60
# goal = f'{sat_ref_name}.Earth.Periapsis'  # Earth periapsis (or apoapsis similarly)

# Apply the parameters to the stop condition
stop_cond_ref.SetStringParameter('EpochVar', epoch_var)
stop_cond_ref.SetStringParameter('StopVar', stop_var)
stop_cond_ref.SetStringParameter('Goal', str(goal))

print(f'EpochVar: {stop_cond_ref.GetStringParameter("EpochVar")}')
print(f'StopVar: {stop_cond_ref.GetStringParameter("StopVar")}')
print(f'Goal: {stop_cond_ref.GetStringParameter("Goal")}')

# As well as the StopCondition's String Parameter's we also need to create relevant Parameters for wider GMAT
# Setup Validator for use during Parameter creation
vdator = gmat.Validator.Instance()
vdator.SetSolarSystem(ss)
vdator.SetObjectMap(mod.GetConfiguredObjectMap())

if not mod.GetParameter(epoch_var):
    vdator.CreateParameter(epoch_var_type, epoch_var)  # create a Parameter for epoch_var
    param = gmat.Validator.Instance().FindObject(epoch_var)
    param.SetRefObjectName(gmat.SPACECRAFT, sat.GetName())  # attach Spacecraft to Parameter

if not mod.GetParameter(stop_var):
    vdator.CreateParameter(stop_var_type, stop_var)  # create a Parameter for stop_var
    param = gmat.Validator.Instance().FindObject(stop_var)
    param.SetRefObjectName(gmat.SPACECRAFT, sat.GetName())  # attach Spacecraft to Parameter

# Mission Command Sequence
mcs = [gmat.BeginMissionSequence(),  # BeginMissionSequence command (required at start of sequence)
       pgate]  # Propagate command

for command in mcs:
    print(f'\n{command}')
    command.SetObjectMap(mod.GetConfiguredObjectMap())
    command.SetGlobalObjectMap(gmat.Sandbox().GetGlobalObjectMap())
    command.SetSolarSystem(gmat.GetSolarSystem())

    gmat.Validator.Instance().ValidateCommand(command)
    command.Initialize()
    mod.AppendCommand(command)
    gmat.Initialize()

print('Running mission...')
mod.RunMission()
print('Run complete!')

sat = gmat.GetRuntimeObject(sat_ref_name)  # update Spacecraft object now it's been propagated
print(f'\nState after running mission: {GetState(sat)}')
print(f'Epoch after running mission: {sat.GetField("Epoch")}\n')
