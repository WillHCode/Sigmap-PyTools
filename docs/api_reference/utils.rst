utils Subpackage
================

The ``utils`` subpackage provides low-level utility functions for geohash operations, GADM downloads, and polygon processing.

GADM Download Utilities
-----------------------

.. autofunction:: sigmap.utils.gadm_download.download_gadm_country

.. autofunction:: sigmap.utils.gadm_download.clear_gadm_temp_files

Geohash Utilities
-----------------

.. autofunction:: sigmap.utils.geohash.encode_geohash

.. autofunction:: sigmap.utils.geohash.candidate_geohashes_covering_bbox

.. autofunction:: sigmap.utils.geohash.geohash_to_polygon

.. autofunction:: sigmap.utils.geohash.geohashes_to_gdf

.. autofunction:: sigmap.utils.geohash.get_geohash_children

.. autofunction:: sigmap.utils.geohash.geohashes_to_boxes

.. autofunction:: sigmap.utils.geohash.geohashes_to_multipolygon

.. autofunction:: sigmap.utils.geohash.lonlat_res_for_length

Polygon Utilities
-----------------

.. autofunction:: sigmap.utils.polygons.build_single_multipolygon

