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


class Orbit:
    def __init__(self):
        pass


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
        # TODO feature: allow passing of arguments as a dictionary, so a dict for Spacecraft that contains
        #  one for Thrusters too
        # self._name = self._specs['name']
        self._gmat_obj = gmat.Construct("Spacecraft", specs['name'])

        for key in specs:
            setattr(self, key, specs[key])

        tanks_list = specs['hardware']['tanks']
        if tanks_list:  # the specs listed tanks to be built
            self._tanks = []
            print('Making tanks...')
            print(f'Number of tanks to make: {len(tanks_list)}')
            self.construct_tanks()
            # TODO: set GMAT sat Tanks field

        # if thrusters is None:
        #     thrusters = {"number": 0, "names": ["Jeff", "Cheers"], }
        # self._name = name
        # self._orbit = orbit
        # self._gmat_obj = gmat_object
        # if orbit:
        #     # use passed orbit params (args)
        #     pass
        if self._specs['gmat_init']:
            gmat.Initialize()

        # if thrusters:
        #     thruster = gmat.Construct('ElectricThruster', 'EP_Thrust1')
        #
        #     return
        #     # TODO feature: add parsing of thruster dict
        #     for index, thruster in range(thrusters["number"]):
        #         if thrusters["number"] != len(thrusters["names"]):
        #             raise SyntaxError('Number of thrusters specified does not match number of names provided')
        #         thrusters_list = [gmat.Construct("Thruster", thruster["names"][index])]

    def __repr__(self):
        return f'Spacecraft with name {self._name} and specifications:\n{json.dumps(self._specs, indent=4)}'

    def __str__(self):
        return f'Spacecraft with name {self._name}'

    @property
    def specs(self):
        return self._specs

    def construct_tanks(self, tanks_list):
        for index, tank in enumerate(tanks_list):
            fuel_mass = tank['FuelMass']
            if fuel_mass or fuel_mass == 0:
                self._tanks.append(ElectricTank(tank['name'], self, fuel_mass))
            else:
                self._tanks.append(ElectricTank(tank['name'], self))
        print(self._tanks)


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
    'orbit': {
        'state_type': 'Cartesian',
        '[other params]': None  # TODO: add orbit params. Cartesian by default
    },
    'dry_mass': 756,  # kg
    'hardware': {'prop_type': 'EP',  # or 'CP'
                 'tanks': [{'name': 'ElectricTank1', 'FuelMass': 0},
                           {'name': 'ElectricTank2', 'FuelMass': 10}],
                 'thrusters': {'num': 1}}
}

sat = Spacecraft(sat_params)
# print(json.dumps(sat.specs, indent=4))

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
