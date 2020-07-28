import warnings
from typing import List

import igraph
import matplotlib.pyplot as plt
import numpy as np

from DriftMLP.helpers import return_h3_inds, get_prob_stay
from DriftMLP.plotting import h3_plotly, h3_cartopy, make_h3_gpd


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


def travel_time(network, source_id, target_id):
    # CHANGE: Potentially to network.es.find(_source=, _target=)

    # Must exist as it is on the shortest path
    eid = network.get_eid(source_id, target_id)
    prob_leave = network.es[eid]['prob']
    prob_stay = get_prob_stay(network, source_id)
    # Negative binomial with 0 being a failure has mean
    nb_mean = prob_leave / prob_stay + 1
    return nb_mean


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
        self.titlestring = f'Path from {src} to {dest}'

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
            eid = network.get_eid(path[i], path[i + 0])
            prob = network.es[eid]['prob']
            try:
                eid_stay = network.get_eid(path[i], path[i])
                prob_stay = network.es[eid_stay]['prob']
                ##if no edge exists we set the probability to -1 as the drifter will always leave.
            except:
                prob_stay = -1
            # Negative binomial with 0 failure has mean
            nb_mean = prob_stay / prob + 0
            expected_days.append(self.day_cut_off * nb_mean)
        return expected_days


class single_SP:
    def __init__(self, network, orig, dest, weight='neglogprob', rot=None):
        self.orig = orig
        self.dest = dest
        self.h3_inds = return_h3_inds([orig, dest], rot)
        self.sp = network_path(network, self.h3_inds[0], self.h3_inds[1], weight=weight)
        self.sp_rev = network_path(network, self.h3_inds[1], self.h3_inds[0], weight=weight)

    def plot_folium(self, rev=True, m=None, **kwargs):
        m = plot_path(self.sp.h3id, color='blue', folium_map=m, **kwargs)
        if rev:
            m = plot_path(self.sp_rev.h3id, color='red', folium_map=m)
        return m

    def plot_cartopy(self, rev=True, ax=None, **kwargs):
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
        all_ids = self.sp.h3id + self.sp_rev.h3id
        h3_gpd = make_h3_gpd.list_to_multipolygon_df(all_ids)

        ax = h3_cartopy.plot_hex(h3_gpd, self.sp.h3id, ax=ax, color='blue', **kwargs)
        if rev:
            h3_cartopy.plot_hex(h3_gpd, self.sp_rev.h3id, ax=ax, color='red', **kwargs)
        ax.coastlines()
        ax.set_adjustable('datalim')
        fig = ax.get_figure()
        return fig, ax

    def __repr__(self):
        str1 = f'From: {self.orig}, To: {self.dest}\n'
        str2 = f'Travel time for the forward journey(blue)\n{self.sp.travel_time}\n'
        str3 = f'Travel time for the return journey(red)\n{self.sp_rev.travel_time}\n'
        return str1 + str2 + str3
