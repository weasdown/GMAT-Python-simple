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

    def AppendCommand(self, command: gpy.GmatCommand) -> bool:
        # print('\nEntered Moderator.AppendCommand()')
        try:
            # print(f'Command type in mod.AppendCommand: {type(command)}')
            # print(f'GenString in AppComm: {command.GetGeneratingString()}')
            print(f'\tAttempting to append command {command.gmat_obj.GetTypeName()} named "{command.name}" '
                  f'to the mission sequence')
            command_gmat_obj = gpy.extract_gmat_obj(command)
            resp: bool = self.gmat_obj.AppendCommand(command_gmat_obj)
            return resp
        except SystemExit as se:  # TODO bugfix: doesn't prevent hang
            print('SystemExit detected in Moderator.AppendCommand()!!')
            raise RuntimeError('Moderator.AppendCommand() attempted to raise a SystemExit:\nse') from se

        except Exception as ex:
            raise RuntimeError(f'\tModerator.AppendCommand() attempted to raise an Exception:\n\t\t{ex}') from ex

    def CreateCommand(self, command_type: str, name: str) -> gmat.GmatCommand:
        # True (retFlag) isn't actually used in source, but still required
        # See GMT-8100 for issue about bool passing bug
        return self.gmat_obj.CreateCommand(command_type, name, True)

    def CreateDefaultCommand(self, command_type: str = 'Propagate', name: str = ''):
        vdator = gpy.Validator()
        vdator.SetSolarSystem(gmat.GetSolarSystem())
        vdator.SetObjectMap(self.GetConfiguredObjectMap())

        return self.gmat_obj.CreateDefaultCommand(command_type, name)

    def CreateDefaultMission(self):
        return self.gmat_obj.CreateDefaultMission()

    def CreateDefaultPropSetup(self):
        return self.gmat_obj.CreateDefaultPropSetup()

    def CreateSpacecraft(self):
        return self.gmat_obj.CreateSpacecraft('Spacecraft', 'DefaultSC', True)

    def CreateDefaultStopCondition(self) -> gmat.StopCondition:
        """
        Create a default StopCondition.
        Based on src/Moderator.CreateDefaultStopCondition().

        :return:
        """

        print('\n** WARNING: USING DEFAULT STOP CONDITION **')  # warning used for debugging

        sat: gmat.Spacecraft = self.GetDefaultSpacecraft()
        sat_name: str = sat.GetName()
        epoch_var = f'{sat_name}.A1ModJulian'  # EpochVar is mEpochParamName in StopCondition source
        stop_var = f'{sat_name}.ElapsedSecs'  # StopVar is mStopParamName in StopCondition source

        if not self.GetParameter(epoch_var):
            epoch_param = gpy.Parameter('A1ModJulian', epoch_var)
            epoch_param.SetRefObjectName(gmat.SPACECRAFT, sat_name)

        if not self.GetParameter(stop_var):
            stop_param: gmat.Parameter = gpy.Parameter('ElapsedSecs', stop_var)
            stop_param.SetRefObjectName(gmat.SPACECRAFT, sat_name)

        stop_cond_name = f'StopOn{stop_var}'
        stop_cond: gmat.StopCondition = self.CreateStopCondition(stop_cond_name)
        stop_cond.SetStringParameter('EpochVar', epoch_var)  # EpochVar is mEpochParamName in StopCondition source
        stop_cond.SetStringParameter('StopVar', stop_var)  # StopVar is mStopParamName in StopCondition source
        # stop_cond.SetStringParameter('Goal', '12000.0')  # SetRhsString() called with goal value in source
        # TODO: remove test line below, uncomment actual default above
        stop_cond.SetStringParameter('Goal', '120')  # SetRhsString() called with goal value in source

        gpy.Initialize()

        return stop_cond

    def CreateParameter(self, param_type: str, name: str):
        try:
            new_param = self.gmat_obj.CreateParameter(param_type, name)
        except Exception as ex:
            if type(ex).__name__ == 'APIException':
                raise gpy.APIException(ex)
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
    def GetParameter(name: str) -> gmat.Parameter:
        vdator = gpy.Validator()
        vdator.SetSolarSystem(gmat.GetSolarSystem())
        vdator.SetObjectMap(gpy.Moderator().GetConfiguredObjectMap())

        obj = vdator.FindObject(name)
        # instead of Validator, could use ElementWrapper or Moderator
        if obj and obj.IsOfType(gmat.PARAMETER):
            if type(obj).__name__ == 'GmatBase':
                # Convert to Swig Parameter (the type required for a Parameter function argument)
                obj: gmat.Parameter = gpy.GmatBase_to_Parameter(obj)
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

    def Initialize(self):
        self.gmat_obj.Initialize()

    def InsertCommand(self, command_to_insert: GmatCommand, preceding_command: GmatCommand):
        return self.gmat_obj.InsertCommand(command_to_insert, preceding_command)

    def RemoveObject(self, obj_type: int, name: str, del_only_if_not_used: bool = True) -> bool:
        return self.gmat_obj.RemoveObject(obj_type, name, del_only_if_not_used)

    def RunMission(self, mission_command_sequence: list[GmatCommand]) -> int:
        """
        Run the mission command sequence

        IMPORTANT: this method has different behaviour and an extra argument relative to the native GMAT method.

        :param mission_command_sequence:
        :return:
        """

        def configure_command(comm: gmat.GmatCommand):
            mod = gmat.Moderator.Instance()
            try:
                sb = gmat.Sandbox()

                # TODO remove print and "if Target" (for debugging only)
                print('    In configure_command()')
                if isinstance(command, gpy.Target):
                    print('Echoing log file for Target command')
                    gmat.EchoLogFile(True)

                # # TODO remove if clause (for debugging only)
                # if isinstance(command, gpy.Propagate):
                #     print(f'\nCommand: {command.name}')
                #     stop_cond_obj: gmat.StopCondition = command.GetRefObject(gmat.STOP_CONDITION,
                #                                                              command.stop_cond.name, 0)
                #     stop_cond_ref_names = stop_cond_obj.GetRefObjectNameArray(gmat.PARAMETER)
                #     stop_cond_ref_types = stop_cond_obj.GetRefObjectTypeArray()
                #     print(stop_cond_ref_names)
                #     print(f'StopCond ref types: {stop_cond_ref_types}')
                #
                #     sep = gmat.GetObject(stop_cond_ref_names[0])
                #     sep.Help()
                #     sep_ref_names = sep.GetRefObjectNameArray(gmat.PARAMETER)
                #     print(sep_ref_names)
                #
                #     print(f'CM all list: {gmat.ConfigManager.Instance().GetListOfAllItems()}')
                #     # print(f'Find SpacePoint: {gmat.FindObject(command.gmat_obj, gmat.SPACE_POINT, )}')
                #     # print(f'scName: {gmat.GetRefObjectName(gmat.SPACE_POINT)}')

                obj_map = gmat.ConfigManager.Instance().GetObjectMap()

                comm.SetSolarSystem(gmat.GetSolarSystem())
                comm.SetObjectMap(obj_map)
                # comm.SetObjectMap(mod.GetConfiguredObjectMap())
                comm.SetGlobalObjectMap(sb.GetGlobalObjectMap())
                print('\tObject mapping complete')

                # print(f'\tValidate: {command.Validate()}')
                # print('\tValidate complete')
                # sb.AddCommand(command.gmat_obj)
                # print('\tsb.AppendCommand complete')
                # gmat.Initialize()
                # command.Initialize()
                # print('\tInitialize complete')

                vdator = gmat.Validator.Instance()

                print('\n\nDebugging output:\n')
                print(comm.GetTypeName())
                print(comm.ClearWrappers())
                print(f'wrapper_names: {comm.GetWrapperObjectNameArray()}')
                print(f'Assignment: {comm.IsOfType("Assignment")}')
                print(f'Write: {comm.IsOfType("Write")}')
                conditional_branch_report_propagate = (comm.IsOfType("ConditionalBranch") or
                                                       comm.GetTypeName() == "Report" or
                                                       comm.GetTypeName() == "Propagate")
                print(f'ConditionalBranch/Report/Propagate: {conditional_branch_report_propagate}')
                print(f'SolverCommand: {comm.IsOfType("SolverCommand")}')
                print(f'GetChildCommand(0): {comm.GetChildCommand(0)}')
                print(f'CheckUndefinedReference: {vdator.CheckUndefinedReference(comm)}')

                valid = vdator.ValidateCommand(comm)
                if not valid:
                    raise RuntimeError(f'{type(comm).__name__} command "{comm.name}" failed ValidateCommand')
                # mod.ValidateCommand is void so cannot be used to assess validity, but it calls
                #  Interpreter.ValidateCommand (also void) that performs useful parameter setup and error handling
                mod.ValidateCommand(comm)
                print('\tValidateCommand complete')

                print(gmat.GetLastCommand(mod.GetFirstCommand()))

                # # TODO bugfix: AppendCommand causing "Process finished with exit code -1073741819 (0xC0000005)".
                # #  Code still completes but not with normal exit code 0.
                mod.AppendCommand(comm, 0)
                print('\tmod.AppendCommand complete')

                if isinstance(comm, gpy.Target):
                    comm.run_mission_configured = True
                    gmat.EchoLogFile(False)

                print(f'    Done for {type(comm).__name__} named "{comm.GetName()}"\n')

            except SystemExit as sys_exit:
                raise RuntimeError(f'GMAT attempted to stop code execution while processing command {comm} - '
                                   f'{sys_exit}')

            except Exception as ex:
                # print(f'Failed command in RunMission: "{command.name}" of type {command.gmat_obj.GetTypeName()}')
                raise RuntimeError(f'configure_command in RunMission failed for "{comm.GetName()}" of type '
                                   f'{comm.GetTypeName()}\n{ex}') from ex

        # gmat.Initialize()

        mission_command_sequence = []

        print('\nEntered Moderator.RunMission()')

        print(
            f'mission_command_sequence: {[f"{type(command).__name__} {command.GetName()}" for command in mission_command_sequence]}')
        if not isinstance(mission_command_sequence, list):
            raise TypeError('mission_command_sequence must be a list of GmatCommand objects'
                            ' (e.g. BeginMissionSequence, Propagate)')

        # if mcs empty, or the first command is not a BeginMissionSequence command, add a BMS to the sequence
        # TODO uncomment
        if not mission_command_sequence or not isinstance(mission_command_sequence[0], gpy.BeginMissionSequence):
            mission_command_sequence.insert(0, gmat.BeginMissionSequence())

        # vdator = gpy.Validator()
        # vdator.SetSolarSystem(gmat.GetSolarSystem())
        # vdator.SetObjectMap(gmat.Moderator.Instance().GetConfiguredObjectMap())

        propagate_commands: list[gpy.Propagate] = []  # start a list of Propagates so their sats can be updated later
        for command in mission_command_sequence:
            print(f'    Attempting to configure {type(command).__name__} named "{command.GetName()}"')
            if not isinstance(command, gmat.GmatCommand):
                raise TypeError('command in RunMission for loop must be an instance of gmat.GmatCommand()\n'
                                f'Type found: {type(command)}')

            if isinstance(command, gpy.Propagate):
                print(f'\tPropagate command found!')
                propagate_commands.append(command)  # add to list so its spacecraft can later be set as propagated

                # # TODO remove (debugging only)
                # print(f'\t\tepoch_var: {command.stop_cond.epoch_var}')
                # print(f'\t\tstop_var: {command.stop_cond.stop_var}')
                # print(f'\t\tgoal: {command.stop_cond.goal}')
                # command_params = command.stop_cond.GetAllParameters()
                # print(f'\t{command_params}')

            if isinstance(command, gpy.Target) and not command.run_mission_configured:
                # Commands within Target branch need to be configured, then the Target command
                configure_command(command)
                for com in command.command_sequence:
                    configure_command(com)

            configure_command(command)

        # obj_map = gmat.ConfigManager.Instance().GetObjectMap()

        print('Finished configuring command sequence')

        run_mission_return = self.gmat_obj.RunMission()
        # TODO: uncomment run_mission_return evaluation below
        if run_mission_return == 1:
            print(f'\nMission run complete!\n')
            for propagate in propagate_commands:
                propagate.sat.was_propagated = True  # mark sat as propagated so GetState uses runtime values
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

    # def ValidateCommand(self, command: GmatCommand | gmat.GmatCommand) -> bool:
    #     command = gpy.extract_gmat_obj(command)
    #     return self.gmat_obj.ValidateCommand(command)


class Sandbox:
    def __init__(self):
        self.gmat_obj = gmat.Moderator.Instance().GetSandbox()

    # def AddCommand(self, command: gpy.GmatCommand | gmat.GmatCommand) -> bool:
    #     return self.gmat_obj.AddCommand(gpy.extract_gmat_obj(command))

    def AddObject(self, obj: gpy.GmatObject) -> bool:
        return self.gmat_obj.AddObject(gpy.extract_gmat_obj(obj))

    def AddSolarSystem(self, ss: gmat.SolarSystem) -> bool:
        return self.gmat_obj.AddSolarSystem(ss)

    def GetObjectMap(self) -> gmat.ObjectMap:
        return self.gmat_obj.GetObjectMap()

    def GetGlobalObjectMap(self) -> gmat.ObjectMap:
        return self.gmat_obj.GetGlobalObjectMap()

    def SetInternalCoordSystem(self, cs: gpy.OrbitState.CoordinateSystem) -> bool:
        return self.gmat_obj.SetInternalCoordSystem(gpy.extract_gmat_obj(cs))
