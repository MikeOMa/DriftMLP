from typing import Tuple
from warnings import warn

import h3.api.basic_int as h3
import numpy as np
from numba import jit
from shapely.geometry import Polygon


class discrete_system:
    def __init__(self):
        pass

    def ind_to_boundary(self):
        pass

    def geo_boundary(self, *args, **kwargs):
        Polygon(self.ind_to_boundary(*args, **kwargs))


class h3_default(discrete_system):
    def __init__(self, res=3):
        self.res = res

    def geo_to_ind(self, lon, lat):
        return h3.geo_to_h3(lng=lon, lat=lat, resolution=self.res)

    def ind_to_boundary(self, ind):
        return h3.h3_to_geo_boundary(ind)

    def ind_to_point(self, ind):
        return h3.h3_to_geo(ind)


@jit(nopython=True)
def get_first_ind(val, grid_array):
    for i, grid_value in enumerate(grid_array):
        if grid_value > val:
            break
    return i


class lon_lat_grid(discrete_system):
    def __init__(self, res=0.5):
        self.res = res
        self.space_range = [-180, 180, -90, 90]
        self.length_of_grid = [self.space_range[1] - self.space_range[0],
                               self.space_range[3] - self.space_range[2]]
        dims_of_grid_float = [i / self.res for i in self.length_of_grid]

        ##Round off the values, then check if res divides the length evenly.
        self.dims_of_grid = [int(i) for i in dims_of_grid_float]
        is_even = [(i - j) < 1e-3 for i, j in zip(dims_of_grid_float, self.dims_of_grid)]
        print(is_even)
        if not all(is_even):
            warn("In the longitude/latitude grid the resolution does not divide the space evenly."
                 " Setting the res parameter sensibly will fix this.")
        self.lon_range, self.lon_step = np.linspace(self.space_range[0], self.space_range[1], self.dims_of_grid[0] + 1,
                                                    retstep=True)
        self.n_lon = self.lon_range.shape[0]
        self.lat_range, self.lat_step = np.linspace(self.space_range[2], self.space_range[3], self.dims_of_grid[1] + 1,
                                                    retstep=True)
        self.coord_grid = [(i, j) for i in self.lon_range for j in self.lat_range]

    def latlonind_to_ind(self, lon_ind, lat_ind):
        ##Maps to a reversible id system
        return lon_ind + self.n_lon * lat_ind

    def ind_to_latlonind(self, id):
        ##Inverse of lat lon ind function above
        lon_ind = id % self.n_lon
        lat_ind = (id - lon_ind) / self.n_lon
        # round results to make them ints.
        return round(lon_ind), round(lat_ind)

    def geo_to_ind(self, lon: float, lat: float):
        ##argmax returns index of first true.
        lon_ind = get_first_ind(lon, self.lon_range)
        lat_ind = get_first_ind(lat, self.lat_range)
        ##return the index that we can reverse.
        return self.latlonind_to_ind(lon_ind, lat_ind)

    def ind_to_boundary(self, ind: int) -> Tuple[Tuple[float]]:
        """

        Returns
        -------
        :
        """
        lon_ind, lat_ind = self.ind_to_latlonind(ind)
        lon_upper = self.lon_range[lon_ind]
        lon_lower = lon_upper - self.lon_step
        lat_upper = self.lat_range[lat_ind]
        lat_lower = lat_upper - self.lat_step
        geometry_points = (
            (lon_upper, lat_upper),
            (lon_upper, lat_lower),
            (lon_lower, lat_lower),
            (lon_lower, lat_upper)
        )
        return geometry_points