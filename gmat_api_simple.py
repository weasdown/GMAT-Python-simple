from __future__ import annotations
import sys
from io import StringIO
from typing import Union
import logging

from load_gmat import gmat

prop_types = ['Chemical', 'Electric']


class GmatObject:
    def __init__(self, obj_type: str, name: str):
        self.obj_type = obj_type
        self.name = name
        self.gmat_obj = gmat.Construct(self.obj_type, self.name)

    # @property
    # def gmat_obj(self):
    #     if not self._gmat_obj:
    #         raise Exception(f'No GMAT object found for {self.name} of type {type(self).__name__}')
    #     else:
    #         return self._gmat_obj

    # @gmat_obj.setter
    # def gmat_obj(self, gmat_obj):
    #     self._gmat_obj = gmat_obj

    @staticmethod
    def get_name_from_kwargs(obj_type: object, kwargs: dict) -> str:
        try:
            name: str = kwargs['name']
        except KeyError:
            raise SyntaxError(f"Required field 'name' not provided when building {type(obj_type).__name__} object")
        return name

    def GetName(self):
        return self.gmat_obj.GetName()

    def Help(self):
        if not self.gmat_obj:
            raise AttributeError(f'No GMAT object found for object {self.__name__} of type {type(self.__name__)}')
        self.gmat_obj.Help()

    def SetField(self, field: str, val: Union[str, int, bool, list]):
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
    def __init__(self, obj_type: str, name: str):
        super().__init__(obj_type, name)

        self.hwstring = 'Test'

    def __repr__(self):
        return f'A piece of Hardware of type {self.obj_type} and name {self.name}'

    # @property
    # def Name(self) -> str:
    #     return self.Name
    #
    # @Name.setter
    # def Name(self, name: str):
    #     self.Name = name

    def IsInitialized(self):
        self.gmat_obj.IsInitialized()


class Spacecraft(HardwareItem):
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

            # parse tanks
            try:
                tanks: dict = hw['Tanks']

                # parse ChemicalTanks
                try:
                    cp_tanks_list: list[dict] = tanks['Chemical']
                    cp_tanks_objs = []
                    for index, cp_tank in enumerate(cp_tanks_list):
                        cp_tanks_objs.append(ChemicalTank.from_dict(cp_tank))
                    sc_hardware.ChemicalTanks = cp_tanks_objs
                except KeyError:
                    raise

                # parse ElectricTanks
                try:
                    ep_tanks_list: list[dict] = tanks['Electric']
                    ep_tanks_objs = []
                    for index, ep_tank in enumerate(ep_tanks_list):
                        ep_tanks_objs.append(ElectricTank.from_dict(ep_tank))
                    sc_hardware.ElectricTanks = ep_tanks_objs
                except KeyError:
                    raise

                sc_hardware.Tanks = {'Chemical': sc_hardware.ChemicalTanks,
                                     'Electric': sc_hardware.ElectricTanks}

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
                    sc_hardware.ChemicalThrusters = cp_thruster_objs
                except KeyError:
                    raise

                # parse ElectricThrusters
                try:
                    ep_thrusters_list: list[dict] = thrusters['Electric']
                    ep_thruster_objs = []
                    for index, ep_thruster in enumerate(ep_thrusters_list):
                        ep_thruster_objs.append(ElectricThruster.from_dict(ep_thruster))
                    sc_hardware.ElectricThrusters = ep_thruster_objs
                except KeyError:
                    raise

                sc_hardware.Thrusters = {'Chemical': sc_hardware.ChemicalThrusters,
                                         'Electric': sc_hardware.ElectricThrusters}

            except KeyError as ke:
                raise KeyError(f'No thrusters found in Hardware dict parsing, key error: {ke}')

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

        self.Hardware = None
        self.Tanks = None
        self.Thrusters = None

        # TODO: replace below with method/loop that extracts all params from GMAT object once initialised
        self.dry_mass = self.GetField('DryMass')

    @classmethod
    def from_dict(cls, specs_dict):
        # Get spacecraft name
        try:
            name = specs_dict['Name']
        except KeyError:
            raise SyntaxError('Spacecraft name required')

        sc = cls(name)

        # Get spacecraft hardware specs
        try:
            hardware = specs_dict['Hardware']
        except KeyError:
            print('No hardware parameters specified in Spacecraft dictionary - none will be built')
            hardware = {}

        hardware_obj = Spacecraft.SpacecraftHardware.from_dict(hardware, sc)
        sc.Hardware = sc.add_hardware(hardware_obj)

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

    def __repr__(self):
        return f'Spacecraft with name {self.name}'

    def add_hardware(self, hardware: SpacecraftHardware):
        self.Hardware = hardware

        self.Thrusters: dict[str, list[ChemicalThruster | ElectricThruster | None]] = self.Hardware.Thrusters
        self.Tanks: dict[str, list[ChemicalTank | ElectricTank | None]] = self.Hardware.Tanks

        # Attach thrusters and tanks to the Spacecraft
        for thruster in self.Thrusters['Chemical']:
            if not thruster:
                print(f'No chemical thrusters found, chemical thruster list is: {self.Thrusters["Chemical"]}')
                raise SyntaxError

            thruster.attach_to_sat(self)
            thruster.attach_to_tanks(thruster.tanks)

        for thruster in self.Thrusters['Electric']:
            if not thruster:
                print(f'No electric thrusters found, electric thruster list is: {self.Thrusters["Chemical"]}')
                break

            thruster.attach_to_sat(self)
            thruster.attach_to_tanks(thruster.tanks)

        for tank in self.Tanks['Chemical']:
            tank.attach_to_sat(self)

        for tank in self.Tanks['Electric']:
            tank.attach_to_sat(self)

        # thrusters = sc.Thrusters
        # print(thrusters)
        # for thruster in thrusters:
        #     thruster.attach_to_tanks(thruster.tanks)

        return self.Hardware

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

    def add_thruster(self, thrusters: list[ChemicalThruster | ElectricThruster]):
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
    # def __init__(self, name: str, sc: Spacecraft, gmat_tank_type: str):
    #     print(name, sc, gmat_tank_type)
    #     super().__init__(gmat_tank_type, name)
    #
    #     self.name = name
    #     self.Spacecraft = sc
    #
    #     if gmat_tank_type not in ['ChemicalTank', 'ElectricTank']:
    #         raise SyntaxError(f'Invalid tank type given - {gmat_tank_type}')
    #     else:
    #         self.tank_type = gmat_tank_type
    #
    #     self.prop_tank = self.gmat_obj
    #     self.Spacecraft = sc
    #     self.fuel_mass = 0

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
        self.spacecraft.add_thruster([self.gmat_obj])

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


class FiniteBurn(GmatObject):
    def __init__(self, name, sc_to_manoeuvre: Spacecraft, thruster: ElectricThruster):
        # TODO generic: convert thruster type to Thruster once class created
        super().__init__('FiniteBurn', name)
        self.Name = name
        self.GmatObj = gmat.Construct('FiniteBurn', self.Name)
        self.GmatObj.SetSolarSystem(gmat.GetSolarSystem())
        self._sc_to_manoeuvre = sc_to_manoeuvre
        self.GmatObj.SetSpacecraftToManeuver(sc_to_manoeuvre.gmat_obj)
        self._thruster = thruster
        self._thrusterName = thruster.GetName()
        self.GmatObj.SetField('Thrusters', self._thrusterName)

    def BeginFiniteBurn(self, fin_thrust):  # TODO type: add FiniteThrust type to fin_thrust
        fin_thrust.EnableThrust()
        sc: Spacecraft = 'GMAT object that FiniteBurn is applied to'  # TODO complete by pulling ref obj
        runtime_thruster = sc.gmat_obj.GetRefObject(gmat.THRUSTER, self._thrusterName)
        runtime_thruster.SetField("IsFiring", True)


class FiniteThrust(GmatObject):  # TODO tidy: consider making subclass of FiniteBurn
    def __init__(self, name: str, spacecraft: Spacecraft, finite_burn: FiniteBurn):
        super().__init__('FiniteThrust', name)
        self.Name = name
        self.GmatObj = gmat.FiniteThrust(name)
        self._spacecraft = spacecraft
        self._finite_burn = finite_burn
        self.GmatObj.SetRefObjectName(gmat.SPACECRAFT, spacecraft.GetName())
        self.GmatObj.SetReference(finite_burn.gmat_obj)

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


def gmat_field_string_to_list(string: str) -> list[str]:
    if string == '{}':  # GMAT list is empty
        string_list = []

    elif ',' not in string:  # GMAT list contains exactly one item
        string_list = [string[1:-1]]  # remove GMAT's curly braces and replace with Python square brackets

    else:  # GMAT list contains more than one item
        string_no_curly_braces = f'{string[1:-1]}'
        string_list = list(string_no_curly_braces.split(', '))  # convert to list using comma as separator
        string_list = [substring[1:-1] for substring in string_list]  # remove extra quotes from each item

    return string_list


def list_to_gmat_field_string(data_list: list) -> str:
    """
    Convert a Python list to a format that GMAT can handle in SetField
    :param data_list:
    :return string:
    """
    if data_list is not []:  # Python list contains at least one item
        string = ', '.join(data_list)  # convert the list to a string, with a comma between each item

    else:  # Python list is empty
        string = '{}'

    return string
