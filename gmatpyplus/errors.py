class GMATNameError(Exception):
    def __init__(self, attempted_name):
        self.add_note(f'No object currently exists in GMAT with the name "{attempted_name}"')


class HardwareException(Exception):
    def __init__(self, details: str) -> None:
        super().__init__()
        self._details: str = details

    @property
    def details(self):
        return self._details

    def __repr__(self):
        return 'Hardware Exception Thrown: $details'


class InvalidGMATTypeException(Exception):
    def __init__(self, obj: object):
        """
        Raised when a class has been referenced within the ``gmat`` (``gmat_py.py``) library that does not exist in that library.

        :param obj: The object that has caused the exception. **Note:** this is not the exception that the invalid type triggered (e.g. AttributeError).
        :type obj: object
        """
        self.add_note(f'Invalid GMAT type: "{type(obj).__name__}"')
