from typing import Dict

import igraph
import numpy as np

## Dict with points on the panama canal and strait of gibraltar
## Can be used to remove these undesired points
RM_DICT = {'panama':
               [[9.071323224898283, -79.69761240838052],
                [8.661515581046203, -80.7277450395157]],
           'straitofgibraltar':
               [[35.9945, -5.5999],
                [35.8804, -5.6149]]}

## Add points to link the strait of gibraltar after removing.
## The first point is on the west, second point on the east.
ADD_DICT = {'straitofgibraltar':
                [[35.954, -7.2],  ## West point
                 [36.0026, -4.0]]  ## East point
            }
TIME_GAP = {'straitofigibraltar':
                [1, 100]}  ## 1 for west to east, 100 for east to west

from DriftMLP.rotations import random_ll_rot


def change_360_to_ew(lon_arr):
    mask_w = lon_arr > 180
    lon_arr[mask_w] = lon_arr[mask_w] - 360
    return (lon_arr)


def check_grid(array, grid):
    """
    grid[0:2] should be lower, upper of array[:,0] grid[2:4] should be  lower,
    upper of array[:,1]
    returns a simple True or False if the array has every crossed the grid
    """
    mask1 = array[:, 0] > grid[0]
    if not any(mask1):
        return mask1
    mask2 = array[:, 0] < grid[1]
    new_mask = mask1 & mask2

    if not any(new_mask):
        return new_mask
    mask3 = array[:, 1] > grid[2]
    new_mask = new_mask & mask3
    if not any(new_mask):
        return new_mask
    mask4 = array[:, 1] < grid[3]

    return(mask4 & new_mask)


def check_any_grid(array, grid):
    """
    grid[0:2] should be lower, upper of array[:,0] grid[2:4] should be  lower,
    upper of array[:,1]
    returns a simple True or False if the array has every crossed the grid
    """
    mask1 = array[:, 0] > grid[0]
    if not any(mask1):
        return False
    mask2 = array[:, 0] < grid[1]
    new_mask = mask1 & mask2

    if not any(new_mask):
        return False
    mask3 = array[:, 1] > grid[2]
    new_mask = new_mask & mask3
    if not any(new_mask):
        return False
    mask4 = array[:, 1] < grid[3]

    return (any(mask4 & new_mask))


def return_h3_inds(loc_list, rot=None):
    if rot is None:
        rot = random_ll_rot(identity=True)

    locs_rotated = [rot(lon=loc[0], lat=loc[1]) for loc in loc_list]
    return [h3.geo_to_h3(lng=loc[0], lat=loc[1], resolution=3)
            for loc in locs_rotated]


def remove_undesired(network: igraph.Graph, dict_rm: Dict = RM_DICT, rot=None, silent=True):
    for key in dict_rm.keys():
        if not silent:
            print(f'Removing {key} from the graph.')

        drop_inds = return_h3_inds(dict_rm[key], rot=rot)
        drop_vid = [v.index for v in G.vs if v['name'] in drop_inds]
        if len(drop_inds > 0):
            network.delete_verices(drop_vid)
        else:
            if not silent:
                print(f'for {key} , {dict_rm[key]} not in graph so it is not dropped')


def get_prob_stay(network, node_id: int):
    stay_edges = network.select(_source=node_id, _target=node_id)
    if len(stay_edges) == 0:
        ##if the edge doesn't exist this probability is zero
        prob_stay = 0
    else:
        prob_stay = stay_edges[0]['prob']
    return prob_stay


def traveltime_to_probleave(travel_time, prob_stay, day_cut_off):
    return (travel_time - day_cut_off) * prob_stay


def add_link(network: igraph.Graph, dict_add: Dict = ADD_DICT, add_gap=TIME_GAP, rot=None, silent=True):
    for key in dict_add.keys():
        assert len(dict_add[key]) == 2, ValueError(f'Components of dict_add must be lenth 2'
                                                   f'One point for east, one point for west'
                                                   f'Error occoured for key {key}')
        assert all([len(x) == 2 for x in dict_add[key]]), \
            ValueError(f'Each point in the dict_add arguement must be length 2',
                       f'Error occured on {key}.')
        if not silent:
            print(f'Adding a link for {key} from the graph.')
        inds = return_h3_inds(dict_add[key], rot=rot)

        ##check that the connection we are adding is in the graph.
        in_graph_bools = [ind in network.es['name'] for ind in inds]
        if all(in_graph_bools):
            west_node = network.vs.select(name=inds[0])[0].index
            east_node = network.vs.select(name=inds[1])[0].index

            stay_west = get_prob_stay(network, west_node)
            stay_east = get_prob_stay(network, east_node)

            going_east_prob = traveltime_to_probleave(add_gap[0], stay_west, network['day_cut_off'])
            going_west_prob = traveltime_to_probleave(add_gap[1], stay_east, network['day_cut_off'])

            # Lets add the desired connection.
            # N=-1 to help easily find these edges in future to see they are artificial.
            network.add_edge(west_node, east_node, prob=going_east_prob, neglogprob=-np.log(going_east_prob), N=-1)
            network.add_edge(east_node, west_node, prob=going_west_prob, neglogprob=-np.log(going_west_prob), N=-1)
