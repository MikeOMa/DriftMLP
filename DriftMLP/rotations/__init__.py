import math
from math import sin, cos

import numpy as np
from scipy.spatial.transform import Rotation as R


def ll_to_xyz(lon, lat):
    lon_rad = math.radians(lon)
    lat_rad = math.radians(lat)
    x = cos(lon_rad) * cos(lat_rad)
    y = sin(lon_rad) * cos(lat_rad)
    z = sin(lat_rad)
    return [x, y, z]


def xyz_to_ll(x, y, z):
    lat_rad = math.asin(z)
    lon_rad = math.atan2(y, x)
    lat = math.degrees(lat_rad)
    lon = math.degrees(lon_rad)
    return [lon, lat]


def random_rot_xyz_quat():
    p = np.random.randn(4)
    p = p / np.linalg.norm(p)
    rot = R.from_quat(p)
    return rot


def random_rot_xyz_arvo(identity=False):
    if identity:
        random_pars = [0, 0, 1]
    else:
        random_pars = np.random.uniform(0, 1, 3)

    theta = random_pars[0] * np.pi * 2
    R1 = np.array([[np.cos(theta), np.sin(theta), 0],
                   [-np.sin(theta), np.cos(theta), 0],
                   [0, 0, 1]]
                  )
    phi = random_pars[1] * np.pi * 2
    z = random_pars[2]
    v = np.array([np.cos(phi) * np.sqrt(z), np.sin(phi) * np.sqrt(z), np.sqrt(1 - z)]).reshape(3, 1)
    R2 = 2 * v @ v.T - np.eye(3)
    final_rot_matrix = R2 @ R1
    rot = R.from_matrix(final_rot_matrix)
    return rot

class random_ll_rot:
    def __init__(self, seed=None, identity=False, method='quat'):
        if seed is not None:
            np.random.seed(seed)

        if identity:
            self.rot = R.from_euler('xyz', [0] * 3)
        elif method == 'arvo':
            self.rot = random_rot_xyz_arvo()
        else:
            self.rot = random_rot_xyz_quat()

    def __call__(self, loc_1, loc_2=None, **kwargs):
        if loc_2 is not None:
            x, y, z = ll_to_xyz(loc_1, loc_2)
            rot_xyz = self.rot.apply([x, y, z], **kwargs)
            ret = xyz_to_ll(*rot_xyz)
        elif isinstance(loc_1, list):
            ret = self.list_call(loc_1)
        elif isinstance(loc_1, np.ndarray):
            ret = self.arr_call(loc_1)
        else:
            ValueError('Supply either loc_1: numeric , loc_2: numeric'
                       'OR loc_1 : list',
                       'OR loc_1 : np.ndarray')
        return ret

    def list_call(self, lon_lat_iter, **kwargs):
        return self.__call__(*lon_lat_iter, **kwargs)

    def arr_call(self, arr, **kwargs):
        ### Coded to use numpys functions for effiency.
        lon_rad = np.radians(arr[:, 0])
        lat_rad = np.radians(arr[:, 1])
        x = np.cos(lon_rad) * np.cos(lat_rad)
        y = np.sin(lon_rad) * np.cos(lat_rad)
        z = np.sin(lat_rad)
        arr = np.vstack([x, y, z]).T
        res = self.rot.apply(arr, **kwargs)
        lon_rad_t = np.arctan2(res[:, 1], res[:, 0])
        lat_rad_t = np.arcsin(res[:, 2])
        lon_t = np.degrees(lon_rad_t)
        lat_t = np.degrees(lat_rad_t)
        loc_arr = np.vstack([lon_t, lat_t]).T
        return(loc_arr)
