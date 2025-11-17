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

__all__ = [
    # Main coverage functions
    "adaptive_geohash_coverage",
    "geohash_coverage",
    # Plotting functions
    "plot_geohash_coverage",
    "quick_plot"
]

__version__ = "0.0.1"
