# DriftMLP 
This package contains tools for implementing the methodology associated with the paper [Estimating the travel time and the most likely path from Lagrangian drifters](https://arxiv.org/abs/2002.07774)
Code to reproduce figures from paper, hence a sample use of this package can be found at [Github link to paper figure reproduction code.](https://github.com/MikeOMa/MLTravelTimesFigures)

## Setup
### Installation

To install the package first install numpy and proj (`conda install proj numpy` if using conda)
Then pip this github page:

`pip install git+https://github.com/MikeOMa/DriftMLP`

### Data preprocessing
This package strongly depends on a hdf5 file which contains all the relevant drifter data.
Therefore, prior to running any analysis the following steps must be carried out:
 
1. Download all files from https://www.aoml.noaa.gov/phod/gdp/interpolated/data/all.php. Save the larger files in a folder called 'raw_data'. Save all the metadata files in a folded called 'metadata'

2. the following 5 lines of code must be run, in the directory containing the two above folders.

```
import h5py 
import DriftMLP.drifter_indexing.makehdf5
ff  = h5py.File('drift.h5', 'w')
makehdf5.makeHDF5(ff) 
ff.close() 
```


### General usage
The package has 2 main usage components

- `DriftMLP.file_to_network` will form the network from the hdf5 file above which is the most computationally intensive part
- `DriftMLP.shortest_path` contains functions which require a network to run.
    - `SingleSP` is sufficient for most usage. It will take the network and a pair of locations and results in a class containing both the path there and back. The travel time of this path may be accessed via the .sp.travel_time attribute. Has methods `.plot_cartopy` and `.plot_folium` for convince. 
    - `network_path` is a more customizable class which can be used for manual adaptations. It takes in two h3 indices and stores the path going from the first to the second. Stores travel path in network indices (`.nid`), spatial discretization indices (`.h3id`) and travel time in days (`.travel_time`).
- `DriftMLP.rotations` contains functionality to generate random rotations. See paper for further details. This has two options one method by ARVO and one by shoemake. The Shoemake quaternion approach is advised.
- `DriftMLP.plotting` Various functions for h3 index sequence plotting. Two backends are there on using folium, one using cartopy. Folium is easier to view and scroll around with. Cartopy/Matplotlib are far more customizable and can produce publication ready graphics.


#TODO

- Document all functions alongside typehints.
- Refactor the code a bit such that the h3 spatial index is less core to the code. Make a class named `SpatialIndex` that can be adapted to different index systems easily.
- Publish to pip/ conda-forge.
- Fix binder link below with example (currently does not work)

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/MikeOMa/DriftMLP/master?filepath=example%2Finteractive.ipynb)
