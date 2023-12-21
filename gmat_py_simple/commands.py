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

    def SetField(self, field: str, val: str | list | int | float):
        self.gmat_obj.SetField(field, val)

    def SetName(self, name: str):
        self.name = name
        self.gmat_obj.SetName(name)

    def SetSolarSystem(self, ss: gmat.SolarSystem):
        self.gmat_obj.SetSolarSystem(ss)

    def SetObjectMap(self, om: gmat.ObjectMap):
        self.gmat_obj.SetObjectMap(om)

    def SetGlobalObjectMap(self, gom: gmat.ObjectMap):
        self.gmat_obj.SetGlobalObjectMap(gom)

    def Validate(self) -> bool:
        return self.gmat_obj.Validate()


class Achieve(GmatCommand):
    def __init__(self, name: str):
        super().__init__('Achieve', name)
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


class EndTarget(GmatCommand):
    def __init__(self, name: str):
        super().__init__('EndTarget', name)
        raise NotImplementedError


class Maneuver(GmatCommand):
    def __init__(self, name: str):
        super().__init__('Maneuver', name)
        raise NotImplementedError


class Propagate(GmatCommand):
    """
    Propagate the orbit of a single spacecraft. For multiple spacecraft, use PropagateMulti
    """

    class StopCondition:
        # def __init__(self, name: str, base_epoch=None, epoch=None, epoch_var=None, stop_var=None,
        #              goal=None, repeat=None):
        def __init__(self, sat: gpy.Spacecraft, epoch_var: str = 'Sat.A1ModJulian', stop_var: str = 'Sat.ElapsedSecs',
                     goal: int | float = 12000.0, name: str = 'StopOnSat.ElapsedSecs', description: str = ''):
            # TODO fill other possible args - see StopCondition.cpp
            # self.base_epoch = base_epoch
            # self.epoch = epoch
            # self.epoch_var = epoch_var
            # self.stop_var = stop_var
            # self.goal = goal
            # self.repeat = repeat
            # self.sat = sat

            """
            Create a StopCondition

            :param sat:
            :param epoch_var:
            :param stop_var:
            :param goal:
            :param name:
            :param description:
            """
            self.sat = sat
            sat_name = self.sat.GetName()

            # TODO: move a lot of this to StopCondition.parse_stop_params. Only keep StopCond creation itself here
            goalless_params = ['Apoapsis', 'Periapsis']  # TODO: complete list
            if True in (param in stop_var for param in goalless_params):  # if stop_var includes a goalless param
                goalless = True
                goal = None
                # self.stop_param_type = param
            else:
                goalless = False
                goal = str(goal)

            self.goal = goal  # assumes that parsing function will have set goal to None if required

            self.body = None
            bodies = CelestialBodies()
            if goalless:
                for param in goalless_params:  # TODO: find a way to combine this into if True in... above
                    if param in stop_var:
                        self.stop_param_type = param
                self.epoch_var = None
                for body in bodies:
                    if body in stop_var:
                        self.body = body
                        continue  # use the first body we find in self.stop_var
            else:
                self.epoch_var = epoch_var
                self.epoch_param_type = self.epoch_var.split('.')[1]

            if goalless and not self.body:
                raise AttributeError('No body found for StopCondition')

            self.stop_var = stop_var

            # currently using the goalless check to tell whether Earth or similar is needed in stop_param_type
            if not goalless:
                # self.stop_var isn't body-based, so need to remove any bodies
                elements = self.stop_var.split('.')
                stop_var_elements = []
                stop_param_type_elements = []
                for ele in elements:
                    if ele not in bodies:
                        stop_var_elements.append(ele)
                        if ele != sat_name:
                            stop_param_type_elements.append(ele)

                self.stop_var = '.'.join(stop_var_elements)
                self.stop_param_type = '.'.join(stop_param_type_elements)

            self.description = description
            self.name = name if name else f'StopOn{self.stop_var}'

            self.gmat_obj = gpy.Moderator().CreateStopCondition(self.name)
            self.gmat_obj.SetSolarSystem(gmat.GetSolarSystem())

            if self.epoch_var:
                self.epoch_param: gpy.Parameter = gpy.CreateParameter(self.epoch_param_type, self.epoch_var)
                self.epoch_param.SetRefObjectName(gmat.SPACECRAFT, sat_name)
                self.SetEpochParameter(self.epoch_param)
                self.SetStringParameter('EpochVar', self.epoch_var)

            # TODO: see parameter.StopParameter and subclasses (ElapsedSecs etc) for quick way to implement stop params

            self.stop_param = gpy.CreateParameter(self.stop_param_type, self.stop_var)
            self.stop_param.SetRefObjectName(gmat.SPACECRAFT, sat_name)
            if goalless:
                self.stop_param.SetRefObjectName(gmat.SPACE_POINT, self.body)
                self.stop_param.SetRefObjectName(gmat.CELESTIAL_BODY, self.body)
                coord_sys_name = self.sat.GetField('CoordinateSystem')
                self.stop_param.SetRefObjectName(gmat.COORDINATE_SYSTEM, coord_sys_name)
            else:
                self.goal_param = gpy.CreateParameter('Variable', self.goal)
                self.SetGoalParameter(self.goal_param)
                self.SetStringParameter('Goal', self.goal)

            self.SetStringParameter('StopVar', self.stop_param.GetName())
            self.SetStopParameter(self.stop_param)

        @classmethod
        def CreateDefault(cls):
            return gmat_py_simple.Moderator().CreateDefaultStopCondition()

        @classmethod
        def parse_stop_params(cls, sat: gpy.Spacecraft,
                              stop_conds: tuple[str | int | float] | str) -> Propagate.StopCondition:
            if isinstance(stop_conds, tuple) and len(stop_conds) == 2:  # most likely, e.g. ('Sat.ElapsedSecs', 12000)
                stop_var = stop_conds[0]
                goal = stop_conds[1]

            elif isinstance(stop_conds, str):  # e.g. ('Sat.Earth.Apoapsis')
                stop_var = stop_conds
                goal = stop_var

            else:
                raise RuntimeError(f'stop_conds is invalid. Must be a 2-element tuple or a string')

            name = f'StopOn{stop_var}'
            stop_cond_obj = cls(sat, stop_var=stop_var, goal=goal, name=name)

            return stop_cond_obj

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
            return self.gmat_obj.SetEpochParameter(epoch_param.swig_param)

        def SetGoalParameter(self, goal_param: gpy.Parameter) -> bool:
            return self.gmat_obj.SetGoalParameter(goal_param.swig_param)

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
    #     super().__init__('Propagate')
    #
    #     self.propagator = propagator if propagator else PropSetup('DefaultProp')
    #     # self.gmat_obj.SetRefObject(self.propagator.gmat_obj, gmat.PROPAGATOR, self.propagator.name, 0)
    #     # self.SetField('Propagator', self.propagator.name)
    #     # self.gmat_obj.SetObject(self.propagator.gmat_obj.GetName(), gmat.PROPAGATOR)
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
    #     self.g_stop_cond = gmat.Construct('StopCondition', 'StopCond')
    #     self.g_stop_cond.Help()
    #     print(f'Stop condition fields: {gmat_obj_field_list(self.g_stop_cond)}')
    #     self.g_stop_cond.SetField('StopVar', self.stop_param)
    #     self.g_stop_cond.SetField('Goal', str(self.goal))
    #     print(f'Newly set g_stop_cond StopVar: {self.g_stop_cond.GetField("StopVar")}')
    #     print(f'Newly set g_stop_cond Goal: {self.g_stop_cond.GetField("Goal")}')
    #     # self.g_stop_cond.SetStopParameter(gmat.Construct('Parameter', self.stop_param))
    #     # self.gmat_obj.SetReference(self.g_stop_cond)
    #     # print(f'StopCondition Generating String: {self.g_stop_cond.GetGeneratingString()}')
    #
    #     # g_stop_param = gmat.Construct('Parameter')
    #     # g_stop_param.SetField('InitialValue', stop_cond_string)
    #     # self.g_stop_cond.SetStopParameter(g_stop_param)
    #
    #     # print(f'Stop condition string: {stop_cond_string}')
    #     # self.SetField('StopCondition', stop_cond_string)
    #     # self.SetStopParameter(stop_cond_string)
    #     # print(f'Newly set stop condition: {self.GetField("StopCondition")}')
    #
    #     if not isinstance(sc, Spacecraft):
    #         raise TypeError('sc parameter must be a Spacecraft object')
    #     else:
    #         self.spacecraft = sc
    #         self.spacecraft.name = sc.name
    #         self.SetField('Spacecraft', self.spacecraft.name)  # complete
    #
    #     # TODO: if stop_value isn't needed because of selected stop_param (e.g. Earth.Apoapsis), set to None
    #     #  assuming for now that stop_value is an int
    #     self.stop = stop
    #
    #     # self.stop_param = self.stop[0]  # default stop_param is "DefaultSC.ElapsedSecs =" (pg 222 of GMAT Arch Spec)
    #     # self.g_stop_cond.SetLhsString(f'{self.spacecraft.name}.{self.stop_param} =')
    #     # print(f'New LHS String: {self.g_stop_cond.GetLhsString()}')
    #
    #     # self.stop_condition = self.stop[1]  # default is 8640 (pg 222 of GMAT Architectectural Specification)
    #     # self.stop_condition = 8640.0  # TODO remove hardcoding once fixed
    #     # self.g_stop_cond.SetRhsString(str(self.stop_condition))
    #     # print(f'New RHS String: {self.g_stop_cond.GetRhsString()}')
    #     # print(f'Whole stop param: {self.g_stop_cond.GetStopParameter()}')
    #
    #     # stop_param_string = f"{self.spacecraft.name}.{self.stop_param} = 8640.0"
    #     # print(f'"{stop_param_string}"')
    #     # self.g_stop_param = gmat.Construct('Parameter')
    #     # self.g_stop_cond.SetStopParameter(self.g_stop_cond)
    #
    #     # print(f'StopParam: {self.g_stop_cond.GetStopParameter()}')
    #
    #     # if self.stop_param == 'ElapsedSecs':  # assuming stop_value is an ElapsedSecs value
    #     #     self.dt = self.stop_condition
    #     # elif self.stop_param == 'ElapsedDays':
    #     #     # TODO bugfix: work for multiple ElapsedDays. ED = 1 works.
    #     #     #  If beyond ~1.3, result Epoch capped to 23 Jul 2014 17:29:17.477. Currently using ED * 86400 then Step.
    #     #     #  Also happens if using ElapsedSecs with e.g. 365*86400 to attempt one year.
    #     #     raise NotImplementedError
    #     #     # self.dt = self.stop_value * 86400
    #     # else:
    #     #     raise NotImplementedError
    #
    #     print(f'self fields: {gmat_obj_field_list(self)}')
    #     self.propagator.SetReference(self.g_stop_cond)
    #     # self.SetField('StopCondition', self.g_stop_cond.GetName())
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
    #
    #     # TODO clarify: are both of these commands needed? Seems just one
    #     propagator.SetObject(sc)  # from pg 61 of API Users Guide
    #     # self.propagator.AddPropObject(sc)  # add the spacecraft to the PropSetup (and hence Propagator)
    #
    #     self.propagator.PrepareInternals()
    #
    #     self.propagator.gator = propagator.GetPropagator()
    #     self.gator = propagator.gator
    #
    #     # self.gator.Step(self.dt)
    #     # self.gator.UpdateSpaceObject()
    #
    #     # self.propagator.Help()
    #
    #     print(f'Propagate Generating String: {self.GetGeneratingString()}')

    def __init__(self, name: str = None, prop: gpy.PropSetup = None, sat: gpy.Spacecraft = None,
                 stop_cond: Propagate.StopCondition | tuple | str = None, synchronized: bool = False):
        if not name:  # make sure the new Propagate has a unique name
            num_propagates: int = len(gmat.GetCommands('Propagate'))
            name = '' if num_propagates == 0 else f'PropagateCommand{num_propagates + 1}'
        super().__init__('Propagate', name)  # sets self.command_type, self.name, self.gmat_obj

        mod = gpy.Moderator()
        sb = mod.gmat_obj.GetSandbox()
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

        vdator = gmat.Validator.Instance()
        vdator.SetSolarSystem(gmat.GetSolarSystem())
        vdator.SetObjectMap(mod.GetConfiguredObjectMap())

        # create a StopCondition if the user didn't supply one
        if stop_cond:
            if isinstance(stop_cond, Propagate.StopCondition):
                self.stop_cond = stop_cond
            elif isinstance(stop_cond, (tuple, str)):
                self.stop_cond = Propagate.StopCondition.parse_stop_params(self.wrapper_sat, stop_cond)
            else:
                raise TypeError('stop_cond must be a StopCondition, or a tuple or string that can be parsed by '
                                'StopCondition.parse_stop_params')
        else:
            self.stop_cond: gmat.StopCondition = Propagate.StopCondition(self.sat)

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

        gmat.Initialize()
        sb.AddObject(self.sat)
        gmat.Initialize()

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
