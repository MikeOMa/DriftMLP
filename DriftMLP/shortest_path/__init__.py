from h3 import h3
from DriftMLP.rotations import random_ll_rot
from DriftMLP.plotting import h3_plotly
import networkx as nx
import numpy as np

def return_h3_inds(loc_list, rot=None):
    if rot is None:
        rot = random_ll_rot(identity=True)

    locs_rotated = [rot(lon=loc[0], lat=loc[1]) for loc in loc_list]
    return [h3.geo_to_h3(lng=loc[0], lat=loc[1], res=3)
            for loc in locs_rotated]


def plot_path(h3_seq, **kwargs):
    m = h3_plotly.visualize_hexagons(h3_seq, **kwargs)
    return m


class single_SP:
    def __init__(self, network, orig, dest, weight='neglogprob'):
        self.orig = orig
        self.dest = dest
        self.h3_inds = return_h3_inds([orig, dest])
        self.sp = nx.shortest_path(network, self.h3_inds[0],
                                   self.h3_inds[1], weight=weight)
        self.sp_rev = nx.shortest_path(network,
                                       self.h3_inds[1], self.h3_inds[0],
                                       weight=weight)

    def plot(self, rev=True, m=None, **kwargs):
        m = plot_path(self.sp, color='blue', **kwargs)
        if rev:
            m = plot_path(self.sp_rev, color='red', folium_map=m)
        return m

    def expected_days(self, network, day_cut_off=5, rev=True):
        if rev:
            path = self.sp_rev
        else:
            path = self.sp
        Expected_days = []
        if len(path) == 0:
            return [np.nan]
        elif not isinstance(path[0], str):
            return [-1]
        for i in range(len(path)-1):
            prob = network[path[i]][path[i+1]]['prob']
            try:
                prob_stay = network[path[i]][path[i]]['prob']
            except KeyError:
                prob_stay = 0
            # Negative binomial with 1 failure has mean
            nb_mean = prob_stay/prob+1
            Expected_days.append(day_cut_off*nb_mean)
        return(Expected_days)
