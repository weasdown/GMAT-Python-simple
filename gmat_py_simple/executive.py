from __future__ import annotations

import gmat_py_simple as gpy
from load_gmat import gmat
from gmat_py_simple import GmatCommand

import sys


def RunMission(mcs: list[GmatCommand]) -> int:
    # Shortcut for running missions
    return gpy.Moderator().RunMission(mcs)


class Moderator:
    def __init__(self):
        self.gmat_obj = gmat.Moderator.Instance()

    def AppendCommand(self, command: gpy.GmatCommand) -> bool:
        try:
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
        stop_cond.SetStringParameter('Goal', '12000.0')  # SetRhsString() called with goal value in source

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

    def CreateSolver(self, solver_type: str, solver_name: str) -> gmat.Solver:
        gpy.extract_gmat_obj(self).CreateSolver(solver_type, solver_name)  # make a Solver within GMAT
        # get Solver as  object specific solver subtype (e.g. gmat.DifferentialCorrector)
        obj: gmat.DifferentialCorrector = gmat.GetObject(solver_name)  # TODO finish obj type list
        return obj

    def CreateStopCondition(self, name: str) -> gmat.StopCondition:
        return self.gmat_obj.CreateStopCondition('StopCondition', name)

    def FindObject(self, name: str):
        raise NotImplementedError('Method available within GMAT but not exposed in API')
        # return self.gmat_obj.FindObject(name)

    def GetConfiguredObject(self, name: str) -> gmat.GmatBase:
        return gpy.extract_gmat_obj(self).GetConfiguredObject(name)

    def GetConfiguredObjectMap(self):
        return self.gmat_obj.GetConfiguredObjectMap()

    def GetDefaultBoundaryValueSolver(self) -> gmat.GmatBase | gmat.Solver:
        """
        Returns a default Differential Corrector. Ported from Moderator.cpp/GetDefaultBoundaryValueSolver().
        :return:
        """
        config_list = self.GetListOfObjects(gmat.SOLVER)
        num_solver = len(config_list)
        if num_solver > 0:
            for i in range(num_solver):
                obj: gmat.GmatBase = self.GetConfiguredObject(config_list[i])
                if obj.IsOfType('BoundaryValueSolver'):
                    obj = gmat.GetObject(obj.GetName())  # get a gmat.DifferentialCorrector rather than a gmat.GmatBase
                    return obj  # note this returns a gmat.GmatBase, different to below

        def_solver: gmat.Solver = self.CreateSolver('DifferentialCorrector', 'DefaultDC')
        return def_solver  # note this returns a gmat.Solver, different to above

    def GetDefaultPropSetup(self) -> gmat.PropSetup:
        config_list: list[str] = self.gmat_obj.GetListOfObjects(gmat.SPACECRAFT)
        if config_list:  # list length > 0
            return self.gmat_obj.GetPropSetup(config_list[0])
        else:  # no spacecraft found, so create one
            return self.gmat_obj.CreatePropSetup('DefaultProp')

    def GetDefaultSpacecraft(self) -> gmat.Spacecraft:
        # Method not exposed to Python API, so have to remake here rather than calling gmat.Moderator().Instance()
        so_config_list: list[str] = gpy.extract_gmat_obj(self).GetListOfObjects(gmat.SPACECRAFT)
        if so_config_list:  # list length > 0
            # self.GetSpacecraft() as in original would return a SpaceObject (not Spacecraft), so use gmat.GetObject()
            return gpy.GetObject(so_config_list[0])
        else:  # no spacecraft found, so create one
            return gpy.extract_gmat_obj(self).CreateSpacecraft('Spacecraft', 'DefaultSC')

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

        obj = vdator.FindObject(name)
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
        def update_command_objs_post_run(command_sequence: list[gpy.GmatCommand | gmat.GmatCommand]):
            propagate_commands: list[gpy.Propagate] = []  # start a list of Propagates so their sats can be updated
            target_commands: list[gpy.Target] = []  # start a list of Targets for checking convergence
            maneuver_commands: list[gpy.Maneuver] = []  # start a list of Maneuvers for updating burns

            for com in command_sequence:
                # add any Propagate commands to their list so their spacecraft can have was_propagated set to True
                if isinstance(com, gpy.Propagate):
                    propagate_commands.append(com)

                # add any Maneuver commands to their list so their Burns can have has_fired set to True
                if isinstance(command, gpy.Maneuver):
                    maneuver_commands.append(command)

                if isinstance(com, gpy.BranchCommand | gmat.BranchCommand):
                    # add any Target commands to their list so their convergence can be checked
                    if isinstance(command, gpy.Target):
                        target_commands.append(command)

                    # Check for any Propagate or Maneuver sub-commands, which need updating too
                    for sub_com in com.command_sequence:
                        if isinstance(sub_com, gpy.Propagate):
                            propagate_commands.append(sub_com)

                        if isinstance(sub_com, gpy.Maneuver):
                            maneuver_commands.append(sub_com)

            for p in propagate_commands:
                p.sat.was_propagated = True  # mark sat as propagated so GetState uses runtime values
                p.sat.gmat_obj = gpy.GmatObject.GetObject(p.sat)  # update sat gmat_obj post-run

            for t in target_commands:
                solver = t.solver
                solver.was_propagated = True
                solver.gmat_obj = gpy.GmatObject.GetObject(solver)
                solver_status = solver.GetIntegerParameter('IntegerSolverStatus')
                if solver_status != 0:  # solver failed
                    raise RuntimeError(f'{solver.gmat_obj.GetTypeName()} "{solver.GetName()}" failed to converge. '
                                       f'Returned code {solver_status}: '
                                       f'{gmat.GmatGlobal.Instance().GetSolverStatusString(solver.GetName())}')

            for m in maneuver_commands:
                m.burn.was_propagated = True
                m.burn.has_fired = True

            return propagate_commands, target_commands, maneuver_commands

        if not isinstance(mission_command_sequence, list):
            raise TypeError('mission_command_sequence must be a list of GmatCommand objects'
                            ' (e.g. BeginMissionSequence, Propagate)')

        # if mcs empty, or the first command is not a BeginMissionSequence command, add a BMS to the sequence
        if not mission_command_sequence or not isinstance(mission_command_sequence[0], gpy.BeginMissionSequence):
            mission_command_sequence.insert(0, gmat.BeginMissionSequence())

        gpy.Initialize()

        mod = gpy.Moderator()

        # configure each command in the mission sequence
        for command in mission_command_sequence:
            command.SetObjectMap(mod.GetConfiguredObjectMap())
            command.SetGlobalObjectMap(gmat.Sandbox().GetGlobalObjectMap())
            command.SetSolarSystem(gmat.GetSolarSystem())

            gpy.Validator().ValidateCommand(command)
            command.Initialize()
            mod.AppendCommand(command)

        print('\nRunning mission...')
        run_mission_return = gpy.extract_gmat_obj(self).RunMission()
        if run_mission_return == 1:  # Mission run complete
            # TODO uncomment (inhibited for debugging)
            update_command_objs_post_run(mission_command_sequence)
            print(f'Mission run complete!\n')
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


class Sandbox:
    def __init__(self):
        self.gmat_obj = gmat.Moderator.Instance().GetSandbox()

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
