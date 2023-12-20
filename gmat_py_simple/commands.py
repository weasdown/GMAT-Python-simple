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


class BeginMissionSequence(GmatCommand):
    def __init__(self):
        super().__init__('BeginMissionSequence', 'BeginMissionSequenceCommand')
        # gpy.Moderator().ValidateCommand(self)
        sb = gpy.Sandbox()
        self.SetObjectMap(sb.GetObjectMap())
        self.SetGlobalObjectMap(sb.GetGlobalObjectMap())
        self.SetSolarSystem(gmat.GetSolarSystem())
        self.Initialize()


class Propagate(GmatCommand):
    """
    Propagate the orbit of a single spacecraft. For multiple spacecraft, use PropagateMulti
    """

    class StopCondition:
        # def __init__(self, name: str, base_epoch=None, epoch=None, epoch_var=None, stop_var=None,
        #              goal=None, repeat=None):
        def __init__(self, sat: gpy.Spacecraft, epoch_var: str = 'A1ModJulian', stop_var: str = 'ElapsedSecs',
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

            self.epoch_var_no_sat = epoch_var
            self.epoch_var = f'{sat_name}.{epoch_var}'

            self.stop_var_no_sat = stop_var
            self.stop_var = f'{sat_name}.{stop_var}'
            self.goal = str(goal)
            self.description = description
            self.name = name if name else f'StopOn{self.stop_var}'

            self.epoch_param: gpy.Parameter = gpy.CreateParameter(self.epoch_var_no_sat, self.epoch_var)
            self.epoch_param.SetRefObjectName(gmat.SPACECRAFT, sat_name)

            self.stop_param: gpy.Parameter = gpy.CreateParameter(self.epoch_var_no_sat, self.epoch_var)
            self.stop_param.SetRefObjectName(gmat.SPACECRAFT, sat_name)

            self.goal_param = gpy.CreateParameter('Variable', self.goal)

            self.gmat_obj = gpy.Moderator().CreateStopCondition(self.name)

            print(f'self.epoch_param: {self.epoch_param}, GMAT type: {self.epoch_param.GetTypeName()}')
            print('Setting params: ')
            print('- Epoch:     ', self.SetEpochParameter(self.epoch_param))
            print('- Stop:      ', self.SetStopParameter(self.stop_param))
            print('- Goal:      ', self.SetGoalParameter(self.goal_param))

            print('Setting string parameters:')
            print('- EpochVar:  ', self.SetStringParameter('EpochVar', self.epoch_var))
            print('- StopVar    ', self.SetStringParameter('StopVar', self.stop_var))
            print('- Goal:      ', self.SetStringParameter('Goal', str(goal)))

            print('\nCurrent parameter values:')
            print('- BaseEpoch: ', self.GetRealParameter('BaseEpoch'))
            print('- Epoch:     ', self.GetRealParameter('Epoch'))
            print('- EpochVar:  ', self.GetStringParameter('EpochVar'))
            print('- StopVar:   ', self.GetStringParameter('StopVar'))
            print('- Goal:      ', self.GetStringParameter('Goal'))
            print('- Repeat:    ', self.GetIntegerParameter('Repeat'))

            self.Validate()
            self.Initialize()

            print('\nStopCondition init complete!')
            # def test_name(n):
            #     # Try the suggested name. If taken, keep adding 1 to name until it is new
            #     name_index = 1
            #     while True:
            #         try:
            #             gmat.GetObject(n)
            #             name_index += 1
            #             n = f'{n}{name_index}'
            #         except AttributeError:  # object not found, so name is new - use it
            #             return n
            #
            # self.name = test_name(f'StopOn{stop_var}')
            #
            # # mod = gpy.Moderator()
            # # stop_cond_vars = [self.epoch_var, self.stop_var]
            # # for var in stop_cond_vars:
            # #     if not mod.GetParameter(var):  # no existing Parameter for var
            # #         param_type = var.split('.')[1]  # remove "Sat." from string
            # #         param = gmat.Moderator.Instance().CreateParameter(param_type, var)
            # #         gmat.Moderator.Instance().SetParameterRefObject(param, 'Spacecraft', sat_name, '', '', 0)
            # #
            # # # if not mod.GetParameter(stop_var):  # no existing Parameter for stop_var
            # # #     stop_param: gmat.Parameter = mod.gmat_obj.CreateParameter('ElapsedSecs', stop_var)
            # # #     gmat.Moderator.Instance().SetParameterRefObject(stop_param, 'Spacecraft', sat_name, '', '', 0)
            # #
            # # # stop_cond_name = f'StopOn{stop_var}'
            # # self.gmat_obj: gmat.StopCondition = mod.CreateStopCondition(self.name)
            # # self.SetStringParameter('EpochVar', self.epoch_var)  # EpochVar is mEpochParamName in StopCondition source
            # # self.SetStringParameter('StopVar', self.stop_var)  # StopVar is mStopParamName in StopCondition source
            # # self.SetStringParameter('Goal', '12000.0')  # SetRhsString() called with goal value in source
            #
            # # TODO: correct epoch_param/stop_param, remove hardcoding from others
            # epoch_param: gmat.Parameter = epoch_var
            # stop_param: gmat.Parameter = stop_var
            # goal: int | float = 12000.0
            # tolerance: int | float = 1
            # repeat_count: int = 0
            # interpolator: gmat.Interpolator = None
            #
            # self.gmat_obj = gmat.Moderator.Instance().CreateStopCondition('StopCondition', name)
            # # self.gmat_obj = gmat.StopCondition(name)
            # """
            # From StopCondition.cpp:
            # StopCondition::StopCondition(const std::string &name, const std::string &desc,
            #                  Parameter *epochParam, Parameter *stopParam,
            #                  const Real &goal, const Real &tol,
            #                  const Integer repeatCount,
            #                  Interpolator *interp)
            # """
            # self.gmat_obj.Help()
            # self.SetStringParameter('EpochVar', self.epoch_var)  # EpochVar is mEpochParamName in StopCondition source
            # self.SetStringParameter('StopVar', self.stop_var)  # StopVar is mStopParamName in StopCondition source
            # self.SetStringParameter('Goal', '12000.0')  # SetRhsString() called with goal value in source

            # if (sat_name not in epoch_var) or (sat_name not in epoch_var):
            #     raise AttributeError('epoch_var and stop_var are required when using a satellite name other than Sat')
            # else:
            #     self.epoch_var = epoch_var
            #     self.stop_var = stop_var
            # self.SetStringParameter('EpochVar', self.epoch_var)  # EpochVar is mEpochParamName in StopCondition source
            # self.SetStringParameter('StopVar', self.stop_var)  # StopVar is mStopParamName in StopCondition source
            # self.SetStringParameter('Goal', '12000.0')  # SetRhsString() called with goal value in source
            # self.SetStringParameter('EpochVar',
            #                         f'{self.sat.GetName()}.A1ModJulian')  # EpochVar is mEpochParamName in StopCondition source
            # self.SetStringParameter('StopVar',
            #                         f'{self.sat.GetName()}.ElapsedSecs')  # StopVar is mStopParamName in StopCondition source
            # self.SetStringParameter('Goal', '12000.0')  # SetRhsString() called with goal value in source
            # self.gmat_obj.Validate()

            # self.gmat_obj = gpy.Moderator().CreateStopCondition(name)

            # # TODO: remove hard-coding of A1ModJulian/ElapsedSecs/12000.0
            # self.SetStringParameter('EpochVar', f'{self.sat.GetName()}.A1ModJulian')
            # self.SetStringParameter('StopVar', f'{self.sat.GetName()}.ElapsedSecs')
            # self.SetStringParameter('Goal', '12000.0')

        @classmethod
        def CreateDefault(cls):
            return gmat_py_simple.Moderator().CreateDefaultStopCondition()

        def SetStringParameter(self, param_name: str, value: str):
            return self.gmat_obj.SetStringParameter(param_name, value)

        def GetIntegerParameter(self, param_name: str) -> int:
            return self.gmat_obj.GetIntegerParameter(param_name)

        def GetName(self):
            return self.gmat_obj.GetName()

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

        # TODO: work out how to convert GmatBase to Parameter
        def SetEpochParameter(self, epoch_param: gpy.Parameter) -> bool:
            return self.gmat_obj.SetEpochParameter(epoch_param.swig_param)

        def SetGoalParameter(self, goal_param: gpy.Parameter) -> bool:
            return self.gmat_obj.SetGoalParameter(goal_param)

        def SetInterpolator(self, interp: gmat.Interpolator) -> bool:
            return self.gmat_obj.SetInterpolator(interp)

        def SetPropDirection(self, direction: int) -> bool:
            return self.gmat_obj.SetPropDirection(direction)

        def SetSolarSystem(self, ss: gmat.SolarSystem) -> bool:
            return self.gmat_obj.SetSolarSystem(ss)

        def SetStopParameter(self, stop_param: gpy.Parameter) -> bool:
            return self.gmat_obj.SetStopParameter(stop_param.swig_param)

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
                 stop_cond: Propagate.StopCondition = None, synchronized: bool = False):
        if not name:  # make sure the new Propagate has a unique name
            num_propagates: int = len(gmat.GetCommands('Propagate'))
            name = 'PropagateCommand' if num_propagates == 0 else f'PropagateCommand{num_propagates + 1}'
        super().__init__('Propagate', name)  # sets self.command_type, self.name, self.gmat_obj

        mod = gpy.Moderator()
        sb = mod.gmat_obj.GetSandbox()
        sb.AddSolarSystem(gmat.GetSolarSystem())

        if prop:
            if 'simple' in str(type(prop)):  # wrapper PropSetup object
                self.prop: gmat.PropSetup = prop.gmat_obj
            elif type(prop).__name__ == 'PropSetup':  # assuming wrapper case handled, so now a GMAT native PropSetup
                # self.prop: gmat.PropSetup = prop
                # TODO: add support for prop being a gmat.PropSetup
                raise TypeError('prop currently expects a gpy.PropSetup - gmat.PropSetup will be supported in future')
            else:
                raise TypeError(f'prop type not recognized in Propagate.__init__(): {type(prop)}')
        else:
            self.prop: gmat.PropSetup = None

        if sat:
            self.wrapper_sat = sat
            self.sat: gmat.Spacecraft = self.wrapper_sat.gmat_obj
        else:
            self.sat: gmat.Spacecraft = None

        if not self.prop:
            self.prop = gmat.Moderator.Instance().CreateDefaultPropSetup('DefaultProp')
            if not self.sat:
                self.sat = mod.GetDefaultSpacecraft()
            else:
                self.sat = gpy.extract_gmat_obj(sat)
            self.prop.AddPropObject(self.sat)

        # gmat.Initialize()
        sb.AddObject(self.prop)

        if not stop_cond:
            stop_cond: Propagate.StopCondition = Propagate.StopCondition(self.sat)

        self.stop_cond: gmat.StopCondition = stop_cond
        self.stop_cond.Initialize()
        print(self.stop_cond.SetStringParameter('EpochVar', f'{self.sat.GetName()}.A1ModJulian'))
        print(self.stop_cond.SetStringParameter('StopVar', f'{self.sat.GetName()}.ElapsedSecs'))
        print(self.stop_cond.SetStringParameter('Goal', '12000.0'))

        # print('No stop_cond found, still')
        #     if self.sat:  # no stop_cond defined, but have a sat so can't use default stop condition
        #         print('Found a satellite but no StopCondition - making one')
        #         self.stop_cond: Propagate.StopCondition = Propagate.StopCondition(self.sat)  # self.sat)

        # if not self.stop_cond:  # no stop_cond defined
        #     print('No stop_cond found, still')
        #     if self.sat:  # no stop_cond defined, but have a sat so can't use default stop condition
        #         print('Found a satellite but no StopCondition - making one')
        #         self.stop_cond: Propagate.StopCondition = Propagate.StopCondition(self.sat)  # self.sat)
        #
        #     else:  # no self.sat defined. Generating default stop condition will also build default sat
        #         # TODO bugfix: this branch doesn't setup objects correctly in Sandbox. Raise NotImplementedError for now
        #         self.sat = mod.CreateSpacecraft()
        #         self.stop_cond = mod.CreateDefaultStopCondition()
        #         raise NotImplementedError

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

        # gmat.Initialize()
        sb.AddObject(self.sat)
        # gmat.Initialize()

        if not synchronized:  # default is not be synchronized
            self.synchronized = False
        else:
            # TODO: check for multiple sats - required for synchro. First need to define syntax for multi-sat prop
            self.synchronized = True

        # TODO: see Propagate.SetRefObject in source for hints about string/param handling behind the scenes
        self.SetRefObject(self.stop_cond, gmat.STOP_CONDITION, self.stop_cond.GetName())

        # sb.AddCommand(self.gmat_obj)
        # print('Added Propagate to Sandbox (in Propagate init)')
        # self.SetSolarSystem(gmat.GetSolarSystem())
        # self.SetObjectMap(gmat.Moderator.Instance().GetConfiguredObjectMap())
        # self.SetGlobalObjectMap(sb.GetGlobalObjectMap())

        # print(f'Propagate valid: {self.Validate()}')
        # print(self.gmat_obj)
        # gpy.Moderator().ValidateCommand(self.gmat_obj)
        # print('Attempting to ValidateCommand (in Propagate.init)...')
        # print(gmat.Moderator.Instance().ValidateCommand(self.gmat_obj))
        # print('Validated')
        # self.TakeAction('PrepareToPropagate')
        self.SetObjectMap(sb.GetObjectMap())
        self.SetGlobalObjectMap(sb.GetGlobalObjectMap())
        self.SetSolarSystem(gmat.GetSolarSystem())

        self.Validate()
        self.Initialize()
        gmat.Initialize()
        print('Propagate init complete!\n')

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
