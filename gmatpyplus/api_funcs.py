from __future__ import annotations

import os.path

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


# TODO confirm return type. Same for gmat.GetObject and GetRuntimeObject?
def GetObject(obj: GmatObject | str) -> gmat.GmatBase:
    """
    Return the latest version of an object so its state info is up-to-date.

    :return: gmat_py.GmatBase
    """

    def _safe_get_object(object_to_get: object):
        try:
            return gmat.GetObject(object_to_get)
        except AttributeError as ae:
            raise InvalidGMATTypeException(object_to_get) from ae

    if isinstance(obj, str):
        return _safe_get_object(obj)

    # obj is not a str
    else:
        try:
            # obj (e.g. sat) not yet propagated
            if not obj.was_propagated:
                return _safe_get_object(obj.name)

            # obj (e.g. sat) has been propagated - gmat.GetObject() would return incorrect values
            elif obj.was_propagated:
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

        # object may not have a self.was_propagated attribute
        except AttributeError:
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
