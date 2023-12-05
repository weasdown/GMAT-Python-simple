from __future__ import annotations

from load_gmat import gmat

import sys
from io import StringIO


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
    # Intercept stdout as that's where gmat.ShowClasses goes to
    old_stdout = sys.stdout  # take snapshot of current (normal) stdout
    # create a StringIO object, assign it to obj_help_stringio and set as the target for stdout
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
    objs_str = objs_stringio.getvalue()  # ShowObjects() table text as a string

    sys.stdout = old_stdout  # revert back to normal handling of stdout

    rows = objs_str.split('\n')  # split the returned text into rows for easier parsing
    data_rows = rows[2:]  # first two rows are always title and blank so remove them
    coord_syses = [None] * len(data_rows)  # create a list to store the coord_syses
    for index, row in enumerate(data_rows):
        row = row[3:]  # remove indent
        coord_syses[index] = row

    coord_syses = list(filter(None, coord_syses))  # filter out any empty strings
    return coord_syses


def CoordSystems() -> list[str]:
    """
    Return GMAT's list of currently defined CoordinateSystems
    :return:
    """
    return get_gmat_objects_of_type('CoordinateSystem')


def CelestialBodies() -> list[str]:
    return get_gmat_objects_of_type('CelestialBody')


def SpacecraftObjs() -> list[str]:
    return get_gmat_objects_of_type('Spacecraft')


def LibrationPoints() -> list[str]:
    return get_gmat_objects_of_type('LibrationPoint')


def Barycenter() -> list[str]:
    return get_gmat_objects_of_type('Barycenter')


def GroundStations() -> list[str]:
    return get_gmat_objects_of_type('GroundStation')


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


def py_str_to_gmat_str(string: str) -> str:
    string = string.replace('_', ' ')  # replace each underscore with a space
    string = string.title()  # set first letter of each word to upper case
    string = string.replace(' ', '')  # remove spaces
    return string


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


def python_liststr_to_gmat_liststr(string_list: list[str]) -> list[str]:
    for index, string in enumerate(string_list):
        string_list[index] = py_str_to_gmat_str(string)  # convert each string and put it back in the list
    return string_list


def gmat_liststr_to_python_liststr(string_list: list[str], is_attr_list: bool = False) -> list[str]:
    for index, string in enumerate(string_list):
        new_string = gmat_str_to_py_str(string, is_attr_list)
        string_list[index] = new_string

    return string_list


def ls2str(py_list: list) -> str:
    """
    Convert a list to a string
    :param py_list:
    :return:
    """
    # return ', '.join(py_list)
    return str(py_list)[1:-1]


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


def gmat_obj_field_list(gmat_obj):
    fields = []
    for i in range(1000):
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
