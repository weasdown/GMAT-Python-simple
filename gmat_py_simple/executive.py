from __future__ import annotations
from typing import Type

import gmat_py_simple.utils
from load_gmat import gmat
from gmat_py_simple import GmatCommand


class Moderator:
    def __init__(self):
        self.gmat_obj = gmat.Moderator.Instance()

    def Initialize(self):
        self.gmat_obj.Initialize()

    def AppendCommand(self, command_to_append: GmatCommand):
        return self.gmat_obj.AppendCommand(command_to_append)

    def CreateCommand(self, command_type: str, name: str) -> gmat.GmatCommand:
        # True (retFlag) isn't actually used in source, but still required
        # See GMT-8100 for issue about bool passing bug
        return self.gmat_obj.CreateCommand(command_type, name, True)

    def CreateDefaultCommand(self, command_type: str = 'Propagate', name: str = ''):
        return self.gmat_obj.CreateDefaultCommand(command_type, name)

    def CreateDefaultMission(self):
        self.gmat_obj.CreateDefaultMission()

    def CreateDefaultStopCondition(self) -> gmat.StopCondition:
        sc: gmat.Spacecraft = self.GetDefaultSpacecraft()
        sc_name: str = sc.GetName()
        epoch_var = f'{sc_name}.A1ModJulian'  # EpochVar is mEpochParamName in StopCondition source
        stop_var = f'{sc_name}.ElapsedSecs'  # StopVar is mStopParamName in StopCondition source

        mod = Moderator()
        if not mod.GetParameter(epoch_var):
            epoch_param = gmat.Moderator.Instance().CreateParameter('A1ModJulian', epoch_var)
            gmat.Moderator.Instance().SetParameterRefObject(epoch_param, 'Spacecraft', sc_name, '', '', 0)
            # epoch_param = gmat.GetObject(epoch_var)
            # epoch_param.Initialize()

        if not mod.GetParameter(stop_var):
            stop_param: gmat.Parameter = mod.gmat_obj.CreateParameter('ElapsedSecs', stop_var)
            # stop_param.SetRefObjectName(gmat.SPACECRAFT, sc_name)
            # stop_param = gmat.GetObject(epoch_var)
            # stop_param.Initialize()
            gmat.Moderator.Instance().SetParameterRefObject(stop_param, 'Spacecraft', sc_name, '', '', 0)

        stop_cond_name = f'StopOn{stop_var}'
        stop_cond: gmat.StopCondition = mod.CreateStopCondition(stop_cond_name)
        stop_cond.SetStringParameter('EpochVar', epoch_var)  # EpochVar is mEpochParamName in StopCondition source
        stop_cond.SetStringParameter('StopVar', stop_var)  # StopVar is mStopParamName in StopCondition source
        stop_cond.SetStringParameter('Goal', '12000.0')  # SetRhsString() called with goal value in source

        # gmat.Initialize()

        return stop_cond

    def CreateParameter(self, param_type: str, name: str):
        return self.gmat_obj.CreateParameter(param_type, name)

    def CreateStopCondition(self, name: str) -> gmat.StopCondition:
        return self.gmat_obj.CreateStopCondition('StopCondition', name)

    def GetConfiguredObject(self, name: str) -> gmat.GmatBase:
        return self.gmat_obj.GetConfiguredObject(name)

    def GetConfiguredObjectMap(self):
        return self.gmat_obj.GetConfiguredObjectMap()

    def GetDefaultPropSetup(self) -> gmat.PropSetup:
        config_list: list[str] = self.gmat_obj.GetListOfObjects(gmat.SPACECRAFT)
        if config_list:  # list length > 0
            return self.gmat_obj.GetPropSetup(config_list[0])
        else:  # no spacecraft found, so create one
            return self.gmat_obj.CreatePropSetup('DefaultProp')

    def GetDefaultSpacecraft(self) -> gmat.Spacecraft:
        so_config_list: list[str] = self.gmat_obj.GetListOfObjects(gmat.SPACECRAFT)
        if so_config_list:  # list length > 0
            return self.gmat_obj.GetSpacecraft(so_config_list[0])
        else:  # no spacecraft found, so create one
            return self.gmat_obj.CreateSpacecraft('Spacecraft', 'DefaultSC')

    def GetDetailedRunState(self):
        drs = self.gmat_obj.GetDetailedRunState()
        if drs == 10000:
            return 'IDLE'
        elif drs == 10001:
            return 'RUNNING'
        elif drs == 10002:
            return 'PAUSED'
        # TODO: add options for optimizer state etc
        else:
            raise Exception(f'Detailed run state not recognised: {drs}')

    def GetListOfObjects(self, obj_type: int, exclude_defaults: bool = False, type_max: int = 0) -> list[str]:
        return self.gmat_obj.GetListOfObjects(obj_type, exclude_defaults, type_max)

    def GetParameter(self, param: str) -> gmat.Parameter:
        return self.gmat_obj.GetParameter(param)

    def GetSpacecraftNotInFormation(self) -> str:
        return self.gmat_obj.GetSpacecraftNotInFormation()

    def GetRunState(self):
        rs = self.gmat_obj.GetRunState()
        if rs == 10000:
            return 'IDLE', 10000
        elif rs == 10001:
            return 'RUNNING', 10001
        elif rs == 10002:
            return 'PAUSED', 10002
        else:
            raise Exception(f'Run state not recognised: {rs}')

    def GetSandbox(self):
        return self.gmat_obj.GetSandbox()

    def GetFirstCommand(self):
        return self.gmat_obj.GetFirstCommand()

    def InsertCommand(self, command_to_insert: GmatCommand, preceding_command: GmatCommand):
        return self.gmat_obj.InsertCommand(command_to_insert, preceding_command)

    def RunMission(self):
        return self.gmat_obj.RunMission()

