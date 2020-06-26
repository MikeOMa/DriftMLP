import igraph

from DriftMLP import form_network
from DriftMLP import shortest_path
from DriftMLP.drifter_indexing import driftiter
from DriftMLP.drifter_indexing import story


def file_to_network(driftfile, drift_kwargs=None, day_cut_off=5, silent=False) -> igraph.Graph:
    if drift_kwargs is None:
        drift_kwargs = {'variables': ['position', 'drogue', 'datetime'],
                        'drop_na': False,
                        'drogue': True}
        print('Making transition matrix with drogued drifters,'
              'see file_to_network function'
              'to change this')
    drift_gen = driftiter.generator(driftfile)
    h3_stories = story.get_story(drift_gen(**drift_kwargs))
    net = form_network.make_transition(h3_stories)
    return net


def network_from_file(fname, **kwargs) -> igraph.Graph:
    name, postfix = fname.split('.')
    if postfix == 'gml':
        net = igraph.igraph_read_graph_graphml(fname)
    elif postfix == 'h5':
        print('Creating network from drifter data')
        net = file_to_network(fname, **kwargs)
    return net


class MLP:
    def __init__(self, fname):
        self.net = network_from_file(fname)

    def get_mlpath(self, lon, lat):
        return shortest_path.single_SP(self.net, lon, lat)
