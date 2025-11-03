import warnings
from typing import Literal

from geopandas import GeoDataFrame
from shapely.geometry.multipolygon import MultiPolygon
from shapely.geometry.polygon import Polygon
from shapely.prepared import PreparedGeometry
from shapely.strtree import STRtree

from ..logger import logging

logger = logging.getLogger(__name__)


def check_tile_coverage_with_prepared(tile_geom: Polygon,
                                      country_geom: MultiPolygon,
                                      prepared_country_geom,
                                      threshold: float=0.95):
    """
    Optimized version using prepared geometry for fast intersection checks,
    but original geometry for actual calculations.

    This is faster than check_tile_coverage() because prepared geometry
    makes the initial intersects() check much faster.

    Returns: 'full', 'partial', or 'none'

    Parameters
    ----------
    tile_geom : shapely.geometry
        Tile geometry to check
    country_geom : shapely.geometry
        Original country geometry (for intersection calculation)
    prepared_country_geom : shapely.prepared.PreparedGeometry
        Prepared version of country_geom (for fast boolean checks)
    threshold : float, default 0.95
        Percentage of tile area that must be inside to be considered 'full'

    Notes
    -----
    Why we need both geometries:
    - prepared_country_geom: Fast for boolean predicates (.intersects(), .contains(), etc.)
    - country_geom: Required for geometric operations (.intersection(), .union(), etc.)

    Prepared geometries are read-only optimization wrappers that don't support
    operations returning new geometries.
    """
    try:
        if not tile_geom.is_valid:
            tile_geom = tile_geom.buffer(0)

        with warnings.catch_warnings():
            warnings.filterwarnings('ignore', category=RuntimeWarning)

            if not prepared_country_geom.intersects(tile_geom):
                return 'none'

            try:
                intersection = tile_geom.intersection(country_geom)
            except Exception:
                # Fallback: use buffer(0) to fix geometry issues
                tile_geom = tile_geom.buffer(0)
                if not country_geom.is_valid:
                    country_geom = country_geom.buffer(0)
                intersection = tile_geom.intersection(country_geom)

            # Handle empty intersection
            if intersection.is_empty:
                return 'none'

            # Calculate coverage ratio
            tile_area = tile_geom.area
            if tile_area == 0:
                return 'none'

            intersection_area = intersection.area
            coverage_ratio = intersection_area / tile_area

            if coverage_ratio >= threshold:
                return 'full'
            elif coverage_ratio > 0:
                return 'partial'
            else:
                return 'none'

    except Exception as e:
        # Fail gracefully
        if hasattr(check_tile_coverage_with_prepared, '_debug') and check_tile_coverage_with_prepared._debug:
            logger.warning(f"Error checking coverage: {e}")
        return 'none'


def SRTree(tiles_gdf: GeoDataFrame,
           country_geom: MultiPolygon,
           predicate: Literal["intersects", "within", "contains", "overlaps",
           "crosses", "touches", "covers", "covered_by", "contains_properly"] | None ="intersects"):
    """
    Use spatial index to find tiles intersecting country geometry.

    Parameters
    ----------
    tiles_gdf : gpd.GeoDataFrame
        GeoDataFrame of tile geometries
    country_geom : shapely.geometry
        Country geometry to query against
    predicate : str, default "intersection"
        Spatial predicate for tree query

    Returns
    -------
    gpd.GeoDataFrame
        GeoDataFrame of intersecting tiles
    """
    tiles_gdf = tiles_gdf[tiles_gdf.geometry.is_valid].copy()

    tree = STRtree(tiles_gdf.geometry)

    with warnings.catch_warnings():
        warnings.filterwarnings('ignore', category=RuntimeWarning)
        candidate_indices = tree.query(country_geom, predicate=predicate)

    return tiles_gdf.iloc[candidate_indices]


