import pickle

import igraph
import numpy as np

from driftmlp import form_network
from driftmlp import shortest_path
from driftmlp.drifter_indexing import driftiter
from driftmlp.drifter_indexing import story
from driftmlp.drifter_indexing.discrete_system import DefaultSystem
from driftmlp.rotations import random_ll_rot
from .plotting.make_gpd import network_to_multipolygon_df


def file_to_network(driftfile=None, drift_kwargs=None, discretizer=DefaultSystem, day_cut_off=5, silent=False,
                    store_story=False, data_iterable=None) -> igraph.Graph:
    if drift_kwargs is None:
        drift_kwargs = {'variables': ['position', 'drogue', 'datetime'],
                        'drop_na': False,
                        'drogue': True}
        print('Making transition matrix with drogued drifters,'
              ' see file_to_network function'
              ' to change this.')
    condition = driftfile is None and driftiter is None
    assert not condition, ValueError("Exactly one of driftfile or driftiter must be not None in 'file_to_network'")

    if driftfile is not None:
        ##Create the drifter generator then call it.
        drift_gen = driftiter.generator(driftfile)(**drift_kwargs)
    elif driftiter is not None:
        drift_gen = data_iterable
    discrete_story = story.get_story(drift_gen, discretizer=discretizer)
    net = form_network.make_transition(discrete_story, day_cut_off=day_cut_off, observations_per_day=4)
    if 'lon_lat_transform' in drift_kwargs.keys():
        net['rotation'] = drift_kwargs['lon_lat_transform']
    if store_story:
        ## This is memory intensive hence why it is off by default!
        net['stories'] = discrete_story
    

    return net


def BootstrapNetwork(network: igraph.Graph, visual=False):
    assert 'stories' in network.attributes(), ValueError(
        'set store_story=True in file to network. Needed for bootstrap network')
    n_drift = len(network['stories'])
    boot_ids = np.random.randint(low=0, high=n_drift, size=n_drift, dtype=int).tolist()
    stories_bootstrap = [network['stories'][i] for i in boot_ids]
    boot_net = form_network.make_transition(stories_bootstrap, day_cut_off=network['day_cut_off'],
                                            observations_per_day=network['observations_per_day'])
    boot_net['rotation'] = network['rotation']
    if 'gpd' in network.attributes() and visual:
        boot_net['gpd'] = network['gpd']
    return boot_net


def GraphML_Reader(fname, process_edgename=True, **kwargs):
    net = igraph.Graph.Read_GraphML(fname)
    """
    edge attribute 'name' needs to match the python typing.
    """
    num_interest = net.vs[0]['name']
    if type(num_interest) in [int, float]:
        warnings.warn('GraphML often handles numerical edge attributes poorly when the numbers are large.' \
                      'If you find a bug check that the edge attributes are right')
    if type(num_interest) is str:
        if num_interest.isdigit():
            net.vs['name'] = [int(i) for i in net.vs['name']]
    if isinstance(net.vs[0]['name'], float):
        net.vs['name'] = [int(i) for i in net.vs['name']]
    return net


def network_from_file(fname, visual=True, discretizer=DefaultSystem, **kwargs) -> igraph.Graph:
    name, postfix = fname.split('.')
    valid_exts = ['h5', 'GraphML', '.p', '.pickle']
    if postfix == 'GraphML':
        net = GraphML_Reader(fname, **kwargs)
    elif postfix == 'h5':
        print('Creating network from drifter data')
        net = file_to_network(fname, discretizer=discretizer, **kwargs)

    elif postfix == 'p':
        net = pickle.load(open(fname, 'rb'))
    else:
        assert False, ValueError(f"{fname} not one of {valid_exts}.")
    ##If rotation is not in the attributes, assume it is identity (no rotation)
    if 'rotation' not in net.attributes():
        net['rotation'] = random_ll_rot(identity=True)
    if 'gpd' not in net.attributes() and visual:
        net['gpd'] = network_to_multipolygon_df(net, discretizer=discretizer)
    return net


class MLP:
    def __init__(self, fname, **kwargs):
        self.net = network_from_file(fname, **kwargs)

    def get_mlpath(self, lon, lat):
        return shortest_path.SingleSP(self.net, lon, lat)
