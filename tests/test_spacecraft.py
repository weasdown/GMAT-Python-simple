import gmat_py_simple
from gmat_py_simple.spacecraft import Spacecraft
from book import Book
import unittest


class TestSpacecraft(unittest.TestCase):
    # @classmethod
    # def setUpClass(cls):
    #     print("\nsetUpClass method: Runs before all tests...")

    def setUp(self):
        self.sat_1 = Spacecraft('TS1',
                                hardware=Spacecraft.SpacecraftHardware(
                                    chem_tanks=gmat_py_simple.ChemicalTank('ChemTank1'),
                                    chem_thrusters=gmat_py_simple.ChemicalThruster('ChemThruster1', 'ChemTank1'))
                                )

    # def setUp(self):
    #     print("\nRunning setUp method...")
    #     self.book_1 = Book('Deep Work', 'Cal Newport', 304, 15, 0.05)
    #     self.book_2 = Book('Grit', 'Angela Duckworth', 447, 16, 0.15)

    def tearDown(self):
        print("Running tearDown method...")

    def test_reading_time(self):
        print("Running test_reading_time...")
        # self.assertEqual(self.book_1.get_reading_time(), f"{304 * 1.5} minutes")
        # self.assertEqual(self.book_2.get_reading_time(), f"{447 * 1.5} minutes")

    # def test_discount(self):
    #     print("Running test_discount...")
    #     # self.assertEqual(self.book_1.apply_discount(), f"${15 - 15 * 0.05}")
    #     # self.assertEqual(self.book_2.apply_discount(), f"${16 - 16 * 0.15}")

    # def test_title(self):
    #     print("Running test_title...")
    #     # self.assertEqual(self.book_1.title, 'Deep Work')
    #     # self.assertIsInstance(self.book_2.title, str)
    #     # self.assertEqual(self.book_2.title, 'Grit')

    # def test_author(self):
    #     print("Running test_author...")
    #     # self.assertEqual(self.book_1.author, 'Cal Newport')
    #     # self.assertEqual(self.book_2.author, 'Angela Duckworth')

    # @classmethod
    # def tearDownClass(cls):
    #     print("\ntearDownClass method: Runs after all tests...")


if __name__ == '__main__':
    unittest.main()
