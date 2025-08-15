from __future__ import annotations

import gmat_py_simple as gpy
from load_gmat import gmat

from datetime import datetime


class GmatObject:
    # TODO: addition of self.gmat_runtime to sat means need to check any functions that call gmat_obj (particularly
    #  properties/setters) to see if they should use gmat_runtime instead
    def __init__(self, obj_type: str, name: str):
        self.obj_type = obj_type
        self._name = name
        self.gmat_obj = gpy.Construct(self.obj_type, self._name)
        self.gmat_obj.SetSolarSystem(gmat.GetSolarSystem())
        self.was_propagated = False

    @staticmethod
    def epoch_to_datetime(epoch: str) -> datetime:
        return datetime.strptime(epoch, '%d %b %Y %H:%M:%S.%f')

    @classmethod
    def from_gmat_obj(cls, obj):
        return cls(type(obj).__name__, obj.GetName())

    def GetBooleanParameter(self, param: str | int) -> bool:
        if isinstance(param, str):
            param = self.GetParameterID(param)
        return gpy.extract_gmat_obj(self).GetBooleanParameter(param)

    def GetEpoch(self, as_datetime: bool = False) -> str | datetime:
        if isinstance(self, gpy.Spacecraft):
            self.gmat_obj.TakeAction('UpdateEpoch')
        up_to_date_obj = self.GetObject()
        # FIXME: inaccurate for Mars in Tut04
        if as_datetime:
            up_to_date_obj.SetField('DateFormat', 'UTCGregorian')
            epoch_str: str = up_to_date_obj.GetField('Epoch')
            epoch_datetime: datetime = self.epoch_to_datetime(epoch_str)
            return epoch_datetime
        else:
            epoch_str: str = up_to_date_obj.GetField('Epoch')
            return epoch_str

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

    def GetObject(self):
        return gpy.GetObject(self)

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

    def GetParameterType(self, param: str | int) -> int:
        if isinstance(param, str):
            param = self.GetParameterID(param)
        return gpy.extract_gmat_obj(self).GetParameterType(param)

    def GetParameterTypeString(self, param: str | int) -> str:
        if isinstance(param, str):
            param = self.GetParameterID(param)
        return gpy.extract_gmat_obj(self).GetParameterTypeString(param)

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

    def GetTypeName(self) -> str:
        return gpy.extract_gmat_obj(self).GetTypeName()

    def Help(self):
        # TODO: upgrade to get list of fields with utils.gmat_obj_field_list then print all fields/values
        self_gmat = self.GetObject()  # update with data from RuntimeObject if necessary
        return self_gmat.Help()

    def Initialize(self):
        try:
            return gpy.extract_gmat_obj(self).Initialize()
        except Exception as ex:
            raise RuntimeError(f'{type(self).__name__} named "{self.name}" failed to Initialize - see exception '
                               f'below:\n\t{ex}') from ex

    def IsInitialized(self):
        return self.gmat_obj.IsInitialized()

    def IsOfType(self, type_name: str | int) -> bool:
        return self.gmat_obj.IsOfType(type_name)

    def SetBooleanParameter(self, param: str | int, value: bool) -> bool:
        if isinstance(param, str):
            param = self.GetParameterID(param)
        return gpy.extract_gmat_obj(self).SetBooleanParameter(param, value)

    def SetIntegerParameter(self, param: str | int, value: int) -> bool:
        if isinstance(param, str):
            param = self.GetParameterID(param)
        return gpy.extract_gmat_obj(self).SetIntegerParameter(param, value)

    def SetField(self, field: str | int, val: str | int | float | bool | list):
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
        """
        Set the value of a real (int or float) parameter.
        Note: this function returns a bool but native GMAT returns the value that was set.

        :param param: str name or int ID for parameter to be set
        :param value: int or float of value to be set
        :return: True if value set successfully, False otherwise
        """
        if isinstance(param, str):
            param = self.GetParameterID(param)
        # gmat_obj.SetRealParameter returns the value set if set successfully, not bool
        value_set: float = gpy.extract_gmat_obj(self).SetRealParameter(param, value)
        set_successfully: bool = value_set == value
        return set_successfully

    # def SetReference(self, ref_obj):
    #     print(self)
    #     self.Help()
    #     try:
    #         return gpy.extract_gmat_obj(self).SetReference(gpy.extract_gmat_obj(ref_obj))
    #     except Exception as ex:
    #         print('RuhRoh')
    #         ref_arr = self.GetRefObjectNameArray(gpy.extract_gmat_obj(ref_obj).GetType())
    #         print(ref_arr)
    #         raise
    #         pass

    def SetReference(self, ref_obj):
        gpy.extract_gmat_obj(self).SetReference(gpy.extract_gmat_obj(ref_obj))

    def SetRefObject(self, obj: gpy.GmatObject | gmat.GmatObject, type_id: int, name: str) -> bool:
        return gpy.extract_gmat_obj(self).SetRefObject(gpy.extract_gmat_obj(obj), type_id, name)

    def SetRefObjectName(self, type_id: int, name: str) -> bool:
        return gpy.extract_gmat_obj(self).SetRefObjectName(type_id, name)

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
            raise RuntimeError(
                f'{type(self).__name__} named "{self.name}" failed to Validate - see GMAT exception above') \
                from ex

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, new_name: str):
        self._name = new_name
        gpy.extract_gmat_obj(self).SetName(new_name)
