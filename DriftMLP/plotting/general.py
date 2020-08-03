import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import pandas as pd


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
