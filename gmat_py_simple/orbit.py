from __future__ import annotations

from load_gmat import gmat

from gmat_py_simple.basics import GmatObject
from gmat_py_simple.spacecraft import Spacecraft


class AtmosphereModel(GmatObject):
    def __init__(self):
        # super().__init__('AtmosphereModel', 'AtmosphereModel')
        # raise NotImplementedError
        pass


class ExponentialAtmosphere(AtmosphereModel):
    def __init__(self):
        super().__init__()
        raise NotImplementedError


class JacchiaRobertsAtmosphere(AtmosphereModel):
    def __init__(self):
        super().__init__()
        raise NotImplementedError


class MSISE90Atmosphere(AtmosphereModel):
    def __init__(self):
        super().__init__()
        raise NotImplementedError


class SimpleExponentialAtmosphere(AtmosphereModel):
    def __init__(self):
        super().__init__()
        raise NotImplementedError


class PhysicalModel(GmatObject):
    def __init__(self, obj_type: str, name: str):
        super().__init__(obj_type, name)


class ForceModel(GmatObject):
    def __init__(self, name: str = 'FM', central_body: str = 'Earth', primary_bodies=None,
                 polyhedral_bodies: list = None, point_masses: list[PointMassForce] = None, drag=None,
                 srp: bool = False, relativistic_correction: bool = False, error_control: list = None,
                 user_defined: list[str] = None):
        super().__init__('ODEModel', name)

        self._central_body = central_body
        self._primary_bodies = primary_bodies if primary_bodies else self._central_body
        self._polyhedral_bodies = polyhedral_bodies

        self._gravity = self.GravityField()
        self.AddForce(self._gravity)

        self._point_masses = point_masses if point_masses else self.PointMassForce(self)
        # self.AddForce(self._point_masses)  # TODO cannot use as well as GravityField

        self._drag = False if drag is None else ForceModel.DragForce(self)

        self._srp = ForceModel.SolarRadiationPressure(self) if srp else False
        self._relativistic_correction = relativistic_correction
        self._error_control = error_control
        self._user_defined = user_defined

        # TODO define allowed values (different to defaults)
        self._allowed_values = {'arg': 'value'}
        defaults = {'error_control': ['RSSStep'], 'point_masses': ['Earth'], 'primary_bodies': []}

        for attr in self._allowed_values:  # TODO check supplied args are allowed
            # use supplied value. If not given (None), use default
            setattr(self, f'_{attr}', defaults[attr]) if attr is None else attr

        # TODO option 1: refer to OrbitState for how to tidily define defaults - implement here
        # TODO option 2: implement below method of default setting in other classes
        for attr in defaults:
            setattr(self, f'_{attr}', defaults[attr]) if attr is None else attr

        # TODO: perform this error check
        def check_valid_args(**kwargs):
            for kwarg in kwargs:
                if kwargs[kwarg] not in self._allowed_values:
                    raise AttributeError('Invalid argument specified')

        # check_valid_args(primary_bodies=primary_bodies)
        gmat.Initialize()

    def AddForce(self, force: PhysicalModel):
        self.gmat_obj.AddForce(force.gmat_obj)

    class PrimaryBody:
        # TODO complete arguments
        def __init__(self, fm: ForceModel, body: str = 'Earth',
                     gravity: ForceModel.GravityField = None,
                     drag: ForceModel.DragForce | False = False):
            self._force_model = fm
            self._body = body if body else self._force_model._central_body
            self._gravity = gravity if gravity else ForceModel.GravityField()
            self._drag = drag if drag else ForceModel.DragForce(self._force_model)

    class DragForce(PhysicalModel):
        def __init__(self, fm: ForceModel, name: str = 'DragForce',
                     atmosphere_model: AtmosphereModel = AtmosphereModel(),
                     historical_weather_source: str = 'ConstantFluxAndGeoMag',
                     predicted_weather_source: str = 'ConstantFluxAndGeoMag',
                     cssi_space_weather_file: str = 'SpaceWeather-All-v1.2.txt',
                     schatten_file: str = 'SchattenPredict.txt', f107: int = 150, f107a: int = 150,
                     magnetic_index: int = 3, schatten_error_model: str = 'Nominal',
                     schatten_timing_model: str = 'NominalCycle', drag_model: str = 'Spherical', density_model=None,
                     input_file=None):
            super().__init__('DragForce', name)
            self._force_model = fm

            self.atmosphere_model = atmosphere_model
            self.historical_weather_source = historical_weather_source
            self.predicted_weather_source = predicted_weather_source
            self.cssi_space_weather_file = cssi_space_weather_file
            self.schatten_file = schatten_file
            self.f107 = f107
            self.f107a = f107a
            self.magnetic_index = magnetic_index
            self.schatten_error_model = schatten_error_model
            self.schatten_timing_model = schatten_timing_model
            self.drag_model = drag_model
            self.density_model = density_model
            self.input_file = input_file

            # TODO SetField in attr for loop

    class FiniteThrust(PhysicalModel):
        def __init__(self, name: str = 'FiniteThrust'):
            super().__init__('FiniteThrust', name)
            raise NotImplementedError

    class Harmonic:
        def __init__(self):
            raise NotImplementedError

    class HarmonicGravity(Harmonic):
        def __init__(self):
            super().__init__()
            raise NotImplementedError

    class HarmonicField(PhysicalModel):
        def __init__(self):
            super().__init__('HarmonicField', 'HarmonicField')
            raise NotImplementedError

    class GravityField(PhysicalModel):
        # TODO change parent class back to HarmonicField if appropriate
        def __init__(self, model: str = 'JGM-2', degree: int = 4, order: int = 4, stm_limit: int = 100,
                     gravity_file: str = 'JGM2.cof', tide_file: str = None, tide_model: str = None):
            super().__init__('GravityField', 'Grav')
            self._model = model

            self._degree = degree
            self.SetField('Degree', self._degree)

            self._order = order
            self.SetField('Order', self._order)

            self._stm_limit = stm_limit
            self.SetField('StmLimit', self._stm_limit)

            self._gravity_file = gravity_file
            self.SetField('PotentialFile', self._gravity_file)

            self._tide_file = tide_file
            if self._tide_file:
                self.SetField('TideFile', self._tide_file)

            if tide_model:
                if tide_model not in [None, 'Solid', 'SolidAndPole']:
                    raise SyntaxError('Invalid tide_model given - must be None, "Solid" or "SolidAndPole"')
                else:
                    self._tide_model = tide_model
                    self.SetField('TideModel', self._tide_model)

    class ODEModel(PhysicalModel):
        def __init__(self, name: str):
            super().__init__('ODEModel', name)
            raise NotImplementedError

    class PointMassForce(PhysicalModel):
        def __init__(self, fm: ForceModel, name: str = 'PMF', point_masses: list[str] = None):
            super().__init__('PointMassForce', name)
            self._force_model = fm
            self._point_masses = point_masses if point_masses else []

            self._force_model.SetField('PointMasses', self._point_masses)

    class SolarRadiationPressure(PhysicalModel):
        def __init__(self, fm: ForceModel, name: str = 'SRP', model: str = 'Spherical'):
            super().__init__('SolarRadiationPressure', name)
            self._force_model = fm
            self.model = model

            print('Creating an SRP object')
            self._force_model.AddForce(self)


class PropSetup(GmatObject):  # prop
    class Propagator(GmatObject):  # gator
        # Labelled in GMAT GUI as "Integrator"
        def __init__(self, integrator: str = 'PrinceDormand78', name: str = 'Prop', **kwargs):
            integrator_allowed_types = ['']
            super().__init__(integrator, name)
            self.integrator = integrator

    def __init__(self, name: str, fm: ForceModel = None, gator: PropSetup.Propagator = None):
        super().__init__('PropSetup', name)
        self.force_model = fm if fm else ForceModel()
        self.gator = gator if gator else PropSetup.Propagator()

        self.SetReference(self.gator)
        self.SetReference(self.force_model)

    def AddPropObject(self, sc: Spacecraft):
        self.gmat_obj.AddPropObject(sc.gmat_obj)

    def PrepareInternals(self):
        self.gmat_obj.PrepareInternals()

    def GetPropagator(self):
        return self.gmat_obj.GetPropagator()
