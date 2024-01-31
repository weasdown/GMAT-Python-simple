import gmat_py_simple
from gmat_py_simple.spacecraft import Spacecraft
from load_gmat import gmat
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
                                    chem_thrusters=gmat_py_simple.ChemicalThruster('ChemThruster1', 'ChemTank1'),
                                    elec_tanks=gmat_py_simple.ElectricTank('ElecTank1'),
                                    elec_thrusters=gmat_py_simple.ElectricThruster('ElecThruster1', 'ElecTank1'),
                                    solar_power_system=gmat_py_simple.SolarPowerSystem('SolarPowerSystem1'),
                                    nuclear_power_system=gmat_py_simple.NuclearPowerSystem('NuclearPowerSystem1'),
                                    imagers=gmat_py_simple.Imager('Imager1')
                                )
                                )

    # def setUp(self):
    #     print("\nRunning setUp method...")
    #     self.book_1 = Book('Deep Work', 'Cal Newport', 304, 15, 0.05)
    #     self.book_2 = Book('Grit', 'Angela Duckworth', 447, 16, 0.15)

    def tearDown(self):
        print("Running tearDown method...")
        gmat.Clear()

    def test_hardware(self):
        print("Running test_reading_time...")
        self.sat_1.Help()

        # Check thrusters, tanks, power systems
        self.assertEqual(self.sat_1.GetField('Thrusters'), '{ChemThruster1, ElecThruster1}')
        self.assertEqual(self.sat_1.GetField('Tanks'), '{ChemTank1, ElecTank1}')
        # self.assertEqual(self.sat_1.GetField('PowerSystem'), 'SolarPowerSystem1')
        # gmat.Initialize()
        print(f'Param 104: {self.sat_1.gmat_obj.GetStringArrayParameter(104)}')  # 104 for ADD_HARDWARE

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
