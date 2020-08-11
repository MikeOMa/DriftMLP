import os

import h5py
import numpy as np
import pandas as pd


def make_all_strings_len2(str_array):
    out = np.array(['0' + string if len(string) ==
                                    1 else string for string in str_array], dtype='str')
    return out


def makeHDF5(hf, folder_raw='raw_data', folder_meta='metadata'):
    file_ends = [i.split('data_')[1] for i in os.listdir(folder_raw)]
    # Grouped_data = [i[1].reset_index() for i in drift_grouped]

    drifters_group = hf.require_group("drifters")
    ID_list = []
    for i in range(len(file_ends)):
        drift_csv, meta_csv = read_drift_files(
            file_ends[i], folder_raw, folder_meta)
        drift_grouped = drift_csv.groupby('id')
        print(f"File Number {i}")
        ID_list = ID_list + [drift_id for drift_id, _ in drift_grouped]

        for drift_id, dat in drift_grouped:
            make_dataset(hf, drift_id, dat, meta_row=meta_csv.loc[drift_id,])

    drifters_base = hf['drifters']
    drifters_base.create_dataset('ids', data=np.array(ID_list))
    hf.close()


def read_drift_files(post_fix, folder_raw, folder_meta):
    drift_csv = pd.read_csv(
        f"{folder_raw}/buoydata_{post_fix}", header=None, delim_whitespace=True)
    metadata_csv = pd.read_csv(
        f"{folder_meta}/dirfl_{post_fix}", header=None, delim_whitespace=True)
    drift_csv.columns = ["id", "month", "day", 'year', 'lat', 'lon',
                         'sst', 've', 'vn', 'spd', 'Var.Lat', 'Var.Lon', 'Var.Temp']
    drift_csv_slice_float = drift_csv[[
        'lat', 'lon', 'sst', 've', 'vn', 'spd', "Var.Lat", "Var.Lon", "Var.Temp"]]
    drift_csv_slice_float = drift_csv_slice_float.apply(
        lambda x: pd.to_numeric(x, downcast='float'))
    drift_csv['day_floor'] = np.floor(drift_csv["day"])
    drift_csv['day_floor'] = drift_csv['day_floor'].astype(int)
    drift_csv['hour'] = (np.mod(drift_csv["day"], 1) * 24).astype(int)
    drift_csv['date_string'] = drift_csv.year.astype("str") + '-' \
                               + make_all_strings_len2(drift_csv.month.astype("str")) + '-' \
                               + make_all_strings_len2(drift_csv.day_floor.astype("str")) + "T" \
                               + make_all_strings_len2(drift_csv.hour.astype("str")) + ":00"

    metadata_csv.columns = ['id', 'WMO_number', 'program_number', 'type', 'deploy_date', 'deploy_time', 'deploy_lat',
                            'deploy_lon', 'end_year', 'end_time', 'end_lat', 'end_lon', 'drogue_off_yr',
                            'drouge_off_time', 'death']
    metadata_csv["deploy_date_string"] = metadata_csv["deploy_date"].apply(
        lambda x: x.replace("/", "-")) + "T" + metadata_csv["deploy_time"]
    metadata_csv["end_date_string"] = metadata_csv["end_year"].apply(
        lambda x: x.replace("/", "-")) + "T" + metadata_csv["end_time"]
    metadata_csv["drogue_date_string"] = metadata_csv["drogue_off_yr"].apply(
        lambda x: x.replace("/", "-")) + "T" + metadata_csv["drouge_off_time"]
    metadata_csv = metadata_csv.set_index("id")
    return drift_csv, metadata_csv


def drougemask(date_array, date_off):
    if date_off == "0000-00-00T00:00":
        return np.full(date_array.shape, True).astype(np.bool)
    date_np = date_array.astype(np.datetime64)
    date_off_dt = np.array(date_off).astype(np.datetime64)
    mask = date_np < date_off_dt
    drogue_pres = mask.astype(np.bool)
    return drogue_pres


def make_dataset(hf, ID, dat, meta_row):
    ID_group_string = f"drifters/{ID}"
    hf.require_group(ID_group_string)
    ID_group = hf[ID_group_string]
    numpy_lat_lon = dat[["lon", "lat"]].to_numpy()

    ID_group.create_dataset("position", data=numpy_lat_lon)
    rest_columns = ['sst', 'Var.Temp']
    rest_col_df_names = ["sst", "sst_variance"]
    numpy_vel = dat[["ve", "vn"]].to_numpy()
    ID_group.create_dataset("velocity", data=numpy_vel)
    dt = h5py.special_dtype(vlen=str)
    date_string_array = dat["date_string"].to_numpy().astype(np.string_)
    ID_group.create_dataset("datetime", data=date_string_array)
    numpy_variance = dat[['Var.Lon', 'Var.Lat']].to_numpy()
    ID_group.create_dataset("position_variance", data=numpy_variance)
    for df_col, df_name in zip(rest_columns, rest_col_df_names):
        ID_group.create_dataset(df_name, data=dat[df_col])
    ID_group.attrs.create(
        "deploydate", meta_row["deploy_date_string"], dtype=dt)
    ID_group.attrs.create("enddate", meta_row["end_date_string"], dtype=dt)
    ID_group.attrs.create(
        "drogueoffdate", meta_row["drogue_date_string"], dtype=dt)
    drouge_mask = drougemask(dat['date_string'].astype(
        np.datetime64).to_numpy(), meta_row["drogue_date_string"])
    ID_group.create_dataset("drogue", data=drouge_mask)
