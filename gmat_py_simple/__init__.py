from .import_lib import gmat_path

from .load_gmat import *

# GMAT's built-in library that interfaces to GMAT's source code.
gmat: types.ModuleType = load_gmat.gmat

from .api_funcs import *
from .basics import *
from .burn import *
from .commands import *
from .executive import *
from .hardware import *
from .interpreter import *
from .parameter import *
from .solver import *
from .spacecraft import *
from .orbit import *
from .utils import *
