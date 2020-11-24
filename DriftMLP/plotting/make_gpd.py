import geopandas as gpd
import igraph
import numpy as np
from shapely.geometry import Point

import cartopy.crs as ccrs
import DriftMLP.plotting.shape_helpers as shp_help
from DriftMLP.drifter_indexing.discrete_system import DefaultSystem


def network_to_multipolygon_df(network: igraph.Graph, discretizer=DefaultSystem):
    h3_id = list(network.vs['name'])
    h3_df = list_to_multipolygon_df(h3_id, discretizer)
    if 'rotation' in network.attributes():
        h3_df['rotated_centroid'] = h3_df.apply(lambda x: Point(
            network['rotation'](x.centroid_col.x, x.centroid_col.y, inverse=True)), axis=1)
    else:
        h3_df['rotated_centroid'] = h3_df['centroid_col']

    return h3_df


def full_multipolygon_df(discretizer=DefaultSystem):
    coords_lat, coords_lon = np.meshgrid(np.linspace(-90, 90, 3000),
                                         np.linspace(-180, 180, 3000))
    h3_list = [discretizer.geo_to_ind(lon=lon, lat=lat)
               for lon, lat in zip(coords_lon.flatten(), coords_lat.flatten())]
    return list_to_multipolygon_df(h3_list, discretizer=discretizer)


def list_to_multipolygon_df(list_of_inds, discretizer=DefaultSystem, split=True):
    """

    Parameters
    ----------
    split : object
    """
    unique_h3 = list(set(list_of_inds))
    polys = [discretizer.ind_to_boundary(cod) for cod in unique_h3]
    if split:
        polys = [shp_help.split_polys(poly) for poly in polys]
    # h3_poly_lon_lat = [Polygon([a[::-1] for a in poly]) for poly in polys]
    geo_df = gpd.GeoDataFrame(
        {'geometry': polys},
        crs="EPSG:4326",
        index=unique_h3)
    ##the normal.centroid shapely will not work to give the same as h3.h3_to_geo
    geo_df.to_crs(crs="EPSG:4326")
    if hasattr(discretizer, 'ind_to_geo'):
        geo_df['centroid_col'] = [Point(discretizer.ind_to_geo(hexa))
                                  for hexa in unique_h3]
    else: 
        geo_df['centroid_col'] = geo_df.centroid

    return geo_df


class network_helpers:
    def __init__(self, h3_transitions, Stations_df):
        self.network = h3_transitions
        self.Stations = Stations_df.copy()
        self.polydf = network_to_multipolygon_df(h3_transitions)
