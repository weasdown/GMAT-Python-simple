from __future__ import annotations

import gmat_py_simple as gpy
from load_gmat import gmat

from typing import Union
from datetime import datetime


class GmatObject:
    # TODO: addition of self.gmat_runtime to sat means need to check any functions that call gmat_obj (particularly
    #  properties/setters) to see if they should use gmat_runtime instead
    def __init__(self, obj_type: str, name: str):
        self.obj_type = obj_type
        self._name = name

        self.gmat_obj = gmat.Construct(self.obj_type, self._name)
        self.gmat_obj.SetSolarSystem(gmat.GetSolarSystem())
        self.was_propagated = False

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

    @staticmethod
    def epoch_to_datetime(epoch: str) -> datetime:
        return datetime.strptime(epoch, '%d %b %Y %H:%M:%S.%f')

    @classmethod
    def from_gmat_obj(cls, obj):
        return cls(type(obj).__name__, obj.GetName())

    def GetEpoch(self, as_datetime: bool = False) -> str | datetime:
        epoch_str: str = self.GetField('Epoch')
        if not as_datetime:
            return epoch_str
        else:
            epoch_datetime: datetime = self.epoch_to_datetime(epoch_str)
            return epoch_datetime

    def GetField(self, field: str | int) -> str:
        """
        Get the value of a field in the Object's GMAT model.

        :param field:
        :return:
        """
        return self.gmat_obj.GetField(field)

    def GetGeneratingString(self) -> str:
        """
        Return the GMAT script commands to form an object
        :return:
        """
        return self.gmat_obj.GetGeneratingString()

    def GetObject(self):
        """
        Return the latest version of an object so its state info is up-to-date
        :return:
        """
        try:
            if not self.was_propagated:  # sat not yet propagated
                return gmat.GetObject(self._name)
            else:  # sat has been propagated so gmat.GetObject() would return incorrect (starting) values
                return gmat.GetRuntimeObject(self._name)

        except AttributeError:  # object may not have a self.was_propagated attribute
            print(f'**Warning** Object {self.name} of type {self.gmat_obj.GetTypeName()} does not have an attribute '
                  f'self.was_propagate. GetObject() is using gmat.GetObject() instead')
            return gmat.GetObject(self._name)

    def GetName(self):
        return self._name

    @staticmethod
    def get_name_from_kwargs(obj_type: object, kwargs: dict) -> str:
        try:
            name: str = kwargs['name']
        except KeyError:
            raise SyntaxError(f"Required field 'name' not provided when building {type(obj_type).__name__} object")
        return name

    def Help(self):
        # TODO: upgrade to get list of fields with utils.gmat_obj_field_list then print all fields/values

        if not self.gmat_obj:
            raise AttributeError(f'No GMAT object found for object {self.__name__} of type {type(self.__name__)}')
        self.gmat_obj.Help()

    def Initialize(self):
        try:
            return self.gmat_obj.Initialize()
        except Exception as ex:
            raise RuntimeError(f'{type(self).__name__} named "{self.name}" failed to Initialize - see GMAT exception '
                               f'above') from ex

    def IsInitialized(self):
        self.gmat_obj.IsInitialized()

    def SetField(self, field: str, val: str | int | float | bool | list):
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

    def SetName(self, name: str):
        self.gmat_obj.SetName(name)

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

    def SetSolarSystem(self, ss: gmat.SolarSystem = gmat.GetSolarSystem()) -> bool:
        return self.gmat_obj.SetSolarSystem(ss)

    def Validate(self) -> bool:
        try:
            return self.gmat_obj.Validate()
        except Exception as ex:
            raise RuntimeError(f'{type(self).__name__} named "{self.name}" failed to Validate - see GMAT exception above') \
                from ex

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, new_name: str):
        self._name = new_name
        self.gmat_obj.SetName(new_name)

