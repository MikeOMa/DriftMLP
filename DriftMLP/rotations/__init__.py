
import numpy as np
import math
from numba import jit
from math import sin, asin, sqrt, radians, cos, atan2, degrees
from scipy.spatial.transform import Rotation as R


@jit
def ll_to_xyz(lon, lat):
    lon_rad = math.radians(lon)
    lat_rad = math.radians(lat)
    x = cos(lon_rad)*cos(lat_rad)
    y = sin(lon_rad)*cos(lat_rad)
    z = sin(lat_rad)
    return [x, y, z]


@jit
def xyz_to_ll(x, y, z):
    lat_rad = math.asin(z)
    lon_rad = math.atan2(y, x)
    lat = math.degrees(lat_rad)
    lon = math.degrees(lon_rad)
    return [lon, lat]


def random_rot_xyz():
    p = np.random.randn(4)
    p = p/np.linalg.norm(p)
    rot = R.from_quat(p)
    return rot


class random_ll_rot:
    def __init__(self, seed=None, identity=True):
        if seed is not None:
            np.random.seed(seed)
        self.rot = random_rot_xyz()
        if identity:
            self.rot = R.from_euler('xyz', [0]*3)

    def __call__(self, lon, lat, **kwargs):
        x, y, z = ll_to_xyz(lon, lat)
        rot_xyz = self.rot.apply([x, y, z], **kwargs)
        lon_rot, lat_rot = xyz_to_ll(*rot_xyz)
        return lon_rot, lat_rot

    def list_call(self, lon_lat_iter, **kwargs):
        return self.__call__(*lon_lat_iter, **kwargs)

    def arr_call(self, arr, **kwargs):
        lon_rad = np.radians(arr[:, 0])
        lat_rad = np.radians(arr[:, 1])
        x = np.cos(lon_rad)*np.cos(lat_rad)
        y = np.sin(lon_rad)*np.cos(lat_rad)
        z = np.sin(lat_rad)
        arr = np.vstack([x, y, z]).T
        res = self.rot.apply(arr, **kwargs)
        lon_rad_t = np.arctan2(res[:, 1], res[:, 0])
        lat_rad_t = np.arcsin(res[:, 2])
        lon_t = np.degrees(lon_rad_t)
        lat_t = np.degrees(lat_rad_t)
        loc_arr = np.vstack([lon_t, lat_t]).T
        return(loc_arr)
