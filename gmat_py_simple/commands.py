from __future__ import annotations

from load_gmat import gmat

from .spacecraft import Spacecraft
from .orbit import PropSetup


def Propagate(sc: Spacecraft, stop_param: str, stop_condition: str | int,
              stop_tolerance: str = None, propagator: PropSetup = None, direction: str = 'Forwards'):
    # TODO remove temporary step arg (using instead of in gator)

    if not isinstance(sc, Spacecraft):
        raise TypeError('sc parameter must be a Spacecraft object')
    else:
        spacecraft = sc

    propagator = propagator if propagator else PropSetup('DefaultProp')

    if stop_param == 'ElapsedSecs':
        dt = stop_condition
    elif stop_param == 'ElapsedDays':
        dt = stop_condition * 86400
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
