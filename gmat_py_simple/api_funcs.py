from load_gmat import gmat
import gmat_py_simple as gpy

import os.path


def GetObject(name: str) -> gmat.GmatBase:
    try:
        obj: gmat.GmatBase = gmat.GetObject(name)
        return obj
    except Exception as ex:
        if str(ex) == "'NoneType' object has no attribute 'GetTypeName'":
            raise gpy.GMATNameError(name) from ex
        else:
            raise ex


def Initialize() -> bool:
    try:
        return gmat.Initialize()
    except Exception as ex:
        ex_str = str(ex).replace('\n', '')
        raise RuntimeError(f'GMAT Initialize failed - GMAT error: "{ex_str}"') from None


def LoadScript(script_path: str) -> bool:
    if not os.path.isfile(script_path):
        raise FileNotFoundError(f'{script_path} does not exist')

    return gmat.LoadScript(script_path)


def RunScript() -> bool:
    return gmat.RunScript()


def ShowObjects():
    return gmat.ShowObjects()
