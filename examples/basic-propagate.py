from __future__ import annotations

from load_gmat import gmat

import os

log_path = os.path.normpath(f'{os.getcwd()}/GMAT-Log.txt')
gmat.UseLogFile(log_path)

gmat.Clear()

script_path = os.path.normpath(f'{os.getcwd()}/basic-propagate.script')


def GetState(sc):
    state: list[None | float] = [None] * 6
    for i in range(13, 19):
        state[i - 13] = float(sat.GetField(i))
    return state


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
sat = gmat.GetObject('DefaultSC')

gmat.Initialize()

# Add the PropSetup and Spacecraft to the Sandbox
sb.AddObject(prop)
sb.AddObject(sat)

# Link the Propagate command to all the other objects
pgate.SetSolarSystem(gmat.GetSolarSystem())
pgate.SetObjectMap(gmat.Moderator.Instance().GetConfiguredObjectMap())
pgate.SetGlobalObjectMap(sb.GetGlobalObjectMap())

pgate.Initialize()

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

sat = gmat.GetRuntimeObject(sat.GetName())
print(f'Sat state after running: {GetState(sat)}')
print(f'Sat epoch after running: {sat.GetField("Epoch")}')

gmat.SaveScript(script_path)
