
Welcome to DriftMLP's documentation!
====================================

**DriftMLP** is a pacakage which gives a measure
of separation which represents the ocean currents.
It implements a relatively straightforward method described in :cite:p:`o2020estimating`.
We use the h3-system from UBER for discretization and provide various plotting and processing methods for this.
Our intended uses of the package are:

- Use as a better measure of separation than geodesic distance when analysing ocean-borne species.

- A method to extract a transitition matrix from the drifter data.

- Exploratory analysis of ocean currents.

If you're using this to just extract a transition matrix
read the about section for exact details
about how the transition matrix is made.




.. toctree::
    :maxdepth: 1
    :caption: Installation:

    started <started.rst>
    about <about.rst>
    help <help.rst>

.. toctree::
    :maxdepth: 1
    :caption: Examples:

    nbs/basic_pathways.ipynb
    nbs/Bootstrap.ipynb

.. bibliography::

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
