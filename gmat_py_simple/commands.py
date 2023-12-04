from __future__ import annotations

from load_gmat import gmat

from gmat_py_simple.spacecraft import Spacecraft
from gmat_py_simple.orbit import PropSetup


def Propagate(propagator: PropSetup, sc: Spacecraft, stop_param: str, stop_value: str | int,
              stop_tolerance: str = None, direction: str = 'Forwards'):
    # TODO remove temporary step arg (using instead of in gator)

    stop_param_allowed_values = {
        # TODO complete this properties list based on options available in GUI Propagate command
        'sc': ['A1ModJulian', 'Acceleration', 'AccelerationX', 'AccelerationY', 'AccelerationZ',
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
               'EquinoctialPDot', 'EquinoctialQ', 'EquinoctialQDot']}

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

    if direction == 'Forwards':
        direction = 1
    elif direction == 'Backwards':
        direction = -1
    else:
        raise SyntaxError('Invalid direction given - accepts only "Forwards" or "Backwards"')

    propagator.AddPropObject(sc)  # add the spacecraft to the PropSetup (and hence Propagator)
    propagator.PrepareInternals()
    propagator.gator = propagator.GetPropagator()
    gator = propagator.gator

    state = gator.GetState()
    print(f'Starting state: {state}')
    print(f'Starting Keplerian state:{spacecraft.GetKeplerianState()}')

    gator.Step(dt)
    gator.UpdateSpaceObject()
    state = gator.GetState()
    print(f'\nNew state: {state}')
    print(f'New Keplerian state:{spacecraft.GetKeplerianState()}')
