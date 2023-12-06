from __future__ import annotations

from load_gmat import gmat

from typing import Union


class GmatObject:
    def __init__(self, obj_type: str, name: str):
        self.obj_type = obj_type
        self.name = name
        self.gmat_obj = gmat.Construct(self.obj_type, self.name)

    # @staticmethod
    # def Construct(obj_type: str, name: str, *args):
    #     """
    #     Make a GMAT object when Construct takes more than two arguments (e.g. for CoordinateSystem)
    #     :param obj_type:
    #     :param name:
    #     :param args:
    #     :return:
    #     """
    #     print(f"Running gmat.Construct({obj_type}, {name}, *{args})")
    #     # return gmat.Construct(obj_type, name, *args)

    @classmethod
    def from_gmat_obj(cls, obj):
        return cls(type(obj).__name__, obj.GetName())

    @staticmethod
    def get_name_from_kwargs(obj_type: object, kwargs: dict) -> str:
        try:
            name: str = kwargs['name']
        except KeyError:
            raise SyntaxError(f"Required field 'name' not provided when building {type(obj_type).__name__} object")
        return name

    def GetName(self):
        return self.gmat_obj.GetName()

    def SetName(self, name: str):
        self.gmat_obj.SetName(name)

    def Help(self):
        # TODO: upgrade to get list of fields with utils.gmat_obj_field_list then print all fields/values

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

    def SetOnOffParameter(self, field: str, OnOff: str):
        if (OnOff == 'On') or (OnOff == 'Off'):
            self.gmat_obj.SetOnOffParameter(field, OnOff)
        else:
            raise SyntaxError(f'Invalid argument OnOff - {OnOff} - must be "On" or "Off"')

    def SetReference(self, ref):
        if 'gmat_py.' not in str(type(ref)):  # wrapper object
            self.gmat_obj.SetReference(ref.gmat_obj)
        else:  # native GMAT object
            self.gmat_obj.SetReference(ref)

    def GetState(self):
        return self.gmat_obj.GetState()

    def GetGeneratingString(self) -> str:
        """
        Return the GMAT script equivalent of an object
        :return:
        """
        return self.gmat_obj.GetGeneratingString()


class HardwareItem(GmatObject):
    def __init__(self, obj_type: str, name: str):
        super().__init__(obj_type, name)

    def __repr__(self):
        return f'A piece of Hardware of type {self.obj_type} and name {self.name}'

    def IsInitialized(self):
        self.gmat_obj.IsInitialized()


class Parameter(GmatObject):
    # TODO: see src/base/parameter/Parameter.cpp
    #  key should be type ParameterKey, from GmatParam
    def __init__(self, name: str = 'Param', type_str: str = None, key: str = None, owner: str = None, desc: str = None,
                 unit: str = None, dep_obj: str = None, owner_type: int = None, is_time_param: bool = False,
                 is_settable: bool = False, is_plottable: bool = False, is_reportable: bool = False,
                 owned_obj_type: int = None):
        super().__init__('Parameter', name)


class GmatCommand:
    def __init__(self, obj_type: str):
        self.obj_type = obj_type
        self.gmat_obj = gmat.Construct(self.obj_type)

    def GetGeneratingString(self) -> str:
        return self.gmat_obj.GetGeneratingString()

    def GetField(self, field: str):
        self.gmat_obj.GetField(field)

    def SetField(self, field: str, val: str | list | int | float):
        self.gmat_obj.SetField(field, val)

    # def Help(self):
    #     self.gmat_obj.Help()
