from __future__ import annotations

import gmat_py_simple as gpy
from gmat_py_simple import gmat

import sys
from io import StringIO
import logging
import numpy as np


class APIException(Exception):
    pass


def Barycenter() -> list[str]:
    return get_gmat_objects_of_type('Barycenter')


def CelestialBodies() -> list[str]:
    return get_gmat_objects_of_type('CelestialBody')


def class_string_to_GMAT_string(string):
    """
    Convert PEP8-compliant string to GMAT format (CamelCase)
    :param string:
    :return:
    """
    # TODO compare against gmat_str_to_py_str - maybe don't need both
    string_parts_list = [part.capitalize() for part in string.split('_')]
    string = ''.join(string_parts_list)
    if string == 'CoordSys':
        string = 'CoordinateSystem'
    return string


def Construct(obj_type: str, name: str, *args):
    try:
        if args:
            return gmat.Construct(obj_type, name, args)
        else:
            return gmat.Construct(obj_type, name)
    except AttributeError as attr:
        if str(attr) == "'NoneType' object has no attribute 'GetTypeName'":
            raise TypeError(f'GMAT does not recognize the given object type "{obj_type}"')
        else:
            raise attr  # other AttributeErrors are not handled, so raise instead


def CoordSystems() -> list[str]:
    """
    Return GMAT's list of currently defined CoordinateSystems
    :return:
    """
    return get_gmat_objects_of_type('CoordinateSystem')


def CustomHelp(obj):
    print(f'\nCustomHelp for {type(obj).__name__} named "{obj.GetName()}":')
    # print('\nCustomHelp:')
    obj = extract_gmat_obj(obj)
    param_count = obj.GetParameterCount()

    print(f'Object parameter count: {param_count}\n')
    for i in range(param_count):
        try:
            param_name = obj.GetParameterText(i)
            param_type = obj.GetParameterTypeString(i)
            print(f'    Parameter: {param_name}')
            print(f'    - Type: {param_type}')
            if param_type == 'String':
                val = obj.GetStringParameter(i)
            elif param_type == 'StringArray':
                val = obj.GetStringArrayParameter(i)
            elif param_type == 'Integer':
                val = obj.GetIntegerParameter(i)
            elif param_type == 'Object':
                val = obj.GetName()
            elif (param_type == 'Real') or (param_type == 'UnsignedInt') or (param_name == 'InitialEpoch'):
                val = obj.GetRealParameter(i)
            elif param_type == 'Rmatrix':
                val = obj.GetRmatrixParameter(i)
            elif param_type == 'Boolean':
                val = obj.GetBooleanParameter(i)
            else:
                raise TypeError(f'  Unrecognised type: {param_type}')

            print(f'    - Value: {val}\n')

        except Exception as exc:
            print(f'\t{exc}\n')


def extract_gmat_obj(obj):
    obj_type = str(type(obj))
    if obj is None:
        raise SyntaxError('A NoneType object was given')

    if isinstance(obj, gpy.Parameter):
        return obj.gmat_base

    if 'gmat_py_simple' in obj_type:  # wrapper object
        if 'Parameter' in obj_type:
            return obj.gmat_base
        return obj.gmat_obj
    elif 'gmat_py' in obj_type:  # native GMAT object
        return obj
    else:
        raise TypeError(f'obj type not recognised in utils.extract_gmat_obj: {obj_type}')


class GMATNameError(Exception):
    def __init__(self, attempted_name):
        raise RuntimeError(f'No object currently exists in GMAT with the name "{attempted_name}"') from None


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


def generate_script() -> str:
    """
    Return the full GMAT script equivalent of the current file
    :return:
    """
    script = f'globals from gpy: {[item for item in globals().copy().values() if "gmat_py_simple" in str(type(item))]}'
    # TODO complete function
    return script


def get_gmat_classes():
    """
    Get GMAT's list of possible classes

    :return:
    """
    # Intercept stdout as that's where gmat.ShowClasses goes to
    old_stdout = sys.stdout  # take snapshot of current (normal) stdout
    # create a StringIO object, assign it to obj_help_stringio and set as the target for stdout
    sys.stdout = classes_stringio = StringIO()
    gmat.ShowClasses()
    classes_str = classes_stringio.getvalue()  # Help() table text as a string

    sys.stdout = old_stdout  # revert back to normal handling of stdout

    rows: list = classes_str.split('\n')  # split the Help() text into rows for easier parsing
    classes = [None] * len(rows)  # create a list to store the fields
    for index, row in enumerate(rows):
        row = row[3:]
        classes[index] = row

    classes = list(filter(None, classes))  # filter out any empty strings
    return classes


def get_gmat_objects_of_type(obj_type: str) -> list[str]:
    """
    Return GMAT's list of currently defined objects of a given type
    :param obj_type:
    :return:
    """
    # Intercept stdout as that's where gmat.Showcoord_syses goes to
    old_stdout = sys.stdout  # take snapshot of current (normal) stdout
    # create a StringIO object, assign it to objs_stringio and set as the target for stdout
    sys.stdout = objs_stringio = StringIO()
    gmat.ShowObjects(obj_type)
    objs_str: str = objs_stringio.getvalue()  # ShowObjects() table text as a string

    sys.stdout = old_stdout  # revert back to normal handling of stdout

    rows: list[str] = objs_str.split('\n')  # split the returned text into rows for easier parsing
    data_rows: list[str] = rows[2:]  # first two rows are always title and blank so remove them
    coord_syses: list[str | None] = [None] * len(data_rows)  # create a list to store the coord_syses
    for index, row in enumerate(data_rows):
        row = row[3:]  # remove indent
        coord_syses[index] = row

    coord_syses = list(filter(None, coord_syses))  # filter out any empty strings
    return coord_syses


def get_sat_names() -> list[str]:
    return [sat.lstrip() for sat in gmat.ShowObjectsForID(gmat.SPACECRAFT).split('\n')[2:-1]]


def get_sat_objects() -> list[gmat.Spacecraft]:
    # TODO tidy: duplicate of SpacecraftObjs, also similar to get_sat_names()
    sat_names = get_sat_names()
    sat_objs = [None] * len(sat_names)
    for index, name in enumerate(sat_names):
        try:
            # See if there's a RuntimeObject for the sat, to use its latest info
            sat_objs[index]: gmat.GmatBase = gmat.GetRuntimeObject(name)

        except Exception as exc:
            if 'Sandbox Exception: Sandbox::GetInternalObject(' in str(exc):
                logging.info('No Runtime Object for sat - using GetObject instead')
                try:
                    sat_objs[index] = gmat.GetObject(name)
                except Exception:
                    raise
            else:
                raise
    print(f'sat_objs: {sat_objs}')
    return sat_objs


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


def get_type_name_from_id(type_id: int) -> str:
    type_names = ['SPACECRAFT',
                  'FORMATION',
                  'SPACEOBJECT',
                  'GROUND_STATION',
                  'PLATE',
                  'BURN',
                  'IMPULSIVE_BURN',
                  'FINITE_BURN',
                  'COMMAND',
                  'PROPAGATOR',
                  'ODE_MODEL',
                  'PHYSICAL_MODEL',
                  'TRANSIENT_FORCE',
                  'INTERPOLATOR',
                  'SOLAR_SYSTEM',
                  'SPACE_POINT',
                  'CELESTIAL_BODY',
                  'CALCULATED_POINT',
                  'LIBRATION_POINT',
                  'BARYCENTER',
                  'ATMOSPHERE',
                  'PARAMETER',
                  'VARIABLE',
                  'ARRAY',
                  'STRING',
                  'STOP_CONDITION',
                  'SOLVER',
                  'SUBSCRIBER',
                  'REPORT_FILE',
                  'XY_PLOT',
                  'ORBIT_VIEW',
                  'DYNAMIC_DATA_DISPLAY',
                  'EPHEMERIS_FILE',
                  'PROP_SETUP',
                  'FUNCTION',
                  'FUEL_TANK',
                  'THRUSTER',
                  'CHEMICAL_THRUSTER',
                  'ELECTRIC_THRUSTER',
                  'CHEMICAL_FUEL_TANK',
                  'ELECTRIC_FUEL_TANK',
                  'FIELD_OF_VIEW',
                  'CONICAL_FOV',
                  'RECTANGULAR_FOV',
                  'CUSTOM_FOV',
                  'POWER_SYSTEM',
                  'SOLAR_POWER_SYSTEM',
                  'NUCLEAR_POWER_SYSTEM',
                  'HARDWARE',
                  'COORDINATE_SYSTEM',
                  'AXIS_SYSTEM',
                  'ATTITUDE',
                  'MATH_NODE',
                  'MATH_TREE',
                  'BODY_FIXED_POINT',
                  'EVENT',
                  'EVENT_LOCATOR',
                  'DATAINTERFACE_SOURCE',
                  'MEASUREMENT_MODEL',
                  'ERROR_MODEL',
                  'DATASTREAM',
                  'DATA_FILE',
                  'OBTYPE',
                  'DATA_FILTER',
                  'INTERFACE',
                  'MEDIA_CORRECTION',
                  'IMAGER',
                  'SENSOR',
                  'RF_HARDWARE',
                  'ANTENNA',
                  'THRUST_SEGMENT',
                  'REGION',
                  'USER_DEFINED_OBJECT',
                  'USER_OBJECT_ID_NEEDED',
                  'GENERIC_OBJECT',
                  'UNKNOWN_OBJECT',
                  'SCRIPTING',
                  'SHOW_SCRIPT',
                  'OWNED_OBJECT',
                  'MATLAB_STRUCT',
                  'EPHEM_HEADER',
                  'NO_COMMENTS',
                  'DEBUG_INSPECT',
                  'GUI_EDITOR',
                  'OBJECT_EXPORT',
                  'UNKNOWN_STATE',
                  'CARTESIAN_STATE',
                  'EQUINOCTIAL_STATE',
                  'ORBIT_STATE_TRANSITION_MATRIX',
                  'ORBIT_A_MATRIX',
                  'ORBIT_COVARIANCE_MATRIX',
                  'CD_EPSILON',
                  'ATMOS_DENSITY_EPSILON',
                  'MASS_FLOW',
                  'PREDEFINED_STATE_MAX',
                  'USER_DEFINED_BEGIN',
                  'USER_DEFINED_END',
                  'INTEGER_TYPE',
                  'UNSIGNED_INT_TYPE',
                  'UNSIGNED_INTARRAY_TYPE',
                  'INTARRAY_TYPE',
                  'REAL_TYPE',
                  'REALARRAY_TYPE',
                  'REAL_ELEMENT_TYPE',
                  'STRING_TYPE',
                  'STRINGARRAY_TYPE',
                  'BOOLEAN_TYPE',
                  'BOOLEANARRAY_TYPE',
                  'RVECTOR_TYPE',
                  'RMATRIX_TYPE',
                  'TIME_TYPE',
                  'OBJECT_TYPE',
                  'OBJECTARRAY_TYPE',
                  'ON_OFF_TYPE',
                  'ENUMERATION_TYPE',
                  'FILENAME_TYPE',
                  'COLOR_TYPE',
                  'GMATTIME_TYPE',
                  'GENERIC_TYPE',
                  'EQUATION_TYPE',
                  'TypeCount',
                  'UNKNOWN_PARAMETER_TYPE',
                  'PARAMETER_REMOVED',
                  'ERROR_',
                  'WARNING_',
                  'INFO_',
                  'DEBUG_',
                  'GENERAL_',
                  'IDLE',
                  'RUNNING',
                  'PAUSED',
                  'TARGETING',
                  'OPTIMIZING',
                  'ESTIMATING',
                  'SOLVING',
                  'SOLVEDPASS',
                  'WAITING',
                  'CREATED',
                  'CONVERGED',
                  'COPIED',
                  'INITIALIZED',
                  'RUN',
                  'EXCEEDED_ITERATIONS',
                  'FAILED',
                  'UNKNOWN_STATUS',
                  'NUMBER_WT',
                  'VECTOR_WT',
                  'MATRIX_WT',
                  'STRING_WT',
                  'STRING_OBJECT_WT',
                  'OBJECT_PROPERTY_WT',
                  'VARIABLE_WT',
                  'ARRAY_WT',
                  'ARRAY_ELEMENT_WT',
                  'PARAMETER_WT',
                  'OBJECT_WT',
                  'BOOLEAN_WT',
                  'INTEGER_WT',
                  'ON_OFF_WT',
                  'EQUATION_WT',
                  'UNKNOWN_WRAPPER_TYPE',
                  'SUNDAY',
                  'MONDAY',
                  'TUESDAY',
                  'WEDNESDAY',
                  'THURSDAY',
                  'FRIDAY',
                  'SATURDAY',
                  'JANUARY',
                  'FEBRUARY',
                  'MARCH',
                  'APRIL',
                  'MAY',
                  'JUNE',
                  'JULY',
                  'AUGUST',
                  'SEPTEMBER',
                  'OCTOBER',
                  'NOVEMBER',
                  'DECEMBER',
                  'PLUS',
                  'MINUS',
                  'MERCURY',
                  'VENUS',
                  'EARTH',
                  'MARS',
                  'JUPITER',
                  'SATURN',
                  'URANUS',
                  'NEPTUNE',
                  'PLUTO',
                  'NumberOfDefaultPlanets',
                  'LUNA',
                  'NumberOfDefaultMoons']
    for name in type_names:
        if eval(f'gmat.{name}') == type_id:
            return name

    raise RuntimeError(f'Type name could not be found for ID {type_id}')


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


def gmat_liststr_to_python_liststr(string_list: list[str], is_attr_list: bool = False) -> list[str]:
    for index, string in enumerate(string_list):
        new_string = gmat_str_to_py_str(string, is_attr_list)
        string_list[index] = new_string

    return string_list


def gmat_obj_field_list(gmat_obj):
    gmat_obj = gpy.extract_gmat_obj(gmat_obj)

    fields = []
    for i in range(gmat_obj.GetParameterCount()):
        try:
            field_str: str = gmat_obj.GetParameterText(i)
            field = field_str.replace('\n', '')
            fields.append(field)
            i += 1

        except Exception as e:
            if type(e).__name__ == 'APIException':
                break
            else:
                raise

    return fields


def gmat_str_to_py_str(string: str, is_attr: bool = False) -> str:
    new_string = ''
    chars_added = 0
    for i, char in enumerate(string):
        if char.isupper():
            new_string = new_string[0:i + chars_added + 1] + '_' + char.lower()
            chars_added += 1
        else:
            new_string = new_string + char

    if not is_attr:  # don't want leading underscores
        if new_string[0] == '_':
            new_string = new_string[1:]

    return new_string


def GroundStations() -> list[str]:
    return get_gmat_objects_of_type('GroundStation')


def hamilton_product(p: np.ndarray, q: np.ndarray) -> np.array:
    """
    Multiply two quaternions, assuming each has scalar part as final element.
    :param p:
    :param q:
    :return:
    """
    p1, p2, p3, p4 = p[0:4]
    m = np.array([[p4, -p3, p2, p1],
                  [p3, p4, -p1, p2],
                  [-p2, p1, p4, p3],
                  [-p1, -p2, -p3, p4]])
    result = np.matmul(m, q)
    return result


def LibrationPoints() -> list[str]:
    return get_gmat_objects_of_type('LibrationPoint')


def list_to_gmat_field_string(data_list: list) -> str:
    """
    Convert a Python list to a format that GMAT can handle in SetField
    :param data_list:
    :return string:
    """
    if data_list is not []:  # Python list contains at least one item
        string = ', '.join(data_list)  # convert the list to a string, with a comma between each item
        # if len(data_list) > 1:
        #     string = '{' + string + '}'  # add curly braces for GMAT to interpret as a list

    else:  # Python list is empty
        string = '{}'

    return string


def ls2str(py_list: list) -> str:
    """
    Convert a Python list to a string.
    :param py_list: a Python list
    :return: a Python string
    """
    return str(py_list)[1:-1]


def python_liststr_to_gmat_liststr(string_list: list[str]) -> list[str]:
    for index, string in enumerate(string_list):
        string_list[index] = py_str_to_gmat_str(string)  # convert each string and put it back in the list
    return string_list


def py_str_to_gmat_str(string: str) -> str:
    string = string.replace('_', ' ')  # replace each underscore with a space
    string = string.title()  # set first letter of each word to upper case
    string = string.replace(' ', '')  # remove spaces
    return string


# Line below disables false positive "This code is unreachable" warning with np.cross()
# noinspection PyUnreachableCode
def quat_between_vecs(v1: np.ndarray, v2: np.ndarray) -> np.ndarray:
    """
    Find a quaternion representing the shortest-path transformation between two vectors.
    :param v1: a 3-element np.ndarray representing the starting vector
    :param v2: a 3-element np.ndarray representing the final vector
    :return: quaternion that rotates from v1 to v2
    """
    # cross product below to find quat vector part cannot be found if vectors parallel/antiparallel, so check
    check_dot = np.dot(v1, v2)
    if np.isclose(check_dot, 1):  # v1 and v2 are parallel
        return np.array([0, 0, 0, 1])  # identity quaternion to cause no rotation
    elif np.isclose(check_dot, -1):  # v1 and v2 are antiparallel
        return np.array([1, 0, 0, 0])  # quaternion for 180-degree rotation around arbitrary axis

    q_xyz = np.cross(v1, v2)  # quat vector part is cross product of old and new boresights
    mag_v1 = np.linalg.norm(v1)
    mag_v2 = np.linalg.norm(v2)
    q_w = np.sqrt((mag_v1 ** 2) * (mag_v2 ** 2)) + np.dot(v1, v2)
    quat: np.ndarray = np.append(np.array(q_xyz), q_w)  # q = (qx, qy, qz, qw), where qw is scalar part

    return quat


def rotate_vector(vec: np.ndarray | list, axis: str, angle: int | float) -> np.ndarray:
    if axis == 'X':
        new_vec = gpy.rotx(vec, angle)
    elif axis == 'Y':
        new_vec = gpy.roty(vec, angle)
    elif axis == 'Z':
        new_vec = gpy.rotz(vec, angle)
    else:
        raise RuntimeError(f'Rotation axis to get normal vector, "{axis}", is not recognized.')
    return new_vec


def rotx(vec: np.ndarray | list, angle: int | float) -> np.ndarray:
    """
    Rotate a 3-element vector around the X-axis by an angle
    :param vec:
    :param angle:
    :return:
    """
    if len(vec) != 3:
        raise AttributeError(f'Invalid vector length ({len(vec)}) - must be 3')

    # Aliases to help readability and execution speed
    ca = np.cos(angle)
    sa = np.sin(angle)

    rotation_matrix = np.array([[1, 0, 0],
                                [0, ca, -sa],
                                [0, sa, ca]])

    new_vec = np.matmul(rotation_matrix, vec)
    return new_vec


def roty(vec: np.ndarray | list, angle: int | float) -> np.ndarray:
    """
    Rotate a 3-element vector around the Y-axis by an angle
    :param vec:
    :param angle:
    :return:
    """
    if len(vec) != 3:
        raise AttributeError(f'Invalid vector length ({len(vec)}) - must be 3')

    # Aliases to help readability and execution speed
    ca = np.cos(angle)
    sa = np.sin(angle)

    rotation_matrix = np.array([[ca, 0, sa],
                                [0, 1, 0],
                                [-sa, 0, ca]])

    new_vec = np.matmul(rotation_matrix, vec)
    return new_vec


def rotz(vec: np.ndarray | list, angle: int | float) -> np.ndarray:
    """
    Rotate a 3-element vector around the Z-axis by an angle
    :param vec:
    :param angle:
    :return:
    """
    if len(vec) != 3:
        raise AttributeError(f'Invalid vector length ({len(vec)}) - must be 3')

    # Aliases to help readability and execution speed
    ca = np.cos(angle)
    sa = np.sin(angle)

    rotation_matrix = np.array([[ca, -sa, 0],
                                [sa, ca, 0],
                                [0, 0, 1]])

    new_vec = np.matmul(rotation_matrix, vec)
    return new_vec


def rvector6_to_list(rv6) -> list[float | int]:
    rv6_str: str = str(rv6)
    list_str = rv6_str.split(' ')
    ele_strs = [string for string in list_str if string != '']  # remove all the empty strings
    eles_list: list[None | float | int] = [None] * 6
    for index, ele in enumerate(ele_strs):
        try:
            num = float(ele)  # convert string to float
        except ValueError:  # number is likely an int
            num = int(ele)  # convert string to int
        eles_list[index] = num

    return eles_list


def SpacecraftObjs() -> list[str]:
    return get_gmat_objects_of_type('Spacecraft')


def transform_vec_quat(vec: np.ndarray, quat: np.ndarray) -> np.ndarray:
    """
    Rotate a vector using a quaternion and return the resulting vector.

    :param vec:
    :param quat:
    :return:
    """
    vec = np.append(vec, 0)

    q_norm = quat / np.sqrt(sum(quat ** 2))
    q_conj_xyz: np.ndarray = np.array([-e for e in q_norm[0:3]])
    quat_conj: np.ndarray = np.append(q_conj_xyz, q_norm[3])  # negative of vector parts, scalar part same as q_

    new_a = gpy.hamilton_product(quat, vec)
    final_prod = gpy.hamilton_product(new_a, quat_conj)
    new_vec = np.delete(final_prod / np.linalg.norm(final_prod), 3)

    return new_vec


def vectors_orthogonal(vec1: np.ndarray, vec2: np.ndarray) -> bool:
    """
    Return True if the two vectors are orthogonal, False otherwise.

    :param vec1: 3-element np.ndarray
    :param vec2: 3-element np.ndarray
    :return: True if the two vectors are orthogonal, False otherwise.
    """
    return True if np.dot(vec1, vec2) == 0 else False
