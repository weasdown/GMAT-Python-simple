from __future__ import annotations

import gmat_py_simple as gpy
from gmat_py_simple.basics import GmatObject

from load_gmat import gmat


class FiniteBurn(GmatObject):
    def __init__(self, name, thrusters: list[gpy.Thruster] | gpy.Thruster):
        # TODO generic: convert thruster type to Thruster once class created
        super().__init__('FiniteBurn', name)
        self.gmat_obj.SetSolarSystem(gmat.GetSolarSystem())
        self.thrusters = thrusters
        if isinstance(self.thrusters, gpy.Thruster):
            self.SetField('Thrusters', self.thrusters.GetName())
        else:
            self.SetField('Thrusters', [thruster.GetName() for thruster in self.thrusters])


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
        super().__init__('FiniteBurn', name)
        self.coord_sys: gpy.OrbitState.CoordinateSystem = coord_sys
        self.delta_v: list[float | int] = delta_v
        self.decrement_mass: bool = decrement_mass
        self.tanks: gpy.Tank | list[gpy.Tank] = tanks
        self.isp: int | float = 300
        self.gravitational_accel: float = 9.81

        self.SetSolarSystem(gmat.GetSolarSystem())

        self.Help()
