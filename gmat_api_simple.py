import sys
from io import StringIO
from typing import Union
import inspect
import logging

from load_gmat import gmat


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


def get_object_gmat_fields(gmat_obj):
    """
    Get GMAT's list of fields in a GMAT object

    :param gmat_obj:
    :return:
    """
    # Intercept stdout as that's where gmat_obj.Help() goes to
    old_stdout = sys.stdout  # take snapshot of current (normal) stdout
    # create a StringIO object, assign it to obj_help_stringio and set this as the target for stdout
    sys.stdout = obj_help_stringio = StringIO()
    gmat_obj.Help()
    obj_help = obj_help_stringio.getvalue()  # Help() table text as a string

    sys.stdout = old_stdout  # revert back to normal handling of stdout

    rows = obj_help.split('\n')  # split the Help() text into rows for easier parsing
    data_rows = rows[6:]  # first six rows are always headers etc. so remove them
    fields = [None] * len(data_rows)  # create a list to store the fields
    for index, row in enumerate(data_rows):
        row = row[3:]
        row = row.split(' ')[0]
        fields[index] = row

    print(fields)
    return fields


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
    def __init__(self, name: str):  # specs: dict):
        self._allowed_fields = set()

        # TODO: add elements for other orbit states (e.g. 'SMA', 'ECC' for Keplerian) - get OrbitState allowed fields
        self._gmat_allowed_fields = ['NAIFId', 'NAIFIdReferenceFrame', 'SpiceFrameId', 'OrbitSpiceKernelName',
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
        self._allowed_fields.update(self._gmat_allowed_fields,
                                    ['name', 'orbit', 'hardware', 'dry_mass'])

        super().__init__('Spacecraft', name)
        self._dry_mass = None
        self._thrusters = []
        self._tanks = []

        # TODO: consider removing - hides available attrs
        # print('')
        # for key in specs:
        #     print(f'Setting attribute {key}, {specs[key]}')
        #     setattr(self, key, specs[key])  # set object attributes based on passed specs dict
        # print('')

        # self._gmat_obj = gmat.Construct("Spacecraft", specs['name'])

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

        gmat.Initialize()
        # self.update_attrs()

    @classmethod
    def from_dict(cls, specs_dict):
        # TODO remove comment when able
        # See https://stackoverflow.com/questions/12179271/meaning-of-classmethod-and-staticmethod-for-beginner
        # Parse in gmat_init, orbit, hardware from specs_dict

        # TODO: convert all keys to [agreed text case (snake or camel?)]

        try:
            sc = cls(specs_dict['name'])
        except KeyError:
            raise SyntaxError('Spacecraft name required')

        fields = inspect.getfullargspec(Spacecraft.__init__).args[1:]  # get Spacecraft __init__ params, except self
        args = [None] * len(fields)
        for index, field in enumerate(fields):
            try:
                args[index] = specs_dict[field]  # see if the param needed by Spacecraft.__init__ is in specs_dict
            except KeyError:
                print(f'Key {field} not found in the specs_dict passed to Spacecraft.from_dict')
                raise

        # sc = cls(*args)
        #
        # tanks_list = hardware['tanks']
        # if tanks_list:  # the specs listed tanks to be built
        #     self._tanks = []
        #     self.construct_tanks(tanks_list)
        #     # TODO: set GMAT sat Tanks field

        # Find and apply orbit parameters
        try:
            orbit = specs_dict['orbit']
        except KeyError:
            print('No orbit parameters specified in Spacecraft dictionary - using defaults')
            orbit = {}
        sc.construct_orbit_state(orbit)

        # now that the basic spacecraft has been created, set other fields from values in specs_dict
        # TODO handle snake case vs CamelCase difference
        for field in specs_dict:
            print(f'Assessing field: {field}')
            if field not in sc._gmat_allowed_fields:
                print(f'{field} not found in set of GMAT allowed fields')
                if field not in sc._allowed_fields:
                    print(f'{field} not found in set of class allowed fields either')
                    raise NotImplementedError('Error handling for non-allowed fields not implemented')
                else:  # field not allowed by GMAT but allowed by class (further parsing needed)
                    setattr(sc, f'_{field}', specs_dict[field])
            else:  # field is GMAT allowed
                setattr(sc, f'_{field}', specs_dict[field])
                sc.SetField(field, specs_dict[field])

        return sc

    def __repr__(self):
        return f'Spacecraft with name {self._name}'

    def __str__(self):
        return f'Spacecraft with name {self._name}'

    @property
    def dry_mass(self):
        """Return Spacecraft's dry mass"""
        return self._dry_mass

    @dry_mass.setter
    def dry_mass(self, value):
        self._dry_mass = value
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
                self._tanks.append(ElectricTank(tank['name'], self, fuel_mass))
            else:
                self._tanks.append(ElectricTank(tank['name'], self))

    def construct_orbit_state(self, orbit_specs):
        if orbit_specs == {}:  # empty dict was passed
            return

        orbit = OrbitState()
        print(orbit)

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
            print(f'Setting field {class_string_to_GMAT_string(param)} to value {v}')
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
        fin_thrust.EnableThrust()
        sc = 'object that FiniteBurn is applied to'  # TODO complete
        runtime_thruster = sc.gmat_object.GetRefObject(gmat.THRUSTER, self._thruster_name)
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

