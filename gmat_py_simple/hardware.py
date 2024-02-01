from __future__ import annotations

from math import pi, atan2, asin
from typing import Union

import numpy as np

from load_gmat import gmat
import gmat_py_simple as gpy
from gmat_py_simple import GmatObject


class Color(bytearray):
    def __init__(self, name: str = 'DefaultColor', red: int = 0, green: int = 0, blue: int = 0, alpha: int = 1):
        super().__init__()
        self.name = name
        self.gmat_obj = gmat.RgbColor()

        # Initialize RGB color to black
        self.red: int = red if red is not None else self.gmat_obj.Red()

        self.green: int = green if green is not None else self.gmat_obj.Green()
        self.blue: int = blue if blue is not None else self.gmat_obj.Blue()
        self.alpha: int = alpha if alpha is not None else self.gmat_obj.Alpha()  # opaque
        self.rgb_color = bytearray([self.red, self.green, self.blue, self.alpha])

        # Apply the custom color values to the gmat_obj
        self.gmat_obj.Set(self.red, self.green, self.blue, self.alpha)

    def GetIntColor(self):
        # TODO write method
        raise NotImplementedError
        # return self.colortype.int_color

    def ToIntColor(self, color_str: str) -> int:
        return gpy.extract_gmat_obj(self).ToIntColor(color_str)

    def ToRgbString(self, color_uint: int) -> str:
        return gpy.extract_gmat_obj(self).ToRgbString(color_uint)

    def ToRgbList(self, color_uint: int) -> list[int]:
        rgb_str: str = gpy.extract_gmat_obj(self).ToRgbString(color_uint)
        rgb_list: list = [int(ele) for ele in rgb_str[1:-1].split(' ')]
        return rgb_list

    def Red(self) -> int:
        return self.gmat_obj.Red()

    def Green(self) -> int:
        return self.gmat_obj.Green()

    def Blue(self) -> int:
        return self.gmat_obj.Blue()

    def Alpha(self) -> int:
        return self.gmat_obj.Alpha()


class Direction:
    # TODO move to a more appropriate file
    def __init__(self, x: int | float = 0, y: int | float = 0, z: int | float = 1):
        self.x = x
        self.y = y
        self.z = z


class FieldOfView(GmatObject):
    def __init__(self, fov_type: str = None, name: str = 'DefaultFOV'):
        allowed_fov_types = ['ConicalFOV', 'CustomFOV', 'RectangularFOV', None]
        if fov_type not in allowed_fov_types:
            raise TypeError(f'FieldOfView type given in fov_type "{fov_type}" is not recognized. Must be one of:\n'
                            f'{allowed_fov_types}')
        if fov_type is None:
            self.fov_type = 'RectangularFOV'
        else:
            self.fov_type = fov_type
        super().__init__(self.fov_type, name)

        # gmat.Construct returns a GmatBase for FOV, so get object in FOV type from Validator
        # self.gmat_obj = gpy.Moderator().gmat_obj.FindObject(self.name)
        # self.gmat_obj = gpy.Moderator().gmat_obj.CreateFieldOfView(self.fov_type, self.name)
        # self.gmat_obj = gpy.Validator().FindObject(self.name)
        # self.gmat_obj = gmat.Construct('RectangularFOV', 'DefRectFOV')
        # self.gmat_obj = gpy.Moderator().gmat_obj.GetFieldOfView(self.name)
        # print(type(self.gmat_obj))
        # print(self.gmat_obj)
        #
        # self.gmat_obj.Help()

        # # TODO remove (method checking only)
        # self.CheckTargetVisibility([0, 0, 0])
        # pass

    # def CheckTargetVisibility(self, target: list[int | float]):
    #     rv3 = gmat.Rvector3(target)  # convert to a GMAT Rvector3 object
    #     return self.gmat_obj.CheckTargetVisibility(rv3)

    @staticmethod
    def RADECtoConeClock(RA, dec):
        # FIXME: source code assigns both lines below to clock, so unsure which should be cone (see GMT-8120)
        cone = pi / 2 - dec
        clock = RA
        return cone, clock

    @staticmethod
    def UnitVecToRADEC(unit_vec: np.ndarray):
        if unit_vec[0] == 0 and unit_vec[1] == 0:
            if unit_vec[2] > 0:
                dec = pi / 2
            elif unit_vec[2] < 0:
                dec = -pi / 2
            else:
                raise RuntimeError('Vector is all zeros')
            ra = 0
        else:
            ra = atan2(unit_vec[1], unit_vec[0])
            dec = asin(unit_vec[2])

        return ra, dec


class ConicalFOV(FieldOfView):
    def __init__(self, name: str = 'DefaultConicalFOV', color: list = None, fov_angle: int | float = 30):
        super().__init__('ConicalFOV', name)

        self.color = [float(ele) for ele in self.GetField('Color')[1:-1].split(' ')]
        if color is None:
            # color: list = [0, 0, 0]
            color = Color()
        self.color = color  # None case already handled above

        self.fov_angle = fov_angle if fov_angle is not None else 30
        self.SetRealParameter('FieldOfViewAngle', self.fov_angle)

    def CheckTargetVisibility(self):
        raise NotImplementedError


class CustomFOV(FieldOfView):
    def __init__(self, name: str = 'DefaultCustomFOV'):
        super().__init__('CustomFOV', name)

    def CheckTargetVisibility(self):
        raise NotImplementedError


class RectangularFOV(FieldOfView):
    def __init__(self, name: str = 'DefaultRectangularFOV', angle_width: int | float = None,
                 angle_height: int | float = None):
        super().__init__('RectangularFOV', name)

        # Set initial angle width, in degrees
        if angle_width is None:
            self.angle_width = self.GetRealParameter('AngleWidth')
        else:
            self.angle_width = angle_width
            self.SetRealParameter('AngleWidth', self.angle_width)

        # Set initial angle height, in degrees
        if angle_height is None:
            self.angle_height = self.GetRealParameter('AngleHeight')
        else:
            self.angle_height = angle_height
            self.SetRealParameter('AngleHeight', self.angle_height)

        self.Initialize()

    def CheckTargetVisibility(self, target: np.ndarray) -> bool:
        ra, dec = self.UnitVecToRADEC(target)
        cone, clock = self.RADECtoConeClock(ra, dec)

        angle_height = self.GetRealParameter('AngleHeight')
        angle_width = self.GetRealParameter('AngleWidth')

        # using <= assures that 0 width, 0 height FOV never has point in FOV
        # if you want (0.0,0.0) to always be in FOV change to strict inequalities
        if (cone >= angle_height) or (cone <= -angle_height) or (clock >= angle_width) or (clock <= -angle_width):
            return False
        else:
            return True

    def GetMaskClockAngles(self) -> list:
        angle_width = self.GetRealParameter('AngleWidth')
        return [1, angle_width]

    def GetMaskConeAngles(self, degrees: bool = False):
        # # FIXME - broken because of GmatBase type for self
        # if not degrees:
        #     return self.gmat_obj.GetMaskConeAngles()
        # else:
        #     return self.gmat_obj.GetMaskConeAngles() * 180 / pi
        angle_height = self.GetRealParameter('AngleHeight')
        return [1, angle_height]


class Imager(GmatObject):
    def __init__(self, name: str, fov: gpy.FieldOfView | gmat.FieldOfView | str = None, direction_vec=None,
                 second_vec=None, hw_origin_in_bcs=None, r_sb: np.ndarray = None):
        super().__init__('Imager', name)

        self.spacecraft = None

        if fov is None:
            self.fov: RectangularFOV = RectangularFOV()
        elif isinstance(fov, (RectangularFOV, ConicalFOV, CustomFOV)):
            self.fov: RectangularFOV | ConicalFOV | CustomFOV = fov
        elif isinstance(fov, str):
            # fov str is presumed to be a path to an FoV file
            raise NotImplementedError
        else:
            raise TypeError(
                f'Type for fov "{type(fov).__name__}" is not recognized. Must be a FieldOfView object or str'
                f' representing a path to an FoV file')

        # direction_vec is field-of-view boresight vector expressed in spacecraft body coordinates
        if direction_vec is None:
            direction_vec = [0, 0, 1]  # use as default
            self.direction_vec = Direction(direction_vec[0], direction_vec[1], direction_vec[2])
            self.SetField('DirectionX', self.direction_vec.x)
            self.SetField('DirectionY', self.direction_vec.y)
            self.SetField('DirectionZ', self.direction_vec.z)

        # second_vec is the vector, expressed in the body frame, used to resolve the sensor's orientation about the
        # boresite vector
        if second_vec is None:
            second_vec = [0, 0, 1]
            self.second_vec = second_vec

        # origin of the Imager's coordinate system expressed in the spacecraft’s body coordinate system
        if hw_origin_in_bcs is None:
            hw_origin_in_bcs = [0, 0, 0]
            self.hw_origin_in_bcs = hw_origin_in_bcs

        # r_sb is rotation matrix from spacecraft body frame to Imager frame
        if r_sb is None:
            self.r_sb11 = self.GetRealParameter('R_SB11')
            self.r_sb12 = self.GetRealParameter('R_SB12')
            self.r_sb13 = self.GetRealParameter('R_SB13')
            self.r_sb21 = self.GetRealParameter('R_SB21')
            self.r_sb22 = self.GetRealParameter('R_SB22')
            self.r_sb23 = self.GetRealParameter('R_SB23')
            self.r_sb31 = self.GetRealParameter('R_SB31')
            self.r_sb32 = self.GetRealParameter('R_SB32')
            self.r_sb33 = self.GetRealParameter('R_SB33')
            self.r_sb = np.array([[self.r_sb11, self.r_sb12, self.r_sb13],
                                  [self.r_sb21, self.r_sb22, self.r_sb23],
                                  [self.r_sb31, self.r_sb32, self.r_sb33],])

            # # use 3x3 identity matrix as default (same as within GMAT)
            # self.r_sb: np.ndarray = np.eye(3, 3)
            # self.r_sb11 = int(self.r_sb[0][0])
            # self.SetRealParameter('R_SB11', self.r_sb11)
            # self.r_sb12 = int(self.r_sb[0][1])
            # self.SetRealParameter('R_SB12', self.r_sb12)
            # self.r_sb13 = int(self.r_sb[0][2])
            # self.SetRealParameter('R_SB13', self.r_sb13)
            # self.r_sb21 = int(self.r_sb[1][0])
            # self.SetRealParameter('R_SB21', self.r_sb21)
            # self.r_sb22 = int(self.r_sb[1][1])
            # self.SetRealParameter('R_SB22', self.r_sb22)
            # self.r_sb23 = int(self.r_sb[1][2])
            # self.SetRealParameter('R_SB23', self.r_sb23)
            # self.r_sb31 = int(self.r_sb[2][0])
            # self.SetRealParameter('R_SB31', self.r_sb31)
            # self.r_sb32 = int(self.r_sb[2][1])
            # self.SetRealParameter('R_SB32', self.r_sb32)
            # self.r_sb33 = int(self.r_sb[2][2])
            # self.SetRealParameter('R_SB33', self.r_sb33)

        else:  # r_sb is not None
            self.r_sb: np.ndarray = r_sb
            self.r_sb11 = float(r_sb[0][0])
            self.SetRealParameter('R_SB11', self.r_sb11)
            self.r_sb12 = float(r_sb[0][1])
            self.SetRealParameter('R_SB12', self.r_sb12)
            self.r_sb13 = float(r_sb[0][2])
            self.SetRealParameter('R_SB13', self.r_sb13)
            self.r_sb21 = float(r_sb[1][0])
            self.SetRealParameter('R_SB21', self.r_sb21)
            self.r_sb22 = float(r_sb[1][1])
            self.SetRealParameter('R_SB22', self.r_sb22)
            self.r_sb23 = float(r_sb[1][2])
            self.SetRealParameter('R_SB23', self.r_sb23)
            self.r_sb31 = float(r_sb[2][0])
            self.SetRealParameter('R_SB31', self.r_sb31)
            self.r_sb32 = float(r_sb[2][1])
            self.SetRealParameter('R_SB32', self.r_sb32)
            self.r_sb33 = float(r_sb[2][2])
            self.SetRealParameter('R_SB33', self.r_sb33)

        # Attach FOV to Imager
        self.SetStringParameter(22, self.fov.GetName())  # 22 for FOV_MODEL
        self.SetRefObjectName(gmat.FIELD_OF_VIEW, self.fov.name)
        self.SetRefObject(self.fov, gmat.FIELD_OF_VIEW, self.fov.name)

        print(self.CheckTargetVisibility([1, 0, 0]))
        pass

    def __repr__(self):
        return f'An Imager named "{self.GetName()}"'

    def attach_to_sat(self, sat: gpy.Spacecraft | gmat.Spacecraft):
        sat_gmat = gpy.extract_gmat_obj(sat)
        sat_gmat.SetStringParameter(104, self.GetName())  # 104 for sat's ADD_HARDWARE

    @staticmethod
    def from_dict(imager_dict: dict[str, Union[str, int, float]]):
        raise NotImplementedError
        # try:
        #     name = imager_dict['Name']
        # except KeyError:  # no name found - use default
        #     name = 'DefaultImager'
        # imager = Imager(name)
        #
        # fields: list[str] = list(imager_dict.keys())
        # fields.remove('Name')
        #
        # # TODO convert to imager.SetFields
        # for field in fields:
        #     imager.SetField(field, imager_dict[field])
        #     setattr(imager, field, imager_dict[field])
        #
        # imager.Validate()
        #
        # return imager

    def CheckTargetVisibility(self, target: np.ndarray | list):
        """

        :param target: unit vector to the target in the spacecraft body frame
        :return: True if the target vector points within the Imager's FOV, False otherwise
        """
        # NOTE: this only considers rotation, not translation
        print('\n** Warning! Imager.CheckTargetVisibility currently only considers rotation and not translation, so its'
              ' result may be incorrect for situations involving translation **\n')
        if isinstance(target, list):
            target = np.array(target)
        vec = self.r_sb.diagonal() * target
        return self.fov.CheckTargetVisibility(vec)

    def GetFieldOfView(self) -> gmat.GmatBase:
        # self.gmat_obj.GetFieldOfView() returns a SwigPyObject that isn't usable
        # Instead, get FOV's name with GetRefObjectName, then get its object with gmat.GetObject
        fov_name = self.GetRefObjectName(gmat.FIELD_OF_VIEW)
        fov: gmat.GmatBase = gmat.GetObject(fov_name)
        return fov

    def GetMaskClockAngles(self) -> list:
        return list(self.gmat_obj.GetMaskClockAngles().GetRealArray())

    def GetMaskConeAngles(self) -> list:
        return list(self.gmat_obj.GetMaskConeAngles().GetRealArray())


class NuclearPowerSystem(GmatObject):
    def __init__(self, name: str):
        super().__init__('NuclearPowerSystem', name)

        self.spacecraft = None

        # TODO add parsing of each field under Help()
        # self.Help()
        pass

    def __repr__(self):
        return f'A NuclearPowerSystem named "{self.GetName()}"'

    def attach_to_sat(self, sat: gpy.Spacecraft | gmat.Spacecraft) -> bool:
        self.spacecraft = sat
        if sat.GetField('PowerSystem') == '':
            self.spacecraft.add_nps(self)
        else:
            return False

    @staticmethod
    def from_dict(nps_dict: dict[str, Union[str, int, float]]):
        try:
            name = nps_dict['Name']
        except KeyError:  # no name found - use default
            name = 'DefaultNuclearPowerSystem'
        nps = NuclearPowerSystem(name)

        fields: list[str] = list(nps_dict.keys())
        fields.remove('Name')

        # TODO convert to nps.SetFields
        for field in fields:
            nps.SetField(field, nps_dict[field])
            setattr(nps, field, nps_dict[field])

        nps.Validate()

        return nps


class SolarPowerSystem(GmatObject):
    def __init__(self, name: str):
        super().__init__('SolarPowerSystem', name)

        self.spacecraft = None

        # TODO add parsing of each field under Help()
        # self.Help()
        pass

    def __repr__(self):
        return f'A SolarPowerSystem named "{self.GetName()}"'

    def attach_to_sat(self, sat: gpy.Spacecraft | gmat.Spacecraft):
        self.spacecraft = sat
        if sat.GetField('PowerSystem') == '':
            self.spacecraft.add_sps(self)
        else:
            return False
        pass

    @staticmethod
    def from_dict(sps_dict: dict[str, Union[str, int, float]]):
        if sps_dict == {}:
            return

        name = sps_dict.get('Name', 'DefaultSolarPowerSystem')
        sps = SolarPowerSystem(name)

        fields: list[str] = list(sps_dict.keys())
        fields.remove('Name')

        # TODO convert to sps.SetFields
        for field in fields:
            sps.SetField(field, sps_dict[field])
            setattr(sps, field, sps_dict[field])

        sps.Validate()

        return sps
