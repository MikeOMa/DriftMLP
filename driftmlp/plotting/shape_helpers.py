from typing import List

from shapely.geometry import LineString, MultiPolygon, Polygon
from shapely.ops import split


def lng180_to_360(list_of_coords: List) -> List:
    return [[i[0] + 360, i[1]] if i[0] < 0 else i for i in list_of_coords]


def lng360_to_180(list_of_coords):
    att = [[i[0] - 360, i[1]] if i[0] > 180 else i for i in list_of_coords]
    neg = [i[0] < 0 for i in att]
    if any(neg):
        return [[-180, i[1]] if i[0] == 180 else i for i in att]
    else:
        return att


def splitpoly_at_primemeridean(list_of_coords, shapely_ret=True):
    trans = lng180_to_360(list_of_coords)
    shp = Polygon(trans)
    prime_meridean = LineString([[180, -100], [180, 100]])
    q = list(split(shp, prime_meridean))
    shapes = []
    for i in q:
        p = list(i.exterior.coords)
        coords = lng360_to_180(p)
        shapes.append(coords)
    if shapely_ret:
        return MultiPolygon([Polygon(shape) for shape in shapes])
    else:
        return shapes


def split_polys(list_of_coords, shapely_ret=True):
    lon = [i[0] for i in list_of_coords]
    lon_close_lower = [i < -176 for i in lon]
    lon_close_upper = [i > 176 for i in lon]
    if any(lon_close_upper) and any(lon_close_lower):
        return splitpoly_at_primemeridean(list_of_coords, shapely_ret=shapely_ret)
    else:
        if shapely_ret:
            return Polygon(list_of_coords)
        else:
            return [list_of_coords]
