def change_360_to_ew(lon_arr):
    mask_w = lon_arr > 180
    lon_arr[mask_w] = lon_arr[mask_w]-360
    return(lon_arr)
