import numpy as np


def change_360_to_ew(lon_arr):
    mask_w = lon_arr > 180
    lon_arr[mask_w] = lon_arr[mask_w]-360
    return(lon_arr)


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

    return(any(mask4 & new_mask))
