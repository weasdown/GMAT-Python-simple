# Sets up the Python path so imports of load_gmat and gmat_py_simple work.

import os
import sys

# Set this to the full path to your GMAT install's api folder.
gmat_api: str = 'C:/Users/[USER]/dev/GMAT/gmat-win-R2022a/GMAT/api'

# Set this to the full path to the gmat_py_simple library's parent folder.
gmat_py_simple_path: str = 'C:/Users/[USER]/dev/GMAT/GMAT-Python-simple'

sys.path.append(os.path.abspath(gmat_api))
sys.path.append(os.path.abspath(gmat_py_simple_path))
