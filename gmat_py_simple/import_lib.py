import os


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
        gmat_directory: str = f.readline()

    return gmat_directory


gmat_path: str = _gmat_path()
