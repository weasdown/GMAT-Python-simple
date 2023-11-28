from __future__ import annotations
import sys
from io import StringIO
from typing import Union
import logging

from load_gmat import gmat

prop_types = ['Chemical', 'Electric']


class GmatObject:
    def __init__(self, obj_type: str, name: str):
        self.ObjType = obj_type
        self.Name = name
        self._gmat_obj = gmat.Construct(self.ObjType, self.Name)

    @property
    def gmat_obj(self):
        if not self._gmat_obj:
            raise Exception(f'No GMAT object found for {self.Name} of type {type(self).__name__}')
        else:
            return self._gmat_obj

    @gmat_obj.setter
    def gmat_obj(self, gmat_obj):
        self._gmat_obj = gmat_obj

    @property
    def gmatName(self):
        return self.gmat_obj.GetName()

    @staticmethod
    def get_name_from_kwargs(obj_type: object, kwargs: dict) -> str:
        try:
            name: str = kwargs['name']
        except KeyError:
            raise SyntaxError(f"Required field 'name' not provided when building {type(obj_type).__name__} object")
        return name

    def GetName(self):
        return self.gmatName

    def Help(self):
        if not self.gmat_obj:
            raise AttributeError(f'No GMAT object found for object {self.__name__} of type {type(self.__name__)}')
        self.gmat_obj.Help()

    def SetField(self, field: str, val: Union[str, int, bool]):
        """
        Set a field in the Object's GMAT model.

        :param field:
        :param val:
        :return:
        """
        self.gmat_obj.SetField(field, val)

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
        return self.gmat_obj.GetField(field)


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
        #         # gmat_fieldName = f'{.replace("_","")}'
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
    def __init__(self, object_type: str, name: str):
        super().__init__(object_type, name)

    def __repr__(self):
        return f'A piece of Hardware of type {self.ObjType} and name {self.Name}'

    # @property
    # def Name(self) -> str:
    #     return self.Name
    #
    # @Name.setter
    # def Name(self, name: str):
    #     self.Name = name

    def IsInitialized(self):
        self.GmatObj.IsInitialized()


class SpacecraftHardware:
    """
    Container for a Spacecraft's hardware objects.
    """

    def __init__(self, spacecraft: Spacecraft):
        self.spacecraft = spacecraft

        self.ChemicalTanks = [None]
        self.ElectricTanks = [None]
        self.Tanks = {'Chemical': self.ChemicalTanks,
                      'Electric': self.ElectricTanks}

        self.ChemicalThrusters = [None]
        self.ElectricThrusters = [None]
        self.Thrusters = {'Chemical': self.ChemicalThrusters,
                          'Electric': self.ElectricThrusters}

        self.SolarPowerSystem = None
        self.NuclearPowerSystem = None

        self.Imagers = [None]

        # self.from_dict(hardware)

    def __repr__(self):
        return (f'{type(self).__name__} object with the following parameters:'
                # f'\n- Spacecraft: {self.Spacecraft.GetName()},'
                f'\n- Tanks: {self.Tanks},'
                f'\n- Thrusters: {self.Thrusters},'
                f'\n- SolarPowerSystem: {self.SolarPowerSystem},'
                f'\n- NuclearPowerSystem: {self.NuclearPowerSystem},'
                f'\n- Imagers: {self.Imagers}')

    @classmethod
    def from_dict(cls, hw: dict, sc: Spacecraft):
        sc_hardware = cls(sc)

        # parse thrusters
        try:
            thrusters: dict = hw['Thrusters']

            # parse ChemicalThrusters
            try:
                chem_thrusters_list: list[dict] = thrusters['Chemical']
                cp_thruster_objs = []
                for index, cp_thruster in enumerate(chem_thrusters_list):
                    cp_thruster_objs.append(ChemicalThruster.from_dict(cp_thruster))
                sc_hardware.ChemicalThrusters = cp_thruster_objs

            except KeyError:
                print('No chemical thrusters found in Hardware dict parsing')

            # parse ElectricThrusters
            try:
                elec_thrusters_list: list[dict] = thrusters['Electric']
                elec_thruster_objs = []
                for index, ep_thruster in enumerate(elec_thrusters_list):
                    elec_thruster_objs.append(ElectricThruster.from_dict(ep_thruster))
                sc_hardware.ElectricThrusters = elec_thruster_objs

            except KeyError:
                print('No electric thrusters found in Hardware dict parsing')

            sc_hardware.Thrusters = {'Chemical': sc_hardware.ChemicalThrusters,
                                     'Electric': sc_hardware.ElectricThrusters}

        except KeyError:
            print('No thrusters found in Hardware dict parsing')

        # parse tanks
        try:
            tanks: dict = hw['Tanks']

            # parse ChemicalTanks
            try:
                cp_tanks_list: list[dict] = tanks['Chemical']
                print(f'CP tanks in schw.from_dict: {cp_tanks_list}')
                cp_tanks_objs = []
                for index, cp_tank in enumerate(cp_tanks_list):
                    cp_tanks_objs.append(ChemicalTank.from_dict(sc_hardware.spacecraft, cp_tank))
                sc_hardware.ChemicalTanks = cp_tanks_objs
                print(sc_hardware.ChemicalTanks)
            except KeyError:
                print('No chemical tanks found in Hardware dict parsing')

            # parse ElectricTanks
            try:
                ep_tanks_list: list[dict] = tanks['Electric']
                ep_tanks_objs = []
                for index, ep_tank in enumerate(ep_tanks_list):
                    ep_tank_obj = ElectricTank.from_dict(sc_hardware.spacecraft, ep_tank)
                    ep_tanks_objs.append(ep_tank_obj)
                sc_hardware.ElectricTanks = ep_tanks_objs
            except KeyError:
                print('No electric tanks found in Hardware dict parsing')

            sc_hardware.Tanks = {'Chemical': sc_hardware.ChemicalTanks,
                                 'Electric': sc_hardware.ElectricTanks}

        except KeyError:
            print('No tanks found in Hardware dict parsing')

        # TODO: parse SolarPowerSystem, NuclearPowerSystem, Imager

        return sc_hardware

    # @property
    # def Thrusters(self):
    #     return self.Thrusters
    #
    # @Thrusters.setter
    # def Thrusters(self, thrusters):
    #     self.Thrusters = thrusters

    # @property
    # def Thrusters(self) -> list:  # TODO: specify return type is list of ChemicalThrusters/ElectricThrusters
    #     """Return SpacecraftHardware's list of Thrusters"""
    #     return list(thruster.__name__ for thruster in self.Thrusters)
    #
    # @Thrusters.setter
    # def Thrusters(self, value):
    #     self.Thrusters = value


class Spacecraft(HardwareItem):
    def __init__(self, **kwargs):
        # self.Help()

        # TODO: add elements for other orbit states (e.g. 'SMA', 'ECC' for Keplerian) - get OrbitState allowed fields
        try:
            name = kwargs['Name']
        except KeyError:
            raise SyntaxError('Name is a required field to build a Spacecraft')

        _AllowedFields = set()
        # TODO: add fields for non-Cartesian orbit states
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

        self.Hardware = None
        self.Tanks = None
        self.Thrusters = None

        super().__init__('Spacecraft', name)

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
        #             tName = thruster['Name']
        #             prop_type = thruster['PropType']
        #         except KeyError:
        #             raise SyntaxError("Thruster name ('Name') and propulsion type ('PropType') are required fields")
        #
        #         if prop_type == 'Chemical':
        #             thruster = ChemicalThruster(name=tName, sc=self, tank=tank)
        #         elif prop_type == 'Electrical':
        #             thruster = ElectricThruster(name=tName, sc=self, tank=tank)
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

        # self.GmatObj = gmat.Construct("Spacecraft", specs['name'])

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

        # self.Help()

        # print(self.Thrusters)
        # gmat.ShowObjects()
        # gmat.Help("ChemicalThruster1")
        # gmat.Help("ElectricThruster1")
        gmat.Initialize()

        # self.update_attrs()
        # TODO: replace below with method/loop that extracts all params from GMAT object once initialised
        dry_mass = self.GetField('DryMass')
        self.DryMass = dry_mass

    @classmethod
    def from_dict(cls, specs_dict):
        # TODO remove comment when able
        # See https://stackoverflow.com/questions/12179271/meaning-of-classmethod-and-staticmethod-for-beginner
        # Parse in gmat_init, orbit, hardware from specs_dict

        # TODO: convert all keys to [agreed text case (snake or camel?)]

        # Get spacecraft name
        try:
            name = specs_dict['Name']
        except KeyError:
            raise SyntaxError('Spacecraft name required')

        sc = cls(Name=name)

        # Get spacecraft hardware list
        try:
            hardware = specs_dict['Hardware']
        except KeyError:
            print('No hardware parameters specified in Spacecraft dictionary - none will be built')
            hardware = {}

        hardware_obj = SpacecraftHardware.from_dict(hardware, sc)
        sc.add_hardware(hardware_obj)

        # sc.Help()

        gmat.Initialize()

        # try:
        #     hardware = kwargs['Hardware']
        # except KeyError:
        #     print('No Hardware specified for Spacecraft creation')
        #     hardware = None
        #
        # self.Hardware = hardware
        # print(f'self.Hardware.Tanks: {self.Hardware.Tanks}')
        #
        # prop_types = ['Chemical', 'Electric']
        # for prop_type in prop_types:
        #     try:
        #         for tank in self.Hardware.Tanks[prop_type]:
        #             print(f'Tank: {tank}, of type {type(tank).__name__}')
        #             # tank.attach_to_sat()
        #             self.add_tank(tank)
        #
        #     except TypeError as e:
        #         if e.args[0] == "'NoneType' object is not iterable":
        #             if self.Thrusters:
        #                 raise SyntaxError(f'No {prop_type} tanks found in self.Hardware but thrusters were found')
        #         else:
        #             raise

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
        # TODO: move this to an Orbit class - not relevant to Hardware. Orbit will be called from Spacecraft
        # try:
        #     orbit = specs_dict['Orbit']
        # except KeyError:
        #     print('No orbit parameters specified in Spacecraft dictionary - using defaults')
        #     orbit = {}

        # print(f'orbit (in s/c.from_dict): {orbit}')

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

        # sc.construct_orbit_state(orbit)

        return sc

    def __repr__(self):
        return f'Spacecraft with name {self.Name}'

    def __str__(self):
        return f'Spacecraft with name {self.Name}'

    def add_hardware(self, hardware: SpacecraftHardware):
        self.Hardware = hardware
        print(f'hardware in Spacecraft.add_hardware: {hardware}')

        self.Thrusters: dict[str, list[ChemicalThruster | ElectricThruster | None]] = self.Hardware.Thrusters
        self.Tanks: dict[str, list[ChemicalTank | ElectricTank | None]] = self.Hardware.Tanks

        # Attach thrusters and tanks to the Spacecraft
        cp_thrusters_list: list = self.Thrusters['Chemical']
        for thruster in cp_thrusters_list:
            thruster.attach_to_sat(self)

        ep_thrusters_list: list = self.Thrusters['Electric']
        for thruster in ep_thrusters_list:
            thruster.attach_to_sat(self)

        cp_tanks_list: list = self.Tanks['Chemical']
        for tank in cp_tanks_list:
            tank.attach_to_sat(self)

        ep_tanks_list: list = self.Tanks['Electric']
        for tank in ep_tanks_list:
            tank.attach_to_sat(self)

    @staticmethod
    def list_convert_gmat_to_python(list_str: str) -> list:  # TODO: define return type as list[Union[str, Tank]]
        """
        Convert a GMAT-format list to a Python-format one.
        :param list_str:
        :return:
        """
        python_list = list_str[1:-1].split(',')  # remove curly braces
        return python_list

    # @property
    # def Thrusters(self) -> list:  # TODO: specify return type is list of ChemicalThrusters/ElectricThrusters
    #     """Return Spacecraft's list of Thrusters"""
    #     return self.Hardware.Thrusters
    #
    # @property
    # def Tanks(self) -> list:  # TODO: specify return type is list of ChemicalTanks/ElectricTanks
    #     """Return Spacecraft's list of Tanks"""
    #     return self.Hardware.Tanks
    #
    # @Tanks.setter
    # def Tanks(self, tanks):
    #     self.Tanks = tanks

    # def AddThruster(self, thruster):  # TODO: specify thruster type (ChemicalThruster/ElectricThruster)
    #     self.Hardware.Thrusters.append(thruster.Name)
    #     self.Hardware['Thrusters'] = self._Thrusters
    #     thruster.attach_to_sat()

    # @property
    # def dry_mass(self):
    #     """Return Spacecraft's dry mass"""
    #     return self._dry_mass
    #
    # @dry_mass.setter
    # def dry_mass(self, value):
    #     self._dry_mass = value
    #     self.SetField('DryMass', value)

    def add_tank(self, tank: ChemicalTank | ElectricTank):
        raise NotImplementedError
        existing_tanks = self.GetField('Tanks')
        # self.sc.gmat_object.SetField('Tanks', self.Name)

    def construct_tanks(self, tanks_dict: dict):
        for index, tank in enumerate(tanks_dict):
            fuel_mass = tank['FuelMass']
            if fuel_mass or fuel_mass == 0:
                # TODO error catch: handle case of no tank name provided
                self.Tanks.append(ElectricTank(tank['name'], self, fuel_mass))
            else:
                self.Tanks.append(ElectricTank(tank['name'], self))

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


class Tank(HardwareItem):
    def __init__(self, name: str, sc: Spacecraft, gmat_tank_type: str):
        print(name, sc, gmat_tank_type)
        super().__init__(gmat_tank_type, name)

        self.name = name
        self.Spacecraft = sc

        if gmat_tank_type not in ['ChemicalTank', 'ElectricTank']:
            raise SyntaxError(f'Invalid tank type given - {gmat_tank_type}')
        else:
            self.tank_type = gmat_tank_type

        self.prop_tank = self.gmat_object
        self.Spacecraft = sc
        self.fuel_mass = 0

    def __repr__(self):
        return f'A Tank of type {type(self.prop_tank).__name__} with name {self.Name}'

    @classmethod
    def from_dict(cls, sc: Spacecraft, prop_type: str, tank_dict: dict):
        try:
            name: str = tank_dict['Name']
        except KeyError:
            raise SyntaxError('Required field Name not found for building Tank')

        if prop_type == 'Chemical':
            tank_type = 'ChemicalTank'
        elif prop_type == 'Electric':
            tank_type = 'ElectricTank'
        else:
            raise SyntaxError(f'Invalid propulsion type found while building Tank: {prop_type}')

        print('Almost at end of Tank classmethod')
        tank = cls(name, sc, tank_type)
        return tank

    def attach_to_sat(self):
        sat = self.Spacecraft
        sat.SetField('Tanks', self.Name)

    def attach_to_tanks(self, tanks: list[str]):
        # TODO complete
        # convert Python list to GMAT list (convert to string and remove square brackets)
        tanks = str(tanks)[1:-1]

        # self.GmatObj.SetField('Tank', tanks)
        raise NotImplementedError


class ChemicalTank(Tank):
    def __init__(self, tank: Tank):
        name = tank.Name
        sc = tank.Spacecraft
        self.Tank = super().__init__(name, sc, 'ChemicalTank')

    @classmethod
    def from_dict(cls, sc: Spacecraft, tank_dict: dict, **kwargs):
        tank = super().from_dict(sc, 'Chemical', tank_dict)
        print(tank)
        return tank

    def attach_to_sat(self):
        return super().attach_to_sat()

    # @classmethod
    # def from_dict(cls, sc: Spacecraft, tank_dict: dict, **kwargs):
    #     tank = super().from_dict(sc, 'Chemical', tank_dict)
    #     return tank


class ElectricTank(Tank):
    def __init__(self, tank: Tank):
        name = tank.Name
        sc = tank.Spacecraft
        self.Tank = super().__init__(name, sc, 'ElectricTank')

        # TODO add FuelMass and other fields
        # self.fuel_mass = fuel_mass
        # self.GmatObj.SetField('FuelMass', self.fuel_mass)
        self.attach_to_sat()

    def __repr__(self):
        return f'An ElectricTank with name {self.Name} and fuel {self.fuel_mass}'

    def attach_to_sat(self):
        self.Spacecraft.add_tank(self)
        # self.sc.gmat_object.SetField('Tanks', self.Name)

    @classmethod
    def from_dict(cls, sc: Spacecraft, tank_dict: dict, **kwargs):
        return super(ElectricTank, cls).from_dict(sc, 'Electric', tank_dict)


class Thruster(HardwareItem):
    # def __init__(self, name: str, thruster_type: str, **kwargs):
    #     self.Spacecraft = None
    #     self.thruster_type = thruster_type
    #
    #     super().__init__(thruster_type, name)
    #     self.name = self.GmatObj.GetName()
    #
    #     try:
    #         self.thrust = kwargs['thrust']
    #     except KeyError:
    #         pass

    def __init__(self, thruster_type: str, name: str):
        self.thruster_type = thruster_type  # 'ChemicalThruster' or 'ElectricThruster'
        self.name = name
        super().__init__(self.thruster_type, self.name)

    # @classmethod
    # def from_dict(cls, prop_type: str, thruster_dict: dict, sc: Spacecraft = None, tanks: list['str'] = None) \
    #         -> ChemicalThruster | ElectricThruster:
    #
    #     try:
    #         name: str = thruster_dict['Name']
    #     except KeyError:
    #         raise SyntaxError('Required field Name not found for building Thruster')
    #
    #     if prop_type == 'Chemical':
    #         thruster = ChemicalThruster(name, tanks)
    #         thruster.prop_type = prop_type
    #     elif prop_type == 'Electric':
    #         thruster = ElectricThruster(name, tanks)
    #         thruster.prop_type = prop_type
    #     else:
    #         raise SyntaxError(f'Invalid propulsion type found while building Thruster: {prop_type}')
    #
    #     if sc:
    #         Thruster.attach_to_sat(sc, name)
    #
    #     return thruster

    @staticmethod
    def from_dict(th_dict: dict[str, Union[str, int, float]]):
        # TODO parse th_dict for fields
        name = th_dict['Name']
        print(f'name in api.Thruster.from_dict: {name}')
        # f'\nthr_type: {thr_type}')
        # try:
        #     thr = cls(thr_type, name)
        # except AttributeError:
        #     if thr_type == 'Chemical':
        #         raise SyntaxError(f"thr_type given as 'Chemical' - did you mean 'ChemicalThruster'?")
        #     elif thr_type == 'Electric':
        #         raise SyntaxError(f"thr_type given as 'Electric' - did you mean 'ElectricThruster'?")
        #     else:
        #         raise

        return name

    def attach_to_sat(self, sc: Spacecraft):
        # TODO feature: convert to append to existing Thrusters list
        sc.SetField('Tanks', self.Name)

    def attach_to_tanks(self, tanks: list[str]):
        # raise NotImplementedError
        # convert Python list to GMAT list (convert to string and remove square brackets)
        tanks = str(tanks)[1:-1]

        self.GmatObj.SetField('Tank', tanks)


class ChemicalThruster(Thruster):
    def __init__(self, name: str, tanks: list[str], decrement_mass: bool = True):
        super().__init__(name, 'ChemicalThruster')
        self.Name = self.GmatObj.GetName()
        # self._Spacecraft = sc
        self._Tanks = tanks
        self._DecrementMass = decrement_mass

        # Attach the thruster to the specified satellite and tanks
        # self.attach_to_sat(self._Spacecraft)
        self.attach_to_tanks(self._Tanks)

        self.GmatObj.SetField('DecrementMass', self._DecrementMass)
        # self._mix_ratio = [-1]

    # def __repr__(self):
    #     return f'A ChemicalThruster with name {self.Name}'

    def __repr__(self):
        return f'A ChemicalThruster with name {self.Name}'

    @classmethod
    def from_dict(cls, cp_th_specs, **kwargs):
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

        print('In ChemThruster.from_dict, directly before cls() call')
        chem_thruster = cls(name=name, tanks=tanks)

        # TODO: pull out optional fields (Thrust, DecrementMass, etc - full ElectricThruster set)
        #  then do chem_thruster.SetFields(...)

        return chem_thruster

    def attach_to_tanks(self, tanks: list[str]):
        # convert Python list to GMAT list (convert to string and remove square brackets)
        tanks = str(tanks)[1:-1]

        self.GmatObj.SetField('Tank', tanks)


class ElectricThruster(Thruster):  # TODO make this a child of a new class, Thruster, that inherits from Hardware
    # def __init__(self, name: str, tanks: list[str], decrement_mass: bool = True):
    #     super().__init__('ElectricThruster', name)
    #     self._tank = tanks
    #     self._decrement_mass = decrement_mass
    #
    #     # self.attach_to_sat(sc)
    #     self.attach_to_tanks(tanks)
    #
    #     self.GmatObj.SetField('DecrementMass', self._decrement_mass)

    def __init__(self, name: str):
        super().__init__('ElectricThruster', name)

    def __repr__(self):
        return (f'An {type(self).__name__} with:'
                f'\n- name: {self.name},'
                f'\n- thruster type: {self.thruster_type},'
                f'\n- GMAT object: {self.gmat_obj}')

    @classmethod
    def from_dict(cls, ep_th_dict: dict[str, Union[str, int, float]]):
        # TODO move to Thruster, then use super() here

        ep_thr = cls(ep_th_dict['Name'])

        fields: list[str] = list(ep_th_dict.keys())
        fields.remove('Name')

        # TODO convert to thr.SetFields
        for field in fields:
            ep_thr.SetField(field, ep_th_dict[field])

        return ep_thr

    # def __repr__(self):
    #     return f'An ElectricThruster with name {self.Name}'

    # @classmethod
    # def from_dict(cls, ep_th_specs):
    #     """
    #     Generate an ElectricThruster from a dictionary.
    #     :param ep_th_specs:
    #     :return:
    #     """
    #
    #     try:
    #         name: str = ep_th_specs['Name']
    #         # sc: Spacecraft = ep_th_specs['Spacecraft']
    #         tanks: str | list = ep_th_specs['Tanks']
    #
    #     except KeyError as e:
    #         raise SyntaxError(f'Required field {e} was not provided for building Electric Thruster')
    #
    #     if isinstance(tanks, str):  # ensure a list of tanks is always provided
    #         tanks = list(tanks.split(','))
    #
    #     ep_thruster = cls(name, tanks)
    #
    #     # TODO: pull out optional fields (Thrust, DecrementMass, etc - full ElectricThruster set)
    #     #  then do chem_thruster.SetFields(...)
    #
    #     return ep_thruster

    # def attach_to_tanks(self, tanks: list[str]):
    #     # convert Python list to GMAT list (convert to string and remove square brackets)
    #     tanks = str(tanks)[1:-1]
    #
    #     self.GmatObj.SetField('Tank', tanks)
    #
    # def attach_to_sat(self, sat: Spacecraft):
    #     # TODO feature: convert to append to existing Thrusters list
    #     sat.SetField('Thrusters', self.Name)

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


class FiniteBurn(GmatObject):
    def __init__(self, name, sc_to_manoeuvre: Spacecraft, thruster: ElectricThruster):
        # TODO generic: convert thruster type to Thruster once class created
        super().__init__()
        self.Name = name
        self.GmatObj = gmat.Construct('FiniteBurn', self.Name)
        self.GmatObj.SetSolarSystem(gmat.GetSolarSystem())
        self._sc_to_manoeuvre = sc_to_manoeuvre
        self.GmatObj.SetSpacecraftToManeuver(sc_to_manoeuvre.gmat_object)
        self._thruster = thruster
        self._thrusterName = thruster.GetName()
        self.GmatObj.SetField('Thrusters', self._thrusterName)

    def BeginFiniteBurn(self, fin_thrust):  # TODO type: add FiniteThrust type to fin_thrust
        fin_thrust.EnableThrust()
        sc = 'GMAT object that FiniteBurn is applied to'  # TODO complete by pulling ref obj
        runtime_thruster = sc.GmatObject.GetRefObject(gmat.THRUSTER, self._thrusterName)
        runtime_thruster.SetField("IsFiring", True)


class FiniteThrust(GmatObject):  # TODO tidy: consider making subclass of FiniteBurn
    def __init__(self, name: str, spacecraft: Spacecraft, finite_burn: FiniteBurn):
        super().__init__()
        self.Name = name
        self.GmatObj = gmat.FiniteThrust(name)
        self._spacecraft = spacecraft
        self._finite_burn = finite_burn
        self.GmatObj.SetRefObjectName(gmat.SPACECRAFT, spacecraft.GetName())
        self.GmatObj.SetReference(finite_burn.gmat_object)

    # TODO sense: create BeginFiniteBurn method in FiniteBurn that does this and other steps needed to enable thrust
    def EnableThrust(self):
        gmat.ConfigManager.Instance().AddPhysicalModel(self.GmatObj)


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

        oName_string = o.__name__
        print(f'oName_string: {oName_string}')
        temp = gmat.Construct(oName_string, '')
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
