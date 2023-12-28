from __future__ import annotations

import gmat_py_simple as gpy
from load_gmat import gmat


def CreateParameter(param_type: str, name: str) -> Parameter:
    return Parameter(param_type, name)


def GmatBase_to_Parameter(gb: gmat.GmatBase) -> gmat.Parameter:
    # get the object's name and use that to get its Swig Parameter representation from the Validator
    name = gb.GetName()
    return gmat.Validator.Instance().GetParameter(name)


class Parameter:
    def __init__(self, param_type: str, name: str):
        self.param_type = param_type
        self.name = name
        self.gmat_obj = gpy.Moderator().CreateParameter(self.param_type, self.name)  # SwigPyObject instance
        self.swig_param = self.gmat_obj  # SwigPyObject instance
        self.gmat_base = gmat.Validator.Instance().FindObject(self.name)  # GmatBase instance

    def GetName(self) -> str:
        self.name: str = self.gmat_base.GetName()
        return self.name

    def GetTypeName(self) -> str:
        return self.gmat_base.GetTypeName()

    def SetRefObjectName(self, type_int: int, name: str) -> bool:
        # GMAT's SetRefObjectName cannot be called on a Swig Parameter object, only a GmatBase (or subclass thereof)
        # self_obj = gmat.GetObject(self.GetName())
        return self.gmat_obj.SetRefObjectName(type_int, name)

    def Help(self):
        return self.gmat_base.Help()


# TODO: make a class for each type of StopCondition, e.g. ElapsedSecs, Apoapsis etc, that generates a
#  properly-formed StopCondition of that type. Will help with code completion.
class StopParameter(Parameter):
    def __init__(self, param_type: str, name: str):
        super().__init__(param_type, name)
        raise NotImplementedError


class ElapsedSecs(StopParameter):
    def __init__(self):
        super().__init__()


class ElapsedDays(StopParameter):
    def __init__(self):
        super().__init__()
