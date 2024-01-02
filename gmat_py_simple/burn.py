from __future__ import annotations

import gmat_py_simple as gpy
from gmat_py_simple.basics import GmatObject

from load_gmat import gmat


class FiniteBurn(GmatObject):
    def __init__(self, name, thrusters: gpy.Thruster | list[gpy.Thruster]):
        # TODO generic: convert thruster type to Thruster once class created
        super().__init__('FiniteBurn', name)

        self.thrusters: list[str] = [thruster.name for thruster in thrusters]
        self.SetField('Thrusters', self.thrusters)


class FiniteThrust(GmatObject):  # TODO tidy: consider making subclass of FiniteBurn
    def __init__(self, name: str, spacecraft: gpy.Spacecraft, finite_burn: FiniteBurn):
        super().__init__('FiniteThrust', name)
        self.Name = name
        self.GmatObj = gmat.FiniteThrust(name)
        self._spacecraft = spacecraft
        self._finite_burn = finite_burn
        self.GmatObj.SetRefObjectName(gmat.SPACECRAFT, spacecraft.GetName())
        self.GmatObj.SetReference(finite_burn.gmat_obj)

    # TODO sense: create BeginFiniteBurn method in FiniteBurn that does this and other steps needed to enable thrust
    def EnableThrust(self):
        gmat.ConfigManager.Instance().AddPhysicalModel(self.GmatObj)


class ImpulsiveBurn(GmatObject):
    def __init__(self, name, coord_sys: gpy.OrbitState.CoordinateSystem, delta_v: list[float | int],
                 decrement_mass: bool = False, tanks: gpy.Tank | list[gpy.Tank] = None, isp: int | float = 300,
                 gravitational_accel: float = 9.81):
        super().__init__('ImpulsiveBurn', name)

        self.coord_sys: gpy.OrbitState.CoordinateSystem = coord_sys
        self.SetField('CoordinateSystem', self.coord_sys.name)

        self.delta_v: list[float | int] = delta_v
        for index, element in enumerate(delta_v):
            self.SetField(f'Element{index+1}', element)

        self.decrement_mass: bool = decrement_mass
        self.SetField('DecrementMass', self.decrement_mass)

        self.tanks: list[str] = [tank.name for tank in tanks] if tanks is not None else None
        if self.tanks is not None:
            self.SetField('Tanks', self.tanks)

        self.isp: int | float = isp
        self.SetField('Isp', self.isp)

        self.gravitational_accel: float = gravitational_accel
        self.SetField('GravitationalAccel', self.gravitational_accel)

        self.SetSolarSystem(gmat.GetSolarSystem())

        self.Validate()
        self.Initialize()
        # gpy.Initialize()  # TODO: uncomment once DiffCorr fixed
