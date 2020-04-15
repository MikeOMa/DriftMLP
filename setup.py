import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="driftmlp",
    version="0.2",
    author="Mike O'Malley",
    author_email="m.omalley2@lancaster.ac.uk",
    description="A set of tools for data extraction from the GDP database and estimating travel times",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MikeOMa/DriftMLP",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
