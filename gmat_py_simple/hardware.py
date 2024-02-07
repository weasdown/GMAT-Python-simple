from __future__ import annotations

from math import pi, atan2, asin
from typing import Union

import numpy as np

from load_gmat import gmat
import gmat_py_simple as gpy
from gmat_py_simple import GmatObject


class Antenna(GmatObject):
    def __init__(self, name: str, boresight: np.ndarray | list = np.array([1, 0, 0])):
        super().__init__('Antenna', name)

        self._boresight = np.array(boresight) if not isinstance(boresight, np.ndarray) else boresight

        raise NotImplementedError


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


# class Direction:
#     # TODO move to a more appropriate file
#     def __init__(self, x: int | float = 0, y: int | float = 0, z: int | float = 1):
#         self.x = x
#         self.y = y
#         self.z = z


class FieldOfView(GmatObject):
    def __init__(self, attached_object: gpy.Imager | gpy.Antenna, fov_type: str = None, name: str = 'DefaultFOV'):
        allowed_fov_types = ['ConicalFOV', 'CustomFOV', 'RectangularFOV', None]
        if fov_type not in allowed_fov_types:
            raise TypeError(f'FieldOfView type given in fov_type "{fov_type}" is not recognized. Must be one of:\n'
                            f'{allowed_fov_types}')
        if fov_type is None:
            self.fov_type = 'RectangularFOV'
        else:
            self.fov_type = fov_type

        super().__init__(self.fov_type, name)

        self.attached_obj = attached_object  # e.g. an Imager or Antenna that uses this FieldOfView

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
    def __init__(self, attached_object: gpy.Imager | gpy.Antenna, name: str = 'DefaultConicalFOV', color: list = None,
                 fov_angle: int | float = 30):
        super().__init__(attached_object, 'ConicalFOV', name)

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
    def __init__(self, attached_object: gpy.Imager | gpy.Antenna, name: str = 'DefaultCustomFOV'):
        super().__init__(attached_object, 'CustomFOV', name)

    def CheckTargetVisibility(self):
        raise NotImplementedError


class RectangularFOV(FieldOfView):
    def __init__(self, attached_object: gpy.Imager | gpy.Antenna, name: str = 'DefaultRectangularFOV',
                 angle_width: int | float = None, angle_height: int | float = None):
        super().__init__(attached_object, 'RectangularFOV', name)

        self._boresight = self.attached_obj.boresight  # inherit boresight from attached Imager/Antenna

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

    def CustomCheckTargetVisibility(self, target: np.ndarray | list) -> bool:
        """
        Determine whether a point is within the Imager's field of view.

        Note: this currently assumes that the Y-axis is the boresight, the X-axis is towards the right of the FOV, and
        the Z-axis is pointing up in the FOV. The origin is taken to be the center of the Imager's sensor/FOV.
        # TODO: change this to match GMAT, which uses z for boresight, v for second_vec, x for normalized version of
           normal to z and v (N), y as z cross x.

        Overall process:
        1) Find the vectors that give the edges of the FOV
        2) Find the normal vector to each pair of adjacent vectors such that the normal points into the FOV
        3) The target is in the FOV if the dot product of the target's position vector and the normal vector is
        positive, for all four of the normal vectors.

        :param target: np array or list representation of a 3D position vector for the target point
        :return in_fov: bool - True if target is in field of view, False if not
        """

        def get_edge_vectors(bs: np.ndarray, a: int | float, b: int | float):
            a2 = a / 2
            b2 = b / 2

            # Find vectors: K: top left edge of FOV, L: top right, M: bottom left, N: bottom right
            klmn = []  # list that will be filled with vectors for edges of FOV
            vector_params = ((1, 1), (-1, 1), (1, -1), (-1, -1))  # multipliers to give correct vector orientations

            for vec in vector_params:
                # Pre-calculate cosine and sine of half-width and half-height
                # Multiply a2 and b2 by 1 or -1 as appropriate for the vector being calculated
                a2_for_vec = a2 * vec[0]
                b2_for_vec = b2 * vec[1]
                ca2 = np.cos(np.deg2rad(a2_for_vec))
                sa2 = np.sin(np.deg2rad(a2_for_vec))
                cb2 = np.cos(np.deg2rad(b2_for_vec))
                sb2 = np.sin(np.deg2rad(b2_for_vec))

                # Rotate boresight around Z-axis by a2 degrees (direction as appropriate)
                trans_mat = np.array([[ca2, -sa2, 0, 0],
                                      [sa2, ca2, 0, 0],
                                      [0, 0, 1, 0],
                                      [0, 0, 0, 1]])
                z_rot = np.matmul(trans_mat, bs)

                # Rotate z_rot around X-axis by b2 degrees (direction as appropriate)
                trans_mat = np.array([[1, 0, 0, 0],
                                      [0, cb2, -sb2, 0],
                                      [0, sb2, cb2, 0],
                                      [0, 0, 0, 1]])
                vec = np.matmul(trans_mat, z_rot)
                vec = vec[:-1]  # remove the last element (1) that was just to enable matrix multiplication

                klmn.append(vec)  # append the calculated vector to the list of K, L, M, N vectors

            return klmn

        # Check target position vector is valid
        if len(target) != 3:
            raise AttributeError(f'target has an invalid number of elements ({len(target)}) - must be 3 to represent a '
                                 f'3D position vector for the target point')
        # Convert to numpy array if a list to use numpy's better performance
        if isinstance(target, list):
            target: np.ndarray = np.array(target)

        # TODO: transform boresight to consider Imager second_vec and rotation_matrix
        boresight = np.append(self._boresight, 1)

        alpha = self.angle_width
        beta = self.angle_height

        # Find the vectors that define the four corners of the FOV
        # k: top left edge of FOV, l: top right, m: bottom left, n: bottom right
        k, l, m, n = get_edge_vectors(boresight, alpha, beta)

        # normal_params: pairs of vectors that will be cross-producted to find a normal vector pointing into the FOV
        # Each pair of vectors forms a planar face of the FOV
        # Note: vectors must be given in this order (e.g. n, m rather than m, n) for cross product to point into FOV
        normals_params = ((m, k), (l, n), (k, l), (n, m))  # left, right, top, bottom
        normal_vecs = np.array([np.cross(param[0], param[1]) for param in normals_params])

        # If the target is within the FOV, the normal will point more towards the target than away. This means the dot
        # product of the normal and the target's position vector will be positive
        dot_results = np.dot(normal_vecs, target)

        return True if all(dot_results > 0) else False

    def GetMaskClockAngles(self) -> list:
        angle_width = self.GetRealParameter('AngleWidth')
        return [1, angle_width]

    def GetMaskConeAngles(self):
        # # FIXME - broken because of GmatBase type for self
        # if not degrees:
        #     return self.gmat_obj.GetMaskConeAngles()
        # else:
        #     return self.gmat_obj.GetMaskConeAngles() * 180 / pi
        angle_height = self.GetRealParameter('AngleHeight')
        return [1, angle_height]


# Line below disables false positive "This code is unreachable" warning with np.cross()
# noinspection PyUnreachableCode
class Imager(GmatObject):
    def __init__(self, name: str, fov: gpy.FieldOfView | gmat.FieldOfView | str = None,
                 rotation_matrix: np.ndarray = None, boresight: np.ndarray | list = None,
                 second_vec: np.ndarray | list = None, hw_origin_in_bcs=None):
        super().__init__('Imager', name)
        self.Initialize()  # must be initialized here so vector/matrix parameters are set correctly

        bs = [self.GetRealParameter('DirectionX'), self.GetRealParameter('DirectionY'),
              self.GetRealParameter('DirectionZ')]
        print(f'Boresight straight after init Initialize: {bs}')  # [1, 0, 0]

        self.spacecraft = None

        self.rot_mat_fields = ['R_SB11', 'R_SB12', 'R_SB13',
                               'R_SB21', 'R_SB22', 'R_SB23',
                               'R_SB31', 'R_SB32', 'R_SB33']

        if rotation_matrix is None:  # rotation matrix from spacecraft body frame to Imager frame
            # Get list of values then reshape from 1x9 to 3x3 and store as ndarray
            gmat_rot_mat_vals = [self.GetRealParameter(field) for field in self.rot_mat_fields]
            self._rotation_matrix: np.ndarray = np.reshape(np.array(gmat_rot_mat_vals), (3, 3))
        else:
            self._rotation_matrix = rotation_matrix

        if boresight is None:
            dir_x_def: float = self.GetRealParameter('DirectionX')
            dir_y_def: float = self.GetRealParameter('DirectionY')
            dir_z_def: float = self.GetRealParameter('DirectionZ')
            self._boresight = np.array([dir_x_def, dir_y_def, dir_z_def])
        else:  # a boresight vector has been provided
            if len(boresight) != 3:
                raise AttributeError(
                    f'Imager boresight argument an invalid number of elements ({len(boresight)}) - must'
                    f' be 3 to represent a 3D direction vector for the Imager\'s boresight')
            # Ensure self._boresight is a np.ndarray - convert from list if necessary
            if isinstance(boresight, list):
                self._boresight: np.ndarray = np.array([float(ele) for ele in boresight])
            else:
                self._boresight = boresight
            self.SetRealParameter('DirectionX', float(self._boresight[0]))
            self.SetRealParameter('DirectionY', float(self._boresight[1]))
            self.SetRealParameter('DirectionZ', float(self._boresight[2]))

        # second_vec is the 3D vector, expressed in the body frame, used to resolve the sensor's orientation about the
        #  boresite vector
        if second_vec is None:  # user did not provide second_vec, so get default from gmat_obj
            sec_dir_x_def: float = self.GetRealParameter('SecondDirectionX')
            sec_dir_y_def: float = self.GetRealParameter('SecondDirectionY')
            sec_dir_z_def: float = self.GetRealParameter('SecondDirectionZ')

            self.second_vec = np.array([sec_dir_x_def, sec_dir_y_def, sec_dir_z_def])
        else:  # second_vec is not None, so the user provided one
            # Expecting a 3D vector
            if len(second_vec) != 3:
                raise AttributeError(
                    f'Imager second_vec argument an invalid number of elements ({len(second_vec)}) - must'
                    f' be 3 to represent a 3D direction vector for the Imager\'s second vector')
            # Ensure self.second_vec is a np.ndarray - convert from list if necessary
            if isinstance(second_vec, list):
                self._second_vec: np.ndarray = np.array([float(ele) for ele in second_vec])
            elif isinstance(second_vec, np.ndarray):
                self._second_vec: np.ndarray = second_vec
            self.SetRealParameter('DirectionX', float(self._boresight[0]))
            self.SetRealParameter('DirectionY', float(self._boresight[1]))
            self.SetRealParameter('DirectionZ', float(self._boresight[2]))

        # TODO: pass self.rotation_matrix, self._boresight, self.second_vec to FieldOfView creation
        #  but also check against FieldOfView creation in src
        if fov is None:
            self.fov: RectangularFOV = RectangularFOV(self)
        elif isinstance(fov, (RectangularFOV, ConicalFOV, CustomFOV)):
            self.fov: RectangularFOV | ConicalFOV | CustomFOV = fov
            self.fov.attached_obj = self
        elif isinstance(fov, str):
            # fov str is presumed to be a path to an FoV file
            raise NotImplementedError
        else:
            raise TypeError(
                f'Type for fov "{type(fov).__name__}" is not recognized. Must be a FieldOfView object or str'
                f' representing a path to an FoV file')

        # origin of the Imager's coordinate system expressed in the spacecraft’s body coordinate system
        if hw_origin_in_bcs is None:
            hw_origin_in_bcs = [0, 0, 0]
            self.hw_origin_in_bcs = hw_origin_in_bcs

        # Attach FOV to Imager
        self.SetStringParameter(22, self.fov.GetName())  # 22 for FOV_MODEL
        self.SetRefObjectName(gmat.FIELD_OF_VIEW, self.fov.name)
        self.SetRefObject(self.fov, gmat.FIELD_OF_VIEW, self.fov.name)

        self.Initialize()

    def __repr__(self):
        return f'An Imager named "{self.GetName()}"'

    def attach_to_sat(self, sat: gpy.Spacecraft | gmat.Spacecraft):
        sat_gmat = gpy.extract_gmat_obj(sat)
        sat_gmat.SetStringParameter(104, self.GetName())  # 104 for sat's ADD_HARDWARE

    @property
    def boresight(self):
        return self._boresight

    @boresight.setter
    def boresight(self, boresight):
        print('In boresight.setter')
        print(self._boresight)

        # TODO assume that the transformation being applied between the old and new boresights will also apply to the
        #  second_vec, so update that too. That will prevent the new boresight having a problematic cross product with
        #  the old second_vec
        old_boresight = [self.GetRealParameter('DirectionX'), self.GetRealParameter('DirectionY'),
                         self.GetRealParameter('DirectionZ')]
        old_second_vec = [self.GetRealParameter('SecondDirectionX'), self.GetRealParameter('SecondDirectionY'),
                          self.GetRealParameter('SecondDirectionZ')]

        self._boresight = boresight
        self.SetRealParameter('DirectionX', boresight[0])
        self.SetRealParameter('DirectionY', boresight[1])
        self.SetRealParameter('DirectionZ', boresight[2])

        self.Initialize()

        # TODO remove (debugging only)
        new_boresight = [self.GetRealParameter('DirectionX'), self.GetRealParameter('DirectionY'),
                         self.GetRealParameter('DirectionZ')]

        # FIXME: update_rotation_matrix throws error when this method setting boresight to [0, 1, 0]
        # At Imager initialization (within GMAT), rotation_matrix is calculated based on boresight, so needs updating
        self.update_rotation_matrix()

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

    def CheckTargetVisibility(self, target: np.ndarray | list) -> bool:
        """

        :param target: unit vector to the target in the spacecraft body frame
        :return: True if the target vector points within the Imager's FOV, False otherwise
        """
        # NOTE: this only considers rotation, not translation
        print('\n** Warning! Imager.CheckTargetVisibility currently only considers rotation and not translation, so its'
              ' result may be incorrect for situations involving translation **\n'
              '** Please use CustomCheckTargetVisibility instead until this replaces CheckTargetVisibility **\n')
        if isinstance(target, list):
            target = np.array(target)
        vec = self.rotation_matrix.diagonal() * target
        return self.fov.CheckTargetVisibility(vec)

    def CustomCheckTargetVisibility(self, target: np.ndarray | list) -> bool:
        print('\n# TODO: check whether self.boresight already in spacecraft body frame - use self.rotation_matrix to '
              'transform if not (printed in Imager.CustomCheckTargetVisibility)\n')  # TODO - see print string
        return self.fov.CustomCheckTargetVisibility(target)

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

    @property
    def rotation_matrix(self):
        return self._rotation_matrix

    @rotation_matrix.setter
    def rotation_matrix(self, rot_mat: np.ndarray):
        self._rotation_matrix = rot_mat
        new_rot_mat = rot_mat.reshape(-1)  # flatten the 3x3 array into a 1x9 array
        set_vals = [self.SetRealParameter(field, float(value)) for field, value in
                    zip(self.rot_mat_fields, new_rot_mat)]  # self.SetRealParameter returns True when successfully set
        if not all(set_vals):  # if not all values have been set successfully
            raise RuntimeError('Not all rotation matrix elements were successfully set in Imager.SetRotationMatrix() '
                               '(not all elements of all_set_successfully were True)')

    @property
    def second_vec(self):
        return self._second_vec

    @second_vec.setter
    def second_vec(self, second_vec):
        self._second_vec = second_vec
        # At Imager initialization (within GMAT), rotation_matrix is based on second_vec, so needs updating
        self.update_rotation_matrix()

    def update_rotation_matrix(self):
        # At Imager initialization (within GMAT), rotation_matrix is based on boresight and second_vec, so needs
        #  updating if either one changes. Process given in remarks on page 406 (PDF pg 415) of GMAT R2022a User Guide
        z = self.boresight
        n: np.ndarray = np.cross(z, self._second_vec)  # normal to boresight and second_vec
        m: float = np.linalg.norm(n)  # magnitude of n
        if np.isclose(m, 0):
            raise RuntimeError('magnitude of cross product of boresight and second_vec vectors is close to 0, which '
                               f'would cause major problems for GMAT. (magnitude is {m})')
        x = n / m
        y = np.cross(z, x)
        self.rotation_matrix = np.array([x, y, z])


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
