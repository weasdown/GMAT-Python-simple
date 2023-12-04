from __future__ import annotations

import gmat_py_simple.spacecraft as sc
from gmat_py_simple.basics import GmatObject

from load_gmat import gmat


class FiniteBurn(GmatObject):
    def __init__(self, name, sc_to_manoeuvre: sc.Spacecraft, thruster: sc.ElectricThruster):
        # TODO generic: convert thruster type to Thruster once class created
        super().__init__('FiniteBurn', name)
        self.Name = name
        self.GmatObj = gmat.Construct('FiniteBurn', self.Name)
        self.GmatObj.SetSolarSystem(gmat.GetSolarSystem())
        self._sc_to_manoeuvre = sc_to_manoeuvre
        self.GmatObj.SetSpacecraftToManeuver(sc_to_manoeuvre.gmat_obj)
        self._thruster = thruster
        self._thrusterName = thruster.GetName()
        self.GmatObj.SetField('Thrusters', self._thrusterName)

    def BeginFiniteBurn(self, fin_thrust):  # TODO type: add FiniteThrust type to fin_thrust
        raise NotImplementedError
        # TODO complete implementing the below code:
        # fin_thrust.EnableThrust()
        # sc: Spacecraft = 'GMAT object that FiniteBurn is applied to'  # TODO complete by pulling ref obj
        # runtime_thruster = sc.gmat_obj.GetRefObject(gmat.THRUSTER, self._thrusterName)
        # runtime_thruster.SetField("IsFiring", True)


class FiniteThrust(GmatObject):  # TODO tidy: consider making subclass of FiniteBurn
    def __init__(self, name: str, spacecraft: sc.Spacecraft, finite_burn: FiniteBurn):
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

