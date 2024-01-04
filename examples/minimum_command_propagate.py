# Minimum Propagate example
# Written by William Easdown Babb

from __future__ import annotations

from load_gmat import gmat


mod = gmat.Moderator.Instance()


def GetState(spacecraft) -> list[float]:
    state: list[float | None] = [None] * 6
    for i in range(13, 19):
        state[i - 13] = float(spacecraft.GetField(i))  # int field refs used to be state type agnostic
    return state


internal_coord_sys = mod.CreateCoordinateSystem('InternalEarthMJ2000Eq', True, True)
sat = mod.CreateSpacecraft('Spacecraft', 'DefaultSC')  # create Spacecraft object
sat.SetInternalCoordSystem(internal_coord_sys)  # assign internal coordinate system to sat
sat.SetRefObject(mod.GetCoordinateSystem('EarthMJ2000Eq'), gmat.COORDINATE_SYSTEM, 'EarthMJ2000Eq')

print(f'Before running mission: {GetState(sat)}')

fm = gmat.ODEModel('DefaultPropSetup_ForceModel')  # create a ForceModel/ODEModel
prop = mod.CreateDefaultPropSetup('DefaultPropSetup')  # Propagator object
prop.SetODEModel(fm)  # attach the ForceModel to the Propagator

gmat.Initialize()

mod.CreateDefaultParameters()

epoch_var = f'{sat.GetName()}.A1ModJulian'
stop_var = f'{sat.GetName()}.ElapsedSecs'
stop_cond = gmat.StopCondition(f'StopOn{stop_var}')  # create StopCondition object

if not mod.GetParameter(epoch_var):
    param = mod.CreateParameter('A1ModJulian', epoch_var)
    # SetRefObjectName() doesn't work with params from mod.CreateParameter(), so use Validator to convert
    param = gmat.Validator.Instance().FindObject(param.name)
    param.SetRefObjectName(gmat.SPACECRAFT, sat.GetName())
if not mod.GetParameter(stop_var):
    param = gpy.Parameter('ElapsedSecs', stop_var)
    # SetRefObjectName() doesn't work with params from mod.CreateParameter(), so use Validator to convert
    param = gmat.Validator.Instance().FindObject(param.name)
    param.SetRefObjectName(gmat.SPACECRAFT, sat.GetName())

# Set stop parameters
stop_cond.SetStringParameter('EpochVar', epoch_var)  # A1ModJulian
stop_cond.SetStringParameter('StopVar', stop_var)  # ElapsedSecs
stop_cond.SetStringParameter('Goal', str(12000.0))

# Create and setup Propagate command
# pgate = gmat.Propagate()
pgate = mod.CreateDefaultCommand('Propagate')
# print(type(pgate), pgate.GetTypeName())
pgate.SetName('DefaultPropagate')
# pgate.SetObject(prop.GetName(), gmat.PROP_SETUP)  # attach Propagator to Propagate
# pgate.SetObject(sat.GetName(), gmat.SPACECRAFT)  # attach Spacecraft to Propagate

# TODO bugfix: SetRefObject() crashes if pgate = gmat.Propagate() (pgate type is _py312.gmat_py.Propagate) rather than
#  pgate = mod.CreateDefaultCommand('Propagate') (pgate type is gmat_py.GmatCommand)
# pgate.SetRefObject(stop_cond, gmat.STOP_CONDITION, '', 0)  # attach Propagator to Propagate
# pgate.SetSolarSystem(gmat.GetSolarSystem())

# Mission Command Sequence
mcs = [
    gmat.BeginMissionSequence(),  # BeginMissionSequence command
    pgate  # Propagate to Sat.ElapsedSecs = 12000.0
]

for command in mcs:
    if not isinstance(command, gmat.BeginMissionSequence):
        command.SetObjectMap(mod.GetConfiguredObjectMap())
        command.SetGlobalObjectMap(gmat.Sandbox().GetGlobalObjectMap())

        valid = gmat.Validator.Instance().ValidateCommand(command)
        command.Initialize()
        mod.AppendCommand(command)

mod.RunMission()
sat = gmat.GetRuntimeObject(sat.GetName())  # update Spacecraft object now it's been propagated

print(f'After running mission: {GetState(sat)}')
