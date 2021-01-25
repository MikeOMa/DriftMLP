import warnings
from typing import List

import igraph
import matplotlib.pyplot as plt
import numpy as np

from DriftMLP.drifter_indexing.discrete_system import DefaultSystem
from DriftMLP.helpers import get_prob_stay
from DriftMLP.plotting import h3_plotly, h3_cartopy, make_gpd


def plot_path(h3_seq, **kwargs):
    m = h3_plotly.visualize_hexagons(h3_seq, **kwargs)
    return m


def sp_igraph(network: igraph.Graph, name_from: int = None, name_to: int = None, weight='neglogprob',
              node_fromto=None) -> List[int]:
    """

    Parameters
    ----------
    network
    name_from
    name_to
    weight

    Returns
    -------
    sp : List[int]

    """
    if node_fromto is None:
        node_from = network.vs.select(name=name_from)[0]
        node_to = network.vs.select(name=name_to)[0]
    else:
        node_from, node_to = node_fromto

    all_sp = network.get_shortest_paths(node_from, node_to, weights=weight)
    ##convert to integer

    return all_sp


def travel_time(network, source_id, target_id):
    # CHANGE: Potentially to network.es.find(_source=, _target=)

    # Must exist as it is on the shortest path

    eid = network.get_eid(source_id, target_id)
    prob_leave = network.es[eid]['prob']
    prob_stay = get_prob_stay(network, source_id)
    # Negative binomial with 0 being a failure has mean
    nb_mean = prob_stay / prob_leave + 1
    return nb_mean


def AllPairwisePaths(network, source_list):
    return [get_all_paths(network, src, source_list) for src in source_list]


def get_all_paths(network, src, dest_list, weight='neglogprob'):
    try:
        from_node = network.vs(name=src)[0].index
    except IndexError:
        return [network_path(network, -1, -1, path=[]) for _ in range(len(dest_list))]
    to_vertex_seqs = [network.vs(name=to_name) for to_name in dest_list]
    mask_node_in_graph = [len(vert_seq) == 1 for vert_seq in to_vertex_seqs]
    to_nodes = [vert_seq[0].index
                for _bool, vert_seq in zip(mask_node_in_graph, to_vertex_seqs)
                if _bool]
    sps = network.get_shortest_paths(from_node, to_nodes, weights=weight)
    results_list = []
    dest_node_list = []
    count = 0
    for node_in_graph in mask_node_in_graph:
        if node_in_graph:
            results_list.append(sps[count])
            dest_node_list.append(to_nodes[count])
            count += 1
        else:
            results_list.append([])
            ### if the node is not in the list
            dest_node_list.append(-1)
    ret = [network_path(network, src, dest, path=path) for dest, path in zip(dest_list, results_list)]
    return ret


def check_path(path: List, src: int, dest: int):
    """

    Parameters
    ----------
    path : object
    """
    if path == []:
        path_message = 'empty'
        ret = []
    elif np.isnan(path[0]):
        path_message = 'dest not in graph'
        ret = []
    elif dest == src:
        path_message = 'src=dest'
        ret = [src]
    elif (path[0] != src):
        path_message = 'path[0]!=src'
        ret = []
    elif (path[-1] != dest):
        path_message = 'path[-1]!=dest'
        ret = []
    else:
        path_message = None
        ret = path
    return path_message, ret


class network_path:
    def __init__(self, network, src, dest, path=None, **kwargs):
        self.src = src
        self.dest = dest
        try:
            self.src_net = network.vs(name=src)[0].index
        except IndexError:
            self.src_net = -1

        try:
            self.dest_net = network.vs(name=dest)[0].index
        except IndexError:
            self.dest_net = -1

        self.day_cut_off = network['day_cut_off']
        if self.dest_net == -1 or self.src_net == -1:
            self.all_sps = [np.nan]
            self.nid = [np.nan]
        elif path is None:
            self.all_sps = sp_igraph(network, node_fromto=[self.src_net, self.dest_net], **kwargs)
            if len(self.all_sps) > 1:
                warnings.warn(f'more than one SP for source node {src}, {dest}')
            self.nid = self.all_sps[-1]
        else:
            # Include all_sps to match the above.
            # Also all_sps can be used to see the original pathway if check_path edits it.
            self.all_sps = [path]
            self.nid = path
        self.error_msg, self.nid = check_path(self.nid, self.src_net, self.dest_net)
        self.h3id = network.vs[self.nid]['name']
        self.travel_time_list = self.expected_days(network)
        self.travel_time = sum(self.travel_time_list)
        self.titlestring = f'Path from {src} to {dest}'

    def update_nid(self, network):
        """
        Changes self.nid to match the new network. Useful if a different network with the same nodes is being used.
        Parameters
        ----------
        network: nx.Graph
        """
        self.backup_ind = self.nid.copy()
        self.nid = [network.vs.select(name=ind)[0].index for ind in self.h3id]

    def expected_days(self, network: igraph.Graph) -> List[float]:
        """

        Parameters
        ----------
        path : List[int]
            A path in node index's (NOT H3 indices)
        network: igraph.Graph
            network each node being a h3 index
        day_cut_off

        Returns
        -------

        """
        path = self.nid
        if len(path) == 0:
            traveltime_list = [-1]
        elif not isinstance(path[0], int):
            traveltime_list = [-1]
        else:
            traveltime_list = [travel_time(network, path[i], path[i + 1]) * self.day_cut_off
                               for i in range(len(path) - 1)]
        return traveltime_list


class SingleSP:
    def __init__(self, network, orig, dest, weight='neglogprob', discretizer=DefaultSystem):
        self.orig = orig
        self.dest = dest
        self.h3_inds = discretizer.return_inds([orig, dest])
        self.FromNetwork(network, weight)
        self.discretizer = discretizer

    def FromNetwork(self, network, weight):
        self.sp = network_path(network, self.h3_inds[0], self.h3_inds[1], weight=weight)
        self.sp_rev = network_path(network, self.h3_inds[1], self.h3_inds[0], weight=weight)

    def plot_folium(self, rev=True, m=None, **kwargs):
        m = plot_path(self.sp.h3id, color='blue', folium_map=m, **kwargs)
        if rev:
            m = plot_path(self.sp_rev.h3id, color='red', folium_map=m)
        return m

    def plot_cartopy(self, rev=True, ax=None, gpd_df=None, color='blue', type_plot='hex', **kwargs):
        """
        Note this function cannot plot rotated paths. Unless type='line'
        Parameters
        ----------
        rev : bool
            To plot the reverse path too or not
        ax : plt.Axes
            Apply an axis if you like
        kwargs
            kwarg dict for  h3_cartopy.plot_hex

        Returns
        -------
            figure, ax : plt.Figure, plt.Axes
                figure and axes with the lines on it
        """
        if gpd_df is None:
            all_ids = self.sp.h3id + self.sp_rev.h3id
            gpd_df = make_gpd.list_to_multipolygon_df(all_ids, self.discretizer)
        if type_plot == 'hex':
            ax = h3_cartopy.plot_hex(gpd_df, self.sp.h3id, ax=ax, color=color, **kwargs)
            if rev:
                h3_cartopy.plot_hex(gpd_df, self.sp_rev.h3id, ax=ax, color='red', **kwargs)
        else:
            h3_cartopy.plot_line(gpd_df, self.sp.h3id, 'centroid_col', ax=ax, color=color, **kwargs)
            if rev:
                h3_cartopy.plot_hex(gpd_df, self.sp_rev.h3id, centroid_col='centroid_col', ax=ax, color='red', **kwargs)
        ax.coastlines()
        ax.set_adjustable('datalim')
        fig = ax.get_figure()
        return fig, ax

    def __repr__(self):
        str1 = f'From: {self.orig}, To: {self.dest}\n'
        str2 = f'Travel time for the forward journey(blue)\n{self.sp.travel_time}\n'
        str3 = f'Travel time for the return journey(red)\n{self.sp_rev.travel_time}\n'
        return str1 + str2 + str3
