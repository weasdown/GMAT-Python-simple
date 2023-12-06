from __future__ import annotations

from load_gmat import gmat

from gmat_py_simple import GmatObject
from gmat_py_simple.spacecraft import Spacecraft
from gmat_py_simple.orbit import PropSetup


def Propagate(propagator: PropSetup, sc: Spacecraft, stop_param: str, stop_value: str | int = None,
              stop_tolerance: str = None, backProp: bool = False):
    stop_param_allowed_values = {
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
                       'HX', 'HY', 'HZ', 'INC', 'IncomingBVAZI', 'IncomingC3Energy', 'IncomingDHA', 'IncomingRadPer',
                       'IncomingRHA', 'Latitude', 'Longitude', 'LST', 'MA', 'MHA', 'MLONG', 'MM', 'ModEquinoctialF',
                       'ModEquinoctialG', 'ModEquinoctialH', 'ModEquinoctialK', 'MRP1', 'MRP2', 'MRP3', 'OrbitPeriod',
                       'OrbitTime', 'OutgoingBVAZI', 'OutgoingC3Energy', 'OutgoingDHA', 'OutgoingRadPer',
                       'OutgoingRHA', 'Periapsis', 'PlanetodeticAZI', 'PlanetodeticHFPA', 'PlanetodeticLAT',
                       'PlanetodeticLON', 'PlanetodeticRMAG', 'PlanetodeticVMAG', 'Q1', 'Q2', 'Q3', 'Q4', 'RA', 'RAAN',
                       'RadApo', 'RadPer', 'RAV', 'RLA', 'RMAG', 'SemilatusRectum', 'SMA', 'SPADDragScaleFactor',
                       'SPADDragScaleFactorSigma', 'SPADSRPScaleFactor', 'SPADSRPScaleFactorSigma', 'SRPArea',
                       'SystemCenterOfMassX', 'SystemCenterOfMassY', 'SystemCenterOfMassZ', 'SystemMomentOfInertiaXX',
                       'SystemMomentOfInertiaXY', 'SystemMomentOfInertiaXZ', 'SystemMomentOfInertiaYY',
                       'SystemMomentOfInertiaYZ', 'SystemMomentOfInertiaZZ', 'TA', 'TAIModJulian', 'TDBModJulian',
                       'TLONG', 'TLONGDot', 'TotalMass', 'TTModJulian', 'UTCModJulian', 'VelApoapsis', 'VelPeriapsis',
                       'VMAG', 'VX', 'VY', 'VZ', 'X', 'Y', 'Z']}

    class StopCondition(GmatObject):
        def __init__(self, obj_type: str, name: str):
            super().__init__('StopCondition', name)
            self.base_epoch = None
            self.epoch = None
            self.epoch_var = None
            self.stop_var = None
            self.goal = None
            self.repeat = None

    if not isinstance(sc, Spacecraft):
        raise TypeError('sc parameter must be a Spacecraft object')
    else:
        spacecraft = sc

    propagator = propagator if propagator else PropSetup('DefaultProp')

    if stop_param == 'ElapsedSecs':  # assuming stop_value is an ElapsedSecs value
        dt = stop_value
    elif stop_param == 'ElapsedDays':
        dt = stop_value * 86400
    else:
        raise NotImplementedError

    # TODO use direction
    if isinstance(backProp, bool):
        direction = -1 if backProp else 1  # propagate backwards (direction -1) if backProp is True, otherwise forwards
    else:
        raise SyntaxError('Invalid direction given - accepts only "Forwards" or "Backwards"')

    print(f'FM in Propagate: {propagator.force_model}')

    # TODO clarify: both of these commands needed?
    propagator.psm.SetObject(sc)  # from pg 61 of API Users Guide
    propagator.AddPropObject(sc)  # add the spacecraft to the PropSetup (and hence Propagator)

    propagator.PrepareInternals()

    propagator.gator = propagator.GetPropagator()
    gator = propagator.gator

    gator.Step(dt)
    gator.UpdateSpaceObject()
