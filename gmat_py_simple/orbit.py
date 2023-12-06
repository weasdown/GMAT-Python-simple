from __future__ import annotations

import logging

from load_gmat import gmat

from gmat_py_simple import basics, utils
# CelestialBodies, SpacecraftObjs, LibrationPoints, Barycenter, GroundStations, GmatObject, \
#     Spacecraft, CoordSystems, py_str_to_gmat_str, gmat_str_to_py_str
from gmat_py_simple.basics import GmatObject
import gmat_py_simple.spacecraft as spc
from gmat_py_simple.utils import *


class AtmosphereModel(GmatObject):
    def __init__(self, name: str = 'AtmoModel', model: str = 'JacchiaRoberts', f107: int = 150, f107a: int = 150,
                 magnetic_index=3, cssi_space_weather_file='SpaceWeather-All-v1.2.txt',
                 schatten_file='SchattenPredict.txt'):

        self.model = model
        self.allowed_models = ['JacchiaRoberts', 'MSISE86', 'MSISE90', 'NRLMSISE00', 'MarsGRAM2005']
        if self.model not in self.allowed_models:
            raise AttributeError(f'model parameter must be one of the following: {self.allowed_models}')

        super().__init__(model, name)

        self.f107 = f107
        self.SetField('F107', self.f107)

        self.f107a = f107a
        self.SetField('F107A', self.f107a)

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
    def __init__(self, name: str = 'FM', central_body: str = 'Earth', primary_bodies=None,
                 polyhedral_bodies: list = None, gravity_field: GravityField = None,
                 point_masses: str | list[str] | PointMassForce = None, drag=None,
                 srp: bool | SolarRadiationPressure = False, relativistic_correction: bool = False,
                 error_control: list = None, user_defined: list[str] = None):
        super().__init__('ODEModel', name)

        def validate_point_masses(pm) -> list[ForceModel.PointMassForce]:
            celestial_bodies = utils.CelestialBodies()

            # point_masses is a single string
            if isinstance(point_masses, str):
                # point mass for a body cannot be set if that body is already in an attached GravityField
                if self.gravity and (self._central_body in point_masses):
                    raise SyntaxError(f'Point mass for {self._central_body} cannot be used because '
                                      f'{self._central_body} is already set as the central body')

                return [ForceModel.PointMassForce(body=point_masses)]

            # point_masses is a single PointMassForce
            elif isinstance(point_masses, ForceModel.PointMassForce):
                if self.gravity and (self._central_body in point_masses.primary_body):
                    raise SyntaxError(f'Point mass for {self._central_body} cannot be used because a GravityField '
                                      f'containing {self._central_body} is already set')
                return [point_masses]

            # point_masses is a list (presumably of celestial body strings)
            elif isinstance(point_masses, list):
                if not all(isinstance(f, str) for f in point_masses):
                    raise TypeError('If point_masses is a list, its items must be strings of celestial body names')

                if not all([f in celestial_bodies for f in point_masses]):
                    raise SyntaxError(f'Not all strings in point_masses are valid celestial body names')

                if self.gravity and (any(force in self._central_body for force in point_masses)):
                    raise SyntaxError(f'Point mass for {self._central_body} cannot be used because '
                                      f'{self._central_body} is already set as the central body')

                # point_masses is a valid list of celestial body name strings
                pmf_list = []
                for body in point_masses:
                    pmf_list.append(ForceModel.PointMassForce(name=f'PMF_{body}', body=body))
                return pmf_list

            else:  # point_masses is not of a valid type
                raise SyntaxError('point_masses must be a single string, list of strings, or a single PointMassForce')

        # TODO define allowed values (different to defaults)
        self._allowed_values = {'arg': 'value'}
        defaults = {'error_control': ['RSSStep'], 'point_masses': ['Earth'], 'primary_bodies': []}

        self._central_body = central_body

        # TODO replace below with creation of GravityFields
        #  PrimaryBodies is alias for GravityFields as per page 162 of GMAT Architectucral Specification
        self._primary_bodies = primary_bodies if primary_bodies else self._central_body

        self._polyhedral_bodies = polyhedral_bodies

        if not gravity_field:
            self.gravity = self.GravityField()  # setup default field
        else:
            self.gravity: ForceModel.GravityField = gravity_field
            self.AddForce(self.gravity)

        self.point_mass_forces: list[ForceModel.PointMassForce] | None = None
        if not point_masses:
            self.SetField('PointMasses', [])
        else:
            self.point_mass_forces = validate_point_masses(point_masses)  # raises exception if point_masses invalid
            for force in self.point_mass_forces:
                self.AddForce(force)

        if not drag:
            self.drag = False
        elif isinstance(drag, ForceModel.DragForce):
            self.drag = drag
            self.AddForce(self.drag)
        else:
            self.drag = ForceModel.DragForce(fm=self)  # create and use a default drag model
            self.AddForce(self.drag)

        # if just srp=True, create and use a default srp object
        if not srp:
            self.srp = None
        elif isinstance(srp, ForceModel.SolarRadiationPressure):
            self.srp = srp
        else:
            ForceModel.SolarRadiationPressure(fm=self)

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
        gmat.Initialize()

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
            self._body = body if body else self._force_model._central_body
            self._gravity = gravity if gravity else ForceModel.GravityField()
            self._drag = drag if drag else ForceModel.DragForce(self._force_model)

    class DragForce(PhysicalModel):
        def __init__(self, fm: ForceModel = None, name: str = 'DF',
                     atmosphere_model: str = 'JacchiaRoberts',
                     drag_model: str = 'Spherical', f107: int = 150, f107a: int = 150, magnetic_index: int = 3,
                     historic_weather_source: str = 'ConstantFluxAndGeoMag',
                     predicted_weather_source: str = 'ConstantFluxAndGeoMag',
                     cssi_space_weather_file: str = 'SpaceWeather-All-v1.2.txt',
                     schatten_file: str = 'SchattenPredict.txt',
                     schatten_error_model: str = 'Nominal',
                     schatten_timing_model: str = 'NominalCycle', density_model=None,
                     input_file=None):

            super().__init__('DragForce', name)

            self.allowed_models = ['JacchiaRoberts', 'MSISE86', 'MSISE90', 'NRLMSISE00', 'MarsGRAM2005']
            if atmosphere_model not in self.allowed_models:
                raise AttributeError(f'model parameter must be one of the following: {self.allowed_models}')
            else:
                self.atmosphere_model = AtmosphereModel(model=atmosphere_model)
                self.SetReference(self.atmosphere_model)

            self.drag_model = drag_model
            self.f107 = f107
            self.f107a = f107a
            self.magnetic_index = magnetic_index

            self.historic_weather_source = historic_weather_source
            self.SetField('HistoricWeatherSource', self.historic_weather_source)

            self.predicted_weather_source = predicted_weather_source
            self.SetField('PredictedWeatherSource', self.predicted_weather_source)

            self.cssi_space_weather_file = cssi_space_weather_file
            self.SetField('CSSISpaceWeatherFile', self.cssi_space_weather_file)

            self.schatten_file = schatten_file
            self.SetField('SchattenFile', self.schatten_file)

            self.schatten_error_model = schatten_error_model
            self.SetField('SchattenErrorModel', self.schatten_error_model)

            self.schatten_timing_model = schatten_timing_model
            self.SetField('SchattenTimingModel', self.schatten_timing_model)

            if self.atmosphere_model == 'MarsGRAM2005':
                self.density_model = density_model
                self.SetField('DensityModel', self.density_model)

                self.input_file = input_file
                self.SetField('InputFile', self.input_file)
            else:
                self.density_model = None
                self.input_file = None

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
        # TODO flux and nominal Sun needed as arguments?
        def __init__(self, fm: ForceModel = None, name: str = 'SRP', model: str = 'Spherical', flux: float | int = 1367,
                     nominal_sun: float | int = 149597870.691):
            super().__init__('SolarRadiationPressure', name)
            self.force_model = fm
            self.model = model
            self.flux = flux
            self.nominal_sun = nominal_sun

            if self.force_model:
                self.force_model.AddForce(self)


class PropSetup(GmatObject):  # variable called prop in GMAT Python examples
    class Propagator(GmatObject):  # variable called gator in GMAT Python examples
        # Labelled in GMAT GUI as "Integrator"
        def __init__(self, integrator: str = 'PrinceDormand78', name: str = 'Prop', **kwargs):
            integrator_allowed_types = ['']
            super().__init__(integrator, name)
            self.integrator = integrator

    def __init__(self, name: str, fm: ForceModel = None, gator: PropSetup.Propagator = None,
                 initial_step_size: int = 60, accuracy: int = 1e-12, min_step: int = 0):
        super().__init__('PropSetup', name)
        self.force_model = fm if fm else ForceModel()
        self.gator = gator if gator else PropSetup.Propagator()

        if initial_step_size:
            self.initial_step_size = initial_step_size
            self.SetField('InitialStepSize', self.initial_step_size)

        if accuracy:
            self.accuracy = accuracy
            self.SetField('Accuracy', self.accuracy)

        if min_step:
            self.min_step = min_step
            self.SetField('MinStep', self.min_step)

        self.SetReference(self.gator)
        self.SetReference(self.force_model)

    def AddPropObject(self, sc: spc.Spacecraft):
        self.gmat_obj.AddPropObject(sc.gmat_obj)

    def PrepareInternals(self):
        self.gmat_obj.PrepareInternals()

    def GetPropagator(self):
        return self.gmat_obj.GetPropagator()

    def GetState(self):
        return self.gator.GetState()


class OrbitState:
    class CoordinateSystem:
        # TODO consider setting __init__ params mostly as kwargs
        def __init__(self, name: str, **kwargs):
            # TODO complete allowed values - see User Guide pages 335-339 (PDF pg 344-348)
            self._allowed_values = {'Axes': ['MJ2000Eq', 'MJ2000Ec', 'ICRF',
                                             'MODEq', 'MODEc', 'TODEq', 'TODEc', 'MOEEq', 'MOEEc', 'TOEEq', 'TOEEc',
                                             'ObjectReferenced', 'Equator', 'BodyFixed', 'BodyInertial',
                                             'GSE', 'GSM', 'Topocentric', 'BodySpinSun'],
                                    'CentralBody': CelestialBodies(),
                                    'Origin': [CelestialBodies() + SpacecraftObjs() + LibrationPoints() + Barycenter() +
                                               GroundStations()],
                                    }
            self._allowed_values['Primary'] = self._allowed_values['Origin']

            self._name = name
            self._origin = None
            self._axes = None
            self._central_body = None

            defaults = {'axes': 'MJ2000Eq', 'central_body': 'Earth', 'origin': 'Earth'}
            for attr in list(defaults.keys()):
                try:  # assume attr is in kwargs
                    val = kwargs[attr]
                    valid_values = self._allowed_values[attr]
                    if val in valid_values:
                        setattr(self, f'_{attr}', val)
                    else:
                        raise AttributeError(f'Invalid {attr} parameter provided - {val}\n'
                                             f'Must provide one of: {valid_values}')
                except KeyError:  # not in kwargs
                    setattr(self, f'_{attr}', defaults[attr])  # set attribute's default value

            if 'no_gmat_object' not in kwargs:
                gmat_obj = gmat.Construct('CoordinateSystem', self._name, self._central_body, self._axes)
                self.gmat_obj = GmatObject.from_gmat_obj(gmat_obj)

            # TODO parse Origin parameter
            # print(f'Currently allowed Origin values:\n{self._allowed_values["Origin"]}')

        def __repr__(self):
            return f'A CoordinateSystem with origin {self._origin} and axes {self._axes}'

        @staticmethod
        def Construct(name: str, central_body: str, axes: str):
            return gmat.Construct('CoordinateSystem', name, central_body, axes)

        @classmethod
        def from_sat(cls, sc: spc.Spacecraft) -> OrbitState.CoordinateSystem:
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
            print(f'New name in GMAT: {self.gmat_obj.GetName()}')

    def __init__(self, **kwargs):
        self._allowed_state_elements = {
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
        self._allowed_values = {'display_state_type': list(self._allowed_state_elements.keys()),
                                # TODO: get names of any other user-defined coordinate systems and add to allowlist
                                'coord_sys': CoordSystems(),
                                # TODO: define valid state_type values - using display_state_type ones for now
                                'state_type': list(self._allowed_state_elements.keys()),
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
                                    'state_type': 'Cartesian', 'sc': None}

        fields_remaining: list[str] = list(self._key_param_defaults.keys())

        # use Cartesian as default StateType
        if 'state_type' not in kwargs:
            self._state_type = 'Cartesian'
        else:  # state_type is specified but may not be valid
            if kwargs['state_type'] not in list(self._allowed_state_elements.keys()):  # invalid state_type was given
                raise SyntaxError(f'Invalid state_type parameter given: {kwargs["state_type"]}\n'
                                  f'Valid values are: {self._allowed_state_elements.keys()}')
            else:
                self._state_type = kwargs['state_type']
            fields_remaining.remove('state_type')

        # Set key parameters to value in kwargs, or None if not specified
        # TODO: add validity checking of other kwargs against StateType
        for param in fields_remaining:
            if param in kwargs:  # arguments must be without leading underscores
                setattr(self, f'_{param}', kwargs[param])
            else:
                setattr(self, f'_{param}', self._key_param_defaults[param])

    def apply_to_spacecraft(self, sc: spc.Spacecraft):
        """
        Apply the properties of this OrbitState to a spacecraft.

        :param sc:
        :return:
        """

        attrs_to_set = []
        # Find out which class attributes are set and apply all of them to the spacecraft
        instance_attrs = self.__dict__.copy()  # get a copy of the instance's current attributes

        # remove attributes that are just for internal class use and shouldn't be applied to a spacecraft
        for attr in ('_allowed_state_elements', '_allowed_values', '_gmat_fields', '_key_param_defaults', '_sc'):
            instance_attrs.pop(attr)

        attrs_to_set.extend(list(instance_attrs))

        # extend attrs_to_set with the elements corresponding to the current state_type
        try:  # state_type is recognized
            elements_for_given_state_type = self._allowed_state_elements[self._state_type]
            attrs_to_set.extend(elements_for_given_state_type)
        except KeyError:  # state_type attribute invalid
            raise AttributeError(f'Invalid state_type set as attribute: {self._state_type}')

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
    def from_dict(cls, orbit_dict: dict, sc: spc.Spacecraft = None) -> OrbitState:
        o_s: OrbitState = cls()  # create OrbitState object, with sc set as None by default

        try:
            o_s._state_type = orbit_dict['StateType']  # extract state_type from dict (required)
        except KeyError:
            raise KeyError(f"Required parameter 'StateType' was not found in OrbitState.from_dict")

        orbit_dict.pop('StateType')  # remove StateType so we don't try setting it again later

        o_s._allowed_values['coord_sys'] = CoordSystems()

        # TODO parse orbit params in orbit_dict

        for attr in orbit_dict:  # initialize other key attrs to None
            if attr[0].islower():
                raise SyntaxError(f'Invalid attribute found - {attr}. Must be in GMAT string format')
            setattr(o_s, gmat_str_to_py_str(attr, True), orbit_dict[attr])

        return o_s
