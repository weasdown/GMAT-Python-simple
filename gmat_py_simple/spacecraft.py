from __future__ import annotations

from load_gmat import gmat

from gmat_py_simple.basics import GmatObject
from gmat_py_simple.orbit import OrbitState
from gmat_py_simple.utils import (gmat_str_to_py_str, gmat_field_string_to_list,
                                  list_to_gmat_field_string, rvector6_to_list, get_sat_objects)

from typing import Union
import logging


class Spacecraft(GmatObject):
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
                logging.warning(f'No tanks found in Hardware dict parsing')

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
                logging.warning(f'No thrusters found in Hardware dict parsing')

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
        self.was_propagated = False  # determines whether to use GetObject() or GetRuntimeObject()
        # TODO create a GetObject() method in GmatObj that abstracts away that distinction

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
        self._dry_mass = self.GetField('DryMass')
        gmat.Initialize()

    def __repr__(self):
        return f'Spacecraft with name {self.name}'

    @classmethod
    def from_dict(cls, specs_dict: dict):
        # TODO bugfix: StateType and DryMass values in dict not being used. Add parsing of CoordSys with correct case.

        # Get spacecraft name
        specs = specs_dict.copy()  # take a copy of the dictionary to avoid editing the original
        try:
            name = specs['Name']
            specs.pop('Name')
        except KeyError:
            raise SyntaxError('Spacecraft name required')

        sc = cls(name)  # create an instance of the Spacecraft class

        # Get spacecraft hardware specs
        try:
            hardware = specs['Hardware']
            specs.pop('Hardware')
        except KeyError:
            logging.warning('No hardware parameters specified in Spacecraft dictionary - none will be built')
            hardware = {}

        hardware_obj = Spacecraft.SpacecraftHardware.from_dict(hardware, sc)
        sc.Hardware = sc.update_hardware(hardware_obj)

        # represent sc's orbit with an OrbitState, with Cartesian as the default state_type
        try:
            orbit = specs['Orbit']
            specs.pop('Orbit')
        except KeyError:
            logging.warning('No hardware parameters specified in Spacecraft dictionary - none will be built')
            orbit = {}

        if not orbit:  # orbit dict is empty
            sc.orbit = OrbitState()
        else:
            sc.orbit = OrbitState.from_dict(orbit)
        sc.orbit.apply_to_spacecraft(sc)

        # Apply remaining specs
        for spec in specs:
            attr_name = gmat_str_to_py_str(spec, True)
            setattr(sc, attr_name, specs[spec])
            sc.SetField(spec, specs[spec])

        gmat.Initialize()

        return sc

    def update_from_runtime_object(self):
        self.gmat_obj = gmat.GetRuntimeObject(self.name)
        self.was_propagated = True

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

    def GetState(self) -> list[float]:
        # TODO: in Propagate command, update sat.was_propagated, to be able to remove the two lines below.
        #  Means won't need it in every function that requires updates from GetRuntimeObject().
        if self.was_propagated:  # spacecraft has been used in a mission run
            self.gmat_obj = self.GetObject()  # update Spacecraft's gmat_obj with the run data

        state: list[float | None] = [None] * 6
        for i in range(13, 19):
            state[i - 13] = float(self.gmat_obj.GetField(i))  # int field refs used to be state type agnostic
        return state

    def GetKeplerianState(self):
        return rvector6_to_list(self.gmat_obj.GetKeplerianState())

    def GetCartesianState(self):
        return rvector6_to_list(self.gmat_obj.GetCartesianState())

    # @property
    # def gmat_runtime(self):
    #     return self._gmat_runtime
    #
    # @gmat_runtime.setter
    # def gmat_runtime(self, grt: gmat.GmatBase):
    #     # if not None, or if not a GmatBase
    #     if not ((grt is not None) or ('gmat_py.GmatBase' not in str(type(grt)))):
    #         raise TypeError('Spacecraft.gmat_runtime can only a gmat.GmatBase object, or None')
    #     else:  # grt is something other than None or a gmat_py.GmatBase
    #         self._gmat_runtime = grt

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


class Tank(GmatObject):
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


class Thruster(GmatObject):
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
