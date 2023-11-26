from __future__ import annotations
import sys
from io import StringIO
from typing import Union
import inspect
import logging

from load_gmat import gmat


class GmatObject:
    def __init__(self):
        self._GmatObj = None
        self._Name = None

    @property
    def gmat_object(self):
        if not self._GmatObj:
            raise Exception(f'No GMAT object found for {self._Name} of type {type(self).__name__}')
        else:
            return self._GmatObj

    @property
    def gmat_name(self):
        return self._GmatObj.GetName()

    def GetName(self):
        return self.gmat_name

    def Help(self):
        if not self._GmatObj:
            raise AttributeError(f'No GMAT object found for object {self.__name__} of type {type(self.__name__)}')
        self._GmatObj.Help()

    def SetField(self, field: str, val: Union[str, int, bool]):
        """
        Set a field in the Object's GMAT model.

        :param field:
        :param val:
        :return:
        """
        self.gmat_object.SetField(field, val)

    def SetFields(self, fields_to_set: dict):
        """
        Set a list of fields in the Object's GMAT model.

        :param fields_to_set:
        :return:
        """
        if not fields_to_set:
            raise SyntaxError('fields_to_set must not be empty')
        specs = fields_to_set.items()
        fields, values = zip(*specs)  # make lists of fields and values from the specs_to_set dict
        for index, _ in enumerate(specs):
            self.SetField(fields[index], values[index])

    def GetField(self, field: str) -> str:
        """
        Get the value of a field in the Object's GMAT model.

        :param field:
        :return:
        """
        return self.gmat_object.GetField(field)


class OrbitState:
    def __init__(self, **kwargs):
        self._allowed_values = {'display_state_type': ['Cartesian', 'Keplerian', 'ModifiedKeplerian', 'SphericalAZFPA',
                                                       'SphericalRADEC', 'Equinoctial'],
                                'coord_sys': ['EarthMJ2000Eq', ],  # TODO: define valid coord_sys values
                                # TODO: define valid state_type values - using display_state_type ones for now
                                'state_type': ['Cartesian', 'Keplerian', 'ModifiedKeplerian', 'SphericalAZFPA',
                                               'SphericalRADEC', 'Equinoctial'],
                                }
        self._elements_cartesian = ['X', 'Y', 'Z', 'VX', 'VY', 'VZ']
        self._elements_keplerian = ['SMA', 'ECC', 'INC', 'RAAN', 'AOP', 'TA']

        self._key_params = ['_epoch', '_state_type', '_display_state_type', '_coord_sys']

        # Set initial default None values for all fundamental attributes
        self._display_state_type = None
        self._state_type = None
        self._coord_sys = None
        self._epoch = None

        # Set whether to use explicit defaults or let GMAT choose.
        # Latter risks clashing between specified parameters
        explicit_defaults = True

        # TODO convert these to try-excepts
        if 'display_state_type' in kwargs:
            if kwargs['display_state_type'] not in self._allowed_values['display_state_type']:
                raise SyntaxError(f'Invalid display state type passed to OrbitState __init__. '
                                  f'Allowed values are: {self._allowed_values["display_state_type"]}')
            else:
                self._display_state_type = kwargs['display_state_type']
        elif explicit_defaults:
            self._display_state_type = 'Cartesian'

        if 'epoch' in kwargs:
            # TODO add epoch validation e.g. str if Cartesian, correct date format
            self._epoch = str(kwargs['epoch'])  # Should this always be str, or only for Cartesian states?
        elif explicit_defaults:
            self._epoch = None

        if 'state_type' in kwargs:
            if kwargs['state_type'] not in self._allowed_values['state_type']:
                raise SyntaxError(f'Invalid state type passed to OrbitState __init__. '
                                  f'Allowed values are: {self._allowed_values["state_type"]}')
            else:
                self._state_type = kwargs['state_type']
        elif explicit_defaults:
            self._state_type = 'Cartesian'

        if 'coord_sys' in kwargs:
            coord_sys = kwargs['coord_sys']
            if coord_sys not in self._allowed_values['coord_sys']:
                raise SyntaxError(f'Invalid coordinate system passed to OrbitState __init__: {coord_sys}. '
                                  f'Allowed values are: {self._allowed_values["coord_sys"]}')
            else:
                self._coord_sys = kwargs['coord_sys']
        elif explicit_defaults:
            self._coord_sys = 'EarthMJ2000Eq'

        if 'sc' in kwargs:
            self.apply_to_spacecraft(kwargs['sc'])

        # Theoretically, create GMAT's OrbitState class, but it doesn't exist...
        # Maybe CoordinateSystem is the closest? But don't same able to Construct it directly

    def apply_to_spacecraft(self, sc):
        """
        Apply the properties of this OrbitState to a spacecraft.

        :param sc:
        :return:
        """
        # print(f'Epoch being set: {self._epoch}')
        # for param in self._key_params:
        #     if param is not None:
        #         # convert param name to CamelCase without underscores, for GMAT
        #         chunks = param.split("_")[1:]
        #         print(chunks)
        #         # gmat_field_name = f'{.replace("_","")}'
        #         # sc.SetField(param, str(getattr(self, param)))

        try:
            if self._state_type == 'Cartesian':
                # Check each element in self._elements_cartesian
                # If there's an attribute for it, set it, otherwise move on to the next one

                for element in self._elements_cartesian:
                    element_string = f'_{element}'
                    try:
                        attr_value = getattr(self, element_string)
                        sc.SetField(element, attr_value)

                    except AttributeError:
                        continue

            # TODO: implement non-Cartesian states
            elif self._state_type == 'Keplerian':
                print('Keplerian state requested')
                raise NotImplementedError('Applying a Keplerian state to a spacecraft is not yet implemented')
            else:
                raise SyntaxError('State type not recognised')
        except KeyError:  # jumps to here on *first* failed state element assignment
            print('OrbitState __init__ did not receive all the correct parameters for the specified state')
            print(f'Using defaults of at least some state elements for state {self._state_type}')


class HardwareItem(GmatObject):
    def __init__(self, object_type, name: str):
        super().__init__()
        self._ObjType = object_type
        self._Name = name
        self._GmatObj = gmat.Construct(self._ObjType, self._Name)

    def __repr__(self):
        return f'A piece of Hardware of type {self._ObjType} and name {self._Name}'

    @property
    def Name(self) -> str:
        return self._Name

    @Name.setter
    def Name(self, name: str):
        self._Name = name

    def IsInitialized(self):
        self._GmatObj.IsInitialized()


class SpacecraftHardware:
    """
    Container for a Spacecraft's hardware objects.
    """
    def __init__(self, hardware: dict):
        self.ChemicalTanks = None
        self.ElectricTanks = None
        self.Tanks = {'Chemical': self.ChemicalTanks,
                      'Electric': self.ElectricTanks}

        self.ChemicalThrusters = None
        self.ElectricThrusters = None
        self.Thrusters = {'Chemical': self.ChemicalThrusters,
                          'Electric': self.ElectricThrusters}

        self.SolarPowerSystem = None
        self.NuclearPowerSystem = None

        self.Imagers = None

        self.parse_hw_dict(hardware)

    def __repr__(self):
        return (f'Object of type {type(self).__name__} with the following parameters:'
                # f'\n- Spacecraft: {self.Spacecraft.GetName()},'
                f'\n- Tanks: {self.Tanks},'
                f'\n- Thrusters: {self.Thrusters},'
                f'\n- SolarPowerSystem: {self.SolarPowerSystem},'
                f'\n- NuclearPowerSystem: {self.NuclearPowerSystem},'
                f'\n- Imagers: {self.Imagers}')

    def parse_hw_dict(self, hw: dict):
        # parse thrusters
        try:
            thrusters: dict = hw['Thrusters']
            required_fields = ['Name', 'Tank', 'DecrementMass']

            # Chemical thrusters
            try:
                chem_thrusters_list: list[dict] = thrusters['Chemical']
                cp_thruster_objs = [None] * len(chem_thrusters_list)

                for index, cp_thruster in enumerate(chem_thrusters_list):
                    # tell the thruster-to-be which Spacecraft to attach to
                    # cp_thruster['Spacecraft'] = self.Spacecraft
                    cp_thruster_objs[index] = ChemicalThruster.from_dict(cp_thruster)
                self.ChemicalThrusters = cp_thruster_objs

            except KeyError:
                print('No chemical thrusters found in Hardware dict parsing')

            # Electric Thrusters
            try:
                elec_thrusters_list: list[dict] = thrusters['Electric']
                ep_thruster_objs = [None] * len(elec_thrusters_list)

                for index, ep_thruster in enumerate(elec_thrusters_list):
                    # tell the thruster-to-be which Spacecraft to attach to
                    # ep_thruster['Spacecraft'] = self.Spacecraft
                    ep_thruster_objs[index] = ElectricThruster.from_dict(ep_thruster)
                self.ElectricThrusters = ep_thruster_objs

            except KeyError:
                print('No electric thrusters found in Hardware dict parsing')

        except KeyError:
            print('No thrusters found in Hardware dict parsing')

        self.Thrusters = {'Chemical': self.ChemicalThrusters,
                          'Electric': self.ElectricThrusters}

        # parse tanks
        try:
            tanks: dict = hw['Tanks']

            try:
                chem_tanks_list: list[dict] = tanks['Chemical']
            except KeyError:
                print('No chemical tanks found in Hardware dict parsing')

            try:
                elec_tanks_list: list[dict] = tanks['Electric']
            except KeyError:
                print('No electric tanks found in Hardware dict parsing')

        except KeyError:
            print('No tanks found in Hardware dict parsing')

        # TODO: parse SolarPowerSystem, NuclearPowerSystem, Imager

    # @property
    # def Thrusters(self) -> list:  # TODO: specify return type is list of ChemicalThrusters/ElectricThrusters
    #     """Return SpacecraftHardware's list of Thrusters"""
    #     return list(thruster.__name__ for thruster in self.Thrusters)
    #
    # @Thrusters.setter
    # def Thrusters(self, value):
    #     self.Thrusters = value

class Spacecraft(HardwareItem):
    def __init__(self, Name: str, **kwargs):  # specs: dict):
        # self.Help()

        # TODO: add elements for other orbit states (e.g. 'SMA', 'ECC' for Keplerian) - get OrbitState allowed fields
        self._AllowedFields = set()
        self._GmatAllowedFields = ['NAIFId', 'NAIFIdReferenceFrame', 'SpiceFrameId', 'OrbitSpiceKernelName',
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
        self._AllowedFields.update(self._GmatAllowedFields,
                                   ['Name', 'Orbit', 'Hardware'])

        super().__init__('Spacecraft', Name)

        self._DryMass = self.GetField('DryMass')
        # 'Thrusters': self.list_convert_gmat_to_python(self.GetField('Thrusters')),
        # 'Tanks': self.list_convert_gmat_to_python(self.GetField('Tanks'))
        # try:
        #     self._Hardware = kwargs['Hardware']
        # except KeyError:
        #     self._Hardware = {}
        #
        # try:
        #     self._Thrusters = self._Hardware['Thrusters']
        # except KeyError:
        #     self._Thrusters = {}
        #
        # try:
        #     self._Tanks = self._Hardware['Tanks']
        # except KeyError:
        #     self._Tanks = {}
        #
        # # TODO tidy: repeats Hardware
        # for field in kwargs:
        #     if field in self._GmatAllowedFields:
        #         value = kwargs[field]
        #         print(f"Setting Spacecraft's field {field} to value {value}")
        #         self.SetField(f'_{field}', value)
        #     else:
        #         if field in self._AllowedFields:
        #             print(f'Setting Spacecraft object attribute - {field}')
        #             self.__setattr__(f'_{field}', kwargs[field])
        #             print(self.__getattribute__(f'_{field}'), '\n')
        #         else:
        #             raise SyntaxError(f'Invalid field found - {field}')
        #
        # print(f'self._Thrusters: {self._Thrusters}')
        # if self._Thrusters:
        #     print(f'self._Thrusters: {self._Thrusters}')
        #     thruster_obj_list = [None] * len(self._Thrusters)
        #     thruster_obj_list = []
        #     for index, thruster in enumerate(self._Thrusters):
        #         try:
        #             t_name = thruster['Name']
        #             prop_type = thruster['PropType']
        #         except KeyError:
        #             raise SyntaxError("Thruster name ('Name') and propulsion type ('PropType') are required fields")
        #
        #         if prop_type == 'Chemical':
        #             thruster = ChemicalThruster(name=t_name, sc=self, tank=tank)
        #         elif prop_type == 'Electrical':
        #             thruster = ElectricThruster(name=t_name, sc=self, tank=tank)
        #
        #         thruster_obj_list.append(thruster)
        #         self._Thrusters = thruster_obj_list
        #     pass
        # else:
        #     print('No thrusters specified when creating Spacecraft object')
        #
        # if self._Tanks:
        #     pass

        # TODO: consider removing - hides available attrs
        # print('')
        # for key in specs:
        #     print(f'Setting attribute {key}, {specs[key]}')
        #     setattr(self, key, specs[key])  # set object attributes based on passed specs dict
        # print('')

        # self._GmatObj = gmat.Construct("Spacecraft", specs['name'])

        # Default orbit specs
        # self._epoch = '21545'
        # self._state_type = 'Cartesian'
        # self._display_state_type = 'Cartesian'
        # self._coord_sys = 'EarthMJ2000Eq'

        # Default physical properties
        # self._dry_mass = 756  # kg

        # TODO generate a list of specs to set, which will be append to self._specs_to_set then set by set_specs()
        # self._specs_to_set = {'Epoch': self._epoch,
        #                       'StateType': self._state_type,
        #                       'DisplayStateType': self._display_state_type,
        #                       'CoordinateSystem': self._coord_sys}

        # TODO: Parse other specs here, append results to self._specs_to_set then set all at end. Rely on *GMAT* (and
        #  not even our lower-level classes/methods) to supply defaults if not provided. We should still check the
        #  compatibility of the various specs provided, to avoid an incompatible set that GMAT doesn't catch.

        # self.SetFields(self._specs_to_set)  # TODO uncomment

        try:
            hardware = kwargs['Hardware']
        except KeyError:
            print('No Hardware specified for Spacecraft creation')
            hardware = None

        self.Hardware = hardware

        # gmat.ShowObjects()
        # gmat.Help("ChemicalThruster1")

        print(self.Thrusters)

        gmat.Initialize()
        # self.update_attrs()

    @classmethod
    def from_dict(cls, specs_dict):
        # TODO remove comment when able
        # See https://stackoverflow.com/questions/12179271/meaning-of-classmethod-and-staticmethod-for-beginner
        # Parse in gmat_init, orbit, hardware from specs_dict

        # TODO: convert all keys to [agreed text case (snake or camel?)]

        try:
            name = specs_dict['Name']
        except KeyError:
            raise SyntaxError('Spacecraft name required')

        # # get Spacecraft's full list of params, except self
        # fields = inspect.getfullargspec(Spacecraft.__init__).args[1:]
        # args = [None] * len(fields)
        # for index, field in enumerate(fields):
        #     try:
        #         args[index] = specs_dict[field]  # see if the param needed by Spacecraft.__init__ is in specs_dict
        #     except KeyError:
        #         print(f'Key {field} not found in the specs_dict passed to Spacecraft.from_dict')
        #         raise

        # sc = cls(*args)
        #
        # tanks_list = hardware['tanks']
        # if tanks_list:  # the specs listed tanks to be built
        #     self._tanks = []
        #     self.construct_tanks(tanks_list)
        #     # TODO: set GMAT sat Tanks field

        # Find and apply orbit parameters
        try:
            orbit = specs_dict['Orbit']
        except KeyError:
            print('No orbit parameters specified in Spacecraft dictionary - using defaults')
            orbit = {}

        try:
            hardware = specs_dict['Hardware']
        except KeyError:
            print('No hardware parameters specified in Spacecraft dictionary - none will be built')
            hardware = {}

        # now that the basic spacecraft has been created, set other fields from values in specs_dict
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
        hardware_obj = SpacecraftHardware(hardware)

        sc = cls(Name=name, Hardware=hardware_obj)

        # sc.construct_orbit_state(orbit)

        return sc

    def __repr__(self):
        return f'Spacecraft with name {self._Name}'

    def __str__(self):
        return f'Spacecraft with name {self._Name}'

    @staticmethod
    def list_convert_gmat_to_python(list_str: str) -> list:  # TODO: define return type as list[Union[str, Tank]]
        """
        Convert a GMAT-format list to a Python-format one.
        :param list_str:
        :return:
        """
        python_list = list_str[1:-1].split(',')  # remove curly braces
        return python_list

    @property
    def Thrusters(self) -> list:  # TODO: specify return type is list of ChemicalThrusters/ElectricThrusters
        """Return Spacecraft's list of Thrusters"""
        return self.Hardware.Thrusters

    # def AddThruster(self, thruster):  # TODO: specify thruster type (ChemicalThruster/ElectricThruster)
    #     self.Hardware.Thrusters.append(thruster.Name)
    #     self.Hardware['Thrusters'] = self._Thrusters
    #     thruster.attach_to_sat()

    @property
    def DryMass(self):
        """Return Spacecraft's dry mass"""
        return self._DryMass

    @DryMass.setter
    def DryMass(self, value):
        self._DryMass = value
        self.SetField('DryMass', value)

    # @property
    # def dry_mass(self):
    #     """Return Spacecraft's dry mass"""
    #     return self._dry_mass
    #
    # @dry_mass.setter
    # def dry_mass(self, value):
    #     self._dry_mass = value
    #     self.SetField('DryMass', value)

    def construct_tanks(self, tanks_dict: dict):
        for index, tank in enumerate(tanks_dict):
            fuel_mass = tank['FuelMass']
            if fuel_mass or fuel_mass == 0:
                # TODO error catch: handle case of no tank name provided
                self._Tanks.append(ElectricTank(tank['name'], self, fuel_mass))
            else:
                self._Tanks.append(ElectricTank(tank['name'], self))

    def construct_orbit_state(self, orbit_specs):
        if orbit_specs == {}:  # empty dict was passed
            return

        kwargs = {'sc': self.gmat_object}

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

    def update_attrs(self):
        raise NotImplementedError('update_attrs not implemented for Spacecraft')


class ElectricTank(HardwareItem):  # TODO make this a child of a new class, Tank, that inherits from Hardware
    def __init__(self, name, sc, fuel_mass=10):
        super().__init__('ElectricTank', name)
        self._name = self._GmatObj.GetName()
        self._sc = sc
        self._fuel_mass = fuel_mass
        self._GmatObj.SetField('FuelMass', self._fuel_mass)
        self.attach_to_sat()

    def __repr__(self):
        return f'An ElectricTank with name {self._name} and fuel {self._fuel_mass}'

    def attach_to_sat(self):
        self._sc.gmat_object.SetField('Tanks', self._name)
        pass


class ElectricThruster(HardwareItem):  # TODO make this a child of a new class, Thruster, that inherits from Hardware
    def __init__(self, name: str, tanks: list[str], decrement_mass: bool = True):
        super().__init__('ElectricThruster', name)
        self._name = self._GmatObj.GetName()
        # self._sc = sc
        self._tank = tanks
        self._decrement_mass = decrement_mass

        # self.attach_to_sat(sc)
        self.attach_to_tanks(tanks)

        self._GmatObj.SetField('DecrementMass', self._decrement_mass)
        self._mix_ratio = [-1]

    def __repr__(self):
        return f'An ElectricThruster with name {self._name}'

    @classmethod
    def from_dict(cls, ep_th_specs):
        """
        Generate an ElectricThruster from a dictionary.
        :param ep_th_specs:
        :return:
        """

        try:
            name: str = ep_th_specs['Name']
            # sc: Spacecraft = ep_th_specs['Spacecraft']
            tanks: str | list = ep_th_specs['Tanks']

        except KeyError as e:
            raise SyntaxError(f'Required field {e} was not provided for building Electric Thruster')

        if isinstance(tanks, str):  # ensure a list of tanks is always provided
            tanks = list(tanks.split(','))

        chem_thruster = cls(name, tanks)

        # TODO: pull out optional fields (Thrust, DecrementMass, etc - full ElectricThruster set)
        #  then do chem_thruster.SetFields(...)

        return chem_thruster

    def attach_to_tanks(self, tanks: list[str]):
        # convert Python list to GMAT list (convert to string and remove square brackets)
        tanks = str(tanks)[1:-1]

        self._GmatObj.SetField('Tank', tanks)

    def attach_to_sat(self, sat: Spacecraft):
        # TODO feature: convert to append to existing Thrusters list
        sat.SetField('Thrusters', self._Name)

    @property
    def mix_ratio(self):
        return self._mix_ratio

    @mix_ratio.setter
    def mix_ratio(self, mix_ratio: list[int]):
        if all(isinstance(ratio, int) for ratio in mix_ratio):  # check that all mix_ratio elements are of type int
            # convert GMAT's Tanks field (with curly braces) to a Python list of strings
            tanks_list = [item.strip("'") for item in self.gmat_object.GetField('Tank')[1:-1].split(', ')]
            if len(mix_ratio) != len(tanks_list):
                raise SyntaxError('Number of mix ratios provided does not equal existing number of tanks')
            else:
                if tanks_list and any(ratio == -1 for ratio in mix_ratio):  # tank(s) assigned but a -1 ratio given
                    raise SyntaxError('Cannot have -1 mix ratio if tank(s) assigned to thruster')
                else:
                    self._mix_ratio = mix_ratio
        else:
            raise SyntaxError('All elements of mix_ratio must be of type int')


class ChemicalTank(HardwareItem):
    pass


class ChemicalThruster(HardwareItem):
    def __init__(self, name: str, tanks: list[str], decrement_mass: bool = True):
        super().__init__('ChemicalThruster', name)
        self._Name = self._GmatObj.GetName()
        # self._Spacecraft = sc
        self._Tanks = tanks
        self._DecrementMass = decrement_mass

        # Attach the thruster to the specified satellite and tanks
        # self.attach_to_sat(self._Spacecraft)
        self.attach_to_tanks(self._Tanks)

        self._GmatObj.SetField('DecrementMass', self._DecrementMass)
        # self._mix_ratio = [-1]

    def __repr__(self):
        return f'A ChemicalThruster with name {self._Name}'

    @classmethod
    def from_dict(cls, cp_th_specs):
        """
        Generate a ChemicalThruster from a dictionary.
        :param cp_th_specs:
        :return:
        """

        try:
            name: str = cp_th_specs['Name']
            # sc: Spacecraft = cp_th_specs['Spacecraft']
            tanks: str | list = cp_th_specs['Tanks']

        except KeyError as e:
            raise SyntaxError(f'Required field {e} was not provided for building Chemical Thruster')

        if isinstance(tanks, str):  # ensure a list of tanks is always provided
            tanks = list(tanks.split(','))

        chem_thruster = cls(name=name, tanks=tanks)

        # TODO: pull out optional fields (Thrust, DecrementMass, etc - full ElectricThruster set)
        #  then do chem_thruster.SetFields(...)

        return chem_thruster

    def attach_to_tanks(self, tanks: list[str]):
        # convert Python list to GMAT list (convert to string and remove square brackets)
        tanks = str(tanks)[1:-1]

        self._GmatObj.SetField('Tank', tanks)

    def attach_to_sat(self, sat: Spacecraft):
        # TODO feature: convert to append to existing Thrusters list
        sat.SetField('Thrusters', self._Name)


class FiniteBurn(GmatObject):
    def __init__(self, name, sc_to_manoeuvre: Spacecraft, thruster: ElectricThruster):
        # TODO generic: convert thruster type to Thruster once class created
        super().__init__()
        self._name = name
        self._GmatObj = gmat.Construct('FiniteBurn', self._name)
        self._GmatObj.SetSolarSystem(gmat.GetSolarSystem())
        self._sc_to_manoeuvre = sc_to_manoeuvre
        self._GmatObj.SetSpacecraftToManeuver(sc_to_manoeuvre.gmat_object)
        self._thruster = thruster
        self._thruster_name = thruster.GetName()
        self._GmatObj.SetField('Thrusters', self._thruster_name)

    def BeginFiniteBurn(self, fin_thrust):  # TODO type: add FiniteThrust type to fin_thrust
        fin_thrust.EnableThrust()
        sc = 'GMAT object that FiniteBurn is applied to'  # TODO complete by pulling ref obj
        runtime_thruster = sc.GmatObject.GetRefObject(gmat.THRUSTER, self._thruster_name)
        runtime_thruster.SetField("IsFiring", True)


class FiniteThrust(GmatObject):  # TODO tidy: consider making subclass of FiniteBurn
    def __init__(self, name: str, spacecraft: Spacecraft, finite_burn: FiniteBurn):
        super().__init__()
        self._name = name
        self._GmatObj = gmat.FiniteThrust(name)
        self._spacecraft = spacecraft
        self._finite_burn = finite_burn
        self._GmatObj.SetRefObjectName(gmat.SPACECRAFT, spacecraft.GetName())
        self._GmatObj.SetReference(finite_burn.gmat_object)

    # TODO sense: create BeginFiniteBurn method in FiniteBurn that does this and other steps needed to enable thrust
    def EnableThrust(self):
        gmat.ConfigManager.Instance().AddPhysicalModel(self._GmatObj)


def class_string_to_GMAT_string(string):
    """
    Convert PEP8-compliant string to GMAT format (CamelCase)
    :param string:
    :return:
    """
    string_parts_list = [part.capitalize() for part in string.split('_')]
    string = ''.join(string_parts_list)
    if string == 'CoordSys':
        string = 'CoordinateSystem'
    return string


def get_subs_of_gmat_class(gmat_class) -> list:
    """
    Get GMAT's list of fields in a GMAT class

    :param gmat_class
    :return: fields: list[str]
    """
    # Target: "GmatBase Exception Thrown: Parameter id = 6 not defined on object"
    # Set: "Factory (sub)class exception: Generic factory creation method not implemented for Set"
    # CallGmatFunction, Global, CallPythonFunction: see Set
    disallowed_classes = ['CallFunction', 'Optimize', 'Propagate', 'ScriptEvent',
                          'Target',
                          'Set', 'CallGmatFunction', 'Global', 'CallPythonFunction', 'RunEstimator', 'RunSimulator',
                          'CommandEcho', 'BeginFileThrust', 'EndFileThrust', 'RunSmoother', 'ModEquinoctial',
                          'IncomingAsymptote']

    print(f'argument gmat_class: {gmat_class}')
    print(f'Subclasses of {gmat_class.__name__}:')
    subs = [ty for ty in gmat_class.__subclasses__()]

    # Save subs to a txt file
    filename = f'Subclasses of GMAT class {gmat_class.__name__}.txt'
    with open(filename, 'w') as file:
        for sub in subs:
            file.write(f'{sub}\n')

    # print('Done')
    #
    # print(f'gmat_class: {gmat_class}')
    # print(f'gmat_class type: {type(gmat_class)}')
    #
    # # Find subclasses of the gmat.GmatObject class, as they're the ones that will have user-set/gettable fields
    #
    # print(f'Parent class of current class: {type(gmat_class).__bases__}')
    #
    # sys.exit()
    #
    # # Intercept stdout as that's where gmat_obj.Help() goes to
    # old_stdout = sys.stdout  # take snapshot of current (normal) stdout
    # # create a StringIO object, assign it to obj_help_stringio and set this as the target for stdout
    # sys.stdout = obj_help_stringio = StringIO()
    # # raise NotImplementedError('Currently assuming a GMAT object rather than GMAT class')
    #
    # if gmat_class in disallowed_classes:
    #     return None
    # else:
    #     temp = gmat.Construct(gmat_class)
    #     temp.Help()
    #     gmat.Clear(temp.GetName())
    #
    # sys.stdout = old_stdout  # revert back to normal handling of stdout
    #
    # obj_help = obj_help_stringio.getvalue()  # Help() table text as a string
    #
    # rows = obj_help.split('\n')  # split the Help() text into rows for easier parsing
    # data_rows = rows[6:]  # first six rows are always headers etc. so remove them
    # fields = [''] * len(data_rows)  # create a list to store the fields
    # for index, row in enumerate(data_rows):
    #     row = row[3:]
    #     row = row.split(' ')[0]  # TODO tweak to get rid of any empty strings (also in get_gmat_classes)
    #     fields[index] = row
    #
    # fields = list(filter(None, fields))  # filter out any empty strings
    return subs


def get_gmat_classes():
    """
    Get GMAT's list of possible classes

    :return:
    """
    # Intercept stdout as that's where gmat_obj.Help() goes to
    old_stdout = sys.stdout  # take snapshot of current (normal) stdout
    # create a StringIO object, assign it to obj_help_stringio and set this as the target for stdout
    sys.stdout = classes_stringio = StringIO()
    gmat.ShowClasses()
    classes_str = classes_stringio.getvalue()  # Help() table text as a string

    sys.stdout = old_stdout  # revert back to normal handling of stdout

    rows = classes_str.split('\n')  # split the Help() text into rows for easier parsing
    data_rows = rows[:]  # first six rows are always headers etc. so remove them
    classes = [None] * len(data_rows)  # create a list to store the fields
    for index, row in enumerate(data_rows):
        row = row[3:]
        classes[index] = row

    classes = list(filter(None, classes))  # filter out any empty strings
    return classes


def fields_for_gmat_base_gmat_command():
    gmat_base_obj = type(gmat.Construct('Propagator')).__bases__[0]
    gmat_base_subs = get_subs_of_gmat_class(gmat_base_obj)
    print(gmat_base_subs)

    constructible_objects = gmat_base_subs
    non_constructible_objects = []

    for sub in gmat_base_subs:
        try:
            obj = gmat.Construct(sub.__name__)
            # obj.Help()
        except AttributeError:
            constructible_objects.remove(sub)
            non_constructible_objects.append(sub)
        except Exception:
            raise

    print(f'constructible_objects: {[o.__name__ for o in constructible_objects]}')

    for o in constructible_objects:
        # Intercept stdout as that's where gmat_obj.Help() goes to
        old_stdout = sys.stdout  # take snapshot of current (normal) stdout
        # create a StringIO object, assign it to obj_help_stringio and set this as the target for stdout

        o_name_string = o.__name__
        print(f'o_name_string: {o_name_string}')
        temp = gmat.Construct(o_name_string, '')
        print(f'Created object {temp.__name__} of type {type(temp)}')

        sys.stdout = obj_help_stringio = StringIO()
        # raise NotImplementedError('Currently assuming a GMAT object rather than GMAT class')
        temp.Help()
        gmat.Clear(temp.GetName())

        sys.stdout = old_stdout  # revert back to normal handling of stdout

        obj_help = obj_help_stringio.getvalue()  # Help() table text as a string

        rows = obj_help.split('\n')  # split the Help() text into rows for easier parsing
        data_rows = rows[6:]  # first six rows are always headers etc. so remove them
        fields = [''] * len(data_rows)  # create a list to store the fields
        for index, row in enumerate(data_rows):
            row = row[3:]
            row = row.split(' ')[0]  # TODO tweak to get rid of any empty strings (also in get_gmat_classes)
            fields[index] = row

        fields = list(filter(None, fields))  # filter out any empty strings
        # print(fields)

        # o.Help()

    # NOTE: GmatCommand is a subclass of GmatBase
    # gmat_command_obj = type(gmat.Construct('Propagate')).__bases__[0].__bases__[0]
    # gmat_command_subs = get_subs_of_gmat_class(gmat_command_obj)
    # print(gmat_command_subs)

    return

    # classes = get_gmat_classes()
    # classes_without_fields = []
    #
    # for gmat_class in classes:
    #     try:
    #         class_fields = get_subs_of_gmat_class(gmat_class)
    #
    #     except Exception:  # TODO add GMAT exception type
    #         classes_without_fields.append(gmat_class)

    # generate text files - one per class, each with list of classes, called [class]_fields.txt

    # generate text file of classes_without_fields

    pass
