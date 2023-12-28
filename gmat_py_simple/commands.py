from __future__ import annotations

from load_gmat import gmat

import gmat_py_simple as gpy
from gmat_py_simple.utils import *


class GmatCommand:
    def __init__(self, command_type: str, name: str):
        self.command_type: str = command_type
        if self.command_type == 'BeginMissionSequence':  # TODO: remove if not needed - TBC
            self.name: str = ''  # the BeginMissionSequence command is not allowed to have a name
        else:
            self.name: str = name

        # CreateCommand currently broken (GMT-8100), so use CreateDefaultCommand and remove extras
        self.gmat_obj: gmat.GmatCommand = gpy.Moderator().CreateDefaultCommand(self.command_type, self.name)
        self.gmat_obj.SetName(self.name)

        if self.command_type == 'Propagate':
            # TODO: find name of mission's spacecraft rather than assuming default
            sat_name = gpy.Moderator().GetDefaultSpacecraft().GetName()
            gmat.Clear(f'{sat_name}.ElapsedSecs')  # stop condition parameter
            gmat.Clear(f'{sat_name}.A1ModJulian')  # stop condition parameter

        self.Validate()
        # TODO bugfix: switch to CreateCommand (uncomment below) when issue GMT-8100 fixed
        # self.gmat_obj: gmat.GmatCommand = gpy.Moderator().CreateCommand(self.command_type, self.name)

    def AddToMCS(self) -> bool:
        return gpy.Moderator().AppendCommand(self)

    def Initialize(self):
        self.gmat_obj.Initialize()

    def GeneratingString(self):
        print(self.GetGeneratingString())

    def GetGeneratingString(self) -> str:
        return self.gmat_obj.GetGeneratingString()

    def GetField(self, field: str):
        self.gmat_obj.GetField(field)

    def GetName(self) -> str:
        return self.gmat_obj.GetName()

    def Help(self):
        self.gmat_obj.Help()

    def SetBooleanParameter(self, param_name: str, value: bool):
        return self.gmat_obj.SetBooleanParameter(param_name, value)

    def SetField(self, field: str, val: str | list | int | float):
        self.gmat_obj.SetField(field, val)

    def SetGlobalObjectMap(self, gom: gmat.ObjectMap):
        self.gmat_obj.SetGlobalObjectMap(gom)

    def SetName(self, name: str):
        self.name = name
        self.gmat_obj.SetName(name)

    def SetObjectMap(self, om: gmat.ObjectMap):
        self.gmat_obj.SetObjectMap(om)

    def SetSolarSystem(self, ss: gmat.SolarSystem):
        self.gmat_obj.SetSolarSystem(ss)

    def SetStringParameter(self, param_name: str, value: str):
        return self.gmat_obj.SetStringParameter(param_name, value)

    def Validate(self) -> bool:
        return self.gmat_obj.Validate()


class Achieve(GmatCommand):
    def __init__(self, name: str):
        super().__init__('Achieve', name)
        raise NotImplementedError


class BeginFiniteBurn(GmatCommand):
    def __init__(self, name: str):
        super().__init__('BeginFiniteBurn', name)
        raise NotImplementedError


class BeginMissionSequence(GmatCommand):
    def __init__(self):
        super().__init__('BeginMissionSequence', 'BeginMissionSequenceCommand')
        # gpy.Moderator().ValidateCommand(self)
        sb = gpy.Sandbox()
        self.SetObjectMap(sb.GetObjectMap())
        self.SetGlobalObjectMap(sb.GetGlobalObjectMap())
        self.SetSolarSystem(gmat.GetSolarSystem())
        self.Initialize()


class EndFiniteBurn(GmatCommand):
    def __init__(self, name: str):
        super().__init__('EndFiniteBurn', name)
        raise NotImplementedError


class EndTarget(GmatCommand):
    def __init__(self, name: str):
        super().__init__('EndTarget', name)
        raise NotImplementedError


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

        self.SetSolarSystem(gmat.GetSolarSystem())
        self.SetObjectMap(gpy.Moderator().GetConfiguredObjectMap())
        self.SetGlobalObjectMap(gpy.Sandbox().GetGlobalObjectMap())

        self.Validate()


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

            self.sat = sat
            sat_name = self.sat.GetName()

            # epoch_param_type = 'A1ModJulian'  # default TODO remove
            # stop_param_type = 'ElapsedSecs'  # default TODO remove
            #
            # epoch_var = f'{sat_name}.{stop_param}'

            (self.stop_param_type,
             self.stop_var,
             self.epoch_param_type,
             self.epoch_var,
             self.goal) = self.parse_stop_cond(stop_cond)

            self.name = f'StopOn{self.stop_var}={self.goal}'
            mod = gpy.Moderator()
            self.gmat_obj = mod.CreateStopCondition(self.name)
            self.gmat_obj.SetSolarSystem(gmat.GetSolarSystem())

            # Use GetParameter in create_x_param to return GmatBase form of param
            # self.stop_param = self.create_stop_param(self.stop_param_type, self.stop_var)
            self.stop_param: gpy.Parameter = gpy.Parameter(self.stop_param_type, self.stop_var)
            self.stop_param.SetRefObjectName(gmat.SPACECRAFT, sat_name)
            self.stop_param.SetRefObjectName(gmat.SPACE_POINT, 'Earth')  # TODO: remove hard-coding
            self.SetStopParameter(self.stop_param)
            # StopVar is sometimes called mStopParamName in StopCondition source
            self.SetStringParameter('StopVar', self.stop_param.GetName())
            # mod.gmat_obj.SetParameterRefObject(self.stop_param, 'Spacecraft', sat_name, '', '', 0)
            # print(self.gmat_obj.GetStopParameter())
            # self.stop_param = gmat.GetObject(self.stop_var)

            # self.stop_param = gmat.GetObject(self.stop_var)
            # self.stop_param.SetRefObjectName(gmat.SPACE_POINT, 'Earth')
            # # self.stop_param.SetRefObjectName(gmat.SPACE_POINT, self.body)
            # self.stop_param.SetRefObjectName(gmat.CELESTIAL_BODY, self.body)
            # coord_sys_name = self.sat.GetField('CoordinateSystem')
            # self.stop_param.SetRefObjectName(gmat.COORDINATE_SYSTEM, coord_sys_name)
            # else:
            #     self.goal_param = gpy.CreateParameter('Variable', f'Goal={self.goal}')
            #     self.SetGoalParameter(self.goal_param)
            #     self.SetStringParameter('Goal', self.goal)
            #     self.goal_param.SetRefObjectName(gmat.SPACECRAFT, sat_name)

            # self.SetStringParameter('StopVar', self.stop_var)
            # self.SetStopParameter(self.stop_param)
            # print(self.gmat_obj.GetStopParameter())

            self.epoch_param: gpy.Parameter = gpy.Parameter(self.epoch_param_type, self.epoch_var)
            self.epoch_param.SetRefObjectName(gmat.SPACECRAFT, sat_name)
            self.SetEpochParameter(self.epoch_param)
            # self.epoch_param.SetRefObjectName(gmat.SPACE_POINT, 'Earth')  # TODO: remove hard-coding
            self.SetStringParameter('EpochVar', self.epoch_param.GetName())
            # self.gmat_obj.SetStringParameter('EpochVar',
            #                                  self.epoch_var)  # EpochVar is mEpochParamName in StopCondition source
            # TODO: epoch_param always needed, or sometimes not so "if epoch_var" or similar?
            # print(self.epoch_param)
            # self.SetEpochParameter(self.epoch_param)
            # self.epoch_param = gmat.GetObject(self.epoch_var)
            # mod.gmat_obj.SetParameterRefObject(self.epoch_param, 'Spacecraft', sat_name, '', '', 0)
            # self.epoch_param.SetRefObjectName(gmat.SPACECRAFT, sat_name)
            # self.SetEpochParameter(self.epoch_param)

            if self.goal:
                # TODO: should this param be used somewhere?
                # self.goal_param: gpy.Parameter = gpy.CreateParameter('Variable', self.goal)
                # self.goal_param.SetRefObjectName(gmat.SPACECRAFT, sat_name)
                # self.goal_param.SetRefObjectName(gmat.SPACE_POINT, 'Earth')  # TODO: remove hard-coding
                self.gmat_obj.SetStringParameter('Goal', self.goal)  # SetRhsString() called with goal value in source
                # mod.gmat_obj.SetParameterRefObject(self.goal_param, 'Spacecraft', sat_name, '', '', 0)
                # self.gmat_obj.SetGoalParameter(self.goal_param)

            if not self.Validate():
                raise RuntimeError('Validate() failed for StopCondition')
            self.Initialize()

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
            if isinstance(stop_cond, tuple) and len(stop_cond) == 2:  # most likely. E.g. ('Sat.ElapsedSecs', 12000)
                stop_var = stop_cond[0]
                goal = str(stop_cond[1])

            elif isinstance(stop_cond, str):  # e.g. 'Sat.Earth.Apoapsis'
                stop_var = stop_cond
                goal = str(stop_var)

            else:
                # TODO: definitely max of 2 elements?
                raise RuntimeError(f'stop_conds is invalid. Must be a 2-element tuple or a string')

            stop_param_type = stop_var[len(self.sat.name) + 1:]  # remove sat name and . from stop_var
            epoch_param_type = 'A1ModJulian'  # TODO: determine other epoch_var options and when to use them
            epoch_var = f'{self.sat.name}.{epoch_param_type}'

            return stop_param_type, stop_var, epoch_param_type, epoch_var, goal

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

        def SetStringParameter(self, param_name: str, value: str):
            return self.gmat_obj.SetStringParameter(param_name, value)

        def GetIntegerParameter(self, param_name: str) -> int:
            return self.gmat_obj.GetIntegerParameter(param_name)

        def GetName(self):
            return self.gmat_obj.GetName()

        def GetAllParameters(self):
            return ('\nCurrent parameter values:\n'
                    f'- BaseEpoch: {self.GetRealParameter("BaseEpoch")}\n'
                    f'- Epoch:     {self.GetRealParameter("Epoch")}\n'
                    f'- EpochVar:  {self.GetStringParameter("EpochVar")}\n'
                    f'- StopVar:   {self.GetStringParameter("StopVar")}\n'
                    f'- Goal:      {self.GetStringParameter("Goal")}\n'
                    f'- Repeat:    {self.GetIntegerParameter("Repeat")}')

        def GetRealParameter(self, param_name: str) -> int | float:
            return self.gmat_obj.GetRealParameter(param_name)

        def GetStringParameter(self, param_name: str) -> str:
            return self.gmat_obj.GetStringParameter(param_name)

        def Help(self):
            self.gmat_obj.Help()

        def Initialize(self):
            return self.gmat_obj.Initialize()

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
            return self.gmat_obj.SetGoalParameter(goal_param)

        def SetInterpolator(self, interp: gmat.Interpolator) -> bool:
            return self.gmat_obj.SetInterpolator(interp)

        def SetPropDirection(self, direction: int) -> bool:
            return self.gmat_obj.SetPropDirection(direction)

        def SetSolarSystem(self, ss: gmat.SolarSystem) -> bool:
            return self.gmat_obj.SetSolarSystem(ss)

        def SetStopParameter(self, stop_param: gpy.Parameter) -> bool:
            if 'gmat_py_simple' in str(type(stop_param)):
                return self.gmat_obj.SetStopParameter(stop_param.swig_param)
            else:
                return self.gmat_obj.SetStopParameter(stop_param)

        def Validate(self) -> bool:
            return self.gmat_obj.Validate()

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
        if not name:  # make sure the new Propagate has a unique name
            num_propagates: int = len(gmat.GetCommands('Propagate'))
            name = '' if num_propagates == 0 else f'PropagateCommand{num_propagates + 1}'
        super().__init__('Propagate', name)  # sets self.command_type, self.name, self.gmat_obj

        mod = gpy.Moderator()
        sb = gpy.Sandbox()
        sb.AddSolarSystem(gmat.GetSolarSystem())

        if sat:
            self.wrapper_sat = sat
            self.sat: gmat.Spacecraft = self.wrapper_sat.gmat_obj
        else:
            self.sat: gmat.Spacecraft = None

        if prop:
            self.prop = extract_gmat_obj(prop)
        else:
            self.prop = gmat.Moderator.Instance().CreateDefaultPropSetup('DefaultProp')
            if not self.sat:
                self.sat = mod.GetDefaultSpacecraft()
            else:
                self.sat = gpy.extract_gmat_obj(sat)
            self.prop.AddPropObject(self.sat)  # let self.sat be propagated by self.prop

        sb.AddObject(self.prop)  # add prop to Sandbox

        # vdator = gmat.Validator.Instance()
        # vdator.SetSolarSystem(gmat.GetSolarSystem())
        # vdator.SetObjectMap(mod.GetConfiguredObjectMap())

        # create a StopCondition if the user didn't supply one
        if stop_cond:
            if isinstance(stop_cond, Propagate.StopCondition):
                self.stop_cond = stop_cond
            elif isinstance(stop_cond, (tuple, str)):  # a tuple or string has been given for the stop_cond argument
                # self.stop_cond = Propagate.StopCondition.parse_stop_params(self.wrapper_sat, stop_cond)
                self.stop_cond = Propagate.StopCondition(self.wrapper_sat, stop_cond)
            else:
                raise TypeError('stop_cond must be a StopCondition, or a tuple or string that can be parsed by '
                                'StopCondition.parse_stop_params')
        else:
            self.stop_cond: gmat.StopCondition = Propagate.StopCondition(self.sat,
                                                                         (f'{self.sat.name}.ElapsedSecs', 12000.0))

        # # Check for existing Formation
        form = mod.GetListOfObjects(gmat.FORMATION)
        if not form:  # no Formation exists
            if not self.sat:
                self.sat = mod.GetDefaultSpacecraft()

        else:  # a Formation does exist
            sc_name = mod.GetSpacecraftNotInFormation()
            if sc_name:
                self.gmat_obj.SetObject(sc_name, gmat.SPACECRAFT)
            if not sc_name:
                self.gmat_obj.SetObject(form[0], gmat.SPACECRAFT)

        coord_sys_name = self.sat.GetField('CoordinateSystem')
        coord_sys = gmat.GetObject(coord_sys_name)
        sb.SetInternalCoordSystem(coord_sys)

        sb.AddObject(self.sat)

        if not synchronized:  # default is not be synchronized
            self.synchronized = False
        else:
            # TODO: check for multiple sats - required for synchro. First need to define syntax for multi-sat prop
            self.synchronized = True

        self.SetRefObject(self.stop_cond, gmat.STOP_CONDITION, self.stop_cond.GetName())

        self.SetSolarSystem(gmat.GetSolarSystem())
        self.SetObjectMap(mod.GetConfiguredObjectMap())
        self.SetGlobalObjectMap(sb.GetGlobalObjectMap())

        self.Validate()

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

    # def Validate(self):
    #     """
    #     Return True if valid, False otherwise.
    #
    #     :return:
    #     """
    #     return self.gmat_obj.Validate()


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


class Target(GmatCommand):
    def __init__(self, name: str, solver: str | gpy.DifferentialCorrector, solver_mode: str = 'Solve',
                 exit_mode: str = 'SaveAndContinue', command_sequence: list[GmatCommand] = None):
        super().__init__('Target', name)
        # 'Show Progress Window' argument not implemented (for now) - seems to be a GUI-only option

        raise NotImplementedError

    def ApplyCorrections(self):
        raise NotImplementedError


class Vary(GmatCommand):
    def __init__(self, name: str):
        super().__init__('Vary', name)
        raise NotImplementedError
