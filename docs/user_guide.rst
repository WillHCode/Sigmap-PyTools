User Guide
==========

This guide provides an overview of the main features and how to use them.

Basic Usage
-----------

Downloading Country Geometries
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Download country geometries from the GADM database:

.. code-block:: python

   import sigmap.polygeohasher as polygeohasher

   # Download Belgium at country level (level 0)
   belgium = polygeohasher.download_gadm_country("BEL", level=0)

   # Download France at administrative level 1
   france_regions = polygeohasher.download_gadm_country("FRA", level=1)

The function automatically handles caching and downloads only if the file doesn't exist locally.

Generating Geohash Coverage
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Adaptive Coverage
^^^^^^^^^^^^^^^^^

Adaptive coverage refines geohash tiles based on their intersection with the polygon:

.. code-block:: python

   coverage = polygeohasher.adaptive_geohash_coverage(
       belgium.geometry.iloc[0],
       max_level=5,
       threshold=0.95
   )

Single-Level Coverage
^^^^^^^^^^^^^^^^^^^^^

Single-level coverage uses a fixed geohash precision:

.. code-block:: python

   coverage = polygeohasher.geohash_coverage(
       belgium.geometry.iloc[0],
       level=3
   )

Visualization
~~~~~~~~~~~~~

Plot your geohash coverage:

.. code-block:: python

   polygeohasher.plot_geohash_coverage(
       belgium.geometry.iloc[0],
       coverage,
       style='adaptive',
       save_path='coverage.png'
   )

Geohash Utilities
---------------

Encoding Coordinates
~~~~~~~~~~~~~~~~~~~~~

Convert coordinates to geohash:

.. code-block:: python

   geohash = polygeohasher.encode_geohash(4.35, 50.85, L=5)
   # Returns: 'u151m'

Converting Geohashes to Geometries
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Convert geohash strings to GeoDataFrames:

.. code-block:: python

   geohashes = ['u151m', 'u151j', 'u151q']
   gdf = polygeohasher.geohashes_to_gdf(geohashes)

Best Practices
--------------

* Use adaptive coverage for complex polygons with varying detail requirements
* Use single-level coverage when you need uniform tile sizes
* Cache GADM downloads to avoid repeated downloads
* Use appropriate max_level values based on your polygon size and precision needs

