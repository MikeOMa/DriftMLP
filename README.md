# DriftMLP 
This package contains tools for implementing the methodology associated with the paper [Estimating the travel time and the most likely path from Lagrangian drifters](https://arxiv.org/abs/2002.07774)
Code to reproduce figures from paper, hence a sample use of this package can be found at [Github link to paper figure reproduction code.](https://github.com/MikeOMa/MLTravelTimesFigures)

### Documentation 
The Documentation can be found @ https://driftmlp.readthedocs.io/ 

### Interactive Web Application

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/MikeOMa/DriftMLP_Interactive_Notebook/main?urlpath=apps%2Finteractive.ipynb)

### Minimal Example
The below example produces an estimate of the pathway and travel time of going between `from_loc` and `to_loc`. 

```angular2html
import driftmlp

T_mat = driftmlp.read_default_network()
from_loc = [-90.90, 23.88]
to_loc = [-9.88, 35.80] 
SP = driftmlp.shortest_path.SingleSP(T_mat, from_loc, to_loc)
display(SP)
SP.plot_folium()
```

### General usage
The package has 2 main usage components

- `DriftMLP.driftfile_to_network` will form the network from the hdf5 file above which is the most computationally intensive part
- `DriftMLP.shortest_path` module contains functions which require a network to run.
    - `SingleSP` is sufficient for most usage. It will take the network and a pair of locations and results in a class containing both the path there and back. The travel time of this path may be accessed via the .sp.travel_time attribute. Has methods `.plot_cartopy` and `.plot_folium` for convince. 
    - `network_path` is a more customizable class which can be used for manual adaptations. It takes in two h3 indices and stores the path going from the first to the second. Stores travel path in network indices (`.nid`), spatial discretization indices (`.h3id`) and travel time in days (`.travel_time`).
- `DriftMLP.rotations` contains functionality to generate random rotations. See paper for further details. This has two options one method by ARVO and one by shoemake. The Shoemake quaternion approach is advised.
- `DriftMLP.plotting` Various functions for h3 index sequence plotting. Two backends are there on using folium, one using cartopy. Folium is easier to view and scroll around with. Cartopy/Matplotlib are far more customizable and can produce publication ready graphics.

