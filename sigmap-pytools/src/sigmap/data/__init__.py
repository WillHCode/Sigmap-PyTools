"""
Data collection subpackage for sigmap-pytools.

This subpackage provides wrappers for collecting geospatial data from various sources:
- Copernicus Marine: Ocean and marine data
- ERA5 (via CDS API): Climate reanalysis data
- CHELSA: High-resolution climate data

All data collection functions support filtering by:
- Geographic bounding boxes
- Geohash-based regions
- Shapely polygons/multipolygons
"""

from .copernicus import (
    fetch_copernicus_data,
    list_copernicus_products,
    get_copernicus_coverage,
)

from .era5 import (
    fetch_era5_data,
    list_era5_variables,
    get_era5_coverage,
)

from .chelsa import (
    fetch_chelsa_data,
    list_chelsa_variables,
    get_chelsa_coverage,
)

__all__ = [
    # Copernicus functions
    "fetch_copernicus_data",
    "list_copernicus_products",
    "get_copernicus_coverage",

    # ERA5 functions
    "fetch_era5_data",
    "list_era5_variables",
    "get_era5_coverage",

    # CHELSA functions
    "fetch_chelsa_data",
    "list_chelsa_variables",
    "get_chelsa_coverage",
]

__version__ = "0.0.1"