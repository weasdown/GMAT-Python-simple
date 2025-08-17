import os


def _gmat_path(from_env: bool = True) -> str:
    """Import this library."""
    return _gmat_path_from_env() if from_env else _gmat_path_from_config_file()


def _gmat_path_from_env() -> str:
    """Gets the path to the GMAT directory from the "GMAT" environment variable."""
    try:
        gmat_env: str = os.environ['GMAT']
    except KeyError:
        raise ValueError('"GMAT" environment variable not set.')

    return gmat_env


def _gmat_path_from_config_file() -> str:
    """Gets the path to the GMAT directory from a configuration file."""
    raise NotImplementedError


# TODO remove prints (debugging only)
print('Attempting to import...')

gmat_path: str = _gmat_path()
print(f'GMAT found at {gmat_path}')

print('\nImport complete!')
