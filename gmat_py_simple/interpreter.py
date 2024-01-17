from __future__ import annotations

import gmat_py_simple as gpy
from load_gmat import gmat


class Validator:
    def __init__(self):
        self.gmat_obj = gmat.Validator.Instance()

    def CreateSystemParameter(self, param_created: bool, name: str, manage: int = 1):
        # TODO bugfix: param_created bool not accepted - see GMT-8100 on Jira
        if manage not in [0, 1, 2]:
            raise SyntaxError('manage argument must be 0, 1 or 2')

        return self.gmat_obj.CreateSystemParameter(param_created, name, manage)

    def FindObject(self, name: str):
        return self.gmat_obj.FindObject(name)

    def SetObjectMap(self, om: gmat.ObjectMap) -> bool:
        return self.gmat_obj.SetObjectMap(om)

    def SetSolarSystem(self, ss: gmat.SolarSystem = gmat.GetSolarSystem()) -> bool:
        return self.gmat_obj.SetSolarSystem(ss)

    def ValidateCommand(self, command: gpy.GmatCommand | gmat.GmatCommand):
        return self.gmat_obj.ValidateCommand(gpy.extract_gmat_obj(command))

