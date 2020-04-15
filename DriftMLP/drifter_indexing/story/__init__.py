from time import time
from h3 import h3


def grid_story(traj_pos):
    """
        Input: traj_pos, an array of shape (:,2) which has longitude in the first column, latitude in the second
                day_cut_off: when to slice the trajectory

        Output: A list of each grid indicy returning -1 if lng is nan
    """
    story = []
    n_obs = len(traj_pos)
    traj_points = [traj_pos[i, :] for i in range(0, n_obs)]
    for point in traj_points:
        lng, lat = point
        # is lng is nan add index else add -1
        if isinstance(lng, float):
            in_grid_id = h3.geo_to_h3(lng=lng, lat=lat, res=3)
            story.append(in_grid_id)
        else:
            story.append('0')
    return story


def get_story(drift_iter, silent=True):
    ###
    t_start = time()
    list_of_storys = []
    c = 0

    for data_dict in drift_iter:
        story = grid_story(data_dict['position'])
        list_of_storys.append(story)
        c += 1
    if not silent:
        print("Number of Drifters used: {}".format(c))
        print("Time Taken to match drifters to grids: %f sec" %
              (time()-t_start))
    return list_of_storys
