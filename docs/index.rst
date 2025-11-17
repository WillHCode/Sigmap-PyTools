sigmap-pytools
==============

.. image:: https://img.shields.io/pypi/v/sigmap-pytools.svg
   :target: https://pypi.org/project/sigmap-pytools/
   :alt: PyPI version

A Python package for downloading and manipulating geometries by subdividing them using geohash. This package provides efficient tools for spatial processing, geohash-based polygon subdivision, visualization, and geospatial data collection.



What is sigmap-pytools?
-----------------------

sigmap-pytools is a Python package that enables efficient spatial processing by subdividing polygon geometries using geohash encoding. The package is organized into three main subpackages:

**polygeohasher** - Geohash-based polygon subdivision and visualization:

* **Geohash-based Polygon Subdivision**: Generate adaptive or fixed-level geohash coverage for any polygon geometry
* **Flexible Coverage Algorithms**:
  
  * Adaptive coverage with multi-level refinement
  * Single-level coverage for uniform tiling
* **Visualization Tools**: Plot geohash coverage with customizable styling

**utils** - Low-level utility functions:

* **GADM Integration**: Download country geometries directly from the GADM database
* **Coordinate Encoding**: Convert coordinates to geohash strings and vice versa
* **Geohash Utilities**: Comprehensive set of tools for geohash manipulation and conversion
* **Polygon Processing**: Utilities for working with polygon geometries

**data** - Geospatial data collection from multiple sources:

* **Copernicus Marine**: Download ocean and marine data
* **ERA5**: Access climate reanalysis data via CDS API
* **CHELSA**: Retrieve high-resolution climate data

Installation
------------

Install from PyPI:

.. code-block:: bash

   pip install sigmap-pytools

Requirements
------------

* Python >=3.12
* geopandas >=1.1.1
* shapely >=2.1.2
* numpy >=2.3.3
* pandas >=2.3.3
* matplotlib

Quick Start
------------

.. code-block:: python

   import sigmap.polygeohasher as polygeohasher
   from shapely.geometry import Point
   import geopandas as gpd

   # Download a country geometry
   belgium = polygeohasher.download_gadm_country("BEL", level=0)

   # Generate adaptive geohash coverage
   coverage = polygeohasher.adaptive_geohash_coverage(
       belgium.geometry.iloc[0],
       max_level=5,
       threshold=0.95
   )

   # Plot the results
   polygeohasher.plot_geohash_coverage(
       belgium.geometry.iloc[0],
       coverage,
       style='adaptive'
   )

Contents
--------

.. toctree::
   :maxdepth: 2

   installation
   user_guide
   api_reference
   examples

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

