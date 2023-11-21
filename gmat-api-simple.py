import json

from load_gmat import gmat


class GmatObject:
    def __init__(self):
        self._gmat_obj = None
        self._name = None

    @property
    def gmat_object(self):
        if not self._gmat_obj:
            raise Exception(f'No GMAT object found for {self._name} of type {type(self).__name__}')
        else:
            return self._gmat_obj

    @property
    def gmat_name(self):
        return self._gmat_obj.GetName()

    def GetName(self):
        return self.gmat_name

    def Help(self):
        if not self._gmat_obj:
            raise AttributeError(f'No GMAT object found for object {self.__name__} of type {type(self.__name__)}')
        self._gmat_obj.Help()


class OrbitState:
    def __init__(self, sc, **kwargs):
        self._allowed_values = {'display_state_type': ['Cartesian', 'Keplerian', 'ModifiedKeplerian', 'SphericalAZFPA',
                                                       'SphericalRADEC', 'Equinoctial'],
                                'coord_sys': [],  # TODO: define valid coord_sys values
                                # TODO: define valid state_type values - using display_state_type ones for now
                                'state_type': ['Cartesian', 'Keplerian', 'ModifiedKeplerian', 'SphericalAZFPA',
                                               'SphericalRADEC', 'Equinoctial'],
                                }

        if 'display_state_type' in kwargs:
            if kwargs['display_state_type'] not in self._allowed_values['display_state_type']:
                raise SyntaxError(f'Invalid display state type passed to OrbitState __init__. '
                                  f'Allowed values are: {self._allowed_values["display_state_type"]}')
            else:
                display_state_type = kwargs['display_state_type']
                sc.gmat_object.SetField('DisplayStateType', display_state_type)
        else:
            display_state_type = 'Cartesian'

        if 'epoch' in kwargs:
            sc.gmat_object.SetField('Epoch', str(kwargs['epoch']))

        if 'state_type' in kwargs:
            if kwargs['state_type'] not in self._allowed_values['state_type']:
                raise SyntaxError(f'Invalid state type passed to OrbitState __init__. '
                                  f'Allowed values are: {self._allowed_values["state_type"]}')
            else:
                state_type = kwargs['state_type']
                sc.gmat_object.SetField('StateType', state_type)
        else:
            state_type = 'Cartesian'

        if 'coord_sys' in kwargs:
            if kwargs['coord_sys'] not in self._allowed_values['coord_sys']:
                raise SyntaxError(f'Invalid coordinate system passed to OrbitState __init__. '
                                  f'Allowed values are: {self._allowed_values["coord_sys"]}')
            else:
                coord_sys = kwargs['coord_sys']
                sc.gmat_object.SetField('CoordinateSystem', coord_sys)
        else:
            coord_sys = 'EarthMJ2000Eq'

        try:
            if state_type == 'Cartesian':
                print(f'x: {kwargs["x"]}')
                sc.gmat_object.SetField('X', kwargs['x'])
                sc.gmat_object.SetField('Y', kwargs['y'])
                sc.gmat_object.SetField('Z', kwargs['z'])
                sc.gmat_object.SetField('VX', kwargs['vx'])
                sc.gmat_object.SetField('VY', kwargs['vy'])
                sc.gmat_object.SetField('VZ', kwargs['vz'])
            # TODO: implement non-Cartesian states
            elif state_type == 'Keplerian':
                print('Keplerian state requested')
                pass
            else:
                raise SyntaxError('State type not recognised')
        except KeyError:  # jumps to here on *first* failed state element assignment
            print('OrbitState __init__ did not receive all the correct parameters for the specified state')
            print(f'Using defaults of at least some state elements for state {state_type}')


class Hardware(GmatObject):
    def __init__(self, object_type, name):
        super().__init__()
        self._obj_type = object_type
        self._name = name
        self._gmat_obj = gmat.Construct(self._obj_type, self._name)

    def __repr__(self):
        return f'A piece of Hardware of type {self._obj_type} and name {self._name}'

    def IsInitialized(self):
        self._gmat_obj.IsInitialized()


class ElectricThruster(Hardware):  # TODO make this a child of a new class, Thruster, that inherits from Hardware
    def __init__(self, name, sc, tank, decrement_mass=True):
        super().__init__('ElectricThruster', name)
        self._name = self._gmat_obj.GetName()
        self._sc = sc
        self._tank = tank
        self._decrement_mass = decrement_mass
        self.attach_to_sat()
        self.attach_to_tank()
        self._gmat_obj.SetField('DecrementMass', self._decrement_mass)
        self._mix_ratio = [-1]

    def __repr__(self):
        return f'A Thruster with name {self._name}'

    def attach_to_tank(self):
        self._gmat_obj.SetField('Tank', self._tank.gmat_object.GetName())

    def attach_to_sat(self):
        # TODO feature: convert to append to existing Thrusters list
        self._sc.gmat_object.SetField('Thrusters', self._name)

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


class ElectricTank(Hardware):  # TODO make this a child of a new class, Tank, that inherits from Hardware
    def __init__(self, name, sc, fuel_mass=10):
        super().__init__('ElectricTank', name)
        self._name = self._gmat_obj.GetName()
        self._sc = sc
        self._fuel_mass = fuel_mass
        self._gmat_obj.SetField('FuelMass', self._fuel_mass)
        self.attach_to_sat()

    def __repr__(self):
        return f'An ElectricTank with name {self._name} and fuel {self._fuel_mass}'

    def attach_to_sat(self):
        self._sc.gmat_object.SetField('Tanks', self._name)
        pass


class Spacecraft(Hardware):
    def __init__(self, specs: dict):
        super().__init__('Spacecraft', specs['name'])
        self._specs = specs  # TODO define default params type so name is required but others use defaults
        for key in specs:
            setattr(self, key, specs[key])  # set object attributes based on passed specs dict
        self._gmat_obj = gmat.Construct("Spacecraft", specs['name'])

        # Default orbit specs
        self._epoch = '21545'
        self._state_type = 'Cartesian'
        self._display_state_type = 'Cartesian'
        self._coord_sys = 'EarthMJ2000Eq'

        tanks_list = specs['hardware']['tanks']
        if tanks_list:  # the specs listed tanks to be built
            self._tanks = []
            self.construct_tanks(tanks_list)
            # TODO: set GMAT sat Tanks field

        print(f'Orbit specs passed to Spacecraft init: {specs["orbit"]}')

        if specs['orbit']:
            self.construct_orbit_state(specs['orbit'])
        else:
            print('No orbit params found while build Spacecraft - using defaults')

        init_value = specs['gmat_init']
        if init_value:
            if not isinstance(init_value, bool):
                raise SyntaxError('gmat_init must be True or False')
            gmat.Initialize()

    def __repr__(self):
        return f'Spacecraft with name {self._name} and specifications:\n{json.dumps(self._specs, indent=4)}'

    def __str__(self):
        return f'Spacecraft with name {self._name}'

    @property
    def specs(self):
        return self._specs

    def construct_tanks(self, tanks_list: dict):
        for index, tank in enumerate(tanks_list):
            fuel_mass = tank['FuelMass']
            if fuel_mass or fuel_mass == 0:
                # TODO error catch: handle case of no tank name provided
                self._tanks.append(ElectricTank(tank['name'], self, fuel_mass))
            else:
                self._tanks.append(ElectricTank(tank['name'], self))

    def construct_orbit_state(self, orbit_specs):
        print(f'Orbit specs passed to construct_orbit_state: {orbit_specs}')
        if 'epoch' in orbit_specs:
            print('Epoch found in specs')
            self._epoch = orbit_specs['epoch']
        if 'state_type' in orbit_specs:
            print('State type found in specs')
            self._state_type = orbit_specs['state_type']
        if 'coord_sys' in orbit_specs:
            print(f'Coordinate system found in specs: {orbit_specs["coord_sys"]}')
            self._coord_sys = orbit_specs['coord_sys']
        sc_orbit = OrbitState(self, epoch=self._epoch,
                              state_type=self._state_type,
                              display_state_type=self._display_state_type, )
        # coord_sys=self._coord_sys)


class FiniteBurn(GmatObject):
    def __init__(self, name, sc_to_manoeuvre: Spacecraft, thruster: ElectricThruster):
        # TODO generic: convert thruster type to Thruster once class created
        super().__init__()
        self._name = name
        self._gmat_obj = gmat.Construct('FiniteBurn', self._name)
        self._gmat_obj.SetSolarSystem(gmat.GetSolarSystem())
        self._sc_to_manoeuvre = sc_to_manoeuvre
        self._gmat_obj.SetSpacecraftToManeuver(sc_to_manoeuvre.gmat_object)
        self._thruster = thruster
        self._thruster_name = thruster.GetName()
        self._gmat_obj.SetField('Thrusters', self._thruster_name)

    def BeginFiniteBurn(self, fin_thrust):  # TODO type: add FiniteThrust type to fin_thrust
        finite_thrust.EnableThrust()
        runtime_thruster = sat.gmat_object.GetRefObject(gmat.THRUSTER, self._thruster_name)
        runtime_thruster.SetField("IsFiring", True)


class FiniteThrust(GmatObject):  # TODO tidy: consider making subclass of FiniteBurn
    def __init__(self, name: str, spacecraft: Spacecraft, finite_burn: FiniteBurn):
        super().__init__()
        self._name = name
        self._gmat_obj = gmat.FiniteThrust(name)
        self._spacecraft = spacecraft
        self._finite_burn = finite_burn
        self._gmat_obj.SetRefObjectName(gmat.SPACECRAFT, spacecraft.GetName())
        self._gmat_obj.SetReference(finite_burn.gmat_object)

    # TODO sense: create BeginFiniteBurn method in FiniteBurn that does this and other steps needed to enable thrust
    def EnableThrust(self):
        gmat.ConfigManager.Instance().AddPhysicalModel(self._gmat_obj)


# TODO add parameter parsing to Spacecraft class
sat_params = {
    'name': 'Servicer',
    'gmat_init': False,
    'orbit': {  # TODO: add other orbit params. Cartesian by default
        # 'coord_sys': 'EarthMJ2000Eq sdfsdf',
        'state_type': 'Keplerian',
    },
    'dry_mass': 756,  # kg
    'hardware': {'prop_type': 'EP',  # or 'CP'
                 'tanks': [{'name': 'ElectricTank1', 'FuelMass': 0},
                           {'name': 'ElectricTank2', 'FuelMass': 10}],
                 'thrusters': {'num': 1}}
}

sat = Spacecraft(sat_params)
print('sat specs:')
print(json.dumps(sat.specs, indent=4))
print(sat.specs['orbit'])
gmat.Initialize()
sat.Help()

ep_tank = ElectricTank('EP_Tank', sat)
# print(ep_tank)

ep_thruster = ElectricThruster('EP_Thruster', sat, ep_tank)
# print(ep_thruster)

# gmat.ShowObjects()
# sat.Help()

gmat.Initialize()
ep_thruster.IsInitialized()

ep_thruster.mix_ratio = [1]

burn = FiniteBurn('FiniteBurn1', sat, ep_thruster)
finite_thrust = FiniteThrust('FiniteThrust1', sat, burn)

burn.BeginFiniteBurn(finite_thrust)
