import numpy as np

from driftmlp import file_to_network


def drift_gen():
    for i in range(20):
        lon = np.linspace(-40, 60, 300)
        lat = np.linspace(-60, 60, 300)
        pos = np.vstack([lon, lat]).T

        yield {'position': pos}


def test_network_creation():
    net = file_to_network(data_iterable=drift_gen())
    return net
