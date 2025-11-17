"""
Utils: Utility functions for geohash operations, GADM downloads, and polygon processing.

This subpackage provides low-level utilities used by other sigmap subpackages.
"""

from .gadm_download import (
    download_gadm_country,
    clear_gadm_temp_files,
)
from .geohash import (
    encode_geohash,
    candidate_geohashes_covering_bbox,
    geohash_to_polygon,
    geohashes_to_gdf,
    get_geohash_children,
    geohashes_to_boxes,
    geohashes_to_multipolygon,
    lonlat_res_for_length,
)
from .polygons import (
    build_single_multipolygon,
)

__all__ = [
    # GADM download utilities
    "download_gadm_country",
    "clear_gadm_temp_files",
    # Geohash utilities
    "encode_geohash",
    "candidate_geohashes_covering_bbox",
    "geohash_to_polygon",
    "geohashes_to_gdf",
    "get_geohash_children",
    "geohashes_to_boxes",
    "geohashes_to_multipolygon",
    "lonlat_res_for_length",
    # Polygon utilities
    "build_single_multipolygon",
]
