from __future__ import annotations

from gmat_py_simple import gmat
import gmat_py_simple as gpy

import os.path


## TODO remove commented code
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
            # TODO apply RuntimeObject fields to Object so we can keep the native type rather than GmatBase
            # rt_obj = gmat.GetRuntimeObject(obj.GetName())
            # fields = [rt_obj.GetField(val) for val in range(250)]
            # for index, value in enumerate(fields):
            #     obj.SetField(index, value)

            # if isinstance(obj, gpy.Spacecraft):
            #     objs_to_update = [obj.hardware.chem_thrusters, obj.hardware.chem_tanks,
            #                       obj.hardware.elec_thrusters, obj.hardware.elec_tanks]
            #     for hw_list in objs_to_update:
            #         for hw_item in hw_list:
            #             hw_item.GetObject()

            return gmat.GetRuntimeObject(obj.GetName())

    except AttributeError:  # object may not have a self.was_propagated attribute
        raise


def Initialize() -> bool:
    try:
        return gmat.Initialize()
    except Exception as ex:
        gmat.ShowObjects()
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
