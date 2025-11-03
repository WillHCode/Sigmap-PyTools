API Reference
==============

This page provides detailed documentation for all public functions and classes.

Main Coverage Functions
------------------------

.. automodule:: sigmap.polygeohasher
   :members:
   :undoc-members:
   :show-inheritance:

.. autofunction:: sigmap.polygeohasher.adaptative_geohash_coverage.adaptive_geohash_coverage

.. autofunction:: sigmap.polygeohasher.adaptative_geohash_coverage.geohash_coverage

Plotting Functions
------------------

.. autofunction:: sigmap.polygeohasher.plot_geohash_coverage.plot_geohash_coverage

.. autofunction:: sigmap.polygeohasher.plot_geohash_coverage.quick_plot

GADM Download Utilities
------------------------

.. autofunction:: sigmap.polygeohasher.utils.gadm_download.download_gadm_country

.. autofunction:: sigmap.polygeohasher.utils.gadm_download.clear_gadm_temp_files

Geohash Utilities
-----------------

.. autofunction:: sigmap.polygeohasher.utils.geohash.encode_geohash

.. autofunction:: sigmap.polygeohasher.utils.geohash.candidate_geohashes_covering_bbox

.. autofunction:: sigmap.polygeohasher.utils.geohash.geohash_to_polygon

.. autofunction:: sigmap.polygeohasher.utils.geohash.geohashes_to_gdf

.. autofunction:: sigmap.polygeohasher.utils.geohash.get_geohash_children

.. autofunction:: sigmap.polygeohasher.utils.geohash.geohashes_to_boxes

.. autofunction:: sigmap.polygeohasher.utils.geohash.geohashes_to_multipolygon

.. autofunction:: sigmap.polygeohasher.utils.geohash.lonlat_res_for_length

Polygon Utilities
-----------------

.. autofunction:: sigmap.polygeohasher.utils.polygons.build_single_multipolygon

