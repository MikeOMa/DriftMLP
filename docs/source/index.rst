
Welcome to DriftMLP's documentation!
====================================

**driftmlp** is a pacakage which gives a measure
of separation which represents the ocean currents. The intended use of the package uses the global drifter program data :cite:p:`GDP`.
The package can be used with other datasets; however the default parameters will need to be carefully tested.


driftmlp implements a relatively straightforward method described in :cite:p:`o2020estimating`.
We use the h3-system from UBER for discretization and provide various plotting and processing methods for this.
Our intended uses of the package are:

- Use as a better measure of separation than geodesic distance when analysing ocean-borne species.

- A method to extract a transitition matrix from the global drifter program data.

- Exploratory analysis of ocean currents.

If you're using this to just extract a transition matrix
read the paper to see exactly what transition matrix is created.





.. toctree::
    :maxdepth: 1
    :caption: Installation:

    Started <started.rst>
    Help <help.rst>

.. toctree::
    :maxdepth: 1
    :caption: Examples:

    nbs/basic_pathways.ipynb
    nbs/Bootstrap.ipynb
    nbs/Rotations.ipynb

.. bibliography::

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
