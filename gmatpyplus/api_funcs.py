from __future__ import annotations

import os.path

import gmatpyplus as gp
from gmatpyplus import gmat
from gmatpyplus.errors import InvalidGMATTypeException
from gmatpyplus.foundation import GmatObject


## TODO remove commented code
# def GetObject(name: str) -> gmat.GmatBase:
#     try:
#         obj: gmat.GmatBase = gmat.GetObject(name)
#         return obj
#     except Exception as ex:
#         if str(ex) == "'NoneType' object has no attribute 'GetTypeName'":
#             raise gp.GMATNameError(name) from ex
#         else:
#             raise ex


def GetObject(obj: GmatObject | str) -> gmat.GmatBase:
    # TODO determine return type. Same for gmat.GetObject and GetRuntimeObject?
    """
    Return the latest version of an object so its state info is up-to-date.

    :return: gmat_py.GmatBase
    """

    if isinstance(obj, str):
        try:
            return gmat.GetObject(obj)
        except AttributeError as ex:
            if str(ex) == "'NoneType' object has no attribute 'GetTypeName'":
                raise gp.GMATNameError(obj) from ex
            else:
                raise ex

    try:
        if not obj.was_propagated:  # sat not yet propagated
            try:
                return gmat.GetObject(obj.name)
            except AttributeError as ae:
                raise InvalidGMATTypeException(obj) from ae

        elif obj.was_propagated:  # sat has been propagated - gmat.GetObject() would return incorrect values
            # TODO apply RuntimeObject fields to Object so we can keep the native type rather than GmatBase
            # rt_obj = gmat.GetRuntimeObject(obj.GetName())
            # fields = [rt_obj.GetField(val) for val in range(250)]
            # for index, value in enumerate(fields):
            #     obj.SetField(index, value)

            # if isinstance(obj, gp.Spacecraft):
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
