from typing import Union

from load_gmat import gmat

from . import GmatObject


class ForceModel(GmatObject):
    class Drag:
        def __init__(self, atmosphere_model: str = 'MSISE90', historical_weather_source:):
            self._atmosphere_model = atmosphere_model

    def __init__(self, name: str = None, central_body: str = 'Earth', primary_bodies=None,
                 polyhedral_bodies: list = None, point_masses=None, drag: Drag = None,
                 srp: bool = False, relativistic_correction: bool = False, error_control: list = None,
                 user_defined: list[str] = None
                 ):

        # TODO define allowed values (different to defaults)
        self._allowed_values = {'arg': 'value'}
        defaults = {'error_control': ['RSSStep'], 'point_masses': ['Earth'], 'primary_bodies': []}

        for attr in self._allowed_values:  # TODO check supplied args are allowed
            # use supplied value. If not given (None), use default
            setattr(self, f'_{attr}', defaults[attr]) if attr is None else attr

        # TODO option 1: refer to OrbitState for how to tidily define defaults - implement here
        # TODO option 2: implement below method of default setting in other classes
        for attr in defaults:
            val = attr
            print(val)
            setattr(self, f'_{attr}', defaults[attr]) if attr is None else attr

        # self._error_control = ['RSSStep'] if error_control is None else error_control

        def check_valid_args(**kwargs):
            for kwarg in kwargs:
                if kwargs[kwarg] not in self._allowed_values:
                    raise AttributeError('Invalid argument specified')

        if not name:
            self._name = name
        super().__init__('ODEModel', name)

        # check_valid_args('primary_bodies'=primary_bodies)

        if not srp:  # srp argument is 'False'
            self._srp = 'Off'
        else:  # srp model type has been specified
            # TODO check srp against allowed values
            self._srp = 'On'

        pass


class PropSetup(GmatObject):  # prop
    def __init__(self, name: str, fm: ForceModel = None):
        super().__init__('PropSetup', name)
        if fm:
            self.force_model = fm
        else:
            self.force_model = ForceModel()

    class Propagator(GmatObject):  # gator
        # Labelled in GMAT GUI as "Integrator"
        def __init__(self, integrator: str = 'PrinceDormand78', name: str = 'Prop', **kwargs):
            # TODO confirm whether obj_type is PropSetup or Propagator
            integrator_allowed_types = ['']

            super().__init__(integrator, name)

    pass
