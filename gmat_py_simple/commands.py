from __future__ import annotations

from load_gmat import gmat

from gmat_py_simple import GmatObject
from gmat_py_simple.spacecraft import Spacecraft
from gmat_py_simple.orbit import PropSetup
from gmat_py_simple.utils import *


class GmatCommand:
    def __init__(self, obj_type: str):
        self.obj_type = obj_type
        self.gmat_obj = gmat.Construct(self.obj_type)

    def GetGeneratingString(self) -> str:
        return self.gmat_obj.GetGeneratingString()

    def GetField(self, field: str):
        self.gmat_obj.GetField(field)

    def SetField(self, field: str, val: str | list | int | float):
        self.gmat_obj.SetField(field, val)

    # def Help(self):
    #     self.gmat_obj.Help()


class Propagate(GmatCommand):
    class StopCondition(GmatObject):
        def __init__(self, name: str, base_epoch=None, epoch=None, epoch_var=None, stop_var=None,
                     goal=None, repeat=None):
            super().__init__('StopCondition', name)
            self.base_epoch = base_epoch
            self.epoch = epoch
            self.epoch_var = epoch_var
            self.stop_var = stop_var
            self.goal = goal
            self.repeat = repeat

    """
    Propagate section of pgate = gmat.Moderator.Instance().CreateDefaultCommand('Propagate', 'Pgate') below.
    Note: name (2nd arg) not used - have to set afterwards with pgate.SetName('Pgate')
    Full source code in src/base/executive/Moderator.cpp/CreateDefaultCommand()
    
    else if (type == "Propagate")
      {
         cmd->SetObject(GetDefaultPropSetup()->GetName(), Gmat::PROP_SETUP);
         
         StringArray formList = GetListOfObjects(Gmat::FORMATION);
         
         if (formList.size() == 0)
         {
            cmd->SetObject(GetDefaultSpacecraft()->GetName(), Gmat::SPACECRAFT);
         }
         else
         {
            // Get first spacecraft name not in formation
            std::string scName = GetSpacecraftNotInFormation();
            if (scName != "")
               cmd->SetObject(scName, Gmat::SPACECRAFT);
            else
               cmd->SetObject(formList[0], Gmat::SPACECRAFT);
         }
         
         cmd->SetRefObject(CreateDefaultStopCondition(), Gmat::STOP_CONDITION, "", 0);
         cmd->SetSolarSystem(theSolarSystemInUse);
      }    
    """

    def __init__(self, propagator: PropSetup, sc: Spacecraft, stop: tuple = ('DefaultSC.ElapsedSecs', 8640),
                 stop_tolerance: str = 1e-7, mode: str = None, prop_forward: bool = True):
        self.stop_param_allowed_values = {
            # TODO complete this properties list based on options available in GUI Propagate command
            'Spacecraft': ['A1ModJulian', 'Acceleration', 'AccelerationX', 'AccelerationY', 'AccelerationZ',
                           'AltEquinoctialP', 'AltEquinoctialQ', 'Altitude', 'AngularVelocityX', 'AngularVelocityY',
                           'AngularVelocityZ', 'AOP', 'Apoapsis', 'AtmosDensity', 'AtmosDensityScaleFactor',
                           'AtmosDensityScaleFactorSigma', 'AZI', 'BdotR', 'BdotT', 'BetaAngle', 'BrouwerLongAOP',
                           'BrouwerLongECC', 'BrouwerLongINC', 'BrouwerLongMA', 'BrouwerLongRAAN', 'BrouwerLongSMA',
                           'BrouwerShortAOP', 'BrouwerShortECC', 'BrouwerShortINC', 'BrouwerShortMA',
                           'BrouwerShortRAAN', 'BrouwerShortSMA', 'BVectorAngle', 'BVectorMag', 'C3Energy', 'Cd',
                           'CdSigma', 'Cr', 'CrSigma', 'DCM11', 'DCM12', 'DCM13', 'DCM21', 'DCM22', 'DCM23', 'DCM31',
                           'DCM32', 'DCM33', 'DEC', 'DECV', 'DelaunayG', 'Delaunayg', 'DelaunayH', 'Delaunayh',
                           'DelaunayL', 'Delaunayl', 'DLA', 'DragArea', 'DryCenterOfMassX', 'DryCenterOfMassY',
                           'DryCenterOfMassZ', 'DryMass', 'DryMassMomentOfInertiaXX', 'DryMassMomentOfInertiaXY',
                           'DryMassMomentOfInertiaXZ', 'DryMassMomentOfInertiaYY', 'DryMassMomentOfInertiaYZ',
                           'DryMassMomentOfInertiaZZ', 'EA', 'ECC', 'ElapsedDays', 'ElapsedSecs', 'Energy',
                           'EquinoctialH', 'EquinoctialHDot', 'EquinoctialK', 'EquinoctialKDot', 'EquinoctialP',
                           'EquinoctialPDot', 'EquinoctialQ', 'EquinoctialQDot', 'EulerAngle1', 'EulerAngle2',
                           'EulerAngle3', 'EulerAngleRate1', 'EulerAngleRate2', 'EulerAngleRate3', 'FPA', 'HA', 'HMAG',
                           'HX', 'HY', 'HZ', 'INC', 'IncomingBVAZI', 'IncomingC3Energy', 'IncomingDHA',
                           'IncomingRadPer',
                           'IncomingRHA', 'Latitude', 'Longitude', 'LST', 'MA', 'MHA', 'MLONG', 'MM', 'ModEquinoctialF',
                           'ModEquinoctialG', 'ModEquinoctialH', 'ModEquinoctialK', 'MRP1', 'MRP2', 'MRP3',
                           'OrbitPeriod',
                           'OrbitTime', 'OutgoingBVAZI', 'OutgoingC3Energy', 'OutgoingDHA', 'OutgoingRadPer',
                           'OutgoingRHA', 'Periapsis', 'PlanetodeticAZI', 'PlanetodeticHFPA', 'PlanetodeticLAT',
                           'PlanetodeticLON', 'PlanetodeticRMAG', 'PlanetodeticVMAG', 'Q1', 'Q2', 'Q3', 'Q4', 'RA',
                           'RAAN',
                           'RadApo', 'RadPer', 'RAV', 'RLA', 'RMAG', 'SemilatusRectum', 'SMA', 'SPADDragScaleFactor',
                           'SPADDragScaleFactorSigma', 'SPADSRPScaleFactor', 'SPADSRPScaleFactorSigma', 'SRPArea',
                           'SystemCenterOfMassX', 'SystemCenterOfMassY', 'SystemCenterOfMassZ',
                           'SystemMomentOfInertiaXX',
                           'SystemMomentOfInertiaXY', 'SystemMomentOfInertiaXZ', 'SystemMomentOfInertiaYY',
                           'SystemMomentOfInertiaYZ', 'SystemMomentOfInertiaZZ', 'TA', 'TAIModJulian', 'TDBModJulian',
                           'TLONG', 'TLONGDot', 'TotalMass', 'TTModJulian', 'UTCModJulian', 'VelApoapsis',
                           'VelPeriapsis',
                           'VMAG', 'VX', 'VY', 'VZ', 'X', 'Y', 'Z']}
        # Copied from GMAT src/base/command/Propagate.cpp/PARAMETER_TEXT
        self.params = ['AvailablePropModes', 'PropagateMode', 'InterruptFrequency', 'StopTolerance', 'Spacecraft',
                       'Propagator', 'StopCondition', 'PropForward', 'AllSTMs', 'AllAMatrices', 'AllCovariances']

        super().__init__('Propagate')

        self.propagator = propagator if propagator else PropSetup('DefaultProp')
        # self.gmat_obj.SetRefObject(self.propagator.gmat_obj, gmat.PROPAGATOR, self.propagator.name, 0)
        # self.SetField('Propagator', self.propagator.name)
        # self.gmat_obj.SetObject(self.propagator.gmat_obj.GetName(), gmat.PROPAGATOR)

        if mode:
            if mode != 'Synchronized':  # TODO: BackProp a valid option here, or handled separately?
                raise SyntaxError('Invalid mode was specified. If given, must be "Synchronized"')
            self.mode = mode
            self.SetField('PropagateMode', self.mode)  # believe complete - TODO test with multiple sats
        else:
            self.mode = None

        if '.' not in stop[0]:
            self.stop_param = f'{sc.name}.{stop[0]}'
        else:
            self.stop_param = stop[0]

        print(f'stop_param: {self.stop_param}')
        self.goal = stop[1]
        print(f'goal: {self.goal}')
        stop_cond_string = f'{self.stop_param} = {self.goal}'

        self.g_stop_cond = gmat.Construct('StopCondition', 'StopCond')
        self.g_stop_cond.Help()
        print(f'Stop condition fields: {gmat_obj_field_list(self.g_stop_cond)}')
        self.g_stop_cond.SetField('StopVar', self.stop_param)
        self.g_stop_cond.SetField('Goal', str(self.goal))
        print(f'Newly set g_stop_cond StopVar: {self.g_stop_cond.GetField("StopVar")}')
        print(f'Newly set g_stop_cond Goal: {self.g_stop_cond.GetField("Goal")}')
        # self.g_stop_cond.SetStopParameter(gmat.Construct('Parameter', self.stop_param))
        # self.gmat_obj.SetReference(self.g_stop_cond)
        # print(f'StopCondition Generating String: {self.g_stop_cond.GetGeneratingString()}')

        # g_stop_param = gmat.Construct('Parameter')
        # g_stop_param.SetField('InitialValue', stop_cond_string)
        # self.g_stop_cond.SetStopParameter(g_stop_param)

        # print(f'Stop condition string: {stop_cond_string}')
        # self.SetField('StopCondition', stop_cond_string)
        # self.SetStopParameter(stop_cond_string)
        # print(f'Newly set stop condition: {self.GetField("StopCondition")}')

        if not isinstance(sc, Spacecraft):
            raise TypeError('sc parameter must be a Spacecraft object')
        else:
            self.spacecraft = sc
            self.spacecraft.name = sc.name
            self.SetField('Spacecraft', self.spacecraft.name)  # complete

        # TODO: if stop_value isn't needed because of selected stop_param (e.g. Earth.Apoapsis), set to None
        #  assuming for now that stop_value is an int
        self.stop = stop

        # self.stop_param = self.stop[0]  # default stop_param is "DefaultSC.ElapsedSecs =" (pg 222 of GMAT Arch Spec)
        # self.g_stop_cond.SetLhsString(f'{self.spacecraft.name}.{self.stop_param} =')
        # print(f'New LHS String: {self.g_stop_cond.GetLhsString()}')

        # self.stop_condition = self.stop[1]  # default is 8640 (pg 222 of GMAT Architectectural Specification)
        # self.stop_condition = 8640.0  # TODO remove hardcoding once fixed
        # self.g_stop_cond.SetRhsString(str(self.stop_condition))
        # print(f'New RHS String: {self.g_stop_cond.GetRhsString()}')
        # print(f'Whole stop param: {self.g_stop_cond.GetStopParameter()}')

        # stop_param_string = f"{self.spacecraft.name}.{self.stop_param} = 8640.0"
        # print(f'"{stop_param_string}"')
        # self.g_stop_param = gmat.Construct('Parameter')
        # self.g_stop_cond.SetStopParameter(self.g_stop_cond)

        # print(f'StopParam: {self.g_stop_cond.GetStopParameter()}')

        # if self.stop_param == 'ElapsedSecs':  # assuming stop_value is an ElapsedSecs value
        #     self.dt = self.stop_condition
        # elif self.stop_param == 'ElapsedDays':
        #     # TODO bugfix: work for multiple ElapsedDays. ED = 1 works.
        #     #  If beyond ~1.3, result Epoch capped to 23 Jul 2014 17:29:17.477. Currently using ED * 86400 then Step.
        #     #  Also happens if using ElapsedSecs with e.g. 365*86400 to attempt one year.
        #     raise NotImplementedError
        #     # self.dt = self.stop_value * 86400
        # else:
        #     raise NotImplementedError

        print(f'self fields: {gmat_obj_field_list(self)}')
        self.propagator.SetReference(self.g_stop_cond)
        # self.SetField('StopCondition', self.g_stop_cond.GetName())

        self.stop_tolerance = stop_tolerance
        self.SetField('StopTolerance', self.stop_tolerance)  # complete

        if isinstance(prop_forward, bool):
            # propagate forwards (direction 1) if prop_forward is True, otherwise backwards (direction -1)
            self.prop_forward = prop_forward
            self.gmat_obj.SetBooleanParameter('PropForward', self.prop_forward)  # complete
        else:
            raise SyntaxError('Invalid prop_forward given - accepts only True or False')

        # TODO clarify: are both of these commands needed? Seems just one
        propagator.SetObject(sc)  # from pg 61 of API Users Guide
        # self.propagator.AddPropObject(sc)  # add the spacecraft to the PropSetup (and hence Propagator)

        self.propagator.PrepareInternals()

        self.propagator.gator = propagator.GetPropagator()
        self.gator = propagator.gator

        # self.gator.Step(self.dt)
        # self.gator.UpdateSpaceObject()

        # self.propagator.Help()

        print(f'Propagate Generating String: {self.GetGeneratingString()}')

    def CreateDefault(self):

        pass
