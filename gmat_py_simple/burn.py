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
        return gpy.extract_gmat_obj(self).HasFired()
        # return self.has_fired
        # raise NotImplementedError

    def IsFiring(self) -> bool:
        return gpy.extract_gmat_obj(self).IsFiring()
        # raise NotImplementedError

    def GetDeltaVInertial(self) -> float:
        return gpy.extract_gmat_obj(self).GetDeltaVInertial()
        # raise NotImplementedError

    def GetEpochAtLastFire(self):
        return gpy.extract_gmat_obj(self).GetEpochAtLastFire()
        # raise NotImplementedError

    def GetTotalAcceleration(self) -> list[float]:
        """
        Return a 3-element vector of current acceleration if IsFiring is True.
        :return:
        """
        return gpy.extract_gmat_obj(self).GetTotalAcceleration()

    def GetTotalMassFlowRate(self) -> float:
        return gpy.extract_gmat_obj(self).GetTotalMassFlowRate()
        # raise NotImplementedError

    def GetTotalThrust(self) -> float:
        return gpy.extract_gmat_obj(self).GetTotalThrust()
        # raise NotImplementedError

    def SetSpacecraftToManeuver(self, spacecraft: gpy.Spacecraft | gmat.Spacecraft):
        # No return value from internal GMAT so don't return here either
        gpy.extract_gmat_obj(self).SetSpacecraftToManeuver(gpy.extract_gmat_obj(spacecraft))


class FiniteBurn(Burn):
    def __init__(self, name, thrusters: gpy.Thruster | list[gpy.Thruster]):
        super().__init__('FiniteBurn', name)

        # Attach specified thruster(s) to FiniteBurn
        self.thrusters: list[gpy.Thruster] = [thrusters]
        for thruster in self.thrusters:
            thruster_name = thruster.GetName()
            self.SetStringParameter('Thrusters', thruster_name)
            self.SetRefObject(thruster, gmat.THRUSTER, thruster_name)

        # Set default spacecraft as the burn's spacecraft to maneuver, as a placeholder
        # This is later updated by any BeginFiniteBurn commands that call this burn
        # sat = gpy.Moderator().GetDefaultSpacecraft()
        # self.spacecraft = sat
        # self.SetRefObject(self.spacecraft, gmat.SPACECRAFT, self.spacecraft.GetName())
        # self.SetSpacecraftToManeuver(sat)
        # self.SetStringParameter('SpacecraftName', self.spacecraft.GetName())

        # print(self.gmat_obj.GetRefObjectNameArray(gmat.SPACECRAFT))
        # gpy.CustomHelp(self)

        # self.Initialize()


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
        self.origin: str = self.GetStringParameter('Origin')
        self.axes: str = self.GetStringParameter('Axes')
        self.origin = self.GetStringParameter('Origin')

        # Update coordinate system if user has supplied one
        if coord_sys is not None:
            if not isinstance(coord_sys, gpy.OrbitState.CoordinateSystem | gmat.CoordinateSystem):
                raise TypeError(f'CoordinateSystem type "{type(coord_sys).__name__}" not recognized in ImpulsiveBurn '
                                f'init')
            coord_sys.Initialize()
            coord_sys_new: gpy.OrbitState.CoordinateSystem | gmat.CoordinateSystem = coord_sys
            self.coord_sys_name = coord_sys_new.GetName()

            # Extract celestial body (e.g. Earth) and axes (e.g. MJ2000Eq) from CoordinateSystem
            if isinstance(coord_sys_new, gpy.OrbitState.CoordinateSystem):
                self.origin: gmat.Planet = coord_sys_new.origin  # obj for celestial body at coordinate system origin
                self.axes: gpy.OrbitState.CoordinateSystem.Axes = coord_sys_new.axes
                self.axes_name: str = self.axes.name
            else:
                # coord_sys is of type gmat.CoordinateSystem
                self.origin_name: str = coord_sys_new.GetField('Origin')
                # self. origin is GMAT object for celestial body at coordinate system origin
                self.origin: gmat.Planet = gmat.GetSolarSystem().GetBody(self.origin_name)
                self.axes_name: str = coord_sys_new.GetField('Axes')
                self.axes: gmat.GmatBase = coord_sys_new.GetRefObject(gmat.AXIS_SYSTEM, self.axes_name)

            # Attach the new CoordinateSystem to the ImpulsiveBurn
            self.SetStringParameter(1, self.coord_sys_name)  # 1 for CS, 2 for Origin, 3 for Axes
            self.SetRefObject(coord_sys_new, gmat.COORDINATE_SYSTEM, self.coord_sys_name)

            # Attach CoordinateSystem's celestial body (Origin) to the ImpulsiveBurn
            self.SetStringParameter(2, self.origin_name)  # 1 for CS, 2 for Origin, 3 for Axes
            self.SetRefObject(self.origin, gmat.CELESTIAL_BODY, self.origin_name)

            # Attach CoordinateSystem's Axes to the ImpulsiveBurn
            self.SetStringParameter(3, self.axes_name)  # 1 for CS, 2 for Origin, 3 for Axes

        # Set default spacecraft as the burn's spacecraft to maneuver, as a placeholder
        # This is later updated by any Maneuver commands that call this burn
        sat = gpy.Moderator().GetDefaultSpacecraft()
        self.SetSpacecraftToManeuver(sat)

        self.delta_v: list[float | int] = delta_v
        for index, element in enumerate(delta_v):
            self.SetField(f'Element{index + 1}', element)

        self.decrement_mass: bool = decrement_mass
        self.SetBooleanParameter('DecrementMass', self.decrement_mass)

        self.tanks: list[str] = [tank.name for tank in tanks] if tanks is not None else None
        if self.tanks is not None:
            self.SetStringParameter(self.gmat_obj.FUEL_TANK, str(self.tanks))

        self.isp: int | float = isp
        self.SetRealParameter('Isp', self.isp)

        self.gravitational_accel: float = gravitational_accel
        self.SetRealParameter('GravitationalAccel', self.gravitational_accel)

        self.delta_tank_mass = self.GetRealParameter('DeltaTankMass')
        # 0.0 initially, updated after burn fired if decrement_mass is True

        self.SetSolarSystem(gmat.GetSolarSystem())

        gpy.Initialize()
        self.Initialize()
