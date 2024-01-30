# project/test.py

import unittest
from gmat_py_simple.spacecraft import Spacecraft


class TestSpacecraft(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.spacecraft = Spacecraft('TestSat')

    def test_name(self):
        self.assertEqual(self.spacecraft.GetName(), 'TestSat', 'The name has not been set')


if __name__ == '__main__':
    unittest.main()
