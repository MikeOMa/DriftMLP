from typing import List, Tuple

import cartopy
import cartopy.crs as ccrs
import geopandas as gpd
import matplotlib as mpl
import matplotlib.pyplot as plt


def extent_box(oned_coords: List, scale: float = 1., is_lon: bool = True) -> List:
    """

    Parameters
    ----------
    is_lon : object
    """
    min_max = [min(oned_coords), max(oned_coords)]
    rng = min_max[1] - min_max[0]
    add = rng * scale
    bounds = [min_max[0] - add - 1, min_max[1] + add + 1]
    if is_lon:
        if bounds[0] < -180:
            bounds[0] = -179.999
        if bounds[1] > 180:
            bounds[1] = 179.999
    else:
        if bounds[0] < -90:
            bounds[0] = -89.999
        if bounds[1] > 90:
            bounds[1] = 89.999

    return bounds


def gpd_extents(h3_gpd):
    x_bound, y_bound = h3_gpd.unary_union.envelope.exterior.coords.xy

    grid_bounds = extent_box(x_bound, is_lon=True) + \
                  extent_box(y_bound, is_lon=False)
    return grid_bounds


def default_figure(fig=None) -> Tuple[plt.figure, plt.axes]:
    """

    Parameters
    ----------
    fig : object
    """
    if fig is None:
        fig = plt.figure()
    ax = plt.subplot(projection=ccrs.PlateCarree())
    return fig, ax


def ax_none_handler(ax):
    if ax is None:
        fig, ax = default_figure()
    else:
        assert isinstance(ax, cartopy.mpl.geoaxes.GeoAxesSubplot), \
            ValueError("given ax is not GeoAxesSubplot. Give a cartopy projection when creating the axis")
        return ax.get_figure(), ax


def plot_hex(h3_gpd: gpd.GeoDataFrame, h3_inds, ax=None, set_extent=True, *args, **kwargs):
    new_df = h3_gpd.loc[h3_inds].copy()
    # new_df.plot(column='probs', legend=True)
    # crs_proj4 = crs.proj4_init
    if ax is None:
        fig, ax = default_figure()

    crsplotting = ccrs.PlateCarree()
    for n, hexa in new_df.iterrows():
        ax.add_geometries([hexa.geometry], crs=crsplotting, *args, **kwargs)
    if set_extent:
        ax.set_extent(gpd_extents(new_df), crs=crsplotting)
    return ax


def coloredshapes(h3_gpd, h3_inds, color_var, origin=None, ax=None, vmax=None, ax_loc=[0.87, 0.2, 0.02, 0.6]):
    new_df = h3_gpd.loc[h3_inds].copy()
    assert new_df.shape[0] == len(color_var), ValueError(
        "color_var must be the same length as h3_inds")
    new_df['color_var'] = color_var
    crs = ccrs.PlateCarree()
    new_df_proj = new_df  # .to_crs(crs_proj4)
    cmap = plt.cm.RdYlBu_r

    probs_list = new_df_proj.color_var.to_list()
    probs_list.sort()
    if vmax is None:
        try:
            vmax = probs_list[-2] * 1.5
        except ValueError:
            print('setting vmax=1 as fail')
            vmax = 1

    norm = mpl.colors.Normalize(vmin=0., vmax=vmax)
    if ax is None:
        fig, ax = plt.subplots(subplot_kw={'projection': crs})
        x_bound, y_bound = new_df_proj.unary_union.envelope.exterior.coords.xy
        grid_bounds = extent_box(x_bound, lon=True) + \
                      extent_box(y_bound, lon=False)
        ax.set_extent(grid_bounds, crs=crs)
        ax.gridlines(draw_labels=True)
    else:
        fig = ax.get_figure()

    for n, hexa in new_df_proj.iterrows():
        ax.add_geometries([hexa.geometry], crs=crs,
                          facecolor=cmap(norm(hexa.color_var)))

        if n == origin:
            ax.add_geometries([hexa.geometry], crs=crs, edgecolor='black')

    ###
    cax = fig.add_axes(ax_loc)
    # , spacing='proportional')
    cb = mpl.colorbar.ColorbarBase(cax, cmap=cmap, norm=norm, extend='max')
    cb.set_label('transition probability')

    ax.coastlines()
    return fig, ax


def plot_line(h3_gpd, h3_inds, centroid_col=None, ax=None, bounds=None, fig_init=True, **kwargs):
    new_df = h3_gpd.loc[h3_inds].copy()
    # new_df.plot(column='probs', legend=True)
    crs = ccrs.PlateCarree()
    fig = ax.get_figure()
    crs_proj4 = crs.proj4_init
    new_df_proj = new_df  # .to_crs(crs_p
    # new_df_proj = new_df_proj.set_geometry('rotated_centroid')
    if ax is None:
        fig, ax = plt.subplots(subplot_kw={'projection': crs})

        fig_init = True
    if fig_init:
        if bounds is None:
            x_bound, y_bound = new_df_proj.unary_union.envelope.exterior.coords.xy
            grid_bounds = extent_box(x_bound, lon=True) + \
                          extent_box(y_bound, lon=False)
            try:
                ax.set_extent(grid_bounds, crs=crs)
            except:
                print(h3_inds, grid_bounds)
        else:
            ax.set_extent(bounds)

        ax.gridlines()
        ax.coastlines()
    if centroid_col is not None:
        dat = new_df_proj[centroid_col]
    else:
        dat = new_df_proj.centroid
    plot_gpd_points(dat, ax, crs=crs, **kwargs)

    return fig, ax


def plot_gpd_points(dat, ax, crs, fl=False, **kwargs):
    xy = dat.apply(lambda x: x.xy)
    x = xy.apply(lambda x: float(x[0][0])).to_list()
    y = xy.apply(lambda x: float(x[1][0])).to_list()
    ax.plot(x, y, transform=crs, **kwargs)
    if fl:
        ax.plot(x[0], y[0], 'o', transform=crs)
        ax.plot(x[-1], y[-1], 'x', transform=crs)
