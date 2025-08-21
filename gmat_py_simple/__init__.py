import os
import types


def _gmat_path() -> str:
    """Import GMAT's built-in gmat library."""
    gmat_directory: str
    try:
        gmat_directory = _gmat_path_from_env()
    except ValueError:
        try:
            gmat_directory = _gmat_path_from_config_file()
        except FileNotFoundError:
            raise

    return gmat_directory


def _gmat_path_from_env() -> str:
    """Gets the path to the GMAT directory from the "GMAT" environment variable."""
    try:
        gmat_env: str = os.environ['GMAT']

    except KeyError:
        raise ValueError('"GMAT" environment variable not set.')

    return gmat_env


def _gmat_path_from_config_file() -> str:
    """Gets the path to the GMAT directory from a configuration file."""

    config_file = 'gmat_path.txt'

    with open(config_file, 'r') as f:
        # Read the first line of the file, removing any trailing whitespace.
        gmat_directory: str = f.readline().rstrip()

    return gmat_directory


gmat_path: str = _gmat_path()

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
