from __future__ import annotations

import gc
import inspect
import traceback

from load_gmat import gmat

import gmat_py_simple as gpy
from gmat_py_simple.utils import *

from math import pi


class GmatCommand:
    def __init__(self, command_type: str, name: str):
        self.command_type: str = command_type

        # We can use the Python layer of the GMAT Python API to create an object of the correct type
        # This then has full access to the relevant class methods e.g. ClearObject() for a Propagate.
        # If created with Moderator.CreateDefaultCommand(command_type), a GmatCommand object is made instead of the
        # relevant subtype e.g. Propagate
        self.gmat_obj = eval(f'gmat.{self.command_type}()')  # e.g. calls gmat.Propagate() for a Propagate command
        print(self.gmat_obj)

        # Set GMAT object's name
        if self.command_type == 'BeginMissionSequence':  # TODO: remove if not needed - TBC
            self.name: str = ''  # the BeginMissionSequence command is not allowed to have a name
        else:
            self.name: str = name
        self.gmat_obj.SetName(self.name)  # set obj name, as CreateDefaultCommand does not (Jira issue GMT-8095)

        # # CreateCommand currently broken (GMT-8100), so use CreateDefaultCommand and remove any unnecessary objects
        # if self.command_type != 'Propagate':
        #     self.gmat_obj: gmat.GmatCommand = gpy.Moderator().CreateDefaultCommand(self.command_type, self.name)
        # else:
        #     sat_name = gpy.Moderator().GetDefaultSpacecraft().GetName()
        #     # Find which objs exist that would be made during CreateDefaultCommand('Propagate'). Then we won't try to
        #     # remove them later, as they're being used by other objects (e.g. DefaultProp_ForceModel by a PropSetup)
        #     pgate_def_obj_names = ['DefaultProp_ForceModel', f'{sat_name}.A1ModJulian', f'{sat_name}.ElapsedSecs']
        #     existing_pgate_objs = []
        #     for obj_name in pgate_def_obj_names:
        #         try:
        #             gmat.GetObject(obj_name)
        #             # GetObject worked, so object already exists and must not be deleted - add to list
        #             existing_pgate_objs.append(obj_name)
        #
        #         # object doesn't yet exist in GMAT, so can safely be deleted after CreateDefaultCommand('Propagate')
        #         except AttributeError as ex:
        #             pass
        #
        #     # make default Propagate - will also try to add default ForceModel and StopCondition
        #     self.gmat_obj: gmat.GmatCommand = gpy.Moderator().CreateDefaultCommand(self.command_type, self.name)
        #
        #     for def_name in pgate_def_obj_names:  # clear objects that are safe to clear
        #         if def_name in existing_pgate_objs:  # skip object if it already exists (so is used by another object)
        #             pass
        #         else:
        #             gmat.Clear(def_name)  # remove the object from GMAT
        #             # if def_name == 'DefaultProp_ForceModel':  # gmat.ODE_MODEL
        #             #     gpy.Moderator().RemoveObject(gmat.ODE_MODEL, def_name)
        #             # else:  # gmat.PARAMETER
        #             #     gpy.Moderator().RemoveObject(gmat.PARAMETER, def_name)
        #
        #     # Also clear the lists of Spacecraft, Formations and StopConditions reference in the Propagate command
        #     print(self.gmat_obj.GetTypeName())
        #     self.gmat_obj.ClearObject(gmat.SPACECRAFT)
        #     self.gmat_obj.ClearObject(gmat.FORMATION)
        #     self.gmat_obj.ClearObject(gmat.STOP_CONDITION)
        #
        #     # gpy.Initialize()

        # TODO bugfix: switch to CreateCommand (uncomment below) when issue GMT-8100 fixed
        # self.gmat_obj: gmat.GmatCommand = gpy.Moderator().CreateCommand(self.command_type, self.name)

    def AddToMCS(self) -> bool:
        return gpy.Moderator().AppendCommand(self)

    def Initialize(self) -> bool:
        try:
            resp = self.gmat_obj.Initialize()
            if not resp:
                raise RuntimeError('Non-true response from Initialize()')
            return resp
        except Exception as ex:
            raise RuntimeError(f'Initialize failed for {type(self).__name__} named "{self.name}". See GMAT error below:'
                               f'\n{ex}') from ex

    def GeneratingString(self):
        print(self.GetGeneratingString())

    def GetGeneratingString(self) -> str:
        return self.gmat_obj.GetGeneratingString()

    def GetField(self, field: str) -> str:
        return self.gmat_obj.GetField(field)

    def GetMissionSummary(self):
        return self.gmat_obj.GetStringParameter('MissionSummary')

    def GetRefObject(self, type_id: int, name: str):
        return self.gmat_obj.GetRefObject(type_id, name)

    def GetRefObjectName(self):
        raise NotImplementedError

    def GetName(self) -> str:
        return self.gmat_obj.GetName()

    def Help(self):
        self.gmat_obj.Help()

    def SetBooleanParameter(self, param_name: str, value: bool) -> bool:
        return self.gmat_obj.SetBooleanParameter(param_name, value)

    def SetField(self, field: str, value) -> bool:
        return self.gmat_obj.SetField(field, value)

    def SetGlobalObjectMap(self, gom: gmat.ObjectMap) -> bool:
        return self.gmat_obj.SetGlobalObjectMap(gom)

    def SetName(self, name: str) -> bool:
        self.name = name
        return self.gmat_obj.SetName(name)

    def SetObjectMap(self, om: gmat.ObjectMap) -> bool:
        return self.gmat_obj.SetObjectMap(om)

    def SetRefObject(self, obj, obj_type: int, obj_name: str) -> bool:
        obj = gpy.extract_gmat_obj(obj)
        return self.gmat_obj.SetRefObject(obj, obj_type, obj_name)

    def SetRefObjectName(self, type_id: int, name: str) -> bool:
        return self.gmat_obj.SetRefObjectName(type_id, name)

    def SetSolarSystem(self, ss: gmat.SolarSystem = gmat.GetSolarSystem()) -> bool:
        return self.gmat_obj.SetSolarSystem(ss)

    def SetStringParameter(self, param_name: str, value: str) -> bool:
        return self.gmat_obj.SetStringParameter(param_name, value)

    def Validate(self) -> bool:
        try:
            return self.gmat_obj.Validate()
        except Exception as ex:
            raise RuntimeError(f'{type(self).__name__} named "{self.name}" failed to Validate') from ex


# class BranchCommand(GmatCommand):
#     def __init__(self, command_type: str, name: str):
#         super().__init__(command_type, name)


class Achieve(GmatCommand):
    def __init__(self, name: str, solver: gpy.DifferentialCorrector, goal: str, value: int | float,
                 tolerance: float | int = 0.1):
        super().__init__('Achieve', name)

        self.solver = solver
        self.SetField('TargeterName', self.solver.name)
        # type_array = self.gmat_obj.GetRefObjectTypeArray()
        # print(f'{type_array[0]}: {gpy.GetTypeNameFromID(type_array[0])}')
        # print(f'Ref object name array: {self.gmat_obj.GetRefObjectNameArray(127)}')
        self.SetRefObject(self.solver.gmat_obj, gmat.SOLVER, self.solver.name)

        self.goal = goal
        self.SetField('Goal', self.goal)

        self.value = value
        self.SetField('GoalValue', str(self.value))

        self.tolerance = tolerance
        self.SetField('Tolerance', str(self.tolerance))

        # TODO: try the following:
        self.solver.gmat_obj.UpdateSolverGoal(0, self.value)

        # TODO bugfix: Exception thrown during self.solver.Initialize(): gmat_py.APIException: Solver subsystem
        #  exception: Targeter cannot initialize: No goals or variables are set.
        # self.solver.Initialize()

        self.SetSolarSystem()
        self.SetObjectMap(gpy.Moderator().GetConfiguredObjectMap())
        self.SetGlobalObjectMap(gpy.Sandbox().GetGlobalObjectMap())

        # TODO bugfix: Exception thrown during initialize: gmat_py.APIException: Command Exception: Targeter not
        #  initialized for Achieve command "Achieve DC1(DefaultSC.Earth.RMAG = 42165.0, {Tolerance = 0.1});"
        #  Caused by targeter parameter in Achieve being null

        gpy.Initialize()
        self.Initialize()


class BeginFiniteBurn(GmatCommand):
    def __init__(self, name: str):
        super().__init__('BeginFiniteBurn', name)
        raise NotImplementedError


class BeginMissionSequence(GmatCommand):
    def __init__(self):
        # TODO: uncomment to get all items initialized (handling in Tut02 for now)
        gpy.Initialize()  # initialize GMAT so objects are in place for use in command sequence

        super().__init__('BeginMissionSequence', 'BeginMissionSequenceCommand')

        self.SetSolarSystem()
        self.SetObjectMap(gpy.Moderator().GetConfiguredObjectMap())
        self.SetGlobalObjectMap(gpy.Sandbox().GetGlobalObjectMap())

        gpy.Initialize()
        self.Initialize()


class EndFiniteBurn(GmatCommand):
    def __init__(self, name: str):
        super().__init__('EndFiniteBurn', name)
        raise NotImplementedError


class EndTarget(GmatCommand):
    def __init__(self, name: str):
        super().__init__('EndTarget', name)


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

        gpy.Initialize()
        self.Initialize()


class Propagate(GmatCommand):
    """
    Propagate the orbit of a single spacecraft. For multiple spacecraft, use PropagateMulti
    """

    class StopCondition:
        # def __init__(self, name: str, base_epoch=None, epoch=None, epoch_var=None, stop_var=None,
        #              goal=None, repeat=None):
        # def __init__(self, sat: gpy.Spacecraft, epoch_var: str = 'Sat.A1ModJulian', stop_var: str = 'Sat.ElapsedSecs',
        #              goal: int | float = None, name: str = 'StopOnSat.ElapsedSecs', description: str = ''):
        #     # TODO fill other possible args - see StopCondition.cpp
        #     # self.base_epoch = base_epoch
        #     # self.epoch = epoch
        #     # self.epoch_var = epoch_var
        #     # self.stop_var = stop_var
        #     # self.goal = goal
        #     # self.repeat = repeat
        #     # self.sat = sat
        #
        #     # TODO bugfix: handle case where sc has been created then overwritten with same Python name but different
        #     #  GMAT name. Causes error: "Command Exception: *** Currently GMAT expects a Parameter of propagating
        #     #  Spacecraft to be on the LHS of stopping condition (propagating spacecraft not found) in Propagate
        #     #  'Prop One Day' DefaultProp(DefaultSC) {Sat.Earth.Apoapsis};"
        #
        #     # TODO: raise error if goal needed (e.g. number for ElapsedSecs) but not given
        #
        #     """
        #     Create a StopCondition
        #
        #     :param sat:
        #     :param epoch_var:
        #     :param stop_var:
        #     :param goal:
        #     :param name:
        #     :param description:
        #     """
        #     self.sat = sat
        #     sat_name = self.sat.GetName()
        #
        #     # TODO: move a lot of this to StopCondition.parse_stop_params. Only keep StopCond creation itself here
        #     goalless_params = ['Apoapsis', 'Periapsis']  # TODO: complete list
        #     if True in (param in stop_var for param in goalless_params):  # if stop_var includes a goalless param
        #         self.goalless = True
        #         goal = None
        #         # self.stop_param_type = param
        #     else:
        #         self.goalless = False
        #         goal = str(goal)
        #
        #     self.goal = goal  # assumes that parsing function will have set goal to None if required
        #
        #     self.body = None
        #     bodies = CelestialBodies()
        #     if self.goalless:
        #         self.epoch_var = ''
        #         for param in goalless_params:  # TODO: find a way to combine this into if True in... above
        #             if param in stop_var:
        #                 self.stop_param_type = param
        #     else:
        #         self.epoch_var = epoch_var
        #         self.epoch_param_type = self.epoch_var.split('.')[1]
        #
        #     for body in bodies:
        #         if body in stop_var:
        #             self.body = body
        #             continue  # use the first body we find in self.stop_var
        #
        #     if self.goalless and not self.body:
        #         raise AttributeError('No body found for StopCondition')
        #
        #     self.stop_var = stop_var
        #
        #     # currently using the goalless check to tell whether Earth or similar is needed in stop_param_type
        #     if not self.goalless:
        #         # self.stop_var isn't body-based, so need to remove any bodies
        #         elements = self.stop_var.split('.')
        #         stop_var_elements = []
        #         stop_param_type_elements = []
        #         for ele in elements:
        #             if ele not in bodies:
        #                 stop_var_elements.append(ele)
        #                 if ele != sat_name:
        #                     stop_param_type_elements.append(ele)
        #
        #         self.stop_var = '.'.join(stop_var_elements)
        #         self.stop_param_type = '.'.join(stop_param_type_elements)
        #
        #     self.description = description
        #     self.name = name if name else f'StopOn{self.stop_var}'
        #
        #     self.gmat_obj = gpy.Moderator().CreateStopCondition(self.name)
        #     self.gmat_obj.SetSolarSystem(gmat.GetSolarSystem())
        #
        #     # if self.epoch_var:
        #     self.epoch_param: gpy.Parameter = gpy.CreateParameter(self.epoch_param_type, self.epoch_var)
        #     self.epoch_param.SetRefObjectName(gmat.SPACECRAFT, sat_name)
        #     self.SetEpochParameter(self.epoch_param)
        #     self.SetStringParameter('EpochVar', self.epoch_var)
        #
        #     # TODO: see parameter.StopParameter and subclasses (ElapsedSecs etc) for quick way to implement stop params
        #
        #     self.stop_param = gpy.CreateParameter(self.stop_param_type, self.stop_var)
        #     self.stop_param.SetRefObjectName(gmat.SPACECRAFT, sat_name)
        #     if not self.body:  # TODO: work out how to get the body more reliably to avoid needing this fallback clause
        #         self.body = 'Earth'  # if we've not set self.body yet, use Earth as a fallback
        #     self.stop_param.SetRefObjectName(gmat.SPACE_POINT, self.body)
        #     if self.goalless:
        #         # self.stop_param.SetRefObjectName(gmat.SPACE_POINT, self.body)
        #         self.stop_param.SetRefObjectName(gmat.CELESTIAL_BODY, self.body)
        #         coord_sys_name = self.sat.GetField('CoordinateSystem')
        #         self.stop_param.SetRefObjectName(gmat.COORDINATE_SYSTEM, coord_sys_name)
        #     # else:
        #     #     self.goal_param = gpy.CreateParameter('Variable', f'Goal={self.goal}')
        #     #     self.SetGoalParameter(self.goal_param)
        #     #     self.SetStringParameter('Goal', self.goal)
        #     #     self.goal_param.SetRefObjectName(gmat.SPACECRAFT, sat_name)
        #
        #     self.SetStringParameter('StopVar', self.stop_param.GetName())
        #     self.SetStopParameter(self.stop_param)
        #
        #     self.Validate()

        # def __new__(cls, sat, stop_cond):
        #     instance = gmat.StopCondition()
        #     instance.sat = sat
        #     instance.stop_cond = stop_cond
        #     return gmat.StopCondition()

        def __init__(self, sat: gpy.Spacecraft, stop_cond: str | tuple):
            # TODO fill other possible args - see StopCondition.cpp
            # self.base_epoch = base_epoch
            # self.epoch = epoch
            # self.epoch_var = epoch_var
            # self.stop_var = stop_var
            # self.goal = goal
            # self.repeat = repeat
            # self.sat = sat

            # TODO bugfix: handle case where sc has been created then overwritten with same Python name but different
            #  GMAT name. Causes error: "Command Exception: *** Currently GMAT expects a Parameter of propagating
            #  Spacecraft to be on the LHS of stopping condition (propagating spacecraft not found) in Propagate
            #  'Prop One Day' DefaultProp(DefaultSC) {Sat.Earth.Apoapsis};"

            # TODO: raise error if goal needed (e.g. number for ElapsedSecs) but not given

            gmat.Initialize()

            self.sat = sat
            self.sat_name = self.sat.GetName()

            self.propagate_name = inspect.stack()[1][0].f_locals["self"].name

            (self.stop_param_type,
             self.stop_var,
             self.epoch_param_type,
             self.epoch_var,
             self.goal_param_type,
             self.goal,
             self.goalless,
             self.body) = self.parse_stop_cond(stop_cond)

            print(f'\nPropagate name: "{self.propagate_name}"')
            print(f'epoch_var: {self.epoch_var}')
            print(f'stop_var: {self.stop_var}')
            print(f'goal: {self.goal}')

            self.name = f'StopOn{self.stop_var}'

            mod = gpy.Moderator()
            # self.gmat_obj: gmat.StopCondition = mod.CreateStopCondition(self.name)  # create basic StopCondition
            self.gmat_obj = gmat.StopCondition(self.name)  # create basic StopCondition
            # self.SetSolarSystem()

            # Get coordinate system and body/origin details and assign to StopCondition
            self.coord_sys_name = self.sat.GetField('CoordinateSystem')
            self.coord_sys_obj = gmat.GetObject(self.coord_sys_name)
            # get body from CoordinateSystem
            self.body_obj = gmat.GetObject(self.coord_sys_obj.GetField('Origin'))

            # TODO remove (for debugging only)
            self.param_count = 0
            self.periapsis_count = 0

            # TODO remove (only to remove angry highlight on self.setup_all_stop_cond_params())
            self.epoch_param = None
            self.stop_param = None
            self.goal_param = None

            # Setup epoch parameter
            # self.epoch_param = gpy.Parameter(self.epoch_param_type, self.epoch_var)
            # print(f'epoch_param name: {self.epoch_param.name}')
            self.SetStringParameter('EpochVar', self.epoch_var)
            # self.epoch_param = self.setup_stop_cond_param(self.epoch_param, 'Epoch')

            # Setup stop parameter
            # self.stop_param: gpy.Parameter = gpy.Parameter(self.stop_param_type, self.stop_var)
            # print(f'stop_param name: {self.stop_param.name}')
            self.SetStringParameter('StopVar', self.stop_var)
            # self.stop_param = self.setup_stop_cond_param(self.stop_param, 'Stop')

            # Setup goal parameter
            # self.goal_param = gpy.Parameter(self.goal_param_type, self.goal)
            # print(f'goal_param name: {self.goal_param.name}')
            self.SetStringParameter('Goal', self.goal)
            # self.goal_param = self.setup_stop_cond_param(self.goal_param, 'Goal')

            # self.setup_all_stop_cond_params()

            print(self.GetAllParameters())
            pass  # TODO remove (debugging StringParameters for Apo/Periapsis, ElapsedDays)

        @staticmethod
        def create_epoch_param(epoch_param_type: str, epoch_var: str):
            return gpy.Moderator().CreateParameter(epoch_param_type, epoch_var)

        @staticmethod
        def create_stop_param(stop_param_type: str, stop_var: str):
            return gmat.Moderator.Instance().CreateParameter(stop_param_type, stop_var)

        @staticmethod
        def create_goal_param(goal: str):
            # make sure goal is a string - other types not accepted for Variable Parameters
            return gpy.Moderator().CreateParameter('Variable', str(goal))

        def parse_stop_cond(self, stop_cond: str | tuple) -> tuple:
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
                raise RuntimeError(f'stop_conds is invalid. Must be a 2-element tuple or a string')

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
                if sat_from_stop_cond != self.sat_name:
                    raise RuntimeError(
                        f'Name of satellite given in StopCondition "{stop_cond}" ({sat_from_stop_cond}) does'
                        f' not match name for Propagate\'s satellite ({self.sat_name})')
            else:
                raise SyntaxError('Invalid number of parts for stop_cond. Must be two (e.g. "Sat.ElapsedSecs") or three'
                                  '(e.g. "Sat.Earth.Periapsis")')

            stop_param_type = stop_var[len(self.sat.name) + 1:]  # remove sat name and . from stop_var

            # following types taken from src/Moderator.CreateDefaultParameters() Time parameters section
            allowed_epoch_param_types = ['ElapsedSecs', 'ElapsedDays', 'A1ModJulian', 'A1Gregorian',
                                         'TAIModJulian', 'TAIGregorian', 'TTModJulian', 'TTGregorian',
                                         'TDBModJulian', 'TDBGregorian', 'UTCModJulian', 'UTCGregorian']
            # TODO: remove hard-coding of epoch_param_type
            # TODO: decide when to use other epoch_param_types
            epoch_param_type = 'A1ModJulian'
            epoch_var = f'{self.sat.name}.{epoch_param_type}'

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

            return stop_param_type, stop_var, epoch_param_type, epoch_var, goal_param_type, goal, goalless, body

        @classmethod
        def CreateDefault(cls):
            return gmat_py_simple.Moderator().CreateDefaultStopCondition()

        # @classmethod
        # def parse_stop_params(cls, sat: gpy.Spacecraft,
        #                       stop_conds: tuple[str | int | float] | str) -> Propagate.StopCondition:
        #     # TODO: handle parsing of all possible epoch_vars/stop_vars/goals
        #     if isinstance(stop_conds, tuple) and len(stop_conds) == 2:  # most likely, e.g. ('Sat.ElapsedSecs', 12000)
        #         stop_var = stop_conds[0]
        #         goal = stop_conds[1]
        #
        #     elif isinstance(stop_conds, str):  # e.g. ('Sat.Earth.Apoapsis')
        #         stop_var = stop_conds
        #         goal = stop_var
        #
        #     else:
        #         raise RuntimeError(f'stop_conds is invalid. Must be a 2-element tuple or a string')
        #
        #     stop_cond_elements = stop_var.split('.')  # stop_var is string, e.g. Sat.Earth.Apoapsis
        #     sat_name_in_stop_cond = stop_cond_elements[0]
        #     if sat.name != sat_name_in_stop_cond:  # TODO: change condition to doesn't match any s/c names?
        #         raise SyntaxError(f'Spacecraft name given in StopCondition ({sat_name_in_stop_cond}) is different from'
        #                           f' the name of the specified spacecraft ({sat.name})')
        #
        #     name = f'StopOn{stop_var}'
        #     stop_cond_obj = cls(sat, stop_var=stop_var, goal=goal, name=name)
        #
        #     return stop_cond_obj

        def GetIntegerParameter(self, param_name: str) -> int:
            return self.gmat_obj.GetIntegerParameter(param_name)

        def GetName(self):
            return self.gmat_obj.GetName()

        def GetAllParameters(self) -> str:
            return ('\nCurrent parameter values:\n'
                    f'- BaseEpoch: {self.GetRealParameter("BaseEpoch")}\n'
                    f'- Epoch:     {self.GetRealParameter("Epoch")}\n'
                    f'- EpochVar:  {self.GetStringParameter("EpochVar")}\n'
                    f'- StopVar:   {self.GetStringParameter("StopVar")}\n'
                    f'- Goal:      {self.GetStringParameter("Goal")}\n'
                    f'- Repeat:    {self.GetIntegerParameter("Repeat")}')

        def GetEpochParameter(self) -> bool:
            return self.gmat_obj.GetEpochParameter()

        def GetGoalParameter(self) -> bool:
            return self.gmat_obj.GetGoalParameter()

        def GetRealParameter(self, param_name: str) -> int | float:
            return self.gmat_obj.GetRealParameter(param_name)

        def GetStopGoal(self) -> float:
            return self.gmat_obj.GetStopGoal()

        def GetStopParameter(self) -> bool:
            return self.gmat_obj.GetStopParameter()

        def GetStringParameter(self, param_name: str) -> str:
            return self.gmat_obj.GetStringParameter(param_name)

        def Help(self):
            self.gmat_obj.Help()

        def Initialize(self):
            try:
                initialize = self.gmat_obj.Initialize()
                if not initialize:
                    raise RuntimeError('Initialize() failed')
                return initialize
            except Exception as ex:
                print(f'CM list of items in StopCond.Initialize(): {gmat.ConfigManager.Instance().GetListOfAllItems()}')
                raise RuntimeError(f'StopCondition named "{self.name}" failed to Initialize - see exception below:'
                                   f'\n     {ex}') from ex

        def IsTimeCondition(self) -> bool:
            return self.gmat_obj.IsTimeCondition()

        def SetDescription(self, description: str) -> bool:
            self.description = description
            return self.gmat_obj.SetDescription(description)

        def SetEpochParameter(self, epoch_param: gpy.Parameter) -> bool:
            if 'gmat_py_simple' in str(type(epoch_param)):
                return self.gmat_obj.SetEpochParameter(epoch_param.swig_param)
            else:
                return self.gmat_obj.SetEpochParameter(epoch_param)
            # return self.gmat_obj.SetEpochParameter(epoch_param)

        def SetGoalParameter(self, goal_param: gpy.Parameter) -> bool:
            return self.gmat_obj.SetGoalParameter(goal_param.swig_param)

        def SetInterpolator(self, interp: gmat.Interpolator) -> bool:
            return self.gmat_obj.SetInterpolator(interp)

        def SetPropDirection(self, direction: int) -> bool:
            return self.gmat_obj.SetPropDirection(direction)

        def SetRefObject(self, obj, type_int: int, name: str):
            obj = gpy.extract_gmat_obj(obj)
            if not name:
                name = obj.GetName()
            resp = self.gmat_obj.SetRefObject(obj, type_int, name)
            if not resp:
                raise RuntimeError('StopCondition.SetRefObject() failed for arguments:'
                                   f'\t- obj:       {obj}'
                                   f'\t- type_int:  {type_int}')
            return resp

        def SetSolarSystem(self, ss: gmat.SolarSystem = gmat.GetSolarSystem()) -> bool:
            return self.gmat_obj.SetSolarSystem(ss)

        def SetStopParameter(self, stop_param: gpy.Parameter) -> bool:
            if 'gmat_py_simple' in str(type(stop_param)):
                return self.gmat_obj.SetStopParameter(stop_param.swig_param)
            else:
                return self.gmat_obj.SetStopParameter(stop_param)

        def SetStringParameter(self, param_name: str, value: str):
            return self.gmat_obj.SetStringParameter(param_name, value)

        def setup_all_stop_cond_params(self) -> True:
            """
            Shortcut to set up self.epoch_param, self.stop_param, self.goal_param.

            :return: True if completed successfully, otherwise exception
            """
            try:
                self.epoch_param = self.setup_stop_cond_param(self.epoch_param, 'Epoch')
                self.stop_param = self.setup_stop_cond_param(self.stop_param, 'Stop')
                self.goal_param = self.setup_stop_cond_param(self.goal_param, 'Goal')

                gmat.Initialize()  # TODO: assess whether needed - remove if not

                return True

            except Exception as ex:
                raise ex

        def setup_stop_cond_param(self, param: gpy.Parameter, param_type: str = 'Stop, Epoch or Goal') -> gpy.Parameter:
            if param_type not in ['Stop', 'Epoch', 'Goal']:
                raise SyntaxError("param_type must be 'Stop', 'Epoch' or 'Goal'")
            p_name = param.name
            p_g_type = param.GetTypeName()

            if p_g_type == 'Periapsis':
                self.periapsis_count += 1
                # Only modification needed from default is ensuring correct body (e.g. Earth) is set

                # TODO remove (for debugging stop_param and goal_param both making Periapsis params)
                if self.periapsis_count == 2:
                    gmat.ShowObjects()
                    raise RuntimeError('Too many periapses!')

                param.SetRefObjectName(gmat.SPACE_POINT, self.body)
                param.gmat_base.SetRefObject(self.body_obj, gmat.SPACE_POINT, self.body)
                return param

            param.SetSolarSystem()

            # Link spacecraft to parameter
            param.SetRefObjectName(gmat.SPACECRAFT, self.sat_name)
            param.SetRefObject(self.sat, gmat.SPACECRAFT)

            print(f'\nparam_type: {param_type}')
            if param_type == 'Stop':
                # print(param.SetRefObjectName(gmat.COORDINATE_SYSTEM, self.coord_sys_name))
                # print(param.SetRefObject(self.coord_sys_obj, gmat.COORDINATE_SYSTEM))

                print(f'Param GMAT type: {p_g_type}')
                if p_g_type == 'Periapsis':
                    pass
                    # print('Periapsis found')
                    # param.SetStringParameter('DepObject', self.body)

                    # param.SetRefObjectName(gmat.COORDINATE_SYSTEM, self.coord_sys_name)
                    # param.SetRefObject(self.coord_sys_obj, gmat.COORDINATE_SYSTEM)

                    # print(f'Setting body as SPACE_POINT for param {p_name}')
                    # # Add body (e.g. Earth) as SPACE_POINT ref object
                    # param.SetRefObjectName(gmat.SPACE_POINT, self.body)
                    # param.SetRefObject(self.body_obj, gmat.SPACE_POINT)

                    # param.SetRefObjectName(gmat.ORIGIN, self.body)
                    # param.SetRefObject(self.body_obj, gmat.ORIGIN)
                    # raise NotImplementedError

                print(f'self.goalless: {self.goalless}')
                # if self.goalless:
                #     print(f'Setting body as SPACE_POINT for param {p_name}')
                #     # Add body (e.g. Earth) as SPACE_POINT ref object
                #     param.SetRefObjectName(gmat.SPACE_POINT, self.body)
                #     param.SetRefObject(self.body_obj, gmat.SPACE_POINT)
                if not self.goalless:
                    print(f'Setting spacecraft as SPACE_POINT for param {p_name}')
                    # Add spacecraft as SPACE_POINT ref object
                    param.SetRefObjectName(gmat.SPACE_POINT, self.sat_name)
                    param.SetRefObject(self.sat, gmat.SPACE_POINT)

            elif param_type == 'Epoch':
                param.SetRefObjectName(gmat.SPACE_POINT, self.body)
                param.gmat_base.SetRefObject(self.body_obj, gmat.SPACE_POINT, self.body)

                # raise NotImplementedError('Epoch setup not implemented yet')

            elif param_type == 'Goal':
                print(f'Goal branch self.goalless: {self.goalless}')
                # if self.goalless:
                #     param.SetRefObjectName(gmat.SPACE_POINT, self.body)
                #     param.SetRefObject(self.body_obj, gmat.SPACE_POINT)
                # else:
                param.SetRefObjectName(gmat.SPACE_POINT, self.sat_name)
                param.SetRefObject(self.sat.gmat_obj, gmat.SPACE_POINT)

            # Validate parameter
            try:
                print(f'Validate result: {param.Validate()}')
            except RuntimeError as re:
                raise RuntimeError(f'param.Validate() failed for {param_type} Parameter "{p_name}" of type {p_g_type}:'
                                   f'\n{re}\n\n'
                                   f'param_type: {param_type} (Parameter), GMAT type: {p_g_type}, name: {p_name}\n'
                                   f'Ref obj type array: {param.gmat_base.GetRefObjectTypeArray()}\n\n'
                                   f'Ref obj array, SPACECRAFT: {param.gmat_base.GetRefObjectArray(gmat.SPACECRAFT)}\n'
                                   f'Ref obj array, SOLAR_SYSTEM: {param.gmat_base.GetRefObjectArray(gmat.SOLAR_SYSTEM)}\n'
                                   f'Ref obj array, SPACE_POINT: {param.gmat_base.GetRefObjectArray(gmat.SPACE_POINT)}\n'
                                   f'Ref obj array, COORDINATE_SYSTEM: {param.gmat_base.GetRefObjectArray(gmat.COORDINATE_SYSTEM)}\n\n'
                                   f'Ref obj name array, SPACECRAFT: {param.gmat_base.GetRefObjectNameArray(gmat.SPACECRAFT)}\n'
                                   f'Ref obj name array, SOLAR_SYSTEM: {param.gmat_base.GetRefObjectNameArray(gmat.SOLAR_SYSTEM)}\n'
                                   f'Ref obj name array, SPACE_POINT: {param.gmat_base.GetRefObjectNameArray(gmat.SPACE_POINT)}\n'
                                   f'Ref obj name array, COORDINATE_SYSTEM: {param.gmat_base.GetRefObjectNameArray(gmat.COORDINATE_SYSTEM)}') \
                    from None

            # Initialize parameter
            try:
                print(f'Initialize result: {param.Initialize()}')
            except RuntimeError as re:
                raise RuntimeError(f'Exception raised during param.Initialize() for {param_type} Parameter '
                                   f'"{p_name}" of type {p_g_type}:\n{re}\n\n'
                                   f'Ref obj type array: {param.gmat_base.GetRefObjectTypeArray()}\n\n'
                                   f'Ref obj array, SPACECRAFT: {param.gmat_base.GetRefObjectArray(gmat.SPACECRAFT)}\n'
                                   f'Ref obj array, SPACE_POINT: {param.gmat_base.GetRefObjectArray(gmat.SPACE_POINT)}\n'
                                   f'Ref obj array, COORDINATE_SYSTEM: {param.gmat_base.GetRefObjectArray(gmat.COORDINATE_SYSTEM)}\n\n'
                                   f'Ref obj name array, SPACECRAFT: {param.gmat_base.GetRefObjectNameArray(gmat.SPACECRAFT)}\n'
                                   f'Ref obj name array, SPACE_POINT: {param.gmat_base.GetRefObjectNameArray(gmat.SPACE_POINT)}\n'
                                   f'Ref obj name array, COORDINATE_SYSTEM: {param.gmat_base.GetRefObjectNameArray(gmat.COORDINATE_SYSTEM)}') from re

            # Link parameter to StopCondition (self)
            self.SetRefObject(param, gmat.PARAMETER, param.name)

            return param

        def Validate(self) -> bool:
            try:
                valid = self.gmat_obj.Validate()
                if not valid:
                    raise RuntimeError(f'Validate() returned a non-true value: {valid}')
                return valid
            except Exception as ex:
                raise RuntimeError(f'StopCondition named "{self.name}" failed to Validate - see exception below:'
                                   f'\n     {ex}') from ex

    # OLD - from before using CreateDefaultCondition
    # def __init__(self, propagator: PropSetup, sc: Spacecraft, stop: tuple = ('DefaultSC.ElapsedSecs', 8640),
    #              stop_tolerance: str = 1e-7, mode: str = None, prop_forward: bool = True):
    #     self.stop_param_allowed_values = {
    #         # TODO complete this properties list based on options available in GUI Propagate command
    #         'Spacecraft': ['A1ModJulian', 'Acceleration', 'AccelerationX', 'AccelerationY', 'AccelerationZ',
    #                        'AltEquinoctialP', 'AltEquinoctialQ', 'Altitude', 'AngularVelocityX', 'AngularVelocityY',
    #                        'AngularVelocityZ', 'AOP', 'Apoapsis', 'AtmosDensity', 'AtmosDensityScaleFactor',
    #                        'AtmosDensityScaleFactorSigma', 'AZI', 'BdotR', 'BdotT', 'BetaAngle', 'BrouwerLongAOP',
    #                        'BrouwerLongECC', 'BrouwerLongINC', 'BrouwerLongMA', 'BrouwerLongRAAN', 'BrouwerLongSMA',
    #                        'BrouwerShortAOP', 'BrouwerShortECC', 'BrouwerShortINC', 'BrouwerShortMA',
    #                        'BrouwerShortRAAN', 'BrouwerShortSMA', 'BVectorAngle', 'BVectorMag', 'C3Energy', 'Cd',
    #                        'CdSigma', 'Cr', 'CrSigma', 'DCM11', 'DCM12', 'DCM13', 'DCM21', 'DCM22', 'DCM23', 'DCM31',
    #                        'DCM32', 'DCM33', 'DEC', 'DECV', 'DelaunayG', 'Delaunayg', 'DelaunayH', 'Delaunayh',
    #                        'DelaunayL', 'Delaunayl', 'DLA', 'DragArea', 'DryCenterOfMassX', 'DryCenterOfMassY',
    #                        'DryCenterOfMassZ', 'DryMass', 'DryMassMomentOfInertiaXX', 'DryMassMomentOfInertiaXY',
    #                        'DryMassMomentOfInertiaXZ', 'DryMassMomentOfInertiaYY', 'DryMassMomentOfInertiaYZ',
    #                        'DryMassMomentOfInertiaZZ', 'EA', 'ECC', 'ElapsedDays', 'ElapsedSecs', 'Energy',
    #                        'EquinoctialH', 'EquinoctialHDot', 'EquinoctialK', 'EquinoctialKDot', 'EquinoctialP',
    #                        'EquinoctialPDot', 'EquinoctialQ', 'EquinoctialQDot', 'EulerAngle1', 'EulerAngle2',
    #                        'EulerAngle3', 'EulerAngleRate1', 'EulerAngleRate2', 'EulerAngleRate3', 'FPA', 'HA', 'HMAG',
    #                        'HX', 'HY', 'HZ', 'INC', 'IncomingBVAZI', 'IncomingC3Energy', 'IncomingDHA',
    #                        'IncomingRadPer',
    #                        'IncomingRHA', 'Latitude', 'Longitude', 'LST', 'MA', 'MHA', 'MLONG', 'MM', 'ModEquinoctialF',
    #                        'ModEquinoctialG', 'ModEquinoctialH', 'ModEquinoctialK', 'MRP1', 'MRP2', 'MRP3',
    #                        'OrbitPeriod',
    #                        'OrbitTime', 'OutgoingBVAZI', 'OutgoingC3Energy', 'OutgoingDHA', 'OutgoingRadPer',
    #                        'OutgoingRHA', 'Periapsis', 'PlanetodeticAZI', 'PlanetodeticHFPA', 'PlanetodeticLAT',
    #                        'PlanetodeticLON', 'PlanetodeticRMAG', 'PlanetodeticVMAG', 'Q1', 'Q2', 'Q3', 'Q4', 'RA',
    #                        'RAAN',
    #                        'RadApo', 'RadPer', 'RAV', 'RLA', 'RMAG', 'SemilatusRectum', 'SMA', 'SPADDragScaleFactor',
    #                        'SPADDragScaleFactorSigma', 'SPADSRPScaleFactor', 'SPADSRPScaleFactorSigma', 'SRPArea',
    #                        'SystemCenterOfMassX', 'SystemCenterOfMassY', 'SystemCenterOfMassZ',
    #                        'SystemMomentOfInertiaXX',
    #                        'SystemMomentOfInertiaXY', 'SystemMomentOfInertiaXZ', 'SystemMomentOfInertiaYY',
    #                        'SystemMomentOfInertiaYZ', 'SystemMomentOfInertiaZZ', 'TA', 'TAIModJulian', 'TDBModJulian',
    #                        'TLONG', 'TLONGDot', 'TotalMass', 'TTModJulian', 'UTCModJulian', 'VelApoapsis',
    #                        'VelPeriapsis',
    #                        'VMAG', 'VX', 'VY', 'VZ', 'X', 'Y', 'Z']}
    #     # Copied from GMAT src/base/command/Propagate.cpp/PARAMETER_TEXT
    #     self.params = ['AvailablePropModes', 'PropagateMode', 'InterruptFrequency', 'StopTolerance', 'Spacecraft',
    #                    'Propagator', 'StopCondition', 'PropForward', 'AllSTMs', 'AllAMatrices', 'AllCovariances']
    #
    #     if mode:
    #         if mode != 'Synchronized':  # TODO: BackProp a valid option here, or handled separately?
    #             raise SyntaxError('Invalid mode was specified. If given, must be "Synchronized"')
    #         self.mode = mode
    #         self.SetField('PropagateMode', self.mode)  # believe complete - TODO test with multiple sats
    #     else:
    #         self.mode = None
    #
    #     if '.' not in stop[0]:
    #         self.stop_param = f'{sc.name}.{stop[0]}'
    #     else:
    #         self.stop_param = stop[0]
    #
    #     print(f'stop_param: {self.stop_param}')
    #     self.goal = stop[1]
    #     print(f'goal: {self.goal}')
    #     stop_cond_string = f'{self.stop_param} = {self.goal}'
    #
    #     self.stop_tolerance = stop_tolerance
    #     self.SetField('StopTolerance', self.stop_tolerance)  # complete
    #
    #     if isinstance(prop_forward, bool):
    #         # propagate forwards (direction 1) if prop_forward is True, otherwise backwards (direction -1)
    #         self.prop_forward = prop_forward
    #         self.gmat_obj.SetBooleanParameter('PropForward', self.prop_forward)  # complete
    #     else:
    #         raise SyntaxError('Invalid prop_forward given - accepts only True or False')

    def __init__(self, name: str = None, prop: gpy.PropSetup = None, sat: gpy.Spacecraft = None,
                 stop_cond: Propagate.StopCondition | tuple | str = None, synchronized: bool = False):
        # user did not provide a name but must make sure the new Propagate has a unique name
        if not name:
            num_propagates: int = len(gmat.GetCommands('Propagate'))
            name = '' if num_propagates == 0 else f'PropagateCommand{num_propagates + 1}'

        super().__init__('Propagate', name)  # sets self.command_type, self.name, self.gmat_obj

        mod = gpy.Moderator()
        sb = gpy.Sandbox()
        sb.AddSolarSystem(gmat.GetSolarSystem())

        self.sat = sat if sat else None
        if prop:  # user provided a PropSetup object
            self.prop = prop
        else:  # no PropSetup provided - make one instead
            # self.prop = gmat.Moderator.Instance().CreateDefaultPropSetup('DefaultProp')  # note: not a wrapper object
            self.prop = gpy.PropSetup('DefaultProp')
            if not self.sat:  # no satellite provided either - get the default
                self.sat = mod.GetDefaultSpacecraft()
            self.prop.AddPropObject(self.sat)  # let self.sat be propagated by new self.prop

        self.SetObject(self.prop.GetName(), gmat.PROP_SETUP)  # attach self.prop to the Propagate command
        # sb.AddObject(self.prop)  # add self.prop to Sandbox

        # sb.AddObject(self.sat)
        gmat.Initialize()

        # Check for existing Formation (group of Spacecraft)
        formation = mod.GetListOfObjects(gmat.FORMATION)
        if not formation:
            if not self.sat:  # no Formation exists - most likely option
                self.sat = mod.GetDefaultSpacecraft()
                self.sat_name = self.sat.GetName()
            else:
                self.sat_name = self.sat.name
            self.SetObject(self.sat_name, gmat.SPACECRAFT)
        else:  # a Formation does exist
            self.sat_name = mod.GetSpacecraftNotInFormation()
            if self.sat_name:
                self.SetObject(self.sat_name, gmat.SPACECRAFT)
            else:  # sat_name not found, so use first object in formation instead
                self.SetObject(formation[0], gmat.SPACECRAFT)

        if stop_cond:  # use the stop condition that the user provided, parsing it if necessary
            if type(stop_cond).__name__ == 'StopCondition':
                self.stop_cond = stop_cond
            elif isinstance(stop_cond, (tuple, str)):  # a tuple or string has been given for the stop_cond argument
                print('tuple or string StopCondition found')
                self.stop_cond = Propagate.StopCondition(self.sat, stop_cond)
            else:
                raise TypeError('stop_cond must be a StopCondition, or a tuple or string that can be parsed by '
                                f'StopCondition.parse_stop_params. Current type: {type(stop_cond).__name__}')
        else:  # create a StopCondition if the user didn't supply one
            # self.stop_cond: gmat.StopCondition = gpy.Moderator().CreateDefaultStopCondition()
            self.stop_cond = gmat.StopCondition()

        # attach StopCondition to Propagate
        # self.gmat_obj.SetRefObject(self.stop_cond.gmat_obj, gmat.STOP_CONDITION, self.stop_cond.name, 0)
        # self.SetObject(self.stop_cond.gmat_obj, gmat.STOP_CONDITION)

        # coord_sys_name = self.sat.GetField('CoordinateSystem')
        # coord_sys = gmat.GetObject(coord_sys_name)
        # sb.SetInternalCoordSystem(coord_sys)

        if not synchronized:  # default is not be synchronized
            self.synchronized = False
        else:
            # TODO: check for multiple sats - required for synchro. First need to define syntax for multi-sat prop
            self.synchronized = True

        self.SetSolarSystem()
        self.SetObjectMap(mod.GetConfiguredObjectMap())
        self.SetGlobalObjectMap(sb.GetGlobalObjectMap())

        gmat.Initialize()
        print('GMAT initialized')

        # gpy.CustomHelp(self)
        # print(f'Propagate ref obj STOP_CONDITION: {self.gmat_obj.GetRefObjectArray(gmat.STOP_CONDITION)}')
        # # print(f'Propagate StopCondition Parameter: {self.gmat_obj.GetStringArrayParameter(10)}')

        vdator = gpy.Validator()
        vdator.SetSolarSystem(gmat.GetSolarSystem())
        vdator.SetObjectMap(mod.GetConfiguredObjectMap())

        # print('Attemping mod.ValidateCommand(self) in Propagate init')
        # print(f'\t- result: {mod.ValidateCommand(self)}')

        # print('Stop here')

        # print(f'Propagate init Validate: {self.Validate()}')
        # print('Attempting Propagate.Initialize()')
        # print(f'Propagate init Initialize: {self.Initialize()}')
        # print(f'StopCond Initialize at end of Propagate init: {self.stop_cond.Initialize()}')
        # print(f'StopCond valid at end of Propagate init: {self.stop_cond.Validate()}')

        # print(f'StopGoal: {self.stop_cond.GetStopGoal()}')
        # print(f'EpochParam: {self.stop_cond.GetEpochParameter()}')
        # print(f'StopParam: {self.stop_cond.GetStopParameter()}')
        # print(f'GoalParam: {self.stop_cond.GetGoalParameter()}')
        #
        # print(f'Creation of Propagate "{self.name}" complete\n')

    @classmethod
    def CreateDefault(cls, name: str = 'DefaultPropagateCommand'):
        gmat_obj: gmat.Propagate = gmat_py_simple.Moderator().CreateDefaultCommand('Propagate', '')
        gmat_obj.SetName(name)
        return gmat_obj

    def SetObject(self, obj, type_int: int):
        return self.gmat_obj.SetObject(obj, type_int)

    def SetRefObject(self, obj, type_int: int, name: str, index: int = 0):
        """
        Return True if obj successfully set, False otherwise

        :param obj:
        :param type_int:
        :param name:
        :param index:
        :return:
        """
        obj = gpy.extract_gmat_obj(obj)
        response: bool = self.gmat_obj.SetRefObject(obj, type_int, name, index)
        return response

    def TakeAction(self, action: str):
        return self.gmat_obj.TakeAction(action)


class PropagateMulti(Propagate):
    # TODO: consider making this a nested/inner class of Propagate, so would call Propagate.Multi()
    """
    Note: this command does not exist in standard GMAT. It is here to reduce ambiguity when propagating multiple
     spacecraft. This class can only be used to propagate multiple spacecraft - to propagate a single spacecraft, use
      Propagate (which only suports a single spacecraft).

    """

    def __init__(self, name: str = None, prop: gpy.PropSetup = None, sat: gpy.Spacecraft = None,
                 stop_cond: Propagate.StopCondition = None, synchronized: bool = False):
        if not name:  # make sure the new Propagate has a unique name
            num_propagates: int = len(gmat.GetCommands('Propagate'))
            name = f'PropagateMulti{num_propagates + 1}'

        super().__init__(name, prop, sat, stop_cond, synchronized)


class SolverBranchCommand:
    def __init__(self):
        pass


class Target(GmatCommand):
    def __init__(self, name: str, solver: gpy.DifferentialCorrector, solve_mode: str = 'Solve',
                 exit_mode: str = 'SaveAndContinue', command_sequence: list[GmatCommand] = None):
        super().__init__('Target', name)
        # 'Show Progress Window' argument not implemented (for now) - seems to be a GUI-only option

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

        self.run_mission_configured = False  # used in RunMission to track whether Target already setup

        self.solver = solver
        self.SetStringParameter('Targeter', self.solver.name)
        self.SetRefObjectName(gmat.SOLVER, self.solver.name)

        self.solve_mode = solve_mode
        self.SetField('SolveMode', self.solve_mode)

        self.exit_mode = exit_mode
        # TODO: type for ExitMode field must be "Reference Array" - see User Guide pg 813 (PDF pg 822)
        # self.SetField('ExitMode', self.exit_mode)
        print(self.gmat_obj.GetParameterID('ExitMode'))

        self.command_sequence = command_sequence

        self.SetSolarSystem()
        self.SetObjectMap(gpy.Moderator().GetConfiguredObjectMap())
        self.SetGlobalObjectMap(gpy.Sandbox().GetGlobalObjectMap())

        print(self.GetGeneratingString())

        self.Initialize()

    def ApplyCorrections(self):
        raise NotImplementedError


class Vary(GmatCommand):
    def __init__(self, name: str, solver: gpy.DifferentialCorrector, variable: str,
                 initial_value: float | int = 1, perturbation: float | int = 0.0001, lower: float | int = 0.0,
                 upper: float | int = pi, max_step: float | int = 0.5, additive_scale_factor: float | int = 0.0,
                 multiplicative_scale_factor: float | int = 1.0):
        super().__init__('Vary', name)

        self.solver = solver
        self.SetField('SolverName', self.solver.name)
        self.SetRefObject(self.solver.gmat_obj, gmat.SOLVER, self.solver.name)

        self.variable = variable
        self.SetField('Variable', self.variable)

        self.initial_value = initial_value
        self.SetField('InitialValue', str(self.initial_value))

        self.perturbation = perturbation
        self.SetField('Perturbation', str(self.perturbation))

        self.lower = lower
        self.SetField('Lower', str(self.lower))

        self.upper = upper
        self.SetField('Upper', str(self.upper))

        self.max_step = max_step
        self.SetField('MaxStep', str(self.max_step))

        self.additive_scale_factor = additive_scale_factor
        self.SetField('AdditiveScaleFactor', str(self.additive_scale_factor))

        self.multiplicative_scale_factor = multiplicative_scale_factor
        self.SetField('MultiplicativeScaleFactor', str(self.multiplicative_scale_factor))

        self.SetSolarSystem()
        self.SetObjectMap(gpy.Moderator().GetConfiguredObjectMap())
        self.SetGlobalObjectMap(gpy.Sandbox().GetGlobalObjectMap())

        gpy.Moderator().ValidateCommand(self)

        # if not self.Validate():
        #     raise RuntimeError(f'Vary command {self.name} failed to Validate')

        self.Initialize()
