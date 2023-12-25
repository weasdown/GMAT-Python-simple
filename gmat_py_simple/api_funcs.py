from load_gmat import gmat
import gmat_py_simple as gpy


def GetObject(name: str) -> gmat.GmatBase:
    try:
        obj: gmat.GmatBase = gmat.GetObject(name)
        print(obj)
        return obj
    except Exception as ex:
        if str(ex) == "'NoneType' object has no attribute 'GetTypeName'":
            raise gpy.GMATNameError(name) from ex
        else:
            raise ex
