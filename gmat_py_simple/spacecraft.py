from __future__ import annotations

import gmat_py_simple as gpy
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
                self.chemical = []
                self.electric = []

            def __repr__(self):
                return (f'A set of Spacecraft {self.name}:'
                        f'\n\t- chemical:     {self.chemical},'
                        f'\n\t- Electrical:   {self.electric}')

        def __init__(self, spacecraft: Spacecraft):
            self.spacecraft = spacecraft

            self.tanks = self.PropList('Tanks')
            self.thrusters = self.PropList('Thrusters')

            self.chemical_tanks = self.tanks.chemical
            self.electric_tanks = self.tanks.electric

            self.chemical_thrusters = self.thrusters.chemical
            self.electric_thrusters = self.thrusters.electric

            self.solar_power_system = None
            self.nuclear_power_system = None

            self.imagers = [None]

        def __repr__(self):
            return (f'{type(self).__name__} object with the following parameters:'
                    # f'\n- Spacecraft: {self.Spacecraft.GetName()},'
                    f'\n- Tanks: {self.tanks},'
                    f'\n- Thrusters: {self.thrusters},'
                    f'\n- SolarPowerSystem: {self.solar_power_system},'
                    f'\n- NuclearPowerSystem: {self.nuclear_power_system},'
                    f'\n- Imagers: {self.imagers}')

        @classmethod
        def from_dict(cls, hw: dict, sc: Spacecraft) -> Spacecraft.SpacecraftHardware:
            sc_hardware = cls(sc)

            # parse tanks
            try:
                tanks: dict = hw['Tanks']

                # parse ChemicalTanks
                try:
                    cp_tanks_list: list[dict] = tanks['chemical']
                    cp_tanks_objs = []
                    for index, cp_tank in enumerate(cp_tanks_list):
                        cp_tanks_objs.append(ChemicalTank.from_dict(cp_tank))
                    sc_hardware.Tanks.chemical = cp_tanks_objs
                except KeyError:
                    raise

                # parse ElectricTanks
                try:
                    ep_tanks_list: list[dict] = tanks['electric']
                    ep_tanks_objs = []
                    for index, ep_tank in enumerate(ep_tanks_list):
                        ep_tanks_objs.append(ElectricTank.from_dict(ep_tank))
                    sc_hardware.Tanks.electric = ep_tanks_objs
                except KeyError:
                    raise

            except KeyError as ke:
                logging.info(f'No tanks found in Hardware dict parsing')

            # parse thrusters
            try:
                thrusters: dict = hw['Thrusters']

                # parse ChemicalThrusters
                try:
                    cp_thrusters_list: list[dict] = thrusters['chemical']
                    cp_thruster_objs = []
                    for index, cp_thruster in enumerate(cp_thrusters_list):
                        cp_thruster_objs.append(ChemicalThruster.from_dict(cp_thruster))
                    sc_hardware.Thrusters.chemical = cp_thruster_objs
                except KeyError:
                    raise

                # parse ElectricThrusters
                try:
                    ep_thrusters_list: list[dict] = thrusters['electric']
                    ep_thruster_objs = []
                    for index, ep_thruster in enumerate(ep_thrusters_list):
                        ep_thruster_objs.append(ElectricThruster.from_dict(ep_thruster))
                    sc_hardware.Thrusters.electric = ep_thruster_objs
                except KeyError:
                    raise

            except KeyError:
                logging.info(f'No thrusters found in Hardware dict parsing')

            # TODO: parse solar_power_system, nuclear_power_system, Imager

            return sc_hardware

        @property
        def Tanks(self):
            return self.tanks

        @property
        def Thrusters(self):
            return self.thrusters

        @property
        def ChemicalTanks(self):
            return self.tanks.chemical

        @property
        def ElectricTanks(self):
            return self.tanks.electric

        @property
        def ChemicalThrusters(self):
            return self.thrusters.chemical

        @property
        def ElectricThrusters(self):
            return self.thrusters.electric

    def __init__(self, name, **kwargs):
        super().__init__('Spacecraft', name)
        self.was_propagated = False  # determines whether to use GetObject() or GetRuntimeObject()

        # TODO: add elements for non-Cartesian orbit states (e.g. 'SMA', 'ECC' for Kep) - get OrbitState allowed fields
        _allowed_fields = set()
        _gmat_allowed_fields = ['NAIFId', 'NAIFIdReferenceFrame', 'SpiceFrameId', 'OrbitSpiceKernelName',
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
        _allowed_fields.update(_gmat_allowed_fields,
                               ['Name', 'Orbit', 'Hardware'])

        self.hardware: Spacecraft.SpacecraftHardware | None = None
        self.tanks: Spacecraft.SpacecraftHardware.PropList | None = None
        self.chemical_tanks = None  # FIXME - not being updated by from_dict()
        self.electric_tanks = None  # FIXME - not being updated by from_dict()

        self.thrusters: Spacecraft.SpacecraftHardware.PropList | None = None
        self.chemical_thrusters = None  # FIXME - not being updated by from_dict()
        self.electric_thrusters = None  # FIXME - not being updated by from_dict()

        self.orbit = None
        self.dry_mass = self.GetField('DryMass')

        gpy.Initialize()
        self.Initialize()

    def __repr__(self):
        return f'Spacecraft with name {self._name}'

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
            logging.info('No hardware parameters specified in Spacecraft dictionary - none will be built')
            hardware = {}

        hardware_obj = Spacecraft.SpacecraftHardware.from_dict(hardware, sc)  # build wrapper Hardware object from specs
        sc.hardware = sc.update_hardware(hardware_obj)  # apply the new Hardware object to the spacecraft

        # use any Orbit params specified in the specs dictionary
        try:
            orbit = specs['Orbit']
            specs.pop('Orbit')
        except KeyError:
            logging.info('No orbit parameters specified in Spacecraft dictionary - none will be built')
            orbit = {}

        if not orbit:  # orbit dict is empty
            sc.orbit = OrbitState()
        else:
            sc.orbit = OrbitState.from_dict(orbit)  # build wrapper Orbit object from specs
        sc.orbit.apply_to_spacecraft(sc)  # apply the new Hardware object to the spacecraft

        # Apply remaining specs
        for spec in specs:
            attr_name = gmat_str_to_py_str(spec, True)
            setattr(sc, attr_name, specs[spec])
            sc.SetField(spec, specs[spec])

        gpy.Initialize()  # initialize GMAT as a whole
        sc.Initialize()  # initialize the completed Spacecraft object
        sc.Validate()  # validate the completed Spacecraft object

        return sc

    def update_from_runtime_object(self):
        self.gmat_obj = gmat.GetRuntimeObject(self._name)
        self.was_propagated = True

    def update_hardware(self, hardware: SpacecraftHardware):
        self.hardware = hardware

        # Attach thrusters and tanks to the Spacecraft
        for thruster in self.hardware.Thrusters.chemical:
            if not thruster:
                print(f'No chemical thrusters found, chemical thruster list is: {self.Thrusters.chemical}')
                raise SyntaxError

            thruster.attach_to_sat(self)
            thruster.attach_to_tanks(thruster.tanks)

        for thruster in self.hardware.Thrusters.electric:
            if not thruster:
                print(f'No electric thrusters found, electric thruster list is: {self.Thrusters.chemical}')
                break

            thruster.attach_to_sat(self)
            thruster.attach_to_tanks(thruster.tanks)

        for tank in self.hardware.Tanks.chemical:
            tank.attach_to_sat(self)

        for tank in self.hardware.Tanks.electric:
            tank.attach_to_sat(self)

        self.thrusters = self.hardware.thrusters
        self.chemical_thrusters = self.hardware.chemical_thrusters
        self.electric_thrusters = self.hardware.electric_thrusters

        self.tanks = self.hardware.tanks
        self.chemical_tanks = self.hardware.chemical_tanks
        self.electric_tanks = self.hardware.electric_tanks

        return self.hardware

    def update_orbit(self, orbit: OrbitState):
        self.orbit = orbit
        pass

    def GetState(self, state_type: str = 'Current') -> list[float]:
        # update Spacecraft's gmat_obj with latest data (e.g. from mission run)
        self.gmat_obj = self.GetObject()

        allowed_state_types: list[str] = list(gpy.OrbitState().allowed_state_elements.keys())
        if state_type != 'Current':
            if state_type not in allowed_state_types:
                raise AttributeError(f'Given state_type is invalid. Valid options are: '
                                     f'{[state for state in allowed_state_types]}')
            self.SetField('DisplayStateType', state_type)

        state: list[float | None] = [None] * 6
        for i in range(13, 19):
            state[i - 13] = float(self.gmat_obj.GetField(i))  # int field refs used to be state type agnostic
        return state

    def GetKeplerianState(self):
        return rvector6_to_list(self.gmat_obj.GetKeplerianState())

    def GetCartesianState(self):
        return rvector6_to_list(self.gmat_obj.GetCartesianState())

    def GetCoordinateSystem(self) -> gpy.OrbitState.CoordinateSystem:
        return gpy.OrbitState.CoordinateSystem.from_sat(self)

    @property
    def Thrusters(self):
        return self.hardware.Thrusters

    @Thrusters.setter
    def Thrusters(self, thrusters: Spacecraft.SpacecraftHardware.PropList):
        self.thrusters = thrusters

    @property
    def ChemicalThrusters(self):
        return self.hardware.ChemicalThrusters

    @property
    def ElectricThrusters(self):
        return self.hardware.ElectricThrusters

    @property
    def Tanks(self):
        return self.hardware.Tanks

    @Tanks.setter
    def Tanks(self, tanks: Spacecraft.SpacecraftHardware.PropList):
        self.tanks = tanks

    @property
    def ChemicalTanks(self):
        return self.hardware.ChemicalTanks

    @property
    def ElectricTanks(self):
        return self.hardware.ElectricTanks

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

        gmat.Initialize()
        self.Initialize()

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

        tank.Validate()

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
        cp_tank.Validate()
        return cp_tank

    # def attach_to_sat(self):
    #     return super().attach_to_sat()

    # @classmethod
    # def from_dict(cls, sc: Spacecraft, tank_dict: dict, **kwargs):
    #     tank = super().from_dict(sc, 'chemical', tank_dict)
    #     return tank


class ElectricTank(Tank):
    #     # TODO add FuelMass and other fields
    #     # self.fuel_mass = fuel_mass
    #     # self.GmatObj.SetField('FuelMass', self.fuel_mass)

    def __init__(self, name: str):
        super().__init__('ElectricTank', name)
        gpy.Initialize()
        self.Initialize()

    @classmethod
    def from_dict(cls, ep_tank_dict: dict):
        ep_tank = Tank.from_dict('ElectricTank', ep_tank_dict)
        ep_tank.Validate()
        return ep_tank


class Thruster(GmatObject):
    def __init__(self, thruster_type: str, name: str):
        super().__init__(thruster_type, name)
        self.thruster_type = thruster_type  # 'ChemicalThruster' or 'ElectricThruster'
        self.name = name

        self.spacecraft = None
        self.tanks: list[ChemicalTank | ElectricTank] | None = None
        self._decrement_mass = self.decrement_mass

        # self.Initialize()

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

        thr.Validate()

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
        self.Initialize()

    @classmethod
    def from_dict(cls, cp_thr_dict: dict) -> ChemicalThruster:
        cp_thr: ChemicalThruster = Thruster.from_dict('ChemicalThruster', cp_thr_dict)
        cp_thr.Validate()
        return cp_thr


class ElectricThruster(Thruster):
    def __init__(self, name: str):
        super().__init__('ElectricThruster', name)
        self.Initialize()

    @classmethod
    def from_dict(cls, ep_thr_dict: dict):
        ep_thr = Thruster.from_dict('ElectricThruster', ep_thr_dict)
        ep_thr.Validate()
        return ep_thr

    # @property
    # def mix_ratio(self):
    #     return self._mix_ratio

    # @mix_ratio.setter
    # def mix_ratio(self, mix_ratio: list[int]):
    #     if all(isinstance(ratio, int) for ratio in mix_ratio):  # check that all mix_ratio elements are of type int
    #         # convert GMAT's Tanks field (with curly braces) to a Python list of strings
    #         tanks_list = [item.strip("'") for item in self.gmat_obj.GetField('Tank')[1:-1].split(', ')]
    #         if len(mix_ratio) != len(tanks_list):
    #             raise SyntaxError('Number of mix ratios provided does not equal existing number of tanks')
    #         else:
    #             if tanks_list and any(ratio == -1 for ratio in mix_ratio):  # tank(s) assigned but a -1 ratio given
    #                 raise SyntaxError('Cannot have -1 mix ratio if tank(s) assigned to thruster')
    #             else:
    #                 self._mix_ratio = mix_ratio
    #     else:
    #         raise SyntaxError('All elements of mix_ratio must be of type int')
