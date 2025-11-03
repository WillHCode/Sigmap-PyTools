"""
Polygeohasher: A Python package for geohash-based polygon subdivision.

This package provides tools for downloading geometries and subdividing them
using geohash for efficient spatial processing.
"""

from .adaptative_geohash_coverage import (
    adaptive_geohash_coverage,
    geohash_coverage,
)
from .plot_geohash_coverage import (
    plot_geohash_coverage,
    quick_plot,
)
from .utils.gadm_download import (
    download_gadm_country,
    clear_gadm_temp_files,
)
from .utils.geohash import (
    encode_geohash,
    candidate_geohashes_covering_bbox,
    geohash_to_polygon,
    geohashes_to_gdf,
    get_geohash_children,
    geohashes_to_boxes,
    geohashes_to_multipolygon,
    lonlat_res_for_length,
)
from .utils.polygons import (
    build_single_multipolygon,
)

__all__ = [
    # Main coverage functions
    "adaptive_geohash_coverage",
    "geohash_coverage",
    # Plotting functions
    "plot_geohash_coverage",
    "quick_plot",
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

__version__ = "0.0.1"
