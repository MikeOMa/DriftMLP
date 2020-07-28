import geopandas as gpd
import h3.api.basic_int as h3
import igraph
import numpy as np
from shapely.geometry import Point

import DriftMLP.plotting.shape_helpers as shp_help


def network_to_multipolygon_df(network: igraph.Graph):
    h3_id = list(network.vs['name'])
    h3_df = list_to_multipolygon_df(h3_id)
    if 'rotation' in network.attributes():
        h3_df['rotated_centroid'] = h3_df.apply(lambda x: Point(
            network['rotation'](x.centroid_col.x, x.centroid_col.y, inverse=True)), axis=1)
    else:
        h3_df['rotated_centroid'] = h3_df['centroid_col']

    return h3_df


def full_multipolygon_df(res=3):
    coords_lat, coords_lon = np.meshgrid(np.linspace(-90, 90, 500),
                                         np.linspace(-180, 180, 500))
    h3_list = [h3.geo_to_h3(lng=lon, lat=lat, res=res)
               for lon, lat in zip(coords_lon.flatten(), coords_lat.flatten())]
    return list_to_multipolygon_df(h3_list)


def list_to_multipolygon_df(list_of_h3, split=True):
    """

    Parameters
    ----------
    split : object
    """
    unique_h3 = list(set(list_of_h3))
    h3_poly = [h3.h3_to_geo_boundary(cod, geo_json=True) for cod in unique_h3]
    if split:
        h3_poly = [shp_help.split_polys(poly) for poly in h3_poly]
    # h3_poly_lon_lat = [Polygon([a[::-1] for a in poly]) for poly in h3_poly]
    h3_df = gpd.GeoDataFrame(
        {'geometry': h3_poly},
        crs="EPSG:4326",
        index=unique_h3)
    ##the normal.centroid shapely will not work to give the same as h3.h3_to_geo.
    h3_df['centroid_col'] = [Point(h3.h3_to_geo(hexa)[::-1])
                             for hexa in unique_h3]
    return h3_df


class network_helpers:
    def __init__(self, h3_transitions, Stations_df):
        self.network = h3_transitions
        self.Stations = Stations_df.copy()
        self.polydf = network_to_multipolygon_df(h3_transitions)
