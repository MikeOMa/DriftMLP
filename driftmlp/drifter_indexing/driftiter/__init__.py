import warnings

import h5py
import numpy as np

from driftmlp.helpers import change_360_to_ew, check_any_grid

# min max lon, min max lat
north_at = [-82, -9, 18, 60]
"""
This package works on taking the H5py file and returns an easily useable 
iterable.
"""


def drifter_dict(drifter_id_group, variables, na_drop=False):
    """
    Function used to turn the h5py group to a dictionary
    Input:
        drifter_id_ group:  from the h5py file
        variables: Variables to extract
        na_drop: If true drop the na_values, if false replace them with np.nan
    Output:
        dict_out: dictionary with keys variables.
    """
    pos_entry = drifter_id_group["position"]
    if na_drop:
        mask_keep = pos_entry[:, 0] < 400
    else:
        mask_na = pos_entry[:, 0] > 400
        # mask_keep is just a mask of trues
        mask_keep = pos_entry[:, 0] > -np.inf
    dict_out = {key: drifter_id_group[key][:][mask_keep] for key in variables}
    if "position" in variables and not na_drop:
        dict_out["position"][mask_na, :] = np.nan
    if "datetime" in variables:
        # Retype date time so we can use it easily
        dict_out["datetime"] = dict_out["datetime"].astype(np.datetime64)
    return dict_out


def drifter_meta(drifter_id_group, variables):
    """
    Simple function to grab metadata from the h5py group.
    Input:
        drifter_id_group: The group corresponding to one id from the h5py file.
    Output:
        dict_out: with variables as the keys.
    """
    dict_out = {key: drifter_id_group.attrs[key][:] for key in variables}
    return dict_out


def drop_drogue(drift_data, variables, drogue):
    # Do nothing is drogue flag is none
    if drogue is not None:
        assert isinstance(drogue, bool), ValueError(
            "drogue arugment must be a boolean or None"
        )
        # drogue key may not be in drift_data, so use the original h5py reference
        drogue_mask = drift_data["drogue"]
        if not drogue:
            drogue_mask = np.invert(drogue_mask)
        # Do not loop through the keys of drift_data as there are metadata entries

        for var in variables:
            drift_data[var] = drift_data[var][drogue_mask]
    return drift_data


def drift_iter(
    drift_file,
    variables=None,
    attrs=False,
    drift_ids=None,
    drop_na=False,
    scale_ew=True,
    drogue=None,
    int_ids=None,
    lon_lat_transform=None,
):
    # Open file
    H5_open = h5py.File(drift_file, "r")
    # Access the interpolated drifter data
    drift_base = H5_open["drifters"]
    all_ids = drift_base["ids"][:]
    if drift_ids is not None:
        drift_ids = list(drift_ids)
        drift_unique = set(drift_ids)
        if len(drift_unique) != len(drift_ids):
            warnings.warn("Note not all drifter_ids are unique")
        all_ids_set = set(all_ids)
        drift_intercection = drift_unique.intersection(all_ids_set)

        assert len(drift_intercection) == len(drift_unique), ValueError(
            "Some ids in drift_ids are not valid, check input"
        )

        drift_ids = list(drift_intercection)
    elif int_ids is not None:
        drift_ids = [all_ids.tolist()[i] for i in int_ids]
        if len(int_ids) == 1:
            drift_ids = list(drift_ids)
    else:
        drift_ids = all_ids
    n = len(drift_ids)
    drifter_id_group = drift_base[str(all_ids[0])]
    posible = drifter_id_group.keys()
    meta_keys = drifter_id_group.attrs.keys()
    if variables is None:
        variable_list = posible
    else:
        variable_list = set(posible) & set(variables)
        variables_notin = set(variables) - set(posible)
        assert len(variables_notin) == 0, ValueError(
            "Some of variables not contained in the group`.\
        One of which being {}.\
        Note, do not include metadata names, use meta=True instead".format(
                variables_notin.pop()
            )
        )
        if drogue is not None and "drogue" not in variable_list:
            variable_list = variable_list + ["drogue"]

    for i in drift_ids:
        drifter_ds = drift_base[f"{i}"]
        drift_data = drifter_dict(drifter_ds, variables=variable_list, na_drop=drop_na)
        if scale_ew:
            drift_data["position"][:, 0] = change_360_to_ew(
                drift_data["position"][:, 0]
            )
        if lon_lat_transform is not None:
            old_dat = drift_data["position"]
            drift_data["position"] = lon_lat_transform(drift_data["position"])
        drop_drogue(drift_data, variable_list, drogue)

        drift_meta = drifter_meta(drifter_ds, variables=meta_keys)
        # add metadata into drift data
        drift_data.update(drift_meta)
        drift_data["id"] = i
        yield drift_data
    H5_open.close()


def get_drifters_in_grid(drift_file, grid):
    if grid is not None:
        ids = get_id_in_range(drift_iter(drift_file), grid)
    else:
        ids = get_drifter_ids(drift_file)
    return ids


def get_id_in_range(drift_iter, grid=[-np.inf, np.inf, -np.inf, np.inf]):
    id_in_range = [k["id"] for k in drift_iter if check_any_grid(k["position"], grid)]
    return id_in_range


class generator:
    def __init__(self, drift_file, grid=None, **kwargs):
        self.drift_file = drift_file
        self.ids = get_drifters_in_grid(self.drift_file, grid, **kwargs)

    def __call__(self, **kwargs):
        return drift_iter(self.drift_file, drift_ids=self.ids, **kwargs)


def get_drifter_ids(drift_file):
    H5_open = h5py.File(drift_file, "r")
    drift_group = H5_open["drifters"]
    drift_ids = drift_group["ids"][:]
    H5_open.close()
    return drift_ids
