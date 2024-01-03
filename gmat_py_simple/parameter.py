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
        self.gmat_base = gmat.Validator.Instance().FindObject(self.name)  # GmatBase instance

        self.index: int = 0  # used in self.SetRefObject()

    # def AddRefObject(self, obj: gpy.GmatObject) -> bool:
    #     obj = gpy.extract_gmat_obj(obj)
    #     return self.swig_param.AddRefObject(obj)

    def GetName(self) -> str:
        self.name: str = self.gmat_base.GetName()
        return self.name

    def GetRefObjectName(self, type_int: int) -> str:
        # GMAT's SetRefObjectName cannot be called on a Swig Parameter object, only a GmatBase (or subclass thereof)
        return self.gmat_base.GetRefObjectName(type_int)

    def GetTypeName(self) -> str:
        return self.gmat_base.GetTypeName()

    def Help(self):
        return self.gmat_base.Help()

    def Initialize(self):
        return self.gmat_base.Initialize()

    def SetRefObject(self, obj, type_int: int, name: str):
        """
        Return True if obj successfully set, False otherwise

        :param obj:
        :param type_int:
        :param name:
        :param index:
        :return:
        """
        obj = gpy.extract_gmat_obj(obj)
        try:
            response: bool = self.gmat_base.SetRefObject(obj, type_int, name, self.index)
            if not response:
                raise RuntimeError(f'SetRefObject() returned a non-true value: {response}')
            self.index += 1
        except Exception as ex:
            print(f'CM list of items in Parameter.SetRefObject(): {gmat.ConfigManager.Instance().GetListOfAllItems()}')
            raise RuntimeError(f'Parameter named "{self.name}" failed to SetRefObject - see exception below:'
                               f'\n     {ex}') from ex
        return response

    def SetRefObjectName(self, type_int: int, name: str) -> bool:
        # GMAT's SetRefObjectName cannot be called on a Swig Parameter object, only a GmatBase (or subclass thereof)
        return self.gmat_base.SetRefObjectName(type_int, name)

    def SetSolarSystem(self, ss=gmat.SolarSystem()):
        return self.gmat_base.SetSolarSystem(ss)

    def Validate(self) -> bool:
        try:
            valid = self.gmat_base.Validate()
            if not valid:
                raise RuntimeError(f'Validate() returned a non-true value for Parameter {self.name}: {valid}.\n'
                                   f'     (Parameter type: {self.GetTypeName()})')
            return valid
        except Exception as ex:
            print(f'CM list of items in Parameter.Validate(): {gmat.ConfigManager.Instance().GetListOfAllItems()}')
            raise RuntimeError(f'Parameter named "{self.name}" failed to Validate - see exception below:'
                               f'\n     {ex}') from ex

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
