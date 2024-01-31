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

        def __init__(self, spacecraft: Spacecraft = None,
                     chem_tanks: gpy.ChemicalTank | list[gpy.ChemicalTank] = None,
                     elec_tanks: gpy.ElectricTank | list[gpy.ElectricTank] = None,
                     chem_thrusters: gpy.ChemicalThruster | list[gpy.ChemicalThruster] = None,
                     elec_thrusters: gpy.ElectricThruster | list[gpy.ElectricThruster] = None,
                     solar_power_system: gpy.SolarPowerSystem = None,
                     nuclear_power_system: gpy.NuclearPowerSystem = None,
                     imagers: gpy.Imager | list[gpy.Imager] = None):
            self.chem_tanks = chem_tanks if chem_tanks is not None else []
            self.elec_tanks = elec_tanks if elec_tanks is not None else []

            self.chem_thrusters = chem_thrusters if chem_thrusters is not None else []
            self.elec_thrusters = elec_thrusters if elec_thrusters is not None else []

            self.solar_power_system = None if solar_power_system is None else solar_power_system
            self.nuclear_power_system = None if nuclear_power_system is None else nuclear_power_system

            self.imagers = imagers if imagers is not None else []

        def __repr__(self):
            return (f'{type(self).__name__} object with the following parameters:'
                    # f'\n- Spacecraft: {self.Spacecraft.GetName()},'
                    f'\n- ChemicalTanks: {self.chem_tanks},'
                    f'\n- ElectricTanks: {self.elec_tanks},'
                    f'\n- ChemicalThrusters: {self.chem_thrusters},'
                    f'\n- ElectricThrusters: {self.elec_thrusters},'
                    f'\n- SolarPowerSystem: {self.solar_power_system},'
                    f'\n- NuclearPowerSystem: {self.nuclear_power_system},'
                    f'\n- Imagers: {self.imagers}')

        @classmethod
        def from_dict(cls, hw: dict, sc: Spacecraft) -> Spacecraft.SpacecraftHardware:
            sc_hardware = cls(sc)

            # parse ChemicalTanks
            cp_tanks_list: list[dict] = hw.get('ChemicalTanks', [{}])
            cp_tanks_objs = []
            for index, cp_tank in enumerate(cp_tanks_list):
                cp_tanks_objs.append(ChemicalTank.from_dict(cp_tank))
            sc_hardware.chem_tanks = cp_tanks_objs if cp_tanks_objs != [None] else None

            # parse ElectricTanks
            ep_tanks_list: list[dict] = hw.get('ElectricTanks', [{}])
            ep_tanks_objs = []
            for index, ep_tank in enumerate(ep_tanks_list):
                ep_tanks_objs.append(ElectricTank.from_dict(ep_tank))
            sc_hardware.elec_tanks = ep_tanks_objs if ep_tanks_objs != [None] else None

            # parse ChemicalThrusters
            cp_thrusters_list: list[dict] = hw.get('ChemicalThrusters', [{}])
            cp_thruster_objs = []
            for index, cp_thruster in enumerate(cp_thrusters_list):
                cp_thruster_objs.append(ChemicalThruster.from_dict(cp_thruster))
            sc_hardware.chem_thrusters = cp_thruster_objs if cp_thruster_objs != [None] else None

            # parse ElectricThrusters
            ep_thrusters_list: list[dict] = hw.get('ElectricThrusters', [{}])
            ep_thruster_objs = []
            for index, ep_thruster in enumerate(ep_thrusters_list):
                ep_thruster_objs.append(ElectricThruster.from_dict(ep_thruster))
            sc_hardware.elec_thrusters = ep_thruster_objs if ep_thruster_objs != [None] else None

            # parse solar power systems
            solar_power_systems: dict = hw.get('SolarPowerSystem', {})
            sc_hardware.solar_power_system = SolarPowerSystem.from_dict(solar_power_systems)

            # TODO: parse nuclear_power_system, imager

            return sc_hardware

        @property
        def ChemicalTanks(self):
            return self.chem_tanks

        @property
        def ElectricTanks(self):
            return self.elec_tanks

        @property
        def ChemicalThrusters(self):
            return self.chem_thrusters

        @property
        def ElectricThrusters(self):
            return self.elec_thrusters

    def __init__(self, name, hardware: SpacecraftHardware = None, **kwargs):
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

        self.hardware: Spacecraft.SpacecraftHardware = self.SpacecraftHardware(self) if hardware is None else hardware

        # TODO confirm fixed - FIXME - not being updated by from_dict()
        # Setup tanks
        self.chem_tanks = None
        if self.hardware.chem_tanks:
            if isinstance(self.chem_tanks, list):
                self.chem_tanks = self.hardware.chem_tanks
                for tank in self.chem_tanks:
                    tank.attach_to_sat(self)
            else:
                self.chem_tanks = [self.hardware.chem_tanks]
                self.chem_tanks[0].attach_to_sat(self)

        self.elec_tanks = None
        if self.hardware.elec_tanks:
            if isinstance(self.elec_tanks, list):
                self.elec_tanks = self.hardware.elec_tanks
                for tank in self.elec_tanks:
                    tank.attach_to_sat(self)
            else:
                self.elec_tanks = [self.hardware.elec_tanks]
                self.elec_tanks[0].attach_to_sat(self)

        # Setup thrusters
        self.chem_thrusters = None
        if self.hardware.chem_thrusters:
            self.chem_thrusters: ChemicalThruster | list[ChemicalThruster] = self.hardware.chem_thrusters
            if isinstance(self.chem_thrusters, list):
                self.chem_thrusters: list[ChemicalThruster] = self.hardware.chem_thrusters
                for thruster in self.chem_thrusters:
                    thruster.attach_to_sat(self)
                    thruster.attach_to_tanks(thruster.tanks)
            else:  # self.chem_thrusters is a single ChemicalThruster object
                self.chem_thrusters = [self.hardware.chem_thrusters]
                self.chem_thrusters[0].attach_to_sat(self)
                self.chem_thrusters[0].attach_to_tanks(self.chem_thrusters[0].tanks)

        self.elec_thrusters = None
        if self.hardware.elec_thrusters:
            self.elec_thrusters: ElectricThruster | list[ElectricThruster] = self.hardware.elec_thrusters
            if isinstance(self.elec_thrusters, list):
                self.elec_thrusters: list[ElectricThruster] = self.hardware.elec_thrusters
                for thruster in self.elec_thrusters:
                    thruster.attach_to_sat(self)
                    thruster.attach_to_tanks(thruster.tanks)
            else:  # self.elec_thrusters is a single ElectricThruster object
                self.elec_thrusters = [self.hardware.elec_thrusters]
                self.elec_thrusters[0].attach_to_sat(self)
                self.elec_thrusters[0].attach_to_tanks(self.elec_thrusters[0].tanks)

        # Setup power systems
        self.solar_power_system = None
        if self.hardware.solar_power_system is not None:
            self.solar_power_system = self.hardware.solar_power_system
            self.solar_power_system.attach_to_sat(self)

        self.nuclear_power_system = None
        if self.hardware.nuclear_power_system is not None:
            self.nuclear_power_system = self.hardware.nuclear_power_system
            self.nuclear_power_system.attach_to_sat(self)

        # Setup imagers
        self.imagers = None
        if self.hardware.imagers is not None:
            self.imagers: gpy.Imager | list[gpy.Imager] = self.hardware.imagers
            if isinstance(self.imagers, list):
                for imager in self.imagers:
                    imager.attach_to_sat(self)
            else:
                self.imagers.attach_to_sat(self)

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
        if self.hardware.chem_thrusters is not None:
            for thruster in self.hardware.chem_thrusters:
                # if not thruster:
                #     raise RuntimeError(f'No chemical thrusters found, chemical thruster list is: {self.chem_thrusters}'
                #                        f'\n{self.hardware.chem_thrusters}')
                if thruster is not None:
                    thruster.attach_to_sat(self)
                    thruster.attach_to_tanks(thruster.tanks)

        if self.hardware.elec_thrusters is not None:
            for thruster in self.hardware.elec_thrusters:
                # if not thruster:
                #     raise RuntimeError(f'No electric thrusters found, electric thruster list is: {self.elec_thrusters}')
                if thruster is not None:
                    thruster.attach_to_sat(self)
                    thruster.attach_to_tanks(thruster.tanks)

        if self.hardware.chem_tanks is not None:
            for tank in self.hardware.chem_tanks:
                if tank is not None:
                    tank.attach_to_sat(self)

        if self.hardware.elec_tanks is not None:
            for tank in self.hardware.elec_tanks:
                if tank is not None:
                    tank.attach_to_sat(self)

        self.chem_thrusters = self.hardware.chem_thrusters
        self.elec_thrusters = self.hardware.elec_thrusters

        self.chem_tanks = self.hardware.chem_tanks
        self.elec_tanks = self.hardware.elec_tanks

        self.solar_power_system = self.hardware.solar_power_system
        if self.solar_power_system is not None:
            self.hardware.solar_power_system.attach_to_sat(self)

        return self.hardware

    def update_orbit(self, orbit: OrbitState):
        self.orbit = orbit
        pass

    def GetState(self, state_type: str = 'Current', coord_sys: str = 'EarthMJ2000Eq') -> list[float]:
        # Get latest data (e.g. from mission run)
        up_to_date_obj = self.GetObject()

        allowed_state_types: list[str] = list(gpy.OrbitState().allowed_state_elements.keys())
        if state_type != 'Current':
            if state_type not in allowed_state_types:
                raise AttributeError(f'Given state_type is invalid. Valid options are: '
                                     f'{[state for state in allowed_state_types]}')
            up_to_date_obj.SetField('DisplayStateType', state_type)

        state: list[float | None] = [None] * 6
        for i in range(13, 19):
            state[i - 13] = float(up_to_date_obj.GetField(i))  # int field refs used to be state type agnostic

        return state

    def GetKeplerianState(self):
        return rvector6_to_list(self.gmat_obj.GetKeplerianState())

    def GetCartesianState(self):
        return rvector6_to_list(self.gmat_obj.GetCartesianState())

    def GetCoordinateSystem(self) -> gpy.OrbitState.CoordinateSystem:
        return gpy.OrbitState.CoordinateSystem.from_sat(self)

    @property
    def ChemicalThrusters(self):
        return self.hardware.ChemicalThrusters

    @property
    def ElectricThrusters(self):
        return self.hardware.ElectricThrusters

    @property
    def ChemicalTanks(self):
        return self.hardware.ChemicalTanks

    @property
    def ElectricTanks(self):
        return self.hardware.ElectricTanks

    def add_tanks(self, tanks: gpy.Tank | list[gpy.Tank] | str) -> bool:
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
        if isinstance(tanks, str):
            current_tanks_list = [tanks]
            tank = gmat.GetObject(tanks)
            self.SetStringParameter(104, tank.GetName())  # 104 for sat's ADD_HARDWARE
            current_tanks_list.extend(tank.GetName())
        elif isinstance(tanks, gpy.Tank):
            self.SetStringParameter(104, tanks.GetName())  # 104 for sat's ADD_HARDWARE
            current_tanks_list.append(tanks.GetName())
        else:  # tanks is a list of Tanks
            for tank in tanks:
                tanks_to_set: list = [tank.GetName()]
                current_tanks_list.extend(tanks_to_set)
                self.SetStringParameter(104, tank.GetName())  # 104 for sat's ADD_HARDWARE

        value = list_to_gmat_field_string(current_tanks_list)
        self.SetField('Tanks', value)

        return True

    def add_thrusters(self, thrusters: list[ChemicalThruster | ElectricThruster]) -> bool:
        current_thrusters_value: str = self.GetField('Thrusters')
        current_thrusters_list: list = gmat_field_string_to_list(current_thrusters_value)

        # Add tanks by getting name of each tank, adding it to a list, then attaching this list to end of existing one
        if isinstance(thrusters, str):
            thruster = gmat.GetObject(thrusters)
            self.SetStringParameter(104, thruster.GetName())  # 104 for sat's ADD_HARDWARE
        elif isinstance(thrusters, gpy.Thruster):
            self.SetStringParameter(104, thrusters.GetName())  # 104 for sat's ADD_HARDWARE
        else:
            for thruster in thrusters:
                thrusters_to_set: list = [thruster.GetName()]
                current_thrusters_list.extend(thrusters_to_set)
                self.SetStringParameter(104, thruster.GetName())  # 104 for sat's ADD_HARDWARE

        value = list_to_gmat_field_string(current_thrusters_list)
        self.SetField('Thrusters', value)

        return True

    def add_sps(self, solar_power_system: gpy.SolarPowerSystem | gmat.SolarPowerSystem) -> bool:
        self.SetStringParameter(104, solar_power_system.GetName())  # 104 for sat's ADD_HARDWARE
        if self.GetField('PowerSystem') == '':
            self.SetField('PowerSystem', solar_power_system.GetName())
            return True
        else:
            return False

    def add_nps(self, nuclear_power_system: gpy.NuclearPowerSystem | gmat.NuclearPowerSystem) -> bool:
        self.SetStringParameter(104, nuclear_power_system.GetName())  # 104 for sat's ADD_HARDWARE
        if self.GetField('PowerSystem') == '':
            self.SetField('PowerSystem', nuclear_power_system.GetName())
            return True
        else:
            return False


class Tank(GmatObject):
    def __init__(self, tank_type: str, name: str):
        super().__init__(tank_type, name)
        self.tank_type = tank_type  # 'ChemicalTank' or 'ElectricTank'
        self.name = name

        self.spacecraft = None
        self.fuel_mass = self.GetField('FuelMass')

        self.Initialize()

    def __repr__(self):
        return f'{self.tank_type} with name {self.name}'

    @staticmethod
    def from_dict(fuel_type: str, tank_dict: dict[str, Union[str, int, float]]):
        if fuel_type == 'Chemical':
            tank = ChemicalTank(tank_dict['Name'])
        elif fuel_type == 'Electric':
            tank = ElectricTank(tank_dict['Name'])
        else:
            raise SyntaxError(f'Invalid thr_type found in Tank.from_dict: {fuel_type}'
                              f"\nMust be 'Chemical' or 'Electric'")

        fields: list[str] = list(tank_dict.keys())
        fields.remove('Name')
        for field in fields:
            try:
                tank.SetField(field, tank_dict[field])
            except Exception as ex:
                # TODO remove if (debugging only)
                if field != 'AllowNegativeFuelMass':
                    raise RuntimeError(f'Faulting field: {field}. GMAT error:\n\t{ex}')

        tank.Validate()

        return tank

    def attach_to_sat(self, sat: Spacecraft):
        self.spacecraft = sat
        self.spacecraft.add_tanks([gpy.extract_gmat_obj(self)])


class ChemicalTank(Tank):
    def __init__(self, name: str, fuel_mass: int | float = 756, allow_negative_fuel_mass: bool = False,
                 pressure: int | float = 1500, temperature: int | float = 20, ref_temp: int | float = 20,
                 volume: int | float = 0.75, fuel_density: int | float = 1260,
                 pressure_model: str = 'PressureRegulated'):
        super().__init__('ChemicalTank', name)

        self.fuel_mass = self.GetRealParameter('FuelMass')  # kg
        if fuel_mass is not None:
            self.fuel_mass = fuel_mass
            self.SetRealParameter('FuelMass', self.fuel_mass)

        self.allow_negative_fuel_mass = self.GetBooleanParameter('AllowNegativeFuelMass')  # Boolean
        if allow_negative_fuel_mass is not None:
            self.allow_negative_fuel_mass = allow_negative_fuel_mass
            self.SetBooleanParameter('AllowNegativeFuelMass', self.allow_negative_fuel_mass)

        self.pressure = self.GetRealParameter('Pressure')  # kPa
        if pressure is not None:
            self.pressure = pressure
            self.SetRealParameter('Pressure', self.pressure)

        self.temperature = self.GetRealParameter('Temperature')  # Celsius
        if temperature is not None:
            self.temperature = temperature
            self.SetRealParameter('Temperature', self.temperature)

        self.ref_temp = self.GetRealParameter('RefTemperature')  # Celsius
        if ref_temp is not None:
            self.ref_temp = ref_temp
            self.SetRealParameter('RefTemperature', self.ref_temp)

        # Volume
        self.volume = self.GetRealParameter('Volume')  # m^3
        if volume is not None:
            self.volume = volume
            self.SetRealParameter('Volume', self.volume)

        # Fuel density
        self.fuel_density = self.GetRealParameter('FuelDensity')  # kg/m^3
        if fuel_density is not None:
            self.fuel_density = fuel_density
            self.SetRealParameter('FuelDensity', self.fuel_density)

        # Pressure Model
        self.pressure_model = self.GetStringParameter('PressureModel')  # string
        allowed_pressure_models = ['PressureRegulated', 'BlowDown']
        if pressure_model is not None:
            if pressure_model not in allowed_pressure_models:
                raise AttributeError(
                    f'Invalid pressure model specified for {self.GetTypeName()} {self.name}. Must be one of: {allowed_pressure_models}')
            self.pressure_model = pressure_model
            self.SetStringParameter('PressureModel', self.pressure_model)

            self.Initialize()

    @classmethod
    def from_dict(cls, cp_tank_dict: dict) -> gpy.ChemicalTank | None:
        if cp_tank_dict != {}:
            cp_tank = super().from_dict('Chemical', cp_tank_dict)
            cp_tank.Validate()
            return cp_tank
        else:
            return None

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

        # TODO take and parse arguments like in ChemicalTank

        self.Initialize()

    @classmethod
    def from_dict(cls, ep_tank_dict: dict) -> gpy.ElectricTank | None:
        if ep_tank_dict != {}:
            ep_tank = Tank.from_dict('ElectricTank', ep_tank_dict)
            ep_tank.Validate()
            return ep_tank
        else:
            return None


class Thruster(GmatObject):
    def __init__(self, fuel_type: str, name: str, tanks: str | gpy.Tank | gmat.Tank | list[gpy.Tank] |
                                                         list[gmat.FuelTank],
                 mix_ratio: int | float | list[int | float] = None):
        self.fuel_type = fuel_type
        self.thruster_type = f'{self.fuel_type}Thruster'  # 'ChemicalThruster' or 'ElectricThruster'
        super().__init__(self.thruster_type, name)

        self.spacecraft = None

        self.tanks: list[ChemicalTank | ElectricTank] | None = tanks
        self.mix_ratio: list[int | float] = [mix_ratio] if isinstance(mix_ratio, (int, float)) else mix_ratio
        if isinstance(self.tanks, str | gpy.Tank | gmat.FuelTank):
            if mix_ratio is not None and self.mix_ratio != 1:
                raise AttributeError(f'Invalid mix_ratio {self.mix_ratio} given for a single tank')
            self.mix_ratio = [1]
            self.SetField('MixRatio', self.mix_ratio)
            if isinstance(self.tanks, str):
                self.SetField('Tank', self.tanks)
            elif isinstance(self.tanks, gpy.Tank | gmat.Tank):
                self.SetField('Tank', self.tanks.GetName())
        elif isinstance(self.tanks, list):
            if mix_ratio is None:
                raise AttributeError('mix_ratio must be given if multiple tanks have been given')
            else:
                tank_names = [tank.GetName() for tank in self.tanks]
                self.SetField('Tank', tank_names)

        self._decrement_mass = self.decrement_mass

        self.Initialize()

    def __repr__(self):
        return f'A {self.thruster_type} with name {self.name}'

    @staticmethod
    def from_dict(fuel_type: str, thr_dict: dict[str, Union[str, int, float]]):
        name = thr_dict.get('Name')
        tanks = thr_dict.get('Tanks')
        if fuel_type == 'Chemical':
            thr = ChemicalThruster(name, tanks)
        elif fuel_type == 'Electric':
            thr = ElectricThruster(thr_dict['Name'], tanks)
        else:
            raise SyntaxError(f'Invalid fuel_type found in Thruster.from_dict: {fuel_type}.'
                              f"\nMust be 'Chemical' or 'Electric'")

        fields: list[str] = list(thr_dict.keys())
        fields.remove('Name')
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
        gpy.extract_gmat_obj(self).SetField('Tank', tanks)

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
    def __init__(self, name: str, tanks: str | gpy.ChemicalTank | gmat.ChemicalTank |
                                         list[gpy.ChemicalTank] | list[gmat.ChemicalTank]):
        super().__init__('Chemical', name, tanks)

        self.Validate()
        self.Initialize()

    @classmethod
    def from_dict(cls, cp_thr_dict: dict) -> gpy.ChemicalThruster | None:
        if cp_thr_dict != {}:
            cp_thr: ChemicalThruster = Thruster.from_dict('Chemical', cp_thr_dict)
            cp_thr.Validate()
            return cp_thr
        else:
            return None


class ElectricThruster(Thruster):
    def __init__(self, name: str, tanks: str | gpy.ElectricTank | gmat.ElectricTank |
                                         list[gpy.ElectricTank] | list[gmat.ElectricTank]):
        super().__init__('Electric', name, tanks)
        self.Initialize()

    @classmethod
    def from_dict(cls, ep_thr_dict: dict) -> gpy.ElectricThruster | None:
        if ep_thr_dict != {}:
            ep_thr = Thruster.from_dict('Electric', ep_thr_dict)
            ep_thr.Validate()
            return ep_thr
        else:
            return None

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


class SolarPowerSystem(GmatObject):
    def __init__(self, name: str):
        super().__init__('SolarPowerSystem', name)

        self.spacecraft = None

        # TODO add parsing of each field under Help()
        # self.Help()
        pass

    def __repr__(self):
        return f'A SolarPowerSystem named "{self.GetName()}"'

    def attach_to_sat(self, sat: gpy.Spacecraft | gmat.Spacecraft):
        self.spacecraft = sat
        if sat.GetField('PowerSystem') == '':
            self.spacecraft.add_sps(self)
        else:
            return False
        pass

    @staticmethod
    def from_dict(sps_dict: dict[str, Union[str, int, float]]):
        if sps_dict == {}:
            return

        name = sps_dict.get('Name', 'DefaultSolarPowerSystem')
        sps = SolarPowerSystem(name)

        fields: list[str] = list(sps_dict.keys())
        fields.remove('Name')

        # TODO convert to sps.SetFields
        for field in fields:
            sps.SetField(field, sps_dict[field])
            setattr(sps, field, sps_dict[field])

        sps.Validate()

        return sps


class NuclearPowerSystem(GmatObject):
    def __init__(self, name: str):
        super().__init__('NuclearPowerSystem', name)

        self.spacecraft = None

        # TODO add parsing of each field under Help()
        # self.Help()
        pass

    def __repr__(self):
        return f'A NuclearPowerSystem named "{self.GetName()}"'

    def attach_to_sat(self, sat: gpy.Spacecraft | gmat.Spacecraft) -> bool:
        self.spacecraft = sat
        if sat.GetField('PowerSystem') == '':
            self.spacecraft.add_nps(self)
        else:
            return False

    @staticmethod
    def from_dict(nps_dict: dict[str, Union[str, int, float]]):
        try:
            name = nps_dict['Name']
        except KeyError:  # no name found - use default
            name = 'DefaultNuclearPowerSystem'
        nps = NuclearPowerSystem(name)

        fields: list[str] = list(nps_dict.keys())
        fields.remove('Name')

        # TODO convert to nps.SetFields
        for field in fields:
            nps.SetField(field, nps_dict[field])
            setattr(nps, field, nps_dict[field])

        nps.Validate()

        return nps


class Color(bytearray):
    def __init__(self, name: str = 'DefaultColor', red: int = 0, green: int = 0, blue: int = 0, alpha: int = 1):
        super().__init__()
        self.name = name
        self.gmat_obj = gmat.RgbColor()

        # Initialize RGB color to black
        self.red: int = red if red is not None else self.gmat_obj.Red()

        self.green: int = green if green is not None else self.gmat_obj.Green()
        self.blue: int = blue if blue is not None else self.gmat_obj.Blue()
        self.alpha: int = alpha if alpha is not None else self.gmat_obj.Alpha()  # opaque
        self.rgb_color = bytearray([self.red, self.green, self.blue, self.alpha])

        # Apply the custom color values to the gmat_obj
        self.gmat_obj.Set(self.red, self.green, self.blue, self.alpha)

    def GetIntColor(self):
        # TODO write method
        raise NotImplementedError
        # return self.colortype.int_color

    def ToIntColor(self, color_str: str) -> int:
        return gpy.extract_gmat_obj(self).ToIntColor(color_str)

    def ToRgbString(self, color_uint: int) -> str:
        return gpy.extract_gmat_obj(self).ToRgbString(color_uint)

    def ToRgbList(self, color_uint: int) -> list[int]:
        rgb_str: str = gpy.extract_gmat_obj(self).ToRgbString(color_uint)
        rgb_list: list = [int(ele) for ele in rgb_str[1:-1].split(' ')]
        return rgb_list

    def Red(self) -> int:
        return self.gmat_obj.Red()

    def Green(self) -> int:
        return self.gmat_obj.Green()

    def Blue(self) -> int:
        return self.gmat_obj.Blue()

    def Alpha(self) -> int:
        return self.gmat_obj.Alpha()


class Imager(GmatObject):
    class FieldOfView(GmatObject):
        def __init__(self, fov_type: str = None, name: str = 'DefaultFOV'):
            allowed_fov_types = ['ConicalFOV', 'CustomFOV', 'RectangularFOV', None]
            if fov_type not in allowed_fov_types:
                raise TypeError(f'FieldOfView type given in fov_type "{fov_type}" is not recognized. Must be one of:\n'
                                f'{allowed_fov_types}')
            elif fov_type is None:
                super().__init__('RectangularFOV', name)
            else:
                super().__init__(fov_type, name)

    class RectangularFOV(FieldOfView):
        def __init__(self, name: str = 'DefaultRectangularFOV'):
            super().__init__('RectangularFOV', name)

    class ConicalFOV(FieldOfView):
        def __init__(self, name: str = 'DefaultConicalFOV', color: list = None, fov_angle: int | float = 30):
            super().__init__('ConicalFOV', name)

            print(f'Full Colour DB: {gmat.ColorDatabase.Instance().GetAllColorNameArray()}')
            red = gmat.ColorDatabase.Instance().GetRgbColor("Red")
            print(f'Red Color: {red}')

            self.color = [float(ele) for ele in self.GetField('Color')[1:-1].split(' ')]
            if color is None:
                # color: list = [0, 0, 0]
                color = Color()
            self.color = color  # None case already handled above

            self.fov_angle = fov_angle if fov_angle is not None else 30
            self.SetRealParameter('FieldOfViewAngle', self.fov_angle)
            # self.Help()
            pass

    class CustomFOV(FieldOfView):
        def __init__(self, name: str = 'DefaultCustomFOV'):
            super().__init__('CustomFOV', name)

    def __init__(self, name: str, fov: FieldOfView | gmat.FieldOfView | str = None):
        super().__init__('Imager', name)

        self.spacecraft = None

        if fov is None:
            self.fov = self.FieldOfView()
        elif isinstance(fov, Imager.FieldOfView):
            self.fov = fov
        elif isinstance(fov, str):
            # fov is presumed to be a path to an FoV file
            raise NotImplementedError
        else:
            raise TypeError(
                f'Type for fov "{type(fov).__name__}" is not recognized. Must be a FieldOfView object or str'
                f' representing a path to an FoV file')

        self.fov = self.ConicalFOV()

        # TODO: attach self.fov to Imager

        # TODO add parsing of each field under Help()
        # self.Help()
        pass

    def __repr__(self):
        return f'An Imager named "{self.GetName()}"'

    def attach_to_sat(self, sat: gpy.Spacecraft | gmat.Spacecraft):
        sat_gmat = gpy.extract_gmat_obj(sat)
        sat_gmat.SetStringParameter(104, self.GetName())  # 104 for sat's ADD_HARDWARE

    @staticmethod
    def from_dict(imager_dict: dict[str, Union[str, int, float]]):
        raise NotImplementedError
        # try:
        #     name = imager_dict['Name']
        # except KeyError:  # no name found - use default
        #     name = 'DefaultImager'
        # imager = Imager(name)
        #
        # fields: list[str] = list(imager_dict.keys())
        # fields.remove('Name')
        #
        # # TODO convert to imager.SetFields
        # for field in fields:
        #     imager.SetField(field, imager_dict[field])
        #     setattr(imager, field, imager_dict[field])
        #
        # imager.Validate()
        #
        # return imager
