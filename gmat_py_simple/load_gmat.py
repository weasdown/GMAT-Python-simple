import errno
import os
import sys
import types

from gmat_py_simple.import_lib import gmat_path

api_startup = "api_startup_file.txt"
gmat_bin_path = gmat_path + "/bin"
startup = gmat_bin_path + "/" + api_startup

if os.path.exists(startup):
    print(f'Running GMAT in {gmat_path}')

    sys.path.insert(1, gmat_bin_path)

    gmat: types.ModuleType = __import__('gmatpy')

    gmat.Setup(startup)

else:
    message: str = ("Please set up a GMAT startup file named " + api_startup +
                    " in the " + gmat_bin_path + " folder.")

    raise FileNotFoundError(
        errno.ENOENT, message, startup)
