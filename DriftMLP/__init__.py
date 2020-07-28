import igraph

from DriftMLP import form_network
from DriftMLP import shortest_path
from DriftMLP.drifter_indexing import driftiter
from DriftMLP.drifter_indexing import story
from DriftMLP.rotations import random_ll_rot
from .plotting.make_h3_gpd import network_to_multipolygon_df


def file_to_network(driftfile, drift_kwargs=None, day_cut_off=5, silent=False) -> igraph.Graph:
    if drift_kwargs is None:
        drift_kwargs = {'variables': ['position', 'drogue', 'datetime'],
                        'drop_na': False,
                        'drogue': True}
        print('Making transition matrix with drogued drifters,'
              ' see file_to_network function'
              ' to change this.')
    drift_gen = driftiter.generator(driftfile)
    h3_stories = story.get_story(drift_gen(**drift_kwargs))
    net = form_network.make_transition(h3_stories, day_cut_off=day_cut_off, observations_per_day=4)
    if 'lon_lat_transform' in drift_kwargs.keys():
        net['rotation'] = drift_kwargs['lon_lat_transform']

    return net


def network_from_file(fname, visual=True, **kwargs) -> igraph.Graph:
    name, postfix = fname.split('.')
    if postfix == 'gml':
        net = igraph.igraph_read_graph_graphml(fname)
    elif postfix == 'h5':
        print('Creating network from drifter data')
        net = file_to_network(fname, **kwargs)
    ##If rotation is not in the attributes, assume it is identity (no rotation)
    if 'rotation' not in net.attributes():
        net['rotation'] = random_ll_rot(identity=True)
    if 'gpd' not in net.attributes() and visual:
        net['gpd'] = network_to_multipolygon_df(net)
    return net


class MLP:
    def __init__(self, fname):
        self.net = network_from_file(fname)

    def get_mlpath(self, lon, lat):
        return shortest_path.single_SP(self.net, lon, lat)
