from __future__ import annotations

from load_gmat import gmat
import gmat_py_simple as gpy

import os.path


# def GetObject(name: str) -> gmat.GmatBase:
#     try:
#         obj: gmat.GmatBase = gmat.GetObject(name)
#         return obj
#     except Exception as ex:
#         if str(ex) == "'NoneType' object has no attribute 'GetTypeName'":
#             raise gpy.GMATNameError(name) from ex
#         else:
#             raise ex


def GetObject(obj: gpy.GmatObject | str):
    # TODO determine return type. Same for gmat.GetObject and GetRuntimeObject?
    """
    Return the latest version of an object so its state info is up-to-date
    :return:
    """

    if isinstance(obj, str):
        try:
            return gmat.GetObject(obj)
        except AttributeError as ex:
            if str(ex) == "'NoneType' object has no attribute 'GetTypeName'":
                raise gpy.GMATNameError(obj) from ex
            else:
                raise ex

    try:
        if not obj.was_propagated:  # sat not yet propagated
            return gmat.GetObject(obj.name)
        elif obj.was_propagated:  # sat has been propagated - gmat.GetObject() would return incorrect values
            if isinstance(obj, gpy.Spacecraft):
                objs_to_update = [obj.hardware.chemical_thrusters, obj.hardware.chemical_tanks,
                                  obj.hardware.electric_thrusters, obj.hardware.electric_tanks]
                for hw_list in objs_to_update:
                    for hw_item in hw_list:
                        hw_item.GetObject()
            return gmat.GetRuntimeObject(obj.name)

    except AttributeError:  # object may not have a self.was_propagated attribute
        raise


def Initialize() -> bool:
    try:
        return gmat.Initialize()
    except Exception as ex:
        ex_str = str(ex).replace('\n', '')
        raise RuntimeError(f'GMAT Initialize failed - GMAT error: "{ex_str}"') from ex


def LoadScript(script_path: str) -> bool:
    if not os.path.isfile(script_path):
        raise FileNotFoundError(f'{script_path} does not exist')

    return gmat.LoadScript(script_path)


def RunScript() -> bool:
    return gmat.RunScript()


def ShowObjects():
    return gmat.ShowObjects()
