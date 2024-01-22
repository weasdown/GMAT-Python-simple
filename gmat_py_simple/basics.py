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

    @staticmethod
    def epoch_to_datetime(epoch: str) -> datetime:
        return datetime.strptime(epoch, '%d %b %Y %H:%M:%S.%f')

    @classmethod
    def from_gmat_obj(cls, obj):
        return cls(type(obj).__name__, obj.GetName())

    def GetEpoch(self, as_datetime: bool = False) -> str | datetime:
        self.gmat_obj = self.GetObject()  # update object's gmat_obj with latest data (e.g. from mission run)
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

    def GetIntegerParameter(self, param: str | int) -> int:
        if isinstance(param, str):
            param = self.GetParameterID(param)
        return gpy.extract_gmat_obj(self).GetIntegerParameter(param)

    def GetObject(self: gpy.GmatObject):
        """
        Return the latest version of an object so its state info is up-to-date
        :return:
        """
        try:
            if not self.was_propagated:  # sat not yet propagated
                return gmat.GetObject(self._name)
            elif self.was_propagated:  # sat has been propagated - gmat.GetObject() would return incorrect values
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

    def GetParameterID(self, param_name: str) -> int:
        return gpy.extract_gmat_obj(self).GetParameterID(param_name)

    def GetParameterType(self, param: str | int) -> str:
        if isinstance(param, str):
            param = self.GetParameterID(param)
        type_id: int = gpy.extract_gmat_obj(self).GetParameterType(param)
        type_string: str = gpy.utils.GetTypeNameFromID(type_id)
        return type_string

    def GetRealParameter(self, param: str | int) -> float:
        if isinstance(param, str):
            param = self.GetParameterID(param)
        return gpy.extract_gmat_obj(self).GetRealParameter(param)

    def GetRefObject(self, type_id: int, name: str) -> gmat.GmatBase:
        return gpy.extract_gmat_obj(self).GetRefObject(type_id, name)

    def GetRefObjectName(self, type_id: int) -> str:
        return gpy.extract_gmat_obj(self).GetRefObjectName(type_id)

    def GetRefObjectNameArray(self, type_id: int) -> tuple[str]:
        return gpy.extract_gmat_obj(self).GetRefObjectNameArray(type_id)

    def GetRefObjectTypeArray(self) -> tuple[int]:
        return gpy.extract_gmat_obj(self).GetRefObjectTypeArray()

    def GetStringParameter(self, param: str | int) -> str:
        if isinstance(param, str):
            param = self.GetParameterID(param)
        return gpy.extract_gmat_obj(self).GetStringParameter(param)

    def Help(self):
        # TODO: upgrade to get list of fields with utils.gmat_obj_field_list then print all fields/values
        return gpy.extract_gmat_obj(self).Help()

    def Initialize(self):
        try:
            return gpy.extract_gmat_obj(self).Initialize()
        except Exception as ex:
            raise RuntimeError(f'{type(self).__name__} named "{self.name}" failed to Initialize - see exception '
                               f'below:\n\t{ex}') from ex

    def IsInitialized(self):
        return self.gmat_obj.IsInitialized()

    def SetBooleanParameter(self, param: str | int, value: bool) -> bool:
        if isinstance(param, str):
            param = self.GetParameterID(param)
        return gpy.extract_gmat_obj(self).SetBooleanParameter(param, value)

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

    def SetOnOffParameter(self, field: str, on_off: str):
        if (on_off == 'On') or (on_off == 'Off'):
            self.gmat_obj.SetOnOffParameter(field, on_off)
        else:
            raise SyntaxError(f'Invalid argument OnOff - {on_off} - must be "On" or "Off"')

    def SetRealParameter(self, param: str | int, value: int | float) -> bool:
        if isinstance(param, str):
            param = self.GetParameterID(param)
        return gpy.extract_gmat_obj(self).SetRealParameter(param, value)

    def SetReference(self, ref):
        self.gmat_obj.SetReference(gpy.extract_gmat_obj(ref))

    def SetRefObject(self, obj: gpy.GmatObject | gmat.GmatObject, type_id: int, name: str) -> bool:
        return gpy.extract_gmat_obj(self).SetRefObject(gpy.extract_gmat_obj(obj), type_id, name)

    def SetSolarSystem(self, ss: gmat.SolarSystem = gmat.GetSolarSystem()) -> bool:
        return self.gmat_obj.SetSolarSystem(ss)

    def SetStringParameter(self, param: str | int, value: str) -> bool:
        if isinstance(param, str):
            param = self.GetParameterID(param)
        return gpy.extract_gmat_obj(self).SetStringParameter(param, value)

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

