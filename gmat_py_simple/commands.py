from load_gmat import gmat

from .spacecraft import Spacecraft
from .orbit import PropSetup


class Propagate:
    def __init__(self, propagator: PropSetup, sc: Spacecraft, stop_param: str, stop_condition: str,
                 stop_tolerance: str = None, direction: str = 'Forwards'):
        if not isinstance(sc, Spacecraft):
            raise TypeError('sc parameter must be a Spacecraft object')
        else:
            self.spacecraft = sc

        self.propagator = propagator
        self.stop_param = stop_param
        self.stop_condition = stop_condition

        if direction == 'Forwards':
            self.direction = 1
        elif direction == 'Backwards':
            self.direction = -1
        else:
            raise SyntaxError('Invalid direction given - accepts only "Forwards" or "Backwards"')
