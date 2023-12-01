from __future__ import annotations

from load_gmat import gmat

from typing import Union

prop_types = ['Chemical', 'Electric']


class GmatObject:
    def __init__(self, obj_type: str, name: str, *args):
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
