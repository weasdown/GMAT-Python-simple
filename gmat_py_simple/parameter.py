from __future__ import annotations

import gmat_py_simple as gpy
from load_gmat import gmat


# def CreateParameter(param_type: str, name: str) -> Parameter:
#     return Parameter(param_type, name)


def GmatBase_to_Parameter(gb: gmat.GmatBase) -> gmat.Parameter:
    # get the object's name and use that to get its Swig Parameter representation from the Validator
    name = gb.GetName()
    return gmat.Validator.Instance().GetParameter(name)


class Parameter:
    def __init__(self, param_type: str, name: str):
        self.param_type = param_type
        self.name = name

        # See if Parameter already exists. If not, create a new one
        self.gmat_obj = gpy.Moderator().GetParameter(self.name)
        if not self.gmat_obj:
            self.gmat_obj = gpy.Moderator().CreateParameter(self.param_type, self.name)  # SwigPyObject instance

        self.swig_param = self.gmat_obj  # SwigPyObject instance
        self.gmat_base = gpy.Validator().FindObject(self.name)  # GmatBase instance

        self.index: int = 0  # used in self.SetRefObject()

    # def AddRefObject(self, obj: gpy.GmatObject) -> bool:
    #     obj = gpy.extract_gmat_obj(obj)
    #     return self.swig_param.AddRefObject(obj)

    # TODO: make getters/setters as appropriate for following fields (taken from old Parameter class)
    #  (See src / base / parameter / Parameter.cpp). Key should be type ParameterKey, from GmatParam
    #     def __init__(self, name: str = 'Param', type_str: str = None, key: str = None, owner: str = None, desc: str = None,
    #                  unit: str = None, dep_obj: str = None, owner_type: int = None, is_time_param: bool = False,
    #                  is_settable: bool = False, is_plottable: bool = False, is_reportable: bool = False,
    #                  owned_obj_type: int = None):

    def GetName(self) -> str:
        self.name: str = self.gmat_base.GetName()
        return self.name

    def GetParameterID(self, param_name: str) -> int:
        return self.gmat_base.GetParameterID(param_name)

    def GetRefObjectName(self, type_int: int) -> str:
        # GMAT's SetRefObjectName cannot be called on a Swig Parameter object, only a GmatBase (or subclass thereof)
        return self.gmat_base.GetRefObjectName(type_int)

    def GetStringParameter(self, param: str | int) -> str:
        if isinstance(param, str):
            param = self.GetParameterID(param)
        return self.gmat_base.GetStringParameter(param)

    def GetTypeName(self) -> str:
        return self.gmat_base.GetTypeName()

    def Help(self):
        return self.gmat_base.Help()

    def Initialize(self):
        return self.gmat_base.Initialize()

    def SetRefObject(self, obj, type_int: int):
        """
        Return True if obj successfully set, False otherwise

        :param obj:
        :param type_int:
        :return:
        """
        obj = gpy.extract_gmat_obj(obj)
        name = obj.GetName()
        try:
            response: bool = self.gmat_base.SetRefObject(obj, type_int, name)
            if not response:
                raise RuntimeError(f'SetRefObject() returned a non-true value: {response}')
        except Exception as ex:
            if 'GmatBase Exception Thrown' in str(ex):
                pass
            raise RuntimeError(f'Parameter named "{self.name}" failed to SetRefObject'
                               # f' with arguments:'
                               # f'\n\t- obj:         {obj}'
                               # f'\n\t- type_int:    {type_int} (gmat.{gpy.GetTypeNameFromID(type_int)})\n'
                               # f'\n\tRaised exception: {ex}\n'
                               # f'\tGMAT type: {self.GetTypeName()}\n'
                               # f'\tRef obj type array: {self.gmat_base.GetRefObjectTypeArray()}\n\n'
                               # f'\tRef obj array, SPACECRAFT: {self.gmat_base.GetRefObjectArray(gmat.SPACECRAFT)}\n'
                               # f'\tRef obj array, SPACE_POINT: {self.gmat_base.GetRefObjectArray(gmat.SPACE_POINT)}\n'
                               # f'\tRef obj array, COORDINATE_SYSTEM: {self.gmat_base.GetRefObjectArray(gmat.COORDINATE_SYSTEM)}\n\n'
                               # f'\tRef obj name array, SPACECRAFT: {self.gmat_base.GetRefObjectNameArray(gmat.SPACECRAFT)}\n'
                               # f'\tRef obj name array, SPACE_POINT: {self.gmat_base.GetRefObjectNameArray(gmat.SPACE_POINT)}\n'
                               # f'\tRef obj name array, COORDINATE_SYSTEM: {self.gmat_base.GetRefObjectNameArray(gmat.COORDINATE_SYSTEM)}'
                               f'\nGMAT exception: {ex}') \
                from ex
        return response

    def SetRefObjectName(self, type_int: int, name: str) -> bool:
        vdator = gmat.Validator.Instance()
        vdator.SetSolarSystem(gmat.GetSolarSystem())
        vdator.SetObjectMap(gmat.Moderator.Instance().GetConfiguredObjectMap())

        # GMAT's SetRefObjectName doesn't work on Swig Parameter object, only a GmatBase, so get GmatBase from Validator
        self.gmat_base = gmat.Validator.Instance().FindObject(self.name)
        resp = self.gmat_base.SetRefObjectName(type_int, name)
        if not resp:
            raise RuntimeError(f'Parameter.SetRefObjectName() failed for Parameter {self.name} with arguments:'
                               f'\n\t- type_int:  {type_int} (gmat.{gpy.GetTypeNameFromID(type_int)})'
                               f'\n\t- name:      {name}')
        return resp

    def SetSolarSystem(self, ss: gmat.SolarSystem = gmat.GetSolarSystem()):
        return self.gmat_base.SetSolarSystem(ss)

    def SetStringParameter(self, param: str | int, value: str) -> bool:
        if isinstance(param, str):
            param = self.GetParameterID(param)
        resp = gpy.extract_gmat_obj(self).SetStringParameter(param, value)
        if not resp:
            raise RuntimeError(f'Parameter.SetStringParameter() failed for parameter "{self.name}" of type '
                               f'{self.GetTypeName()} with arguments:'
                               f'\n\t- param_name:  {param}'
                               f'\n\t- value:       {value}')
        return resp

    def Validate(self) -> bool:
        try:
            valid = self.gmat_base.Validate()
            if not valid:
                raise RuntimeError(f'Validate() returned a non-true value for Parameter {self.name}: {valid}.\n'
                                   f'     (Parameter type: {self.GetTypeName()})')
            return valid
        except Exception as ex:
            raise RuntimeError(f'Parameter named "{self.name}" failed to Validate - '
                               f'see exception below:\n     {ex}'
                               # f'\nCM list of items in Parameter.Validate(): '
                               # f'{gmat.ConfigManager.Instance().GetListOfAllItems()}'
                               f'') from ex


# TODO: make a class for each type of StopCondition, e.g. ElapsedSecs, Apoapsis etc, that generates a
#  properly-formed StopCondition of that type. Will help with code completion.
# class StopParameter(Parameter):
#     def __init__(self, param_type: str, name: str):
#         super().__init__(param_type, name)
#         raise NotImplementedError
#
#
# class ElapsedSecs(StopParameter):
#     def __init__(self):
#         super().__init__()
#
#
# class ElapsedDays(StopParameter):
#     def __init__(self):
#         super().__init__()

class Variable(Parameter):
    def __init__(self, name: str, value: int = None):
        super().__init__('Variable', name)

        self.value = value if value else 0
        self.SetStringParameter('Expression', str(self.value))

        self.Initialize()
