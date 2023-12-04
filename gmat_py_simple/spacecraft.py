from __future__ import annotations

from load_gmat import gmat

from .basics import *
from .utils import *

from typing import Union
import logging


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
        def from_sat(cls, sc: Spacecraft) -> OrbitState.CoordinateSystem:
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
        self._allowed_values = {'display_state_type': self._allowed_state_elements.keys(),
                                # TODO: get names of any other user-defined coordinate systems and add to allowlist
                                'coord_sys': CoordSystems(),
                                # TODO: define valid state_type values - using display_state_type ones for now
                                'state_type': self._allowed_state_elements,
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
                                    'state_type': 'Cartesian', 'display_state_type': 'Cartesian', 'sc': None}

        fields_remaining: list[str] = list(self._key_param_defaults.keys())

        # use Cartesian as default StateType
        if 'state_type' not in kwargs:
            self._state_type = 'Cartesian'
        else:  # state_type is specified but may not be valid
            if kwargs['state_type'] not in self._allowed_state_elements.keys():  # invalid state_type given
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

    def apply_to_spacecraft(self, sc: Spacecraft):
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
                gmat_attr = py_str_to_gmat_str(attr)
                val = getattr(self, attr)
                if gmat_attr == 'CoordSys':
                    gmat_attr = 'CoordinateSystem'
                if val is not None:
                    sc.SetField(gmat_attr, val)
                raise AttributeError
            except AttributeError:
                # print(f'No value set for attr {attr} - skipping')
                pass

    @classmethod
    def from_dict(cls, orbit_dict: dict, sc: Spacecraft = None) -> OrbitState:
        if 'StateType' not in orbit_dict.keys():
            raise KeyError(f"Required parameter 'StateType' was not found in OrbitState.from_dict")
        else:
            state_type = orbit_dict['StateType']  # extract state_type from dict (required)
        orbit_dict.pop('StateType')  # remove StateType so we don't try setting it again later

        o_s: OrbitState = cls(sc=sc, state_type=state_type)  # create OrbitState object, with sc set as None by default
        o_s._allowed_values['coord_sys'] = CoordSystems()

        # TODO parse orbit params in orbit_dict

        for attr in orbit_dict:  # initialize other key attrs to None
            setattr(o_s, f'_{attr}', orbit_dict[attr])

        return o_s


class Spacecraft(HardwareItem):
    class SpacecraftHardware:
        """
        Container for a Spacecraft's hardware objects.
        """

        class PropList:
            def __init__(self, name: str):
                self.name = name
                self.Chemical = []
                self.Electric = []

            def __repr__(self):
                return (f'A set of Spacecraft {self.name}:'
                        f'\n- Chemical:     {self.Chemical},'
                        f'\n- Electrical:   {self.Electric}')

        def __init__(self, spacecraft: Spacecraft):
            self.spacecraft = spacecraft

            self._Tanks = self.PropList('Tanks')
            self._Thrusters = self.PropList('Thrusters')

            self._ChemicalTanks = self._Tanks.Chemical
            self._ElectricTanks = self._Tanks.Electric

            self._ChemicalThrusters = self._Thrusters.Chemical
            self._ElectricThrusters = self._Thrusters.Electric

            self.SolarPowerSystem = None
            self.NuclearPowerSystem = None

            self.Imagers = [None]

        def __repr__(self):
            return (f'{type(self).__name__} object with the following parameters:'
                    # f'\n- Spacecraft: {self.Spacecraft.GetName()},'
                    f'\n- Tanks: {self._Tanks},'
                    f'\n- Thrusters: {self._Thrusters},'
                    f'\n- SolarPowerSystem: {self.SolarPowerSystem},'
                    f'\n- NuclearPowerSystem: {self.NuclearPowerSystem},'
                    f'\n- Imagers: {self.Imagers}')

        @classmethod
        def from_dict(cls, hw: dict, sc: Spacecraft) -> Spacecraft.SpacecraftHardware:
            sc_hardware = cls(sc)

            # parse tanks
            try:
                tanks: dict = hw['Tanks']

                # parse ChemicalTanks
                try:
                    cp_tanks_list: list[dict] = tanks['Chemical']
                    cp_tanks_objs = []
                    for index, cp_tank in enumerate(cp_tanks_list):
                        cp_tanks_objs.append(ChemicalTank.from_dict(cp_tank))
                    sc_hardware.Tanks.Chemical = cp_tanks_objs
                except KeyError:
                    raise

                # parse ElectricTanks
                try:
                    ep_tanks_list: list[dict] = tanks['Electric']
                    ep_tanks_objs = []
                    for index, ep_tank in enumerate(ep_tanks_list):
                        ep_tanks_objs.append(ElectricTank.from_dict(ep_tank))
                    sc_hardware.Tanks.Electric = ep_tanks_objs
                except KeyError:
                    raise

                # sc_hardware.Tanks = {'Chemical': sc_hardware.ChemicalTanks,
                #                      'Electric': sc_hardware.ElectricTanks}

            except KeyError as ke:
                raise KeyError(f'No tanks found in Hardware dict parsing, key error: {ke}')

            # parse thrusters
            try:
                thrusters: dict = hw['Thrusters']

                # parse ChemicalThrusters
                try:
                    cp_thrusters_list: list[dict] = thrusters['Chemical']
                    cp_thruster_objs = []
                    for index, cp_thruster in enumerate(cp_thrusters_list):
                        cp_thruster_objs.append(ChemicalThruster.from_dict(cp_thruster))
                    sc_hardware.Thrusters.Chemical = cp_thruster_objs
                except KeyError:
                    raise

                # parse ElectricThrusters
                try:
                    ep_thrusters_list: list[dict] = thrusters['Electric']
                    ep_thruster_objs = []
                    for index, ep_thruster in enumerate(ep_thrusters_list):
                        ep_thruster_objs.append(ElectricThruster.from_dict(ep_thruster))
                    sc_hardware.Thrusters.Electric = ep_thruster_objs
                except KeyError:
                    raise

                # sc_hardware.Thrusters = {'Chemical': sc_hardware.ChemicalThrusters,
                #                          'Electric': sc_hardware.ElectricThrusters}

            except KeyError as ke:
                raise KeyError(f'No thrusters found in Hardware dict parsing, key error: {ke}')

            # TODO: parse SolarPowerSystem, NuclearPowerSystem, Imager

            return sc_hardware

        @property
        def Tanks(self):
            return self._Tanks

        @property
        def Thrusters(self):
            return self._Thrusters

        @property
        def ChemicalTanks(self):
            return self._Tanks.Chemical

        @property
        def ElectricTanks(self):
            return self._Tanks.Electric

        @property
        def ChemicalThrusters(self):
            return self._Thrusters.Chemical

        @property
        def ElectricThrusters(self):
            return self._Thrusters.Electric

    def __init__(self, name, **kwargs):
        super().__init__('Spacecraft', name)

        # TODO: add elements for non-Cartesian orbit states (e.g. 'SMA', 'ECC' for Kep) - get OrbitState allowed fields
        _AllowedFields = set()
        _GmatAllowedFields = ['NAIFId', 'NAIFIdReferenceFrame', 'SpiceFrameId', 'OrbitSpiceKernelName',
                              'AttitudeSpiceKernelName',
                              'SCClockSpiceKernelName', 'FrameSpiceKernelName', 'OrbitColor', 'TargetColor',
                              'Epoch', 'X', 'Y', 'Z', 'VX',
                              'VY', 'VZ', 'StateType', 'DisplayStateType', 'AnomalyType', 'CoordinateSystem',
                              'DryMass', 'DateFormat',
                              'OrbitErrorCovariance', 'ProcessNoiseModel', 'Cd', 'Cr', 'CdSigma', 'CrSigma',
                              'DragArea', 'SRPArea', 'Tanks',
                              'Thrusters', 'PowerSystem', 'ExtendedMassPropertiesModel', 'Id', 'SPADSRPFile',
                              'SPADSRPScaleFactor',
                              'SPADSRPInterpolationMethod', 'SPADSRPScaleFactorSigma', 'SPADDragFile',
                              'SPADDragScaleFactor',
                              'SPADDragInterpolationMethod', 'SPADDragScaleFactorSigma',
                              'AtmosDensityScaleFactor',
                              'AtmosDensityScaleFactorSigma', 'AddPlates', 'AddHardware', 'SolveFors',
                              'NPlateSRPEquateAreaCoefficients',
                              'ModelFile', 'ModelOffsetX', 'ModelOffsetY', 'ModelOffsetZ', 'ModelRotationX',
                              'ModelRotationY',
                              'ModelRotationZ', 'ModelScale', 'Attitude']

        # TODO: get string attr names for non-GMAT attrs
        _AllowedFields.update(_GmatAllowedFields,
                              ['Name', 'Orbit', 'Hardware'])

        self.Hardware: Spacecraft.SpacecraftHardware | None = None
        self._Tanks: Spacecraft.SpacecraftHardware.PropList | None = None
        self._Thrusters: Spacecraft.SpacecraftHardware.PropList | None = None

        self._orbit = None

        # TODO: replace below with method/loop that extracts all params from GMAT object once initialised
        self.dry_mass = self.GetField('DryMass')

    def __repr__(self):
        return f'Spacecraft with name {self.name}'

    @classmethod
    def from_dict(cls, specs_dict: dict):
        # Get spacecraft name
        try:
            name = specs_dict['Name']
        except KeyError:
            raise SyntaxError('Spacecraft name required')

        sc = cls(name)  # create an instance of the Spacecraft class

        # Get spacecraft hardware specs
        try:
            hardware = specs_dict['Hardware']
        except KeyError:
            logging.warning('No hardware parameters specified in Spacecraft dictionary - none will be built')
            hardware = {}

        hardware_obj = Spacecraft.SpacecraftHardware.from_dict(hardware, sc)
        sc.Hardware = sc.update_hardware(hardware_obj)

        # represent sc's orbit with an OrbitState, with Cartesian as the default state_type
        try:
            orbit = specs_dict['Orbit']
        except KeyError:
            logging.warning('No hardware parameters specified in Spacecraft dictionary - none will be built')
            orbit = {}

        if not orbit:  # orbit dict is empty
            sc.orbit = OrbitState()
        else:
            sc.orbit = OrbitState.from_dict(orbit)

        sc.orbit.apply_to_spacecraft(sc)

        gmat.Initialize()

        # Find and apply orbit parameters
        # TODO: move this to an Orbit class - not relevant to Hardware. Orbit will be called from Spacecraft
        # try:
        #     orbit = specs_dict['Orbit']
        # except KeyError:
        #     print('No orbit parameters specified in Spacecraft dictionary - using defaults')
        #     orbit = {}

        # print(f'orbit (in s/c.from_dict): {orbit}')

        # now that the basic spacecraft has been created, set other fields from values in specs_dict
        #  use similar flow to in SpacecraftHardware.from_dict: set, remove field, set...
        # TODO handle snake case vs CamelCase difference
        # # Start of fresh part:
        # for field in specs_dict:
        #     # print(f'Assessing field: {field}')
        #     if field not in sc._GmatAllowedFields:
        #         # print(f'{field} not found in set of GMAT allowed fields')
        #         if field not in sc._AllowedFields:
        #             print(f'{field} not found in set of class allowed fields either')
        #             raise NotImplementedError('Error handling for non-allowed fields not implemented')
        #         else:  # field not allowed by GMAT but allowed by class (further parsing needed)
        #             setattr(sc, f'_{field}', specs_dict[field])
        #     else:  # field is GMAT allowed
        #         setattr(sc, f'_{field}', specs_dict[field])
        #         sc.SetField(field, specs_dict[field])

        # sc.construct_orbit_state(orbit)

        return sc

    def update_hardware(self, hardware: SpacecraftHardware):
        self.Hardware = hardware

        # Attach thrusters and tanks to the Spacecraft
        for thruster in self.Hardware.Thrusters.Chemical:
            if not thruster:
                print(f'No chemical thrusters found, chemical thruster list is: {self.Thrusters.Chemical}')
                raise SyntaxError

            thruster.attach_to_sat(self)
            thruster.attach_to_tanks(thruster.tanks)

        for thruster in self.Hardware.Thrusters.Electric:
            if not thruster:
                print(f'No electric thrusters found, electric thruster list is: {self.Thrusters.Chemical}')
                break

            thruster.attach_to_sat(self)
            thruster.attach_to_tanks(thruster.tanks)

        for tank in self.Hardware.Tanks.Chemical:
            tank.attach_to_sat(self)

        for tank in self.Hardware.Tanks.Electric:
            tank.attach_to_sat(self)

        return self.Hardware

    def update_orbit(self, orbit: OrbitState):
        self._orbit = orbit
        pass

    def GetState(self):
        return self.gmat_obj.GetState().GetState()

    def GetKeplerianState(self):
        return self.gmat_obj.GetKeplerianState()

    @property
    def Thrusters(self):
        return self.Hardware.Thrusters

    @Thrusters.setter
    def Thrusters(self, thrusters: Spacecraft.SpacecraftHardware.PropList):
        self._Thrusters = thrusters

    @property
    def ChemicalThrusters(self):
        return self.Hardware.ChemicalThrusters

    @property
    def ElectricThrusters(self):
        return self.Hardware.ElectricThrusters

    @property
    def Tanks(self):
        return self.Hardware.Tanks

    @Tanks.setter
    def Tanks(self, tanks: Spacecraft.SpacecraftHardware.PropList):
        self._Tanks = tanks

    @property
    def ChemicalTanks(self):
        return self.Hardware.ChemicalTanks

    @property
    def ElectricTanks(self):
        return self.Hardware.ElectricTanks

    @staticmethod
    def list_convert_gmat_to_python(list_str: str) -> list:  # TODO: define return type as list[Union[str, Tank]]
        """
        Convert a GMAT-format list to a Python-format one.
        :param list_str:
        :return:
        """
        python_list = list_str[1:-1].split(',')  # remove curly braces
        return python_list

    def add_tanks(self, tanks: list[ChemicalTank | ElectricTank]):
        """
        Add a tank object to a Spacecraft's list of Tanks.

        Note: GMAT Spacecraft Tanks field takes a string containing strings for each tank, e.g.:
         "'ChemicalTank1', 'ElectricTank1'". This is handled by this method.

        :type tanks: list[ChemicalTank | ElectricTank]
        :param tanks:
        :return:
        """
        current_tanks_value: str = self.GetField('Tanks')
        current_tanks_list: list = gmat_field_string_to_list(current_tanks_value)

        # Add tanks by getting name of each tank, adding it to a list, then attaching this list to end of existing one
        tanks_to_set: list = [tank.GetName() for tank in tanks]
        current_tanks_list.extend(tanks_to_set)
        value = list_to_gmat_field_string(current_tanks_list)
        self.SetField('Tanks', value)

    def add_thrusters(self, thrusters: list[ChemicalThruster | ElectricThruster]):
        current_thrusters_value: str = self.GetField('Thrusters')
        current_thrusters_list: list = gmat_field_string_to_list(current_thrusters_value)

        # Add thrusters by getting name of each, adding it to a list, then attaching this list to end of existing one
        thrusters_to_set: list = [thruster.GetName() for thruster in thrusters]
        current_thrusters_list.extend(thrusters_to_set)
        value = list_to_gmat_field_string(current_thrusters_list)
        self.SetField('Thrusters', value)

    # TODO: replace with a complete OrbitState object created from dict, similar to SpacecraftHardware
    def construct_orbit_state(self, orbit_specs):
        if orbit_specs == {}:  # empty dict was passed
            return

        kwargs = {'sc': self.gmat_obj}

        def pull_orbit_param(p: str):
            try:
                param_value = orbit_specs[p]
                kwargs[p] = param_value
                return param_value
            except KeyError:  # key not found in orbit_specs
                logging.warning(f'Could not pull parameter {p} from orbit_specs - using default')

        def set_orbit_param(p: str, v: Union[str, int, float, bool]):
            p = class_string_to_GMAT_string(p)  # convert param name to GMAT format
            # print(f'Setting field {class_string_to_GMAT_string(param)} to value {v}')
            self.SetField(p, v)
            # except gmatpy._py311.gmat_py.APIException:
            #     raise SyntaxError('Ruh Roh')

        def validate_param(p):
            pass

        for param in orbit_specs:
            val = pull_orbit_param(param)
            validate_param(param)
            set_orbit_param(param, val)

        sc_orbit = OrbitState(**kwargs)  # TODO syntax: need to include sc arg in kwargs
        # coord_sys=self._coord_sys)


class Tank(HardwareItem):
    def __init__(self, tank_type: str, name: str):
        super().__init__(tank_type, name)
        self.tank_type = tank_type  # 'ChemicalTank' or 'ElectricTank'
        self.name = name

        self.spacecraft = None
        self.fuel_mass = self.GetField('FuelMass')

    def __repr__(self):
        return f'{self.tank_type} with name {self.name}'

    @staticmethod
    def from_dict(tank_type: str, tank_dict: dict[str, Union[str, int, float]]):
        if tank_type == 'ChemicalTank':
            tank = ChemicalTank(tank_dict['Name'])
        elif tank_type == 'ElectricTank':
            tank = ElectricTank(tank_dict['Name'])
        else:
            raise SyntaxError(f'Invalid thr_type found in Tank.from_dict: {tank_type}'
                              f"\nMust be 'ChemicalTank' or 'ElectricTank'")

        fields: list[str] = list(tank_dict.keys())
        fields.remove('Name')
        # TODO convert to thr.SetFields
        for field in fields:
            tank.SetField(field, tank_dict[field])

        return tank

    def attach_to_sat(self, sat: Spacecraft):
        self.spacecraft = sat
        self.spacecraft.add_tanks([self.gmat_obj])


class ChemicalTank(Tank):
    def __init__(self, name: str):
        super().__init__('ChemicalTank', name)

    # def __init__(self, tank: Tank):
    #     name = tank.Name
    #     sc = tank.Spacecraft
    #     self.Tank = super().__init__(name, sc, 'ChemicalTank')

    @classmethod
    def from_dict(cls, cp_tank_dict: dict):
        cp_tank = super().from_dict('ChemicalTank', cp_tank_dict)
        return cp_tank

    # def attach_to_sat(self):
    #     return super().attach_to_sat()

    # @classmethod
    # def from_dict(cls, sc: Spacecraft, tank_dict: dict, **kwargs):
    #     tank = super().from_dict(sc, 'Chemical', tank_dict)
    #     return tank


class ElectricTank(Tank):
    #     # TODO add FuelMass and other fields
    #     # self.fuel_mass = fuel_mass
    #     # self.GmatObj.SetField('FuelMass', self.fuel_mass)

    def __init__(self, name: str):
        super().__init__('ElectricTank', name)

    @classmethod
    def from_dict(cls, ep_tank_dict: dict):
        ep_tank = Tank.from_dict('ElectricTank', ep_tank_dict)
        return ep_tank


class Thruster(HardwareItem):
    def __init__(self, thruster_type: str, name: str):
        super().__init__(thruster_type, name)
        self.thruster_type = thruster_type  # 'ChemicalThruster' or 'ElectricThruster'
        self.name = name

        self.spacecraft = None
        self.tanks: list[ChemicalTank | ElectricTank] | None = None
        self._decrement_mass = self.decrement_mass

    def __repr__(self):
        return f'A {self.thruster_type} with name {self.name}'

    @staticmethod
    def from_dict(thr_type: str, thr_dict: dict[str, Union[str, int, float]]):
        if thr_type == 'ChemicalThruster':
            thr = ChemicalThruster(thr_dict['Name'])
        elif thr_type == 'ElectricThruster':
            thr = ElectricThruster(thr_dict['Name'])
        else:
            raise SyntaxError(f'Invalid thr_type found in Thruster.from_dict: {thr_type}.'
                              f"\nMust be 'ChemicalThruster' or 'ElectricThruster'")

        fields: list[str] = list(thr_dict.keys())
        fields.remove('Name')

        tanks = thr_dict['Tanks']
        thr.tanks = tanks
        fields.remove('Tanks')

        # TODO convert to thr.SetFields
        for field in fields:
            if field == 'Tanks':
                thr.SetField('Tank', thr_dict[field])
            else:
                thr.SetField(field, thr_dict[field])
            setattr(thr, field, thr_dict[field])

        return thr

    def attach_to_sat(self, sat: Spacecraft):
        self.spacecraft = sat
        self.spacecraft.add_thrusters([self.gmat_obj])

    def attach_to_tanks(self, tanks: list[ChemicalTank | ElectricTank]):
        self.gmat_obj.SetField('Tank', tanks)

    @property
    def decrement_mass(self):
        gmat_value = self.GetField('DecrementMass')
        if gmat_value == 'false':
            return False
        elif gmat_value == 'true':
            return True
        else:
            raise AttributeError(f'Could not get valid DecrementMass value from GMAT object. Value found: {gmat_value}')

    @decrement_mass.setter
    def decrement_mass(self, true_false: bool):
        if type(true_false) is not bool:
            raise SyntaxError('decrement_mass takes either True or False')

        self._decrement_mass = true_false
        self.SetField('DecrementMass', true_false)


class ChemicalThruster(Thruster):
    def __init__(self, name: str):
        super().__init__('ChemicalThruster', name)

    @classmethod
    def from_dict(cls, cp_thr_dict: dict) -> ChemicalThruster:
        cp_thr: ChemicalThruster = Thruster.from_dict('ChemicalThruster', cp_thr_dict)
        return cp_thr


class ElectricThruster(Thruster):
    def __init__(self, name: str):
        super().__init__('ElectricThruster', name)

    @classmethod
    def from_dict(cls, ep_thr_dict: dict):
        ep_thr = Thruster.from_dict('ElectricThruster', ep_thr_dict)
        return ep_thr

    @property
    def mix_ratio(self):
        return self._mix_ratio

    @mix_ratio.setter
    def mix_ratio(self, mix_ratio: list[int]):
        if all(isinstance(ratio, int) for ratio in mix_ratio):  # check that all mix_ratio elements are of type int
            # convert GMAT's Tanks field (with curly braces) to a Python list of strings
            tanks_list = [item.strip("'") for item in self.gmat_obj.GetField('Tank')[1:-1].split(', ')]
            if len(mix_ratio) != len(tanks_list):
                raise SyntaxError('Number of mix ratios provided does not equal existing number of tanks')
            else:
                if tanks_list and any(ratio == -1 for ratio in mix_ratio):  # tank(s) assigned but a -1 ratio given
                    raise SyntaxError('Cannot have -1 mix ratio if tank(s) assigned to thruster')
                else:
                    self._mix_ratio = mix_ratio
        else:
            raise SyntaxError('All elements of mix_ratio must be of type int')
