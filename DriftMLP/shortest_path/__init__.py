import warnings
from typing import List

import h3.api.basic_int as h3
import igraph
import numpy as np

from DriftMLP.plotting import h3_plotly
from DriftMLP.rotations import random_ll_rot


def return_h3_inds(loc_list, rot=None):
    if rot is None:
        rot = random_ll_rot(identity=True)

    locs_rotated = [rot(lon=loc[0], lat=loc[1]) for loc in loc_list]
    return [h3.geo_to_h3(lng=loc[0], lat=loc[1], resolution=3)
            for loc in locs_rotated]


def plot_path(h3_seq, **kwargs):
    m = h3_plotly.visualize_hexagons(h3_seq, **kwargs)
    return m


def sp_igraph(network: igraph.Graph, name_from: int, name_to: int, weight='neglogprob') -> List[int]:
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
    node_from = network.vs.select(name=name_from)[0]
    node_to = network.vs.select(name=name_to)[0]

    all_sp = network.get_shortest_paths(node_from, node_to, weights=weight)
    ##convert to integer

    return all_sp


class network_path:
    def __init__(self, network, src, dest, day_cut_off=5, **kwargs):
        self.src = src
        self.dest = dest
        self.day_cut_off = day_cut_off

        self.all_sps = sp_igraph(network, src, dest, **kwargs)
        if len(self.all_sps) > 1:
            warnings.warn(f'more than one SP for source node {src}, {dest}')
        self.nid = self.all_sps[0]
        self.h3id = network.vs[self.nid]['name']
        self.travel_time_list = self.expected_days(network)
        self.travel_time = sum(self.travel_time_list)

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

        expected_days = []
        if len(path) == 0:
            return [np.nan]
        elif not isinstance(path[0], int):
            return [-1]
        for i in range(len(path) - 1):
            eid = network.get_eid(path[i], path[i + 1])
            prob = network.es[eid]['prob']
            try:
                eid_stay = network.get_eid(path[i], path[i])
                prob_stay = network.es[eid_stay]['prob']
                ##if no edge exists we set the probability to 0 as the drifter will always leave.
            except KeyError:
                prob_stay = 0
            # Negative binomial with 1 failure has mean
            nb_mean = prob_stay / prob + 1
            expected_days.append(self.day_cut_off * nb_mean)
        return expected_days


class single_SP:
    def __init__(self, network, orig, dest, weight='neglogprob'):
        self.orig = orig
        self.dest = dest
        self.h3_inds = return_h3_inds([orig, dest])
        self.sp = network_path(network, self.h3_inds[0], self.h3_inds[1])
        self.sp_rev = network_path(network, self.h3_inds[1], self.h3_inds[0])

    def plot_folium(self, rev=True, m=None, **kwargs):
        if m is None:
            m = plot_path(self.sp.h3id, color='blue', **kwargs)
        if rev:
            m = plot_path(self.sp_rev.h3id, color='red', folium_map=m)
        return m

    def __repr__(self):
        str1 = f'From: {self.orig}, To: {self.dest}\n'
        str2 = f'Travel time for the forward journey(blue)\n{self.sp.travel_time}\n'
        str3 = f'Travel time for the return joorney(red)\n{self.sp_rev.travel_time}\n'
        return str1 + str2 + str3
