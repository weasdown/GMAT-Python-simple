from __future__ import annotations

import gmat_py_simple as gpy
from gmat_py_simple.basics import GmatObject

from load_gmat import gmat


class Burn(GmatObject):
    def __init__(self, obj_type: str, name: str):
        super().__init__(obj_type, name)

        self.has_fired: bool = False

    # FIXME: methods internally dependent on hasFired/Fire() not giving appropriate outputs

    def HasFired(self) -> bool:
        # FIXME determine why GMAT returns False for fired (Impulsive)Burns - using self.has_fired as workaround
        # return gpy.extract_gmat_obj(self).HasFired()
        # return self.has_fired
        raise NotImplementedError

    def IsFiring(self) -> bool:
        # return gpy.extract_gmat_obj(self).IsFiring()
        raise NotImplementedError

    def GetTotalMassFlowRate(self) -> float:
        # return gpy.extract_gmat_obj(self).GetTotalMassFlowRate()
        raise NotImplementedError

    def GetDeltaVInertial(self) -> float:
        # return gpy.extract_gmat_obj(self).GetDeltaVInertial()
        raise NotImplementedError

    def GetTotalAcceleration(self) -> float:
        # return gpy.extract_gmat_obj(self).GetTotalAcceleration()
        raise NotImplementedError

    def GetTotalThrust(self) -> float:
        # return gpy.extract_gmat_obj(self).GetTotalThrust()
        raise NotImplementedError

    def GetEpochAtLastFire(self):
        # return gpy.extract_gmat_obj(self).GetEpochAtLastFire()
        raise NotImplementedError


class FiniteBurn(Burn):
    def __init__(self, name, thrusters: gpy.Thruster | list[gpy.Thruster]):
        # TODO generic: convert thruster type to Thruster once class created
        super().__init__('FiniteBurn', name)

        self.thrusters: list[gpy.Thruster] = [thrusters]
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


class ImpulsiveBurn(Burn):
    def __init__(self, name, coord_sys: gpy.OrbitState.CoordinateSystem = None, delta_v: list[int | float] = None,
                 decrement_mass: bool = False, tanks: gpy.Tank | list[gpy.Tank] = None, isp: int | float = 300,
                 gravitational_accel: float = 9.81):
        super().__init__('ImpulsiveBurn', name)

        if delta_v is None:
            delta_v = [0, 0, 0]

        # Get default coordinate system from GMAT object
        self.coord_sys_name = self.GetStringParameter('CoordinateSystem')
        # self.coord_sys = gmat.GetObject(self.coord_sys_name)  # CoordinateSystem is not RefObject of IB - get from GMAT
        # self.coord_sys.Help()
        self.origin: str = self.GetStringParameter('Origin')
        self.axes: str = self.GetStringParameter('Axes')
        # self.origin = self.GetStringParameter('Origin')

        # Update coordinate system if user has supplied one
        if coord_sys is not None:
            if not isinstance(coord_sys, gpy.OrbitState.CoordinateSystem | gmat.CoordinateSystem):
                raise TypeError(f'CoordinateSystem type "{type(coord_sys).__name__}" not recognized in ImpulsiveBurn '
                                f'init')
            coord_sys.Initialize()
            self.coord_sys: gpy.OrbitState.CoordinateSystem | gmat.CoordinateSystem = coord_sys
            self.coord_sys_name = self.coord_sys.GetName()

            coord_sys = gmat.GetObject('EarthMJ2000Eq')

            # Extract celestial body (e.g. Earth) and axes (e.g. MJ2000Eq) from CoordinateSystem
            if isinstance(coord_sys, gpy.OrbitState.CoordinateSystem):
                self.origin: gmat.Planet = coord_sys.origin  # obj for celestial body at coordinate system origin
                self.axes: gpy.OrbitState.CoordinateSystem.Axes = coord_sys.axes
                self.axes_name: str = self.axes.name
            else:
                # coord_sys is of type gmat.CoordinateSystem
                self.origin_name: str = coord_sys.GetField('Origin')
                # self. origin is GMAT object for celestial body at coordinate system origin
                self.origin: gmat.Planet = gmat.GetObject(self.origin_name)
                self.axes_name: str = coord_sys.GetField('Axes')
                self.axes: gmat.GmatBase = coord_sys.GetRefObject(gmat.AXIS_SYSTEM, self.axes_name)

            # Attach the new CoordinateSystem to the ImpulsiveBurn
            self.SetStringParameter(1, self.coord_sys_name)  # 1 for CS, 2 for Origin, 3 for Axes
            self.SetRefObject(self.coord_sys, gmat.COORDINATE_SYSTEM, self.coord_sys_name)

            # Attach CoordinateSystem's celestial body (Origin) to the ImpulsiveBurn
            self.SetStringParameter(2, self.origin_name)  # 1 for CS, 2 for Origin, 3 for Axes
            self.SetRefObject(self.origin, gmat.CELESTIAL_BODY, self.origin_name)

            # Attach CoordinateSystem's Axes to the ImpulsiveBurn
            self.SetStringParameter(3, self.axes_name)  # 1 for CS, 2 for Origin, 3 for Axes

            # self.coord_sys.Initialize()

        self.delta_v: list[float | int] = delta_v
        for index, element in enumerate(delta_v):
            self.SetField(f'Element{index + 1}', element)

        self.decrement_mass: bool = decrement_mass
        self.SetField('DecrementMass', self.decrement_mass)

        self.tanks: list[str] = [tank.name for tank in tanks] if tanks is not None else None
        if self.tanks is not None:
            # self.SetField('Tanks', self.tanks)
            self.SetStringParameter(self.gmat_obj.FUEL_TANK, str(self.tanks))

        self.isp: int | float = isp
        self.SetField('Isp', self.isp)

        self.gravitational_accel: float = gravitational_accel
        self.SetField('GravitationalAccel', self.gravitational_accel)

        self.SetSolarSystem(gmat.GetSolarSystem())

        # gmat.Initialize()
        # self.Initialize()
        #
        # self.Help()
        # pass
