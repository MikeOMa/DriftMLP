Getting Started
###############

Installation
************
This package can currently only be installed from github. Prior to installation you must have cartopy installed.

.. code-block:: shell

    pip install git+https://github.com/MikeOMa/DriftMLP

(Optional) Setting up the Data
******************************

This section is optional as we do provide a default transition matrix within the package. However, if you would like an
up to date transition matrix you can follow this section to recreate the transition matrix.

This section is also required if one your aims are to estimate grid uncertainty using rotations or if you want to uncertainty using bootstrap.
Both of these functionalities greatly increase the robustness of the results; therefore it is the advised use of this package.

Alternatively if one wishes to use this package for an alternative data source, all that is required is an iterable of longitude-latitude pairs.
An example of this is given at the end of this page.

(Optional) Collecting the drifter data
======================================

The method relies on an estimate of a transition matrix from a very large collection of trajectories. Therefore the first step is to put that
data into a format which is friendly with this package.

In summary the package requires an iterable which returns a dictionary. The dictionary should have an entry ['position'] which
holds positions at equally spaced time intervals $\mathcal{T}_L$.

Here's an example where we use the drifter trajectories.
We run the following from a folder where the `Global Drifter Program <https://www.aoml.noaa.gov/phod/gdp/interpolated/data/all.php>`_
data is stored. By default all metadata (files named drifl_1_5000.dat) should be in a folder called *metadata*.
All trajectory data (files named buoydata_1_5000.csv) should be in a folder  called *raw_data*

.. code-block:: python

    import driftmlp
    import h5py as h5
    file = h5.File("drift.h5", 'wb')
    driftmlp.drifter_indexing.make_hdf5.makeHDF(file, folder_raw="raw_data", folder_meta="meta_data")

This has populated the file "drift.h5" to contain all the drifter data. This input is used throughout the examples.
Typically `drift.h5` will be around 2gb so ensure this is only made once.


(Optional) Populating the transition_matrix
===========================================
Assuming that we have the data collected now we create the transition matrix. The default matrix from this section can be accessed by driftmlp.read_default_network().

.. code-block:: python

    import driftmlp
    dfile = "drift.h5"
    T_mat = driftmlp.driftfile_to_network(dfile)


(Advanced) Using an alternate data source
=========================================

To use this package with a different data source all that is needed is an iterable of longitude-latitude pairs, such as a list of lists.

Note if doing thing very careful consideration will need to be put into both day_cut_off and the resolution use.
See the paper :cite:p:`o2020estimating` for the sensitivity analyses conducted originally.


.. code-block:: python

    import driftmlp
    # Your iterable would look something like this
    # Where each trajectory is a list of longitude, latitude pairs or similar
    iterable = [trajectory_1, trajectory_2, ]
    # Pick the UBER-h3 resolution
    # resolution 3 is roughly similar to 100km square boxes
    # Higher resolution gives a finer scale
    discretizer = driftmlp.drifer_indexing.discrete_system.h3_default(res=3)
    T_mat = driftmlp.driftfile_to_network(data_iterable = iterable, observations_per_day=4, day_cut_off=5, discretizer=discretizer)

