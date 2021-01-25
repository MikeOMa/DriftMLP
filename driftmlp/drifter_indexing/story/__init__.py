from time import time
from typing import List

import numpy as np

from driftmlp.drifter_indexing.discrete_system import DefaultSystem


def grid_story(traj_pos: np.ndarray, discretizer=DefaultSystem) -> List[int]:
    """
    A function to take a numpy array of positions in order longitude, latitude.
    Then returns a list of the h3 index related to that position.
    If the point is na fills in -1

    Parameters
    ----------
    traj_pos : np.array
        (,2) Numpy array containing  longitude, latitude pairs.
    """
    story: List[int] = []
    n_obs = len(traj_pos)
    traj_points = [traj_pos[i, :] for i in range(0, n_obs)]
    for point in traj_points:
        lng, lat = point
        # is lng is nan add index else add -1
        if not np.isnan(lng):
            in_grid_id = discretizer(lon=lng, lat=lat)
            assert in_grid_id != 0, ValueError(
                f'an invalid longitude or latitude has been given to discretizer.geo_to_ind. longitude: {lng}, latitude: {lat}.')
            story.append(in_grid_id)
        else:
            story.append(-1)
    return story


def get_story(drift_iter, discretizer=DefaultSystem, silent=True) -> List[List[int]]:
    ###
    t_start = time()
    list_of_storys = []
    c = 0

    for data_dict in drift_iter:
        story = grid_story(data_dict['position'], discretizer=discretizer)
        list_of_storys.append(story)
        c += 1
    if not silent:
        print("Number of Drifters used: {}".format(c))
        print("Time Taken to match drifters to grids: %f sec" %
              (time()-t_start))
    return list_of_storys
