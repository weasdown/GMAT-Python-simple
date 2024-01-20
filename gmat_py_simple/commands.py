from __future__ import annotations
from math import pi

from load_gmat import gmat

import gmat_py_simple as gpy
from gmat_py_simple.utils import *


class GmatCommand:
    def __init__(self, command_type: str, name: str):
        self.command_type: str = command_type

        mod = gpy.Moderator()
        self.gmat_obj = mod.CreateDefaultCommand(self.command_type)
        # if command_type != 'Target':
        #     # TODO convert all GmatCommand creation to the native Python form e.g. gmat.Propagate()
        #     self.gmat_obj = mod.CreateDefaultCommand(self.command_type)  # type <class 'gmat_py.GmatCommand'>
        # else:
        #     # Target must be in native Python form to allow access to AddBranch()
        #     self.gmat_obj = gmat.Target()

        # Set GMAT object's name
        self.name: str = name
        current_commands_of_type = gmat.GetCommands(self.command_type)
        self.gmat_obj.SetName(name)  # set obj name, as CreateDefaultCommand does not (Jira issue GMT-8095)

        self.SetObjectMap(mod.GetConfiguredObjectMap())
        self.SetGlobalObjectMap(gpy.Sandbox().GetGlobalObjectMap())
        self.SetSolarSystem(gmat.GetSolarSystem())

        if not isinstance(self, gpy.Target | gpy.EndTarget | gpy.Achieve | gpy.Vary):
            try:
                self.Initialize()
            except Exception as ex:
                raise RuntimeError(f'{self.command_type} command named "{self.name}" failed to initialize in '
                                   f'GmatCommand.__init__() - see exception below:\n\t{ex}') from ex

        # self.Initialize()

        # # gmat.Initialize()
        # # FIXME Achieve needs Targeter to be initialized before itself
        # if not isinstance(self, gpy.Achieve):
        #     self.Initialize()

    def AddToMCS(self) -> bool:
        return gpy.Moderator().AppendCommand(self)

    def ClearDefaultObjects(self):
        command_type = self.GetTypeName()
        if command_type != 'Propagate':
            raise RuntimeError('ClearDefaultObjects() only works on Propagate commands')
        else:
            set_before = set(gmat.ConfigManager.Instance().GetListOfAllItems())
            print(f'\nCM list of all before clearing: {set_before}\n')
            sat_name = gpy.Moderator().GetDefaultSpacecraft().GetName()
            # Find which objs exist that would be made during CreateDefaultCommand('Propagate'). Then we won't try to
            # remove them later, as they're being used by other objects (e.g. DefaultProp_ForceModel by a PropSetup)
            pgate_def_obj_names = ['DefaultProp_ForceModel', f'{sat_name}.A1ModJulian', f'{sat_name}.ElapsedSecs']
            existing_pgate_objs = []
            for obj_name in pgate_def_obj_names:
                try:
                    gmat.GetObject(obj_name)
                    # GetObject worked, so object already exists and must not be deleted - add to list
                    existing_pgate_objs.append(obj_name)

                # object doesn't yet exist in GMAT, so can safely be deleted after CreateDefaultCommand('Propagate')
                except AttributeError as ex:
                    pass

            for def_name in pgate_def_obj_names:  # clear objects that are safe to clear
                if def_name in existing_pgate_objs:  # skip object if it already exists (so is used by another object)
                    pass
                else:
                    print(f'\nClearing {def_name}...\n')
                    gmat.Clear(def_name)  # remove the object from GMAT
                    # if def_name == 'DefaultProp_ForceModel':  # gmat.ODE_MODEL
                    #     gpy.Moderator().RemoveObject(gmat.ODE_MODEL, def_name)
                    # else:  # gmat.PARAMETER
                    #     gpy.Moderator().RemoveObject(gmat.PARAMETER, def_name)

            # self.gmat_obj is of type <class 'gmat_py.GmatCommand'> so far
            self.gmat_obj = eval(f'gmat.{command_type}()')  # convert to gmat_py.Propagate that supports ClearObject()

            # Also clear the lists of Spacecraft, Formations and StopConditions referenced in the Propagate command
            self.gmat_obj.ClearObject(gmat.SPACECRAFT)
            self.gmat_obj.ClearObject(gmat.FORMATION)
            self.gmat_obj.ClearObject(gmat.STOP_CONDITION)

            commands = gmat.GetCommands()
            print('\nCommand list:')
            print(''.join([f'Name: {command.GetName()}, type: {command.GetTypeName()}\n' for command in commands]))

            name = self.name
            def_pgate_name = 'Propagate'

            # gmat.ShowObjects()

            gmat.Sandbox().AddCommand(self.gmat_obj)
            self.gmat_obj = gmat.GetObject(self.name)

            set_after = set(gmat.ConfigManager.Instance().GetListOfAllItems())
            print(f'\nCM list of all after clearing: {set_after}\n')
            print(f'Object(s) removed: {set_before - set_after}')

            gmat.ShowObjects()

            return self.gmat_obj
            pass
            # gpy.Initialize()

    def GeneratingString(self):
        print(self.GetGeneratingString())

    def GetGeneratingString(self, mode: int = gmat.NO_COMMENTS, prefix: str = '', use_name: str = 'self.name') -> str:
        use_name = self.name
        return self.gmat_obj.GetGeneratingString(mode, prefix, use_name)

    def GetField(self, field: str) -> str:
        return self.gmat_obj.GetField(field)

    def GetMissionSummary(self):
        return self.gmat_obj.GetStringParameter('MissionSummary')

    def GetName(self) -> str:
        return gpy.extract_gmat_obj(self).GetName()

    def GetNext(self):
        return gpy.extract_gmat_obj(self).GetNext()

    def GetParameterID(self, param_name: str) -> int:
        return gpy.extract_gmat_obj(self).GetParameterID(param_name)

    def GetRefObject(self, type_id: int, name: str, index: int = 0):
        return self.gmat_obj.GetRefObject(type_id, name, index)

    def GetRefObjectName(self, type_int: int) -> str:
        return self.gmat_obj.GetRefObjectName(type_int)

    def GetStringArrayParameter(self, param: str | int) -> tuple:
        if isinstance(param, str):
            param = self.GetParameterID(param)
        return gpy.extract_gmat_obj(self).GetStringArrayParameter(param)

    def GetStringParameter(self, param: str | int) -> str:
        if isinstance(param, str):
            param = self.GetParameterID(param)
        return gpy.extract_gmat_obj(self).GetStringParameter(param)

    def GetTypeName(self) -> str:
        return extract_gmat_obj(self).GetTypeName()

    def Help(self):
        self.gmat_obj.Help()

    def Initialize(self) -> bool:
        try:
            resp = extract_gmat_obj(self).Initialize()
            if not resp:
                raise RuntimeError('Non-true response from Initialize()')
            return resp

        # except SystemExit as sys_ex:
        #     raise RuntimeError(f'Initialize command for {self.__name__} attempted SystemExit - {sys_ex}')
        except Exception as ex:
            raise RuntimeError(f'Initialize failed for {type(self).__name__} named "{self.name}". See GMAT error below:'
                               f'\n\tGMAT internal exception/error: {str(ex).replace("\n", "")}') from ex

    def SetBooleanParameter(self, param: str | int, value: bool) -> bool:
        if isinstance(param, str):
            param = self.GetParameterID(param)
        return gpy.extract_gmat_obj(self).SetBooleanParameter(param, value)

    def SetField(self, field: str, value) -> bool:
        return self.gmat_obj.SetField(field, value)

    def SetGlobalObjectMap(self, gom: gmat.ObjectMap) -> bool:
        return extract_gmat_obj(self).SetGlobalObjectMap(gom)

    def SetIntegerParameter(self, param: str | int, value: int) -> bool:
        if isinstance(param, str):
            param = self.GetParameterID(param)
        return gpy.extract_gmat_obj(self).SetIntegerParameter(param, value)

    def SetName(self, name: str) -> bool:
        self.name = name
        return self.gmat_obj.SetName(name)

    def SetObjectMap(self, om: gmat.ObjectMap) -> bool:
        return extract_gmat_obj(self).SetObjectMap(om)

    # def SetRefObject(self, obj, type_int: int, obj_name: str = '') -> bool:
    #     return extract_gmat_obj(self).SetRefObject(extract_gmat_obj(obj), type_int, obj_name)

    def SetRefObjectName(self, type_id: int, name: str) -> bool:
        return gpy.extract_gmat_obj(self).SetRefObjectName(type_id, name)

    def SetSolarSystem(self, ss: gmat.SolarSystem = gmat.GetSolarSystem()) -> bool:
        return extract_gmat_obj(self).SetSolarSystem(ss)

    def SetStringParameter(self, param: str | int, value: str) -> bool:
        if isinstance(param, str):
            param = self.GetParameterID(param)
        return gpy.extract_gmat_obj(self).SetStringParameter(param, value)

    def Validate(self) -> bool:
        try:
            return self.gmat_obj.Validate()
        except Exception as ex:
            raise RuntimeError(f'{type(self).__name__} named "{self.name}" failed to Validate') from ex


class BranchCommand(GmatCommand):
    def __init__(self, command_type: str, name: str):
        super().__init__(command_type, name)
        self.command_sequence = []

    def AddBranch(self, command: gpy.GmatCommand | gmat.GmatCommand, which: int = 0):
        """
        No return value.
        :param command:
        :param which:
        """
        gpy.extract_gmat_obj(self).AddBranch(gpy.extract_gmat_obj(command), which)

    def Append(self, command: gpy.GmatCommand | gmat.GmatCommand) -> bool:
        command_gmat_obj = gpy.extract_gmat_obj(command)
        return gpy.extract_gmat_obj(self).Append(command_gmat_obj)


class Achieve(GmatCommand):
    def __init__(self, name: str, solver: gpy.DifferentialCorrector | gmat.DifferentialCorrector,
                 variable: str, value: int | float, tolerance: float | int = 0.1):
        super().__init__('Achieve', name)

        self.solver: gpy.DifferentialCorrector | gmat.DifferentialCorrector = solver
        # self.SetField('TargeterName', self.solver.GetName())
        # type_array = self.gmat_obj.GetRefObjectTypeArray()
        # print(f'{type_array[0]}: {gpy.GetTypeNameFromID(type_array[0])}')
        # print(f'Ref object name array: {self.gmat_obj.GetRefObjectNameArray(127)}')
        self.SetStringParameter('TargeterName', self.solver.GetName())
        self.SetRefObject(self.solver, gmat.SOLVER, self.solver.GetName())

        # print(f'TargeterName set in Achieve: {self.GetStringParameter("TargeterName")}')

        self.variable = variable
        # self.SetField('Goal', self.variable)
        self.SetStringParameter('Goal', self.variable)
        # self.solver.SetStringParameter('Variables', str(self.variable))

        self.value = value
        # self.SetField('GoalValue', str(self.value))
        self.SetStringParameter('GoalValue', str(self.value))
        # num_solver_goals = len(solver.GetStringArrayParameter('Goals'))
        # self.solver.gmat_obj.UpdateSolverGoal(num_solver_goals, self.value)
        # print(solver.GetStringArrayParameter('Goals'))
        # self.solver.SetStringParameter('Goals', str(self.value))
        # self.solver.SetStringParameter('Variables', str(self.value))

        self.tolerance = tolerance
        # self.SetField('Tolerance', str(self.tolerance))
        self.SetStringParameter('Tolerance', str(self.tolerance))

        # TODO: try the following:
        # self.solver.UpdateSolverGoal(0, self.value)

        # TODO bugfix: Exception thrown during self.solver.Initialize(): gmat_py.APIException: Solver subsystem
        #  exception: Targeter cannot initialize: No goals or variables are set.
        # self.solver.Initialize()

        # TODO remove (debugging only)
        # CustomHelp(self)
        # gmat.ShowObjects()
        # def_dc = gmat.GetObject('DefaultDC')

        self.SetSolarSystem()
        self.SetObjectMap(gpy.Moderator().GetConfiguredObjectMap())
        self.SetGlobalObjectMap(gpy.Sandbox().GetGlobalObjectMap())

        self.Initialize()
        # self.solver.Initialize()
        print(f"\nVariables in Achieve: {self.solver.GetStringArrayParameter('Variables')}")
        print(f"Goals in Achieve: {self.solver.GetStringArrayParameter('Goals')}\n")
        # print(f"Goals in Achieve: {self.solver.GetStringArrayParameter('Goals')}\n")
        # CustomHelp(self)
        # self.solver.gmat_obj.TakeAction('Reset')
        pass

        # TODO bugfix: Exception thrown during initialize: gmat_py.APIException: Command Exception: Targeter not
        #  initialized for Achieve command "Achieve DC1(DefaultSC.Earth.RMAG = 42165.0, {Tolerance = 0.1});"
        #  Caused by targeter parameter in Achieve being null

        # self.Initialize()
        # gpy.Initialize()

    def SetRefObject(self, obj, type_int: int, obj_name: str = '') -> bool:
        return extract_gmat_obj(self).SetRefObject(extract_gmat_obj(obj), type_int, obj_name)


class BeginFiniteBurn(GmatCommand):
    def __init__(self, name: str):
        super().__init__('BeginFiniteBurn', name)
        raise NotImplementedError


class BeginMissionSequence(GmatCommand):
    def __init__(self):
        # TODO: uncomment to get all items initialized (handling in Tut02 for now)
        # gpy.Initialize()  # initialize GMAT so objects are in place for use in command sequence

        super().__init__('BeginMissionSequence', 'BeginMissionSequenceCommand')

        self.SetSolarSystem()
        self.SetObjectMap(gpy.Moderator().GetConfiguredObjectMap())
        self.SetGlobalObjectMap(gpy.Sandbox().GetGlobalObjectMap())

        # gpy.Initialize()
        self.Initialize()


class EndFiniteBurn(GmatCommand):
    def __init__(self, name: str):
        super().__init__('EndFiniteBurn', name)
        raise NotImplementedError


class EndTarget(BranchCommand):
    def __init__(self, parent_target: gpy.Target, name: str = None):
        if name is None:
            name = f'EndTarget_{parent_target.GetName()}'

        super().__init__('EndTarget', name)

        # self.Append(parent_target)

        # for command in self.target.command_sequence:
        #     self.Append(command)

    def Insert(self, command: gpy.GmatCommand | gmat.GmatCommand,
               prev: gpy.GmatCommand | gmat.GmatCommand = None) -> bool:
        command = gpy.extract_gmat_obj(command)
        prev = gpy.extract_gmat_obj(prev) if prev is not None else None
        return gpy.extract_gmat_obj(self).Insert(command, prev)


class Maneuver(GmatCommand):
    def __init__(self, name: str, burn: gpy.ImpulsiveBurn | gpy.FiniteBurn, spacecraft: gpy.Spacecraft,
                 backprop: bool = False):
        """
        Create a Maneuver command.

        :param name:
        :param burn:
        :param spacecraft:
        :param backprop:
        """

        # TODO: remove below docstring when no longer needed
        """
        In Moderator.cpp/CreateDefaultCommand/try...
            else if (type == "Maneuver")
          {
             // set burn
             id = cmd->GetParameterID("Burn");
             cmd->SetStringParameter(id, GetDefaultBurn("ImpulsiveBurn")->GetName());
             
             // set spacecraft
             id = cmd->GetParameterID("Spacecraft");
             cmd->SetStringParameter(id, GetDefaultSpacecraft()->GetName());
         """

        super().__init__('Maneuver', name)

        self.burn = burn
        self.SetStringParameter(self.gmat_obj.GetParameterID('Burn'), self.burn.name)

        self.spacecraft = spacecraft
        self.SetStringParameter(self.gmat_obj.GetParameterID('Spacecraft'), self.spacecraft.name)

        self.backprop = backprop
        self.SetBooleanParameter(self.gmat_obj.GetParameterID('BackProp'), self.backprop)

        self.SetSolarSystem()
        self.SetObjectMap(gpy.Moderator().GetConfiguredObjectMap())
        self.SetGlobalObjectMap(gpy.Sandbox().GetGlobalObjectMap())

        # gpy.Initialize()
        self.Initialize()


class Propagate(GmatCommand):
    class StopCondition:
        def __init__(self, sat: gmat.Spacecraft | gpy.Spacecraft, stop_cond: str | tuple,
                     gmat_obj: gmat.StopCondition | gmat.GmatBase):
            self.sat = sat
            self.sat_name = self.sat.GetName()
            self.body = 'Earth'  # TODO remove hard-coding

            self.epoch_var = None
            self.epoch_param_type = None

            self.stop_var = None
            self.stop_param_type = None

            # TODO complete this types/properties list based on options available in GUI Propagate command
            self.stop_param_allowed_types = {
                'Spacecraft': ['A1ModJulian', 'Acceleration', 'AccelerationX', 'AccelerationY', 'AccelerationZ',
                               'AltEquinoctialP', 'AltEquinoctialQ', 'Altitude', 'AngularVelocityX', 'AngularVelocityY',
                               'AngularVelocityZ', 'AOP', 'Apoapsis', 'AtmosDensity', 'AtmosDensityScaleFactor',
                               'AtmosDensityScaleFactorSigma', 'AZI', 'BdotR', 'BdotT', 'BetaAngle', 'BrouwerLongAOP',
                               'BrouwerLongECC', 'BrouwerLongINC', 'BrouwerLongMA', 'BrouwerLongRAAN', 'BrouwerLongSMA',
                               'BrouwerShortAOP', 'BrouwerShortECC', 'BrouwerShortINC', 'BrouwerShortMA',
                               'BrouwerShortRAAN', 'BrouwerShortSMA', 'BVectorAngle', 'BVectorMag', 'C3Energy', 'Cd',
                               'CdSigma', 'Cr', 'CrSigma', 'DCM11', 'DCM12', 'DCM13', 'DCM21', 'DCM22', 'DCM23',
                               'DCM31',
                               'DCM32', 'DCM33', 'DEC', 'DECV', 'DelaunayG', 'Delaunayg', 'DelaunayH', 'Delaunayh',
                               'DelaunayL', 'Delaunayl', 'DLA', 'DragArea', 'DryCenterOfMassX', 'DryCenterOfMassY',
                               'DryCenterOfMassZ', 'DryMass', 'DryMassMomentOfInertiaXX', 'DryMassMomentOfInertiaXY',
                               'DryMassMomentOfInertiaXZ', 'DryMassMomentOfInertiaYY', 'DryMassMomentOfInertiaYZ',
                               'DryMassMomentOfInertiaZZ', 'EA', 'ECC', 'ElapsedDays', 'ElapsedSecs', 'Energy',
                               'EquinoctialH', 'EquinoctialHDot', 'EquinoctialK', 'EquinoctialKDot', 'EquinoctialP',
                               'EquinoctialPDot', 'EquinoctialQ', 'EquinoctialQDot', 'EulerAngle1', 'EulerAngle2',
                               'EulerAngle3', 'EulerAngleRate1', 'EulerAngleRate2', 'EulerAngleRate3', 'FPA', 'HA',
                               'HMAG',
                               'HX', 'HY', 'HZ', 'INC', 'IncomingBVAZI', 'IncomingC3Energy', 'IncomingDHA',
                               'IncomingRadPer',
                               'IncomingRHA', 'Latitude', 'Longitude', 'LST', 'MA', 'MHA', 'MLONG', 'MM',
                               'ModEquinoctialF',
                               'ModEquinoctialG', 'ModEquinoctialH', 'ModEquinoctialK', 'MRP1', 'MRP2', 'MRP3',
                               'OrbitPeriod',
                               'OrbitTime', 'OutgoingBVAZI', 'OutgoingC3Energy', 'OutgoingDHA', 'OutgoingRadPer',
                               'OutgoingRHA', 'Periapsis', 'PlanetodeticAZI', 'PlanetodeticHFPA', 'PlanetodeticLAT',
                               'PlanetodeticLON', 'PlanetodeticRMAG', 'PlanetodeticVMAG', 'Q1', 'Q2', 'Q3', 'Q4', 'RA',
                               'RAAN',
                               'RadApo', 'RadPer', 'RAV', 'RLA', 'RMAG', 'SemilatusRectum', 'SMA',
                               'SPADDragScaleFactor',
                               'SPADDragScaleFactorSigma', 'SPADSRPScaleFactor', 'SPADSRPScaleFactorSigma', 'SRPArea',
                               'SystemCenterOfMassX', 'SystemCenterOfMassY', 'SystemCenterOfMassZ',
                               'SystemMomentOfInertiaXX',
                               'SystemMomentOfInertiaXY', 'SystemMomentOfInertiaXZ', 'SystemMomentOfInertiaYY',
                               'SystemMomentOfInertiaYZ', 'SystemMomentOfInertiaZZ', 'TA', 'TAIModJulian',
                               'TDBModJulian',
                               'TLONG', 'TLONGDot', 'TotalMass', 'TTModJulian', 'UTCModJulian', 'VelApoapsis',
                               'VelPeriapsis',
                               'VMAG', 'VX', 'VY', 'VZ', 'X', 'Y', 'Z']}

            self.goal = None
            self.goal_param_type = None
            self.goalless = None

            self.gmat_obj = gmat_obj
            self.name = self.gmat_obj.GetName()

            self.epoch_var = self.gmat_obj.GetStringParameter('EpochVar')
            self.epoch_param_type = None  # TODO get correct param type

            self.stop_var = self.gmat_obj.GetStringParameter('StopVar')
            self.stop_param_type = None  # TODO get correct param type

            self.goal = self.gmat_obj.GetStringParameter('Goal')
            self.goalless = None  # TODO determine correct goalless value or remove attribute entirely if not needed

            (self.stop_param_type,
             self.stop_var,
             self.epoch_param_type,
             self.epoch_var,
             self.goal,
             self.goalless,
             self.body) = self.parse_user_stop_cond(stop_cond)

            self.name = f'StopOn{self.stop_var}'
            self.SetName(self.name)

            self.apply_stop_cond_params(self.epoch_param_type, self.epoch_var, self.stop_param_type, self.stop_var,
                                        self.goal)

        def apply_stop_cond_params(self, epoch_param_type: str, epoch_var: str, stop_param_type: str, stop_var: str,
                                   goal: str | int | float):
            self.SetStringParameter('EpochVar', epoch_var)
            self.SetStringParameter('StopVar', stop_var)
            self.SetStringParameter('Goal', goal)

            mod = gpy.Moderator()
            vdator = gpy.Validator()
            vdator.SetSolarSystem(gmat.GetSolarSystem())
            vdator.SetObjectMap(mod.GetConfiguredObjectMap())

            sat_name = self.sat.GetName()

            # if an epoch parameter does not already exist, make one
            if not mod.GetParameter(epoch_var):
                vdator.CreateParameter(epoch_param_type, epoch_var)  # create a Parameter for epoch_var
                param = gpy.Validator().FindObject(epoch_var)
                param.SetRefObjectName(gmat.SPACECRAFT, sat_name)  # attach Spacecraft to Parameter

            # if a stop parameter does not already exist, make one
            if not mod.GetParameter(stop_var):
                vdator.CreateParameter(stop_param_type, stop_var)  # create a Parameter for stop_var
                param = gpy.Validator().FindObject(stop_var)
                param.SetRefObjectName(gmat.SPACECRAFT, sat_name)  # attach Spacecraft to Parameter

        @classmethod
        def from_user_stop_cond(cls, sat: gpy.Spacecraft | gmat.Spacecraft, user_stop_cond: tuple | str,
                                gmat_obj: gmat.GmatBase = None) -> Propagate.StopCondition:
            # if gmat_obj:
            stop_cond: Propagate.StopCondition = cls(sat, stop_cond=user_stop_cond, gmat_obj=gmat_obj)
            # else:
            #     stop_cond: Propagate.StopCondition = cls(sat, stop_cond=user_stop_cond)
            return stop_cond

        def GetStringParameter(self, param_name: str) -> str:
            return self.gmat_obj.GetStringParameter(param_name)

        def parse_user_stop_cond(self, stop_cond: str | tuple):
            # TODO feature: convert tuple to 2 or 3 element.
            #  Examples: 2: (sat.name, 'Earth.Periapsis'), 3: (sat.name, 'ElapsedSecs', 12000.0)

            # TODO: get stop_tolerance from stop_cond (no example yet but see pg 652/PDF pg 661 of User Guide)

            if isinstance(stop_cond, tuple) and len(stop_cond) == 2:  # most likely. E.g. ('Sat.ElapsedSecs', 12000)
                stop_var = stop_cond[0]
                sat_from_stop_cond, parameter = stop_var.split('.')
                goal = str(stop_cond[1])

            elif isinstance(stop_cond, str):  # e.g. 'Sat.Earth.Apoapsis'
                stop_var = stop_cond
                sat_from_stop_cond, body, parameter = stop_var.split('.')
                goal = 0

            else:
                # TODO: definitely max of 2 elements?
                raise RuntimeError(f'stop_cond is invalid. Must be a 2-element tuple or a string. Given value: '
                                   f'{stop_cond}')

            stop_var_elements = stop_var.split('.')
            num_stop_var_elements = len(stop_var_elements)
            if num_stop_var_elements == 2:
                # print('2 elements found in StopCond parse')
                sat_name, parameter = stop_var.split('.')
                if sat_name != self.sat.name:
                    raise RuntimeError(
                        f'Name of satellite given in StopCondition "{stop_cond}" ({sat_name}) does'
                        f' not match name for Propagate\'s satellite ({self.sat_name})')
                stop_var = '.'.join([sat_name, parameter])

                # Get body from satellite's coordinate system
                coord_sys_name = gpy.GetObject(sat_name).GetField('CoordinateSystem')
                coord_sys_obj = gpy.GetObject(coord_sys_name)
                body = coord_sys_obj.GetField('Origin')

            elif num_stop_var_elements == 3:
                # print('3 elements found in StopCond parse')
                sat_name, body, parameter = stop_var.split('.')
                if sat_name != self.sat.name:
                    raise RuntimeError(
                        f'Name of satellite given in StopCondition "{stop_cond}" ({sat_name}) does'
                        f' not match name for Propagate\'s satellite ({self.sat_name})')

            else:
                raise SyntaxError('Invalid number of parts for stop_cond. Must be two (e.g. "Sat.ElapsedSecs") or three'
                                  '(e.g. "Sat.Earth.Periapsis")')

            stop_param_type = stop_var[len(self.sat.GetName()) + 1:]  # remove sat name and . from stop_var

            # following types taken from src/Moderator.CreateDefaultParameters() Time parameters section
            allowed_epoch_param_types = ['ElapsedSecs', 'ElapsedDays', 'A1ModJulian', 'A1Gregorian',
                                         'TAIModJulian', 'TAIGregorian', 'TTModJulian', 'TTGregorian',
                                         'TDBModJulian', 'TDBGregorian', 'UTCModJulian', 'UTCGregorian']
            # TODO: remove hard-coding of epoch_param_type
            # TODO: decide when to use other epoch_param_types
            epoch_param_type = 'A1ModJulian'
            epoch_var = f'{sat_from_stop_cond}.{epoch_param_type}'

            # non_sat_goals = ['Apoapsis', 'Periapsis']
            # for g in non_sat_goals:
            #     if g in goal:
            #         goal = goal[len(self.sat_name)+1:]  # remove sat name from front of goal

            goalless = False
            goalless_params = ['Apoapsis', 'Periapsis']  # TODO: complete list

            # see whether any goalless param names exist in the stop_var string
            if any(x in stop_var for x in goalless_params):
                goalless = True
                stop_param_type = stop_var_elements[len(stop_var_elements) - 1]  # e.g. 'Periapsis'
                # goal = 0  # TODO remove [- [len(self.sat_name) + 1:]  # remove sat_name, e.g. 'Earth.Periapsis']

            # self.stop_param_type = stop_param_type
            # self.stop_var = stop_var
            #
            # self.epoch_param_type = epoch_param_type
            # self.epoch_var = epoch_var
            #
            # # self.goal_param_type = goal_param_type
            # # self.goal = goal
            # self.goalless = goalless
            #
            # self.body = body

            # # TODO remove hard-coding (debugging only)
            # epoch_var = 'TestSat.A1ModJulian'
            # epoch_param_type = 'A1ModJulian'
            # stop_param_type = 'Periapsis'
            # stop_var = 'TestSat.Earth.Periapsis'
            # goal = 60

            return stop_param_type, stop_var, epoch_param_type, epoch_var, goal, goalless, body

        def SetName(self, name: str) -> bool:
            return extract_gmat_obj(self).SetName(name)

        def SetStringParameter(self, param_name: str, value: str):
            return extract_gmat_obj(self).SetStringParameter(param_name, str(value))

    def __init__(self, name: str, sat: gpy.Spacecraft | gmat.Spacecraft, prop: gpy.PropSetup | gmat.GmatBase,
                 user_stop_cond: tuple | str = None):
        # TODO add None as default for sat, prop, stop_cond and handle appropriately in __init__()
        super().__init__('Propagate', name)
        # gpy.Initialize()
        self.Initialize()

        # Get names of Propagate's ref objects and extract the objects
        prop_ref_name = self.GetRefObjectName(gmat.PROP_SETUP)
        sat_ref_name = self.GetRefObjectName(gmat.SPACECRAFT)

        self.prop = self.GetRefObject(gmat.PROP_SETUP, prop_ref_name)
        # apply any user-provided PropSetup
        if prop:
            self.prop = prop
            # clear existing prop to replace it (also clears sat)
            self.TakeAction('Clear', 'Propagator')
            self.SetObject(prop.GetName(), gmat.PROP_SETUP)

        self.sat = gmat.GetObject(sat_ref_name)  # GetRefObject() throws exception for Spacecraft - use gmat.GetObject()
        # apply any user-provided Spacecraft
        if sat:
            self.sat = sat
            # if sat_ref_name != self.sat.GetName():
            self.SetRefObjectName(gmat.SPACECRAFT, self.sat.GetName())
            # self.SetObject(self.sat.GetName(), gmat.SPACECRAFT)
            # self.TakeAction('SetStopSpacecraft', self.sat.GetName())

        self.stop_cond = self.GetGmatObject(gmat.STOP_CONDITION)
        # apply any user-provided stop condition
        if user_stop_cond:
            self.user_stop_cond = user_stop_cond
            # update default StopCondition with user-provided values by converting to wrapper StopCondition
            self.stop_cond = self.StopCondition(self.sat, self.user_stop_cond, self.stop_cond)
            self.TakeAction('Clear', 'StopCondition')  # clear existing StopCond to replace it
            self.SetRefObject(extract_gmat_obj(self.stop_cond), gmat.STOP_CONDITION, self.stop_cond.name)

    def GetGmatObject(self, type_int: int):
        return self.gmat_obj.GetGmatObject(type_int)

    def parse_user_stop_cond(self, stop_cond: str | tuple):
        # TODO feature: convert tuple to 2 or 3 element.
        #  Examples: 2: (sat.name, 'Earth.Periapsis'), 3: (sat.name, 'ElapsedSecs', 12000.0)

        # TODO: get stop_tolerance from stop_cond (no example yet but see pg 652/PDF pg 661 of User Guide)

        if isinstance(stop_cond, tuple) and len(stop_cond) == 2:  # most likely. E.g. ('Sat.ElapsedSecs', 12000)
            stop_var = stop_cond[0]
            goal = str(stop_cond[1])

        elif isinstance(stop_cond, str):  # e.g. 'Sat.Earth.Apoapsis'
            stop_var = stop_cond
            sat_from_stop_cond, body, parameter = stop_var.split('.')
            goal = str(stop_var)

        else:
            # TODO: definitely max of 2 elements?
            raise RuntimeError(f'stop_cond is invalid. Must be a 2-element tuple or a string. Given value: '
                               f'{stop_cond}')

        stop_var_elements = stop_var.split('.')
        num_stop_var_elements = len(stop_var_elements)
        if num_stop_var_elements == 2:
            sat, parameter = stop_var.split('.')
            stop_var = '.'.join([sat, parameter])

            # Get body from satellite's coordinate system
            coord_sys_name = gmat.GetObject(sat).GetField('CoordinateSystem')
            coord_sys_obj = gmat.GetObject(coord_sys_name)
            body = coord_sys_obj.GetField('Origin')

        elif num_stop_var_elements == 3:
            sat_from_stop_cond, body, parameter = stop_var.split('.')
            sat_name = self.sat.GetName()
            if sat_from_stop_cond != sat_name:
                raise RuntimeError(
                    f'Name of satellite given in StopCondition "{stop_cond}" ({sat_from_stop_cond}) does'
                    f' not match name for Propagate\'s satellite ({sat_name})')
        else:
            raise SyntaxError('Invalid number of parts for stop_cond. Must be two (e.g. "Sat.ElapsedSecs") or three'
                              '(e.g. "Sat.Earth.Periapsis")')

        stop_param_type = stop_var[len(self.sat.GetName()) + 1:]  # remove sat name and . from stop_var

        # following types taken from src/Moderator.CreateDefaultParameters() Time parameters section
        allowed_epoch_param_types = ['ElapsedSecs', 'ElapsedDays', 'A1ModJulian', 'A1Gregorian',
                                     'TAIModJulian', 'TAIGregorian', 'TTModJulian', 'TTGregorian',
                                     'TDBModJulian', 'TDBGregorian', 'UTCModJulian', 'UTCGregorian']
        # TODO: remove hard-coding of epoch_param_type
        # TODO: decide when to use other epoch_param_types
        epoch_param_type = 'A1ModJulian'
        epoch_var = f'{self.sat.GetName()}.{epoch_param_type}'

        # non_sat_goals = ['Apoapsis', 'Periapsis']
        # for g in non_sat_goals:
        #     if g in goal:
        #         goal = goal[len(self.sat_name)+1:]  # remove sat name from front of goal

        goalless = False
        goalless_params = ['Apoapsis', 'Periapsis']  # TODO: complete list

        # goalless parameter found
        if any(x in goal for x in goalless_params):
            goalless = True
            stop_param_type = stop_var_elements[len(stop_var_elements) - 1]  # e.g. 'Periapsis'
            goal_param_type = stop_param_type  # e.g. 'Periapsis'
            goal = stop_var  # TODO remove - [len(self.sat_name) + 1:]  # remove sat_name, e.g. 'Earth.Periapsis'

        else:  # stop condition is not goalless
            # goal already parsed above
            goal_param_type = stop_param_type

        # self.stop_param_type = stop_param_type
        # self.stop_var = stop_var
        #
        # self.epoch_param_type = epoch_param_type
        # self.epoch_var = epoch_var
        #
        # self.goal_param_type = goal_param_type
        # self.goal = goal
        # self.goalless = goalless
        #
        # self.body = body

        return stop_param_type, stop_var, epoch_param_type, epoch_var, goal_param_type, goal, goalless, body

    def SetObject(self, obj_name: str, type_int: int):
        return extract_gmat_obj(self).SetObject(obj_name, type_int)

    def SetRefObject(self, obj, type_int: int, obj_name: str, index: int = 0) -> bool:
        return extract_gmat_obj(self).SetRefObject(extract_gmat_obj(obj), type_int, obj_name, index)

    def TakeAction(self, action: str, action_data: str) -> bool:
        return extract_gmat_obj(self).TakeAction(action, action_data)


# class PropagateMulti(Propagate):
#     # TODO: consider making this a nested/inner class of Propagate, so would call Propagate.Multi()
#     """
#     Note: this command does not exist in standard GMAT. It is here to reduce ambiguity when propagating multiple
#      spacecraft. This class can only be used to propagate multiple spacecraft - to propagate a single spacecraft, use
#       Propagate (which only suports a single spacecraft).
#
#     """
#
#     def __init__(self, name: str = None, prop: gpy.PropSetup = None, sat: gpy.Spacecraft = None,
#                  stop_cond: Propagate.StopCondition = None, synchronized: bool = False):
#         if not name:  # make sure the new Propagate has a unique name
#             num_propagates: int = len(gmat.GetCommands('Propagate'))
#             name = f'PropagateMulti{num_propagates + 1}'
#
#         super().__init__(name, prop, sat, stop_cond, synchronized)


class SolverBranchCommand(BranchCommand):
    def __init__(self, command_type: str, name: str):
        super().__init__(command_type, name)


class SolverSequenceCommand(GmatCommand):
    def __init__(self, command_type: str, name: str):
        super().__init__(command_type, name)


class Target(SolverBranchCommand):
    def __init__(self, name: str, solver: gpy.DifferentialCorrector | gmat.DifferentialCorrector,
                 solve_mode: str = 'Solve', exit_mode: str = 'SaveAndContinue',
                 command_sequence: list[gpy.GmatCommand] = None):
        # 'Show Progress Window' argument not implemented (for now) - seems to be a GUI-only option

        if command_sequence is None:
            command_sequence = [gpy.EndTarget(self, f'EndTarget for Target "{self.name}"')]

        super().__init__('Target', name)

        self.command_sequence = command_sequence

        """
        Parameters:
            Covariance: Rmatrix
            Comment: String
            Summary: String
            MissionSummary: String
            Targeter: String
        """

        """
        From Moderator.CreateDefaultCommand, Target:
        // set DifferentCorrector
        Solver *solver = GetDefaultBoundaryValueSolver();
        id = cmd->GetParameterID("Targeter");
        cmd->SetStringParameter(id, solver->GetName());
        """

        # Get default solver then replace if the user has provided a solver object
        self.def_solver_name = self.GetRefObjectName(gmat.SOLVER)
        self.solver = gmat.GetObject(self.def_solver_name)
        if solver:
            self.solver: gpy.DifferentialCorrector | gmat.DifferentialCorrector = solver
            new_solver_name = self.solver.GetName()
            self.SetStringParameter('Targeter', new_solver_name)
        # self.solver = gmat.GetObject(self.solver_name)
        # self.solver.Initialize()

        self.solve_mode = solve_mode
        self.SetField('SolveMode', self.solve_mode)

        self.exit_mode = exit_mode
        # TODO: type for ExitMode field must be "Reference Array" - see User Guide pg 813 (PDF pg 822)
        # self.SetField('ExitMode', self.exit_mode)

        self.command_sequence: list[gpy.GmatCommand] = command_sequence

        self.SetSolarSystem()
        self.SetObjectMap(gpy.Moderator().GetConfiguredObjectMap())
        self.SetGlobalObjectMap(gpy.Sandbox().GetGlobalObjectMap())

        # # Make sure the final item in the command sequence is an EndTarget object
        if not isinstance(command_sequence[-1], gmat.EndTarget | gpy.EndTarget):
            # self.Append(gpy.EndTarget(f'EndTarget for {self.name}'))
            command_sequence.append(gpy.EndTarget(self))

        # print([command.GetTypeName() for command in command_sequence])

        # end_target = gpy.EndTarget(self)
        # self.AddBranch(end_target)
        # print(end_target.gmat_obj.IsOfType('BranchCommand'))
        # end_target.Append(self)
        # print(self.GetNext())

        for command in self.command_sequence:
            self.Append(gpy.extract_gmat_obj(command))

            # self.AddBranch(gpy.extract_gmat_obj(command))
            # update variables and goals in Achieve commands
            # if isinstance(command, gpy.Achieve | gpy.Vary):
            #     if isinstance(command, gpy.Achieve):
            #         # use Achieve's goal in Target
            #         goals_id = command.solver.GetParameterID('Goals')
            #         command.solver.SetStringParameter(goals_id, command.goal)
            #         # print(command.solver.gmat_obj.GetStringParameter(goals_id))
            #         CustomHelp(command.solver)
            #         print('(For Achieve command\'s solver)')
            #         pass
            #
            #     if isinstance(command, gpy.Vary):
            #         # use Vary's variable in Target
            #         vars_id = command.solver.GetParameterID('Variables')
            #         command.solver.SetStringParameter(vars_id, command.variable)
            #         CustomHelp(command.solver)
            #         print('(For Vary command\'s solver)')
            #         # print(command.solver.gmat_obj.GetStringParameter(1))
            #         pass
                # command.Initialize()
                # self.Initialize()

            # CustomHelp(command.solver)

            # try:
            #     gmat.Initialize()
            #     command.Initialize()
            # except Exception as ex:
            #     raise RuntimeError(f'Initialization failed for {command.GetTypeName()} command named '
            #                        f'"{command.GetName()}" in Target.__init__():\n\t{ex}') from ex

        # print(self.GetGeneratingString())
        # print('\n', self.solver.GetGeneratingString())
        # self.Initialize()
        # gmat.Initialize()
        # self.Initialize()

        # CustomHelp(self.solver)
        # print(f'Target command named "{self.name}" will target {self.variable}')
        pass


class Vary(SolverSequenceCommand):
    def __init__(self, name: str, solver: gpy.DifferentialCorrector | gmat.DifferentialCorrector, variable: str,
                 initial_value: float | int = 1, perturbation: float | int = 0.0001, lower: float | int = 0.0,
                 upper: float | int = pi, max_step: float | int = 0.5, additive_scale_factor: float | int = 0.0,
                 multiplicative_scale_factor: float | int = 1.0):
        super().__init__('Vary', name)

        self.solver = solver
        self.SetStringParameter('SolverName', self.solver.GetName())
        # self.SetRefObject(self.solver, gmat.SOLVER)

        # solver_vars = self.solver.GetStringArrayParameter('Variables')

        self.variable = variable
        self.SetStringParameter('Variable', self.variable)
        # print(f"Variables in Vary directly after setting: {self.solver.GetStringArrayParameter('Variables')}")
        # print(f"Goals in Vary directly after setting: {self.solver.GetStringArrayParameter('Goals')}")
        # self.solver.SetStringParameter('Variables', str(self.variable))

        # gpy.CustomHelp(self.solver)

        if initial_value < lower:
            raise RuntimeError('initial_value is less than lower (minimum value) in Vary.__init__().'
                               f'\n- initial_value:\t{initial_value}'
                               f'\n- lower:\t\t\t{lower}')
        if initial_value > upper:
            raise RuntimeError('initial_value is greater than upper (maximum value) in Vary.__init__().'
                               f'\n- initial_value:\t{initial_value}'
                               f'\n- upper:\t\t\t{upper}')
        self.initial_value = initial_value
        self.SetStringParameter('InitialValue', str(self.initial_value))

        self.perturbation = perturbation
        self.SetStringParameter('Perturbation', str(self.perturbation))

        self.lower = lower
        self.SetStringParameter('Lower', str(self.lower))

        self.upper = upper
        self.SetStringParameter('Upper', str(self.upper))

        self.max_step = max_step
        self.SetStringParameter('MaxStep', str(self.max_step))

        self.additive_scale_factor = additive_scale_factor
        self.SetStringParameter('AdditiveScaleFactor', str(self.additive_scale_factor))

        self.multiplicative_scale_factor = multiplicative_scale_factor
        self.SetStringParameter('MultiplicativeScaleFactor', str(self.multiplicative_scale_factor))

        self.SetSolarSystem()
        self.SetObjectMap(gpy.Moderator().GetConfiguredObjectMap())
        self.SetGlobalObjectMap(gpy.Sandbox().GetGlobalObjectMap())

        self.Initialize()
        print(f"Variables in Vary: {self.solver.GetStringArrayParameter('Variables')}")
        print(f"Goals in Vary: {self.solver.GetStringArrayParameter('Goals')}\n")
        # CustomHelp(self)
        pass

        solver_vars_new = self.solver.GetStringArrayParameter('Variables')
        solver_goals = self.solver.GetStringArrayParameter('Goals')
        # if solver_vars_new and solver_goals:
        #     self.solver.Initialize()

        # ! SetSolverVariables() not needed - already set during object creation !
        # Line 1321 of Vary.cpp: variableID = solver->SetSolverVariables(varData, variableName);
        #  varData is a 6-element array (lines 1307-1312 of Vary.cpp):
        #     // scale by using Eq. 13.5 of Architecture document
        #     varData[0] = (varData[5] + asf) / msf;
        #     varData[1] = (perturbation->EvaluateReal()) / msf;         // pert
        #     varData[2] = (minval + asf) / msf;  // minimum
        #     varData[3] = (maxval + asf) / msf;  // maximum
        #     varData[4] = (variableMaximumStep->EvaluateReal()) / msf;  // largest step
        # self.gmat_obj.SetSolverVariables(f'TestSat.Earth.RMAG', '')

        # SetSolverVariables lead-in
        # msf = 1/float(self.GetStringParameter('MultiplicativeScaleFactor'))
        # if msf <= 0:
        #     raise RuntimeError(f'msf in Vary __init__() was <= 0 (value: {msf})')
        #
        # initval = float(self.GetStringParameter('InitialValue')
        # minval = float(self.GetStringParameter('InitialValue')
        # maxval = float(self.GetStringParameter('InitialValue')

        # # Ported from lines 1308-1312 of Vary.cpp in source
        # var_data: list = [None] * 6
        # var_data[5] = initial_value
        # var_data[0] = (var_data[5] + self.additive_scale_factor) / self.multiplicative_scale_factor
        # var_data[1] = perturbation / self.multiplicative_scale_factor
        # var_data[2] = (self.lower + self.additive_scale_factor) / self.multiplicative_scale_factor
        # var_data[3] = (self.upper + self.additive_scale_factor) / self.multiplicative_scale_factor
        # var_data[4] = self.max_step / self.multiplicative_scale_factor
        #
        # print(self.solver.GetStringArrayParameter('Variables'))
        # print(self.variable)
        # self.solver.SetSolverVariables(var_data, self.variable)

        # self.Initialize()  # adds self.variable to self.solver's Variables list
        #
        # self.solver.Initialize()

        # if not self.Validate():
        #     raise RuntimeError(f'Vary command {self.name} failed self.Validate')
        #
        # if not gpy.Validator().ValidateCommand(self):
        #     raise RuntimeError(f'Vary command {self.name} failed Validator.ValidateCommand')

    def SetRefObject(self, obj: gmat.GmatBase, type_id: int) -> bool:
        return gpy.extract_gmat_obj(self).SetRefObject(gpy.extract_gmat_obj(obj), type_id)
