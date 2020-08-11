import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER


def plot_stations(stations_data, crs=None, names=-1,
                  labelsize='x-large', ax=None,
                  **kwargs):
    if crs is None:
        crs = ccrs.PlateCarree()

    if ax is None:
        ax = plt.axes(projection=crs)

    if isinstance(stations_data, pd.DataFrame):
        plot_data = stations_data.to_numpy()
    else:
        plot_data = stations_data
    ax.plot(plot_data[:, 0], plot_data[:, 1], 'o',
            transform=ccrs.Geodetic(),
            **kwargs)
    if names is not -1:

        if hasattr(names, '__iter__'):
            str_names = [str(i) for i in names]
            assert len(str_names) == plot_data.shape[0], ValueError(
                'Expected names to be the same length as data.')
        else:
            str_names = [str(i) for i in range(plot_data.shape[0])]

        for i in range(plot_data.shape[0]):
            ax.text(plot_data[i, 0], plot_data[i, 1],
                    str_names[i],
                    transform=ccrs.Geodetic(), fontsize=labelsize,
                    fontweight='bold', zorder=11).set_clip_on(True)
    ax.coastlines()
    return ax


def add_standard_gridlines(ax, x_locs=[-180, -45, 0, 45, 180],
                           y_locs=list(range(-80, 80, 10))):
    gl = ax.gridlines(draw_labels=True)
    gl.top_labels = False
    gl.left_labels = False
    gl.xlines = False
    gl.xlocator = mticker.FixedLocator(x_locs)
    gl.ylocator = mticker.FixedLocator(y_locs)
    gl.xformatter = LONGITUDE_FORMATTER
    gl.yformatter = LATITUDE_FORMATTER
    return gl
