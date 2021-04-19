import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="driftmlp",
    version="1.0",
    author="Mike O'Malley",
    author_email="m.omalley2@lancaster.ac.uk",
    install_requires=[
        "numpy>=1.17.2",
        "cartopy>=0.17",
        "h3>=3.6.4",
        "scipy>=1.3.1",
        "python-igraph>0.8",
        "h5py",
        "folium",
        "geopandas",
        "pyproj>=2.2.0",
        "matplotlib",
        "numba",
    ],
    package_dir={'driftmlp': 'driftmlp'},
    package_data={'driftmlp': ['data/*.GraphML']},
    description="A set of tools for data extraction from the GDP database and estimating travel times",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MikeOMa/DriftMLP",
    packages=[
        "driftmlp",
        "driftmlp.shortest_path",
        "driftmlp.form_network",
        "driftmlp.rotations",
        "driftmlp.plotting",
        "driftmlp.drifter_indexing",
        "driftmlp.drifter_indexing.driftiter",
        "driftmlp.drifter_indexing.story",
        "driftmlp.drifter_indexing.makehdf5",
    ],
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
