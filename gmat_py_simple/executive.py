from __future__ import annotations

import gmat_py_simple as gpy
from load_gmat import gmat
from gmat_py_simple import GmatCommand

import sys


def RunMission(mcs: list[GmatCommand]) -> int:
    return gpy.Moderator().RunMission(mcs)


class Moderator:
    def __init__(self):
        self.gmat_obj = gmat.Moderator.Instance()

    def Initialize(self):
        self.gmat_obj.Initialize()

    def AppendCommand(self, command: GmatCommand) -> bool:
        return self.gmat_obj.AppendCommand(command.gmat_obj)

    def CreateCommand(self, command_type: str, name: str) -> gmat.GmatCommand:
        # True (retFlag) isn't actually used in source, but still required
        # See GMT-8100 for issue about bool passing bug
        return self.gmat_obj.CreateCommand(command_type, name, True)

    def CreateDefaultCommand(self, command_type: str = 'Propagate', name: str = ''):
        return self.gmat_obj.CreateDefaultCommand(command_type, name)

    def CreateDefaultMission(self):
        return self.gmat_obj.CreateDefaultMission()

    def CreateDefaultPropSetup(self):
        return self.gmat_obj.CreateDefaultPropSetup()

    def CreateSpacecraft(self):
        return self.gmat_obj.CreateSpacecraft('Spacecraft', 'DefaultSC', True)

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
        try:
            new_param = self.gmat_obj.CreateParameter(param_type, name)
        except Exception as ex:
            if type(ex).__name__ == 'APIException':
                raise gpy.APIException(ex) from ex
            else:
                raise ex
        if new_param is not None:
            return new_param  # GMAT Swig Parameter type
        else:
            raise RuntimeError(f'CreateParameter failed to create a parameter of type {param_type} called {name}')

    def CreateStopCondition(self, name: str) -> gmat.StopCondition:
        return self.gmat_obj.CreateStopCondition('StopCondition', name)

    def FindObject(self, name: str):
        raise NotImplementedError('Method available within GMAT but not exposed in API')
        # return self.gmat_obj.FindObject(name)

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

    @staticmethod
    def GetParameter(name: str):
        obj = gmat.Validator.Instance().FindObject(name)
        # instead of Validator, could use ElementWrapper or Moderator
        if obj and obj.IsOfType(gmat.PARAMETER):
            if type(obj).__name__ == 'GmatBase':
                # Convert to Swig Parameter (the type required for a Parameter function argument)
                obj: gmat.Parameter = gpy.GmatBase_to_Parameter(obj)
                print(type(obj))
            return obj  # obj is a Swig Parameter
        else:
            return None  # Parameter not found

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

    @staticmethod
    def GetSandbox():
        return gpy.Sandbox()

    def GetFirstCommand(self):
        return self.gmat_obj.GetFirstCommand()

    def InsertCommand(self, command_to_insert: GmatCommand, preceding_command: GmatCommand):
        return self.gmat_obj.InsertCommand(command_to_insert, preceding_command)

    def RunMission(self, mission_command_sequence: list[GmatCommand]) -> int:
        """
        Run the mission command sequence

        IMPORTANT: this method has different behaviour and an extra argument relative to the native GMAT method.

        :param mission_command_sequence:
        :return:
        """
        if not isinstance(mission_command_sequence, list):
            raise TypeError('mission_command_sequence must be a list of GmatCommand objects'
                            ' (e.g. BeginMissionSequence, Propagate)')

        # gmat.Initialize()
        mod = gpy.Moderator()
        sb = mod.GetSandbox()

        vdator = gmat.Validator.Instance()
        vdator.SetSolarSystem(gmat.GetSolarSystem())
        vdator.SetObjectMap(mod.GetConfiguredObjectMap())

        propagate_commands: list[gpy.Propagate] = []  # start a list of Propagates so their sats can be updated later
        for command in mission_command_sequence:
            try:
                command.SetSolarSystem(gmat.GetSolarSystem())
                # command.SetObjectMap(sb.GetObjectMap())
                command.SetObjectMap(mod.GetConfiguredObjectMap())
                command.SetGlobalObjectMap(sb.GetGlobalObjectMap())
                command.Initialize()

                appended = mod.AppendCommand(command)
                if not appended:
                    raise RuntimeError(f'Command {command.name} was not successfully appended to the Moderator in'
                                       f' RunMission. Returned value: {appended}')
                mod.ValidateCommand(command)

                if isinstance(command, gpy.Propagate):
                    propagate_commands.append(command)
                    command.TakeAction('PrepareToPropagate')
            except SystemExit as sys_exit:
                raise RuntimeError(f'GMAT attempted to stop code execution while processing command {command} - '
                                   f'{sys_exit}')

        print('\nMission Command Sequence setup complete. Running mission...')

        run_mission_return = self.gmat_obj.RunMission()
        if run_mission_return == 1:
            print(f'Mission run complete!\n')
            for propagate in propagate_commands:
                propagate.wrapper_sat.was_propagated = True  # mark sat as propagated so GetState uses runtime values
            return run_mission_return
        elif run_mission_return == -1:
            raise RuntimeError('Sandbox number given to gmat.Moderator.RunMission() was invalid')
        elif run_mission_return == -2:
            raise RuntimeError('An exception was thrown during Sandbox initialization. See GMAT log for details')
        elif run_mission_return == -3:
            raise RuntimeError('An unknown error during Sandbox initialization. See GMAT log for details')
        elif run_mission_return == -4:
            raise RuntimeError('Execution of RunMission() was interrupted by the user')
        elif run_mission_return == -5:
            raise RuntimeError('An exception was thrown during Sandbox execution. See GMAT log for details')
        elif run_mission_return == -6:
            raise RuntimeError('An unknown error during Sandbox execution. See GMAT log for details')
        else:
            raise RuntimeError(f'RunMission return value not recognized: {run_mission_return}.'
                               f' See GMAT log for possible hints')

    def ValidateCommand(self, command: GmatCommand | gmat.GmatCommand):
        command = gpy.extract_gmat_obj(command)
        self.gmat_obj.ValidateCommand(command)


class Sandbox:
    def __init__(self):
        self.gmat_obj = gmat.Moderator.Instance().GetSandbox()

    def AddCommand(self, command: gpy.GmatCommand | gmat.GmatCommand):
        return self.gmat_obj.AddCommand(gpy.extract_gmat_obj(command))

    def GetObjectMap(self) -> gmat.ObjectMap:
        return self.gmat_obj.GetObjectMap()

    def GetGlobalObjectMap(self) -> gmat.ObjectMap:
        return self.gmat_obj.GetGlobalObjectMap()
