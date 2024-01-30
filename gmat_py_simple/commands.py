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
        # TODO convert all GmatCommand creation to the native Python form e.g. gmat.Propagate() if appropriate

        # Set GMAT object's name
        self.name: str = name
        self.gmat_obj.SetName(name)  # set obj name, as CreateDefaultCommand does not (Jira issue GMT-8095)

        self.SetObjectMap(mod.GetConfiguredObjectMap())
        self.SetGlobalObjectMap(gpy.Sandbox().GetGlobalObjectMap())
        self.SetSolarSystem(gmat.GetSolarSystem())

        # # Excluded object types must have key parameters set before they are initialized
        # if not isinstance(self, (gpy.Target, gpy.EndTarget, gpy.Achieve)):
        #     try:
        #         self.Initialize()
        #     except Exception as ex:
        #         raise RuntimeError(f'{self.command_type} command named "{self.name}" failed to initialize in '
        #                            f'GmatCommand.__init__() - see exception below:\n\t{ex}') from ex

    def AddToMCS(self) -> bool:
        return gpy.Moderator().AppendCommand(self)

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

    def GetParameterType(self, param: str | int) -> int:
        if isinstance(param, str):
            param = self.GetParameterID(param)
        return gpy.extract_gmat_obj(self).GetParameterType(param)

    def GetParameterTypeString(self, param: str | int) -> str:
        if isinstance(param, str):
            param = self.GetParameterID(param)
        return gpy.extract_gmat_obj(self).GetParameterTypeString(param)

    def GetRefObject(self, type_id: int, name: str, index: int = 0):
        return gpy.extract_gmat_obj(self).GetRefObject(type_id, name, index)

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
        gpy.extract_gmat_obj(self).Help()

    def Initialize(self) -> bool:
        try:
            resp = extract_gmat_obj(self).Initialize()
            if not resp:
                raise RuntimeError('Non-true response from Initialize()')
            return resp

        except Exception as ex:
            ex_str = str(ex).replace("\n", "")
            raise RuntimeError(f'Initialize failed for {type(self).__name__} named "{self.name}". See GMAT error below:'
                               f'\n\tGMAT internal exception/error: {ex_str}') from ex

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
        self.SetStringParameter('TargeterName', self.solver.GetName())
        self.SetRefObject(self.solver, gmat.SOLVER, self.solver.GetName())

        self.variable = variable
        self.SetStringParameter('Goal', self.variable)

        # Make Parameter for Goal if one doesn't already exist
        if not gpy.Moderator().GetParameter(self.variable):
            param_eles = self.variable.split('.')
            param_type = param_eles[-1]
            new_param = gpy.Parameter(param_type, self.variable)

            for ele in param_eles:
                if ele in gpy.CoordSystems():
                    # print(f'Updating CS for {new_param.GetName()}')
                    # Update the Parameter's COORDINATE_SYSTEM
                    new_param.SetRefObjectName(gmat.COORDINATE_SYSTEM, ele)
                    cs = gmat.GetObject(ele)
                    new_param.SetRefObject(cs, gmat.COORDINATE_SYSTEM)

                    # Also update the Parameter's SPACE_POINT
                    # print(f'Updating CB for {new_param.GetName()}')
                    body = cs.GetField('Origin')
                    new_param.SetRefObjectName(gmat.SPACE_POINT, body)
                    new_param.SetRefObject(gmat.GetObject(body), gmat.SPACE_POINT)

                if ele in gpy.SpacecraftObjs():
                    # print(f'Updating S/C for {new_param.GetName()}')
                    # Update the Parameter's SPACECRAFT
                    new_param.SetRefObjectName(gmat.SPACECRAFT, ele)
                    sc = gmat.GetObject(ele)
                    new_param.SetRefObject(sc, gmat.SPACECRAFT)

                if ele in gpy.CelestialBodies():
                    # print(f'Updating CB for {new_param.GetName()}')
                    # Update the Parameter's CELESTIAL_BODY (even if COORDINATE_SYSTEM not updated)
                    new_param.SetRefObjectName(gmat.CELESTIAL_BODY, ele)
                    new_param.SetRefObject(gmat.GetObject(ele), gmat.CELESTIAL_BODY)

            new_param.SetSolarSystem(gmat.GetSolarSystem())
            new_param.Initialize()
            # self.SetRefObject(new_param.gmat_base, gmat.PARAMETER)

        #     # param_type is the final element of the self.variable string, e.g. Periapsis for Sat.Earth.Periapsis
        #     param_eles = self.variable.split('.')
        #     param_type = param_eles[-1]
            # new_param = gpy.Parameter(param_type, self.variable)
            # for ele in param_eles:
            #     body = 'Earth'
            #     cs = 'EarthMJ2000Eq'
            #     if ele in gpy.CelestialBodies():  # a CelestialBody is given, so need to set it as a ref object
            #         # TODO: test this
            #         body = ele
            #
            #     if ele in gpy.CoordSystems():
            #         cs = ele
            #
            #     pass
                # new_param.SetRefObjectName(gmat.SPACE_POINT, body)
                # new_param.SetRefObjectName(gmat.COORDINATE_SYSTEM, cs)
                # new_param.Help()
                # print(new_param.gmat_base.GetRefObjectTypeArray())
                # new_param.SetRefObjectName(gmat.CELESTIAL_BODY, ele)

            #     if ele in gpy.CoordSystems():  # a CoordinateSystem is given, so need to set it as a ref object
            #         # TODO remove (debugging only)
            #         test_bddot = gmat.Construct('BdotT', 'TestBdotT')
            #         test_bddot.SetRefObjectName(gmat.SPACECRAFT, 'MAVEN')
            #         # test_bddot.SetReference(gmat.GetObject('MAVEN'))
            #         # print(gpy.Moderator().gmat_obj.GetListOfFactoryItems(gmat.PARAMETER))
            #         # test_bddot.RenameRefObject(gmat.COORDINATE_SYSTEM, 'EarthMJ2000Eq', ele)
            #         test_bddot.SetRefObjectName(gmat.COORDINATE_SYSTEM, ele)
            #         cs = gmat.GetObject(ele)
            #         test_bddot.SetRefObject(cs, gmat.COORDINATE_SYSTEM, cs.GetName())
            #
            #         # test_bddot.SetRefObjectName(gmat.SPACECRAFT, 'MAVEN')
            #         test_bddot.SetRefObject(gmat.GetObject('MAVEN'), gmat.SPACECRAFT, 'MAVEN')
            #
            #         test_bddot.SetSolarSystem(gmat.GetSolarSystem())
            #         # gmat.Initialize()
            #         mod = gpy.Moderator().gmat_obj
            #         mod.SetParameterRefObject(test_bddot, 'BdotT', cs.GetName(), '', '', 1)
            #         test_bddot.Help()
            #         test_bddot.Initialize()
            #
            #         new_param.SetRefObjectName(gmat.COORDINATE_SYSTEM, ele)
            #         # new_param.SetStringParameter(new_param.GetParameterID('CoordinateSystem'), ele)
            #         # new_param.SetRefObject(gmat.GetObject(ele), gmat.COORDINATE_SYSTEM)
            #         new_param.Help()
            #         pass
            #
            # for body in gpy.CelestialBodies():
            #     if body in self.variable:
            #         new_param.SetRefObject(gmat.Planet(body), gmat.COORDINATE_SYSTEM)

        self.value = value
        self.SetStringParameter('GoalValue', str(self.value))

        self.tolerance = tolerance
        self.SetStringParameter('Tolerance', str(self.tolerance))

        self.SetSolarSystem()
        self.SetObjectMap(gpy.Moderator().GetConfiguredObjectMap())
        self.SetGlobalObjectMap(gpy.Sandbox().GetGlobalObjectMap())

        self.Initialize()
        # print(self.GetGeneratingString())
        # gpy.Initialize()
        # self.Initialize()

    def SetRefObject(self, obj, type_int: int, obj_name: str = '') -> bool:
        return extract_gmat_obj(self).SetRefObject(extract_gmat_obj(obj), type_int, obj_name)


class BeginFiniteBurn(GmatCommand):
    def __init__(self, burn: gpy.FiniteBurn | gmat.FiniteBurn, spacecraft: gpy.Spacecraft | gmat.Spacecraft, name: str = ''):
        super().__init__('BeginFiniteBurn', name)

        # Assign the user-provided FiniteBurn to this command
        self.burn = burn
        self.SetRefObjectName(gmat.FINITE_BURN, self.burn.GetName())

        # Assign the user-provided Spacecraft to the FiniteBurn
        self.spacecraft = spacecraft
        self.burn.SetRefObject(self.spacecraft, gmat.SPACECRAFT, self.spacecraft.GetName())
        # self.spacecraft.Help()
        # print(type(self.spacecraft))
        # self.burn.SetSpacecraftToManeuver(gpy.extract_gmat_obj(self.spacecraft))  # update FiniteBurn's associated Spacecraft
        gpy.FiniteBurn.SetSpacecraftToManeuver(self.burn, gpy.extract_gmat_obj(self.spacecraft))  # update FiniteBurn's associated Spacecraft

        self.Initialize()


class BeginMissionSequence(GmatCommand):
    def __init__(self):
        super().__init__('BeginMissionSequence', 'BeginMissionSequenceCommand')

        self.SetSolarSystem()
        self.SetObjectMap(gpy.Moderator().GetConfiguredObjectMap())
        self.SetGlobalObjectMap(gpy.Sandbox().GetGlobalObjectMap())

        self.Initialize()


class EndFiniteBurn(GmatCommand):
    def __init__(self, burn: gpy.FiniteBurn | gmat.FiniteBurn, name: str):
        super().__init__('EndFiniteBurn', name)

        # Assign the user-provided FiniteBurn to this command
        self.burn = burn
        self.SetRefObjectName(gmat.FINITE_BURN, self.burn.GetName())

        self.Initialize()


class EndTarget(BranchCommand):
    def __init__(self, parent_target: gpy.Target, name: str = None):
        if name is None:
            name = f'EndTarget_{parent_target.GetName()}'

        super().__init__('EndTarget', name)

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

        super().__init__('Maneuver', name)

        self.burn = burn
        self.SetStringParameter(self.gmat_obj.GetParameterID('Burn'), self.burn.name)

        self.spacecraft = spacecraft
        self.SetStringParameter(self.gmat_obj.GetParameterID('Spacecraft'), self.spacecraft.name)
        self.burn.SetSpacecraftToManeuver(self.spacecraft)  # update burn's assigned spacecraft

        self.backprop = backprop
        self.SetBooleanParameter(self.gmat_obj.GetParameterID('BackProp'), self.backprop)

        self.SetSolarSystem()
        self.SetObjectMap(gpy.Moderator().GetConfiguredObjectMap())
        self.SetGlobalObjectMap(gpy.Sandbox().GetGlobalObjectMap())

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

            goalless = False
            goalless_params = ['Apoapsis', 'Periapsis']  # TODO: complete list

            # see whether any goalless param names exist in the stop_var string
            if any(x in stop_var for x in goalless_params):
                goalless = True
                stop_param_type = stop_var_elements[len(stop_var_elements) - 1]  # e.g. 'Periapsis'

            return stop_param_type, stop_var, epoch_param_type, epoch_var, goal, goalless, body

        def SetName(self, name: str) -> bool:
            return extract_gmat_obj(self).SetName(name)

        def SetStringParameter(self, param_name: str, value: str):
            return extract_gmat_obj(self).SetStringParameter(param_name, str(value))

    def __init__(self, name: str, sat: gpy.Spacecraft | gmat.Spacecraft, prop: gpy.PropSetup | gmat.GmatBase,
                 user_stop_cond: tuple | str = None):
        # TODO add None as default for sat, prop, stop_cond and handle appropriately in __init__()
        super().__init__('Propagate', name)
        self.Initialize()

        # Get names of Propagate's ref objects and extract the objects
        prop_ref_name = self.GetRefObjectName(gmat.PROP_SETUP)
        sat_ref_name = self.GetRefObjectName(gmat.SPACECRAFT)

        self.prop = self.GetRefObject(gmat.PROP_SETUP, prop_ref_name)  # use default PropSetup initially
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
            self.SetRefObjectName(gmat.SPACECRAFT, self.sat.GetName())

        self.stop_cond = self.GetGmatObject(gmat.STOP_CONDITION)
        # apply any user-provided stop condition
        if user_stop_cond:
            self.user_stop_cond = user_stop_cond
            # update default StopCondition with user-provided values by converting to wrapper StopCondition
            self.stop_cond = self.StopCondition(self.sat, stop_cond=self.user_stop_cond, gmat_obj=self.stop_cond)
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
                 command_sequence: list[gpy.GmatCommand] = None, show_progress_window: bool = False):
        if command_sequence is None:
            # Make sure the command sequence includes at least an EndTarget command
            command_sequence = [gpy.EndTarget(self, f'EndTarget for Target "{self.name}"')]

        super().__init__('Target', name)

        self.command_sequence = command_sequence

        # Get default solver then replace if the user has provided a solver object
        self.def_solver_name = self.GetRefObjectName(gmat.SOLVER)
        self.solver = gmat.GetObject(self.def_solver_name)
        if solver:
            self.solver: gpy.DifferentialCorrector | gmat.DifferentialCorrector = solver
            new_solver_name = self.solver.GetName()
            self.SetStringParameter('Targeter', new_solver_name)

        self.solve_mode = solve_mode
        self.SetStringParameter('SolveMode', self.solve_mode)

        self.exit_mode = exit_mode
        self.SetStringParameter('ExitMode', self.exit_mode)

        self.command_sequence: list[gpy.GmatCommand] = command_sequence

        self.show_progress_window = show_progress_window
        self.SetBooleanParameter('ShowProgressWindow', self.show_progress_window)

        self.SetSolarSystem()
        self.SetObjectMap(gpy.Moderator().GetConfiguredObjectMap())
        self.SetGlobalObjectMap(gpy.Sandbox().GetGlobalObjectMap())

        # # Make sure the final item in the command sequence is an EndTarget object
        if not isinstance(command_sequence[-1], gmat.EndTarget | gpy.EndTarget):
            command_sequence.append(gpy.EndTarget(self))

        # Add each of Target's sub-commands to the mission sequence
        for command in self.command_sequence:
            self.Append(gpy.extract_gmat_obj(command))


class Vary(SolverSequenceCommand):
    def __init__(self, name: str, solver: gpy.DifferentialCorrector | gmat.DifferentialCorrector, variable: str,
                 initial_value: float | int = 1, perturbation: float | int = 0.0001, lower: float | int = 0.0,
                 upper: float | int = pi, max_step: float | int = 0.5, additive_scale_factor: float | int = 0.0,
                 multiplicative_scale_factor: float | int = 1.0):

        user_created_def_ib = False
        def_ib_name = 'DefaultIB'
        def_ib_ele_name = 'DefaultIB.Element1'
        try:
            # an object named DefaultIB existed before Vary's init created one, so assume it's user-owned
            if gmat.GetObject('DefaultIB'):
                user_created_def_ib = True
        except AttributeError:
            # DefaultIB wasn't found, so does not exist
            pass

        super().__init__('Vary', name)

        self.solver = solver
        self.SetRefObject(self.solver, gmat.SOLVER, self.solver.GetName())
        self.SetStringParameter('SolverName', self.solver.GetName())

        self.variable = variable
        self.SetStringParameter('Variable', self.variable)

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

        # If a DefaultIB object exists and the user didn't create it, GMAT did while building this command - delete it
        if not user_created_def_ib:
            gmat.Clear(def_ib_name)

        # print(self.GetGeneratingString())

    def RenameRefObject(self, type_id: int, old_name: str, new_name: str) -> bool:
        return gpy.extract_gmat_obj(self).RenameRefObject(type_id, old_name, new_name)

    def SetRefObject(self, obj: gmat.GmatBase, type_id: int, name: str) -> bool:
        return gpy.extract_gmat_obj(self).SetRefObject(gpy.extract_gmat_obj(obj), type_id, name)
