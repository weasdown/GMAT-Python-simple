from __future__ import annotations

import gmat_py_simple
from load_gmat import gmat

import gmat_py_simple as gpy
from gmat_py_simple.basics import GmatObject
from gmat_py_simple.utils import *


class AtmosphereModel(GmatObject):
    def __init__(self, name: str = 'AtmoModel', atmo_model: str = 'JacchiaRoberts', f107: int = 150,
                 f107a: int = 150,
                 magnetic_index=3, cssi_space_weather_file='SpaceWeather-All-v1.2.txt',
                 schatten_file='SchattenPredict.txt'):

        self.atmo_model = str(atmo_model)
        self.allowed_models = ['JacchiaRoberts', 'MSISE86', 'MSISE90', 'NRLMSISE00', 'MarsGRAM2005']
        if self.atmo_model not in self.allowed_models:
            raise AttributeError(f'model parameter must be one of the following: {self.allowed_models}')

        super().__init__(atmo_model, name)

        if (not isinstance(f107, (int, float))) or (f107 < 0):
            raise TypeError('f107 must be an integer or float greater than 0')
        else:
            if (f107 > 400) or (f107 < 50):
                logging.warning('Realistic values of f107 are between 50 and 400 inclusive')
            self.f107 = f107
            self.SetField('F107', self.f107)

        if (not isinstance(f107a, (int, float))) or (f107a < 0):
            raise TypeError('f107a must be an integer or float greater than 0')
        else:
            if (f107 > 400) or (f107 < 50):
                logging.warning('Realistic values of f107a are between 50 and 400 inclusive')
            self.f107a = f107a
            self.SetField('F107A', self.f107a)

        if (not isinstance(magnetic_index, (int, float))) or (magnetic_index < 0) or (magnetic_index > 9):
            raise TypeError('magnetic_index must be an integer or float between 0 and 9 inclusive')
        else:
            self.magnetic_index = magnetic_index
            self.SetField('MagneticIndex', self.magnetic_index)

        if cssi_space_weather_file:
            self.cssi_space_weather_file = cssi_space_weather_file
            self.SetField('CSSISpaceWeatherFile', self.cssi_space_weather_file)
        else:
            self.cssi_space_weather_file = None

        if schatten_file:
            self.schatten_file = schatten_file
            self.SetField('SchattenFile', self.schatten_file)
        else:
            self.schatten_file = None

        # # TODO: complete merging these fields into AtmosphereModel() (from Drag())
        # self.historic_weather_source = historic_weather_source
        # self.SetField('HistoricWeatherSource', self.historic_weather_source)
        #
        # self.predicted_weather_source = predicted_weather_source
        # self.SetField('PredictedWeatherSource', self.predicted_weather_source)
        #
        # self.cssi_space_weather_file = cssi_space_weather_file
        # self.SetField('CSSISpaceWeatherFile', self.cssi_space_weather_file)
        #
        # self.schatten_file = schatten_file
        # self.SetField('SchattenFile', self.schatten_file)
        #
        # self.schatten_error_model = schatten_error_model
        # self.SetField('SchattenErrorModel', self.schatten_error_model)
        #
        # self.schatten_timing_model = schatten_timing_model
        # self.SetField('SchattenTimingModel', self.schatten_timing_model)


# class ExponentialAtmosphere(AtmosphereModel):
#     def __init__(self):
#         super().__init__()
#         raise NotImplementedError
#
#
# class SimpleExponentialAtmosphere(AtmosphereModel):
#     def __init__(self):
#         super().__init__()
#         raise NotImplementedError


class PhysicalModel(GmatObject):
    def __init__(self, obj_type: str, name: str):
        super().__init__(obj_type, name)


class ForceModel(GmatObject):
    def __init__(self, name: str = 'DefaultProp_ForceModel', central_body: str = 'Earth', primary_bodies=None,
                 polyhedral_bodies: list = None, gravity_field: GravityField = None,
                 point_masses: str | list[str] | PointMassForce = None, drag: DragForce = None,
                 srp: bool | SolarRadiationPressure = False, relativistic_correction: bool = False,
                 error_control: list = None, user_defined: list[str] = None):
        super().__init__('ForceModel', name)

        def validate_point_masses(pm) -> list[ForceModel.PointMassForce]:
            celestial_bodies = CelestialBodies()

            # point_masses is a single string
            if isinstance(point_masses, str):
                # point mass for a body cannot be set if that body is already in an attached GravityField
                if self.gravity and (self.central_body in point_masses):
                    raise SyntaxError(f'Point mass for {self.central_body} cannot be used because '
                                      f'{self.central_body} is already set as the central body')

                return [ForceModel.PointMassForce(body=point_masses)]

            # point_masses is a single PointMassForce
            elif isinstance(point_masses, ForceModel.PointMassForce):
                if self.gravity and (self.central_body in point_masses.primary_body):
                    raise SyntaxError(f'Point mass for {self.central_body} cannot be used because a GravityField '
                                      f'containing {self.central_body} is already set')
                return [point_masses]

            # point_masses is a list (presumably of celestial body strings)
            elif isinstance(point_masses, list):
                if not all(isinstance(f, str) for f in point_masses):
                    raise TypeError('If point_masses is a list, its items must be strings of celestial body names')

                if not all([f in celestial_bodies for f in point_masses]):
                    raise SyntaxError(f'Not all strings in point_masses are valid celestial body names')

                if self.gravity and (any(f in self.central_body for f in point_masses)):
                    # FIXME: breaks Tut04 DeepSpace FM
                    # TODO don't assume Earth
                    raise SyntaxError(f'Point mass for {self.central_body} cannot be used because '
                                      f'{self.central_body} is already set as the central body')

                # point_masses is a valid list of celestial body name strings
                pmf_list = []
                for body in point_masses:
                    pmf_list.append(ForceModel.PointMassForce(name=f'PointMassForce_{body}', body=body))
                return pmf_list

            else:  # point_masses is not of a valid type
                raise SyntaxError('point_masses must be a single string, list of strings, or a single PointMassForce')

        # TODO define allowed values (different to defaults)
        self._allowed_values = {'arg': 'value'}
        defaults = {'error_control': ['RSSStep'], 'point_masses': ['Earth'], 'primary_bodies': []}

        self.central_body = self.GetField('CentralBody')
        if central_body is not None:
            self.central_body = central_body
            self.SetStringParameter('CentralBody', self.central_body)

        # TODO replace below with creation of GravityFields
        #  PrimaryBodies is alias for GravityFields as per page 162 of GMAT Architectucral Specification
        self.gravity = None
        if primary_bodies is not None:
            self.primary_bodies = primary_bodies
            # self.Help()
            # self.SetField('PrimaryBodies', self.primary_bodies)
            # self._primary_bodies = primary_bodies if primary_bodies else self.central_body

            # TODO don't setup gravity field if none specified - breaks interplanetary where grav field irrelevant
            self.gravity = gravity_field
            if gravity_field is not None:
                if isinstance(gravity_field, ForceModel.GravityField):
                    self.gravity: ForceModel.GravityField = gravity_field
                else:
                    raise TypeError(f'gravity_field type not recognized - {type(gravity_field).__name__}.'
                                    f' Must be None or a gpy.ForceModel.GravityField')
                self.AddForce(self.gravity)

        self._polyhedral_bodies = polyhedral_bodies

        self.point_mass_forces: list[ForceModel.PointMassForce] | None = None
        if not point_masses:
            self.SetField('PointMasses', [])
        else:
            self.point_mass_forces = validate_point_masses(point_masses)  # raises exception if point_masses invalid
            for force in self.point_mass_forces:
                self.AddForce(force)

        # if just srp=True, create and use a default srp object
        if not srp:
            self.srp = None
        elif isinstance(srp, ForceModel.SolarRadiationPressure):
            self.srp = srp
            self.AddForce(self.srp)
        else:
            self.srp = ForceModel.SolarRadiationPressure(fm=self)
            self.AddForce(self.srp)

        if not drag:
            self.drag = False
        elif isinstance(drag, ForceModel.DragForce):
            self.drag = drag
            self.AddForce(self.drag)
        else:
            self.drag = ForceModel.DragForce(fm=self)  # create and use a default drag model
            self.AddForce(self.drag)

        # Add other effects
        self.relativistic_correction = relativistic_correction
        self.error_control = error_control
        self.user_defined = user_defined

        # for attr in self._allowed_values:  # TODO check supplied args are allowed
        #     # use supplied value. If not given (None), use default
        #     setattr(self, f'_{attr}', defaults[attr]) if attr is None else attr
        #
        # # TODO option 1: refer to OrbitState for how to tidily define defaults - implement here
        # # TODO option 2: implement below method of default setting in other classes
        # for attr in defaults:
        #     setattr(self, f'_{attr}', defaults[attr]) if attr is None else attr

        # check_valid_args(primary_bodies=primary_bodies)

        gpy.Initialize()
        self.Initialize()

    def __repr__(self):
        return f'ForceModel with name {self.name}'

    def AddForce(self, force: PhysicalModel):
        self.gmat_obj.AddForce(force.gmat_obj)

    class PrimaryBody:
        # TODO complete arguments
        # TODO: use fact that PrimaryBody is alias for GravityField - in init call GravityField.__init__
        def __init__(self, fm: ForceModel, body: str = 'Earth',
                     gravity: ForceModel.GravityField = None,
                     drag: ForceModel.DragForce | False = False):
            self._force_model = fm
            self._body = body if body else self._force_model.central_body
            self._gravity = gravity if gravity else ForceModel.GravityField()
            self._drag = drag if drag else ForceModel.DragForce(self._force_model)

    class DragForce(PhysicalModel):
        def __init__(self, fm: ForceModel = None, name: str = 'DF', atmo_model: str = 'JacchiaRoberts',
                     drag_model: str = 'Spherical', f107: int = 150, f107a: int = 150, magnetic_index: int = 3,
                     historic_weather_source: str = 'ConstantFluxAndGeoMag',
                     predicted_weather_source: str = 'ConstantFluxAndGeoMag',
                     cssi_space_weather_file: str = 'SpaceWeather-All-v1.2.txt',
                     schatten_file: str = 'SchattenPredict.txt', schatten_error_model: str = 'Nominal',
                     schatten_timing_model: str = 'NominalCycle',
                     density_model='Only used if atmo_model is MarsGRAM2005', input_file=None):
            # TODO remove unused args once moved to AtmosphereModel()

            super().__init__('DragForce', name)

            self.primary_body: str = fm.central_body if fm else 'Earth'
            # TODO: move to AtmosphereModel as appropriate
            self.allowed_values = {'models': {'Earth': ['JacchiaRoberts', 'MSISE86', 'MSISE90', 'NRLMSISE00'],
                                              'Mars': 'MarsGRAM2005'},
                                   'drag_model': ['Spherical', 'SPADFile'],
                                   'historic_weather_source': ['ConstantFluxAndGeoMag', 'CSSISpaceWeatherFile'],
                                   'predicted_weather_source': 'SchattenFile',
                                   'schatten_error_model': ['Nominal', 'PlusTwoSigma', 'MinusTwoSigma'],
                                   'schatten_timing_model': ['NominalCycle', 'EarlyCycle', 'LateCycle'],
                                   'density_model': ['High', 'Mean', 'Low']}
            allowed_models = self.allowed_values['models'][self.primary_body]
            if atmo_model not in allowed_models:
                raise AttributeError(f'model parameter must be one of the following: {allowed_models}')
            else:
                self.atmosphere_model = AtmosphereModel(atmo_model=atmo_model)
                self.SetReference(self.atmosphere_model)
                self.SetField('AtmosphereModel', self.atmosphere_model.atmo_model)

            if self.atmosphere_model == 'MarsGRAM2005':
                if density_model != 'Only used if atmo_model is MarsGRAM2005':
                    if density_model in self.allowed_values['density_model']:
                        self.density_model = density_model
                    else:
                        raise AttributeError('density_model must be "High", "Mean" or "Low" (default is "Mean")')
                else:
                    self.density_model = 'Mean'  # default density model
                self.SetField('DensityModel', self.density_model)

                self.input_file = input_file
                self.SetField('InputFile', self.input_file)
            elif self.atmosphere_model:
                self.density_model = None
                self.input_file = None
                self.drag_model = drag_model
                self.f107 = f107
                self.f107a = f107a
                self.magnetic_index = magnetic_index
            else:  # these four fields must not be used if no atmosphere model is specified
                self.drag_model = None
                self.f107 = None
                self.f107a = None
                self.magnetic_index = None

            if not fm:
                self.force_model = None
            else:
                self.force_model = fm
                self.force_model.AddForce(self)

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
        # An object representing the point mass force for a single celestial body

        # fields: ['Covariance', 'Epoch', 'ElapsedSeconds', 'BodyName', 'DerivativeID', 'GravConst', 'Radius',
        # 'EstimateMethod', 'PrimaryBody']
        def __init__(self, name: str = 'PMF', body: str = None):
            super().__init__('PointMassForce', name)
            if body:
                self.primary_body = body
            else:
                self.primary_body = 'Earth'
            self.SetField('BodyName', body)

    class SolarRadiationPressure(PhysicalModel):
        def __init__(self, fm: ForceModel = None, name: str = 'SRP', model: str = 'Spherical', flux: float | int = 1367,
                     nominal_sun: float | int = 149597870.691):
            super().__init__('SolarRadiationPressure', name)

            if model in ['Spherical', 'SPADFile', 'NPlate']:
                self.model = model
            else:
                raise AttributeError('Invalid model given for SolarRadiationPressure. Must be "Spherical", "SPADFile"'
                                     ' or "NPlate')
            if 1200 < flux < 1450:
                self.flux = flux
            else:
                raise AttributeError('flux argument must be between 1200 and 1450 (default is 1367)')

            if 135e6 < nominal_sun < 165e6:
                self.nominal_sun = nominal_sun
            else:
                raise AttributeError('nominal_sun argument must be between 135e6 and 165e6 (default is 149597870.691)')

            self.force_model = fm
            if self.force_model:
                self.force_model.AddForce(self)


class PropSetup(GmatObject):  # variable called prop in GMAT Python examples
    class Propagator(GmatObject):  # variable called gator in GMAT Python examples
        # Labelled in GMAT GUI as "Integrator"
        def __init__(self, integrator: str = 'PrinceDormand78', name: str = 'Prop', **kwargs):
            # TODO: change **kwargs to proper parsing here (for usability)
            # TODO: add parsing of rest of arguments (see defaults in User Guide)
            integrator_allowed_types = ['RungeKutta89', 'PrinceDormand78', 'PrinceDormand45', 'RungeKutta68',
                                        'RungeKutta56', 'AdamsBashforthMoulton', 'SPK', 'Code500', 'STK', 'CCSDS-OEM'
                                                                                                          'PrinceDormand853',
                                        'RungeKutta4', 'SPICESGP4']
            if integrator in integrator_allowed_types:
                self.integrator = integrator
            else:
                raise AttributeError(f'integrator must be one of the following: {integrator_allowed_types}')

            if name == 'Prop':
                name = f'{name}_{integrator}'

            super().__init__(integrator, name)

            gpy.Initialize()

    def __init__(self, name: str, fm: ForceModel = None, gator: PropSetup.Propagator = None,
                 initial_step_size: int = 60, accuracy: int | float = 1e-12, min_step: int = 0, max_step: int = 2700,
                 max_step_attempts: int = 50, stop_if_accuracy_violated: bool = True):
        # TODO add other args as per pg 449 (PDF pg 458) of User Guide
        super().__init__('PropSetup', name)
        self.force_model = fm if fm else ForceModel()
        self.gator = gator if gator else PropSetup.Propagator()
        self.SetReference(self.gator)

        gpy.Initialize()

        if initial_step_size is not None:
            self.initial_step_size = initial_step_size
            self.SetField('InitialStepSize', self.initial_step_size)

        if accuracy is not None:
            self.accuracy = accuracy
            self.SetField('Accuracy', self.accuracy)

        if min_step is not None:
            self.min_step = min_step
            self.SetField('MinStep', self.min_step)

        if max_step is not None:
            self.max_step = max_step
            self.SetField('MaxStep', self.max_step)

        if max_step_attempts is not None:
            self.max_step_attempts = max_step_attempts
            self.SetField('MaxStepAttempts', self.max_step_attempts)

        if stop_if_accuracy_violated is not None:
            self.stop_if_accuracy_violated = stop_if_accuracy_violated
            self.SetField('StopIfAccuracyIsViolated', self.stop_if_accuracy_violated)

        self.SetReference(self.force_model)
        self.psm = self.GetPropStateManager()

        gpy.Initialize()
        self.Initialize()

    def AddPropObject(self, sc: gpy.Spacecraft):
        obj = gpy.extract_gmat_obj(sc)
        self.gmat_obj.AddPropObject(obj)  # GMAT function does not give a return value

    def PrepareInternals(self):
        self.gmat_obj.PrepareInternals()

    def GetPropagator(self):
        return self.gmat_obj.GetPropagator()

    def GetState(self):
        return self.gator.gmat_obj.GetState()

    def GetPropStateManager(self):
        return self.gmat_obj.GetPropStateManager()

    def SetObject(self, sc):
        self.psm.SetObject(sc.gmat_obj)


class OrbitState:
    class CoordinateSystem(GmatObject):
        # TODO convert __init__ params to args with default values

        # TODO complete - will be able to create each type of Axes, for use in CoordinateSystem
        class Axes(GmatObject):
            def __init__(self, axes_type: str, name: str):
                super().__init__(axes_type, name)

        def __init__(self, name: str, origin: str = 'Earth', central_body: str = 'Earth',
                     axes: str = 'MJ2000Eq', **kwargs):
            # TODO: remove kwargs if possible, if not document as another 2do
            # TODO complete allowed values - see User Guide pages 335-339 (PDF pg 344-348)
            #  and src/base/coordsystem/CoordinateSystem.cpp/CreateLocalCoordinateSystem
            self._name = name
            super().__init__('CoordinateSystem', self._name)
            self.origin: str = origin
            self.axes: str = axes
            self.gmat_obj: gmat.CoordinateSystem = gmat.Construct('CoordinateSystem',
                                                                  self._name, self.origin, self.axes)

            self._allowed_values = {'Axes': ['MJ2000Eq', 'MJ2000Ec', 'ICRF',
                                             'MODEq', 'MODEc', 'TODEq', 'TODEc', 'MOEEq', 'MOEEc', 'TOEEq', 'TOEEc',
                                             'ObjectReferenced', 'Equator', 'BodyFixed', 'BodyInertial',
                                             'GSE', 'GSM', 'Topocentric', 'BodySpinSun'],
                                    'CentralBody': CelestialBodies(),
                                    'Origin': [CelestialBodies() + SpacecraftObjs() + LibrationPoints() + Barycenter() +
                                               GroundStations()],
                                    }
            self._allowed_values['Primary'] = self._allowed_values['Origin']
            self.axes = OrbitState.CoordinateSystem.Axes(axes, axes)
            self.origin: gmat.Planet = gmat.GetObject(origin)

            self.central_body = central_body

            # defaults = {'axes': 'MJ2000Eq', 'central_body': 'Earth', 'origin': 'Earth'}
            # for attr in list(defaults.keys()):
            #     try:  # assume attr is in kwargs
            #         val = kwargs[attr]
            #         valid_values = self._allowed_values[attr]
            #         if val in valid_values:
            #             setattr(self, f'_{attr}', val)
            #         else:
            #             raise AttributeError(f'Invalid {attr} parameter provided - {val}\n'
            #                                  f'Must provide one of: {valid_values}')
            #     except KeyError:  # not in kwargs
            #         setattr(self, f'_{attr}', defaults[attr])  # set attribute's default value

            # TODO parse Origin parameter
            # print(f'Currently allowed Origin values:\n{self._allowed_values["Origin"]}')
            gpy.Initialize()
            self.Initialize()

        def __repr__(self):
            return f'A CoordinateSystem with origin {self.origin} and axes {self.axes}'

        @staticmethod
        def Construct(name: str, central_body: str, axes: str):
            print('In static Construct')
            return gmat.Construct('CoordinateSystem', name, central_body, axes)

        @classmethod
        def from_sat(cls, sc: gpy.Spacecraft) -> OrbitState.CoordinateSystem:
            name = sc.gmat_obj.GetRefObjectName(gmat.COORDINATE_SYSTEM)
            sc_cs_gmat_obj = sc.gmat_obj.GetRefObject(150, name)
            origin = sc_cs_gmat_obj.GetField('Origin')
            axes = sc_cs_gmat_obj.GetField('Axes')
            coord_sys = cls(name=name, origin=origin, axes=axes, no_gmat_object=True)
            return coord_sys

        @property
        def name(self) -> str:
            name = getattr(self, '_name', self.gmat_obj.GetName())
            return name

        @name.setter
        def name(self, name):
            self._name = name
            self.gmat_obj.SetName(name)

        def Help(self):
            return GmatObject.Help(self.gmat_obj)

    def __init__(self, **kwargs):
        self.allowed_state_elements = {
            'Cartesian': {'X', 'Y', 'Z', 'VX', 'VY', 'VZ'},
            'Keplerian': {'SMA', 'ECC', 'INC', 'RAAN', 'AOP', 'TA'},
            'ModifiedKeplerian': {'RadApo', 'RadPer', 'INC', 'RAAN', 'AOP', 'TA'},
            'SphericalAZFPA': {'RMAG', 'RA', 'DEC', 'VMAG', 'AZI', 'FPA'},
            'SphericalRADEC': {'RMAG', 'RA', 'DEC', 'VMAG', 'RAV', 'DECV'},
            'Equinoctial': {'SMA', 'EquinoctialH', 'EquinoctialK',
                            'EquinoctialP', 'EquinoctialQ', 'MLONG'},
            'ModifiedEquinoctial': {'SemilatusRectum', 'ModEquinoctialF', 'ModEquinoctialG',
                                    'ModEquinoctialH', 'ModEquinoctialH', 'TLONG'},
            'AlternativeEquinoctial': {'SMA', 'EquinoctialH', 'EquinoctialK',
                                       'AltEquinoctialP', 'AltEquinoctialQ', 'MLONG'},
            'Delaunay': {'Delaunayl', 'Delaunayg', 'Delaunayh', 'DelaunayL', 'DelaunayG', 'DelaunayH'},
            'OutgoingAsymptote': {'OutgoingRadPer', 'OutgoingC3Energy', 'OutgoingRHA',
                                  'OutgoingDHA', 'OutgoingBVAZI', 'TA'},
            'IncomingAsymptote': {'IncomingRadPer', 'IncomingC3Energy', 'IncomingRHA',
                                  'IncomingDHA', 'IncomingBVAZI', 'TA'},
            'BrouwerMeanShort': {'BrouwerShortSMA', 'BrouwerShortECC', 'BrouwerShortINC',
                                 'BrouwerShortRAAN', 'BrouwerShortAOP', 'BrouwerShortMA'},
            'BrouwerMeanLong': {'BrouwerLongSMA', 'BrouwerLongECC', 'BrouwerLongINC',
                                'BrouwerLongRAAN', 'BrouwerLongAOP', 'BrouwerLongMA'}
        }
        # TODO complete self._allowed_values - see pg 599 of GMAT User Guide (currently missing Planetodetic)
        self._allowed_values = {'display_state_type': list(self.allowed_state_elements.keys()),
                                # TODO: get names of any other user-defined coordinate systems and add to allowlist
                                'coord_sys': CoordSystems(),
                                # TODO: define valid state_type values - using display_state_type ones for now
                                'state_type': list(self.allowed_state_elements.keys()),
                                }

        # TODO complete this list
        self._gmat_fields = {'EpochFormat': {'A1ModJulian',
                                             'TAIModJulian',
                                             'UTCModJulian',
                                             'TDBModJulian',
                                             'TTModJulian',
                                             'A1Gregorian',
                                             'TAIGregorian',
                                             'UTCGregorian',
                                             'TDBGregorian',
                                             'TTGregorian'},
                             'Epoch': type(int),
                             # 'CoordinateSystem' will also include user-defined ones
                             'CoordinateSystem': {'EarthMJ2000Eq', 'EarthMJ2000Ec', 'EarthFixed', 'EarthICRF'},
                             'StateType': {},
                             'DisplayStateType': {}
                             }

        self._key_param_defaults = {'date_format': 'TAIModJulian', 'epoch': str(21545), 'coord_sys': 'EarthMJ2000Eq',
                                    'display_state_type': 'Cartesian', 'sc': None}

        fields_remaining: list[str] = list(self._key_param_defaults.keys())

        # use Cartesian as default StateType
        if 'display_state_type' not in kwargs:
            self._display_state_type = 'Cartesian'
        else:  # state_type is specified but may not be valid
            if kwargs['display_state_type'] not in list(self.allowed_state_elements.keys()):
                # invalid display_state_type was given
                raise SyntaxError(f'Invalid display_state_type parameter given: {kwargs["display_state_type"]}\n'
                                  f'Valid values are: {self.allowed_state_elements.keys()}')
            else:
                self._display_state_type = kwargs['display_state_type']
            fields_remaining.remove('display_state_type')

        # Set key parameters to value in kwargs, or None if not specified
        # TODO: add validity checking of other kwargs against DisplayStateType
        for param in fields_remaining:
            if param in kwargs:  # arguments must be without leading underscores
                setattr(self, f'_{param}', kwargs[param])
            else:
                setattr(self, f'_{param}', self._key_param_defaults[param])

    def apply_to_spacecraft(self, sc: gpy.Spacecraft):
        """
        Apply the properties of this OrbitState to a spacecraft.

        :param sc:
        :return:
        """

        attrs_to_set = []
        # Find out which class attributes are set and apply all of them to the spacecraft
        instance_attrs = self.__dict__.copy()  # get a copy of the instance's current attributes

        # remove attributes that are just for internal class use and shouldn't be applied to a spacecraft
        for attr in ('allowed_state_elements', '_allowed_values', '_gmat_fields', '_key_param_defaults', '_sc'):
            instance_attrs.pop(attr)

        attrs_to_set.extend(list(instance_attrs))

        # extend attrs_to_set with the elements corresponding to the current state_type
        try:  # state_type is recognized
            elements_for_given_state_type = self.allowed_state_elements[self._display_state_type]
            attrs_to_set.extend(elements_for_given_state_type)
        except KeyError:  # state_type attribute invalid
            raise AttributeError(f'Invalid state_type set as attribute: {self._display_state_type}')

        for attr in attrs_to_set:
            try:
                # TODO bugfix: setting element e.g. ECC to 'Cartesian'
                # TODO bugfix: setting DisplayStateType to 'Cartesian'
                gmat_attr = py_str_to_gmat_str(attr)
                val = getattr(self, attr)
                if gmat_attr == 'CoordSys':
                    gmat_attr = 'CoordinateSystem'
                if val is not None:
                    if (gmat_attr == 'Epoch') and (not isinstance(val, str)):
                        val = str(val)
                    sc.SetField(gmat_attr, val)
                raise AttributeError
            except AttributeError:
                # print(f'No value set for attr {attr} - skipping')
                pass

    @classmethod
    def from_dict(cls, orbit_dict: dict, sc: gpy.Spacecraft = None) -> OrbitState:
        o_s: OrbitState = cls()  # create OrbitState object, with sc set as None by default

        try:
            o_s._display_state_type = orbit_dict['DisplayStateType']  # get display_state_type from dict (required)
            orbit_dict.pop('DisplayStateType')  # remove DisplayStateType so we don't try setting it again later
        except KeyError:
            try:  # maybe the user used the old name, StateType, instead of DisplayStateType
                o_s._display_state_type = orbit_dict['StateType']
                orbit_dict.pop('StateType')  # remove StateType so we don't try setting it again later
            except KeyError:
                raise KeyError(f"Required parameter 'DisplayStateType' was not found in OrbitState.from_dict")

        o_s._allowed_values['coord_sys'] = CoordSystems()

        # TODO parse orbit params in orbit_dict

        for attr in orbit_dict:  # initialize other key attrs to None
            if attr[0].islower():
                raise SyntaxError(f'Invalid attribute found - {attr}. Must be in GMAT string format')
            setattr(o_s, gmat_str_to_py_str(attr, True), orbit_dict[attr])

        return o_s
