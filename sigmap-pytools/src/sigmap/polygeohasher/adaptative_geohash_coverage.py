import math
import warnings
from collections import defaultdict, deque
from typing import Literal, Any

from geopandas import GeoDataFrame
from shapely.geometry.multipolygon import MultiPolygon
from shapely.prepared import prep
from shapely.strtree import STRtree

from .logger import logging

logger = logging.getLogger(__name__)

from .utils.algorithms import check_tile_coverage_with_prepared
from .utils.gadm_download import download_gadm_country
from .utils.geohash import candidate_geohashes_covering_bbox, geohashes_to_gdf, \
    geohash_to_polygon, get_geohash_children
from .utils.polygons import build_single_multipolygon

def _sanitize_country_geometry(country_geom: MultiPolygon, debug: bool = False) -> tuple[MultiPolygon, tuple[
    Any, Any, Any, Any]] | None:
    """
    Validate and sanitize country geometry.

    Parameters
    ----------
    country_geom : MultiPolygon
        Country geometry to validate
    debug : bool, default False
        Enable debug logging

    Returns
    -------
    tuple or None
        (sanitized_geometry, bounds) if valid, None if empty or invalid
    """
    if not country_geom.is_valid:
        if debug:
            logger.warning("Country geometry invalid, applying buffer(0) fix...")
        country_geom = country_geom.buffer(0)

    if country_geom.is_empty:
        if debug:
            logger.warning("Empty geometry provided — returning empty result.")
        return None

    if any(math.isnan(x) for x in country_geom.bounds): # (lon_min, lat_min, lon_max, lat_max)
        if debug:
            logger.warning("Geometry bounds contain NaN — returning empty result.")
        return None

    return country_geom, country_geom.bounds


def geohash_coverage(
        country_geom: MultiPolygon,
        level: int = 1,
        use_strtree: bool = True,
        predicate: Literal["intersects", "within", "contains", "overlaps",
        "crosses", "touches", "covers", "covered_by",
        "contains_properly"] = 'intersects',
        debug: bool = False,
) -> dict[str, list]:
    """
    Generate geohash coverage for a single level.

    Parameters
    ----------
    country_geom : MultiPolygon
        Country geometry
    level : int
        Geohash level
    use_strtree : bool
        Use spatial index for performance
    predicate : str
        Spatial predicate for filtering
    debug : bool
        Enable debug logging

    Returns
    -------
    dict : Dictionary with level as key and list of geohashes as value
    """
    san = _sanitize_country_geometry(country_geom, debug=debug)
    if san is None:
        return {}
    country_geom, (lon_min, lat_min, lon_max, lat_max) = san

    initial_geos = candidate_geohashes_covering_bbox(
        lon_min, lat_min, lon_max, lat_max, level
    )
    initial_geohashes = [gh for gh, lon, lat in initial_geos]
    initial_gdf = geohashes_to_gdf(initial_geohashes)

    initial_gdf = initial_gdf[initial_gdf.geometry.is_valid].copy()

    candidates = None
    if use_strtree:
        tree = STRtree(initial_gdf.geometry)
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore', category=RuntimeWarning)
            candidate_indices = tree.query(country_geom, predicate=predicate)
        candidates = initial_gdf.iloc[candidate_indices]
    else:
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore', category=RuntimeWarning)
            candidates = initial_gdf[initial_gdf.intersects(country_geom)]

    if candidates is None or len(candidates) == 0:
        if debug:
            logger.debug("No candidate tiles found — returning empty result.")
        return {}

    prepared_country_geom = prep(country_geom)
    result = defaultdict(list)

    with warnings.catch_warnings():
        warnings.filterwarnings('ignore', category=RuntimeWarning)

        for current_gh in candidates['geohash'].values:
            try:
                tile_geom = geohash_to_polygon(current_gh)
            except Exception as e:
                if debug:
                    logger.error(f"Skipping invalid geohash: {current_gh}")
                    logger.error(f"Exception detail: {e}")
                continue

            if not tile_geom.is_valid:
                tile_geom = tile_geom.buffer(0)

            if not prepared_country_geom.intersects(tile_geom):
                continue

            coverage = check_tile_coverage_with_prepared(
                tile_geom,
                country_geom,
                prepared_country_geom,
                threshold=0.95
            )

            if coverage != 'none':
                result[level].append(current_gh)

    if debug:
        logger.debug(f"Single level coverage complete: {len(result.get(level, []))} tiles at level {level}")

    return result


def adaptive_geohash_coverage(
        country_geom: MultiPolygon,
        min_level: int,
        max_level: int,
        coverage_threshold: float = 0.95,
        use_strtree: bool = True,
        predicate: Literal["intersects", "within", "contains", "overlaps",
        "crosses", "touches", "covers", "covered_by",
        "contains_properly"] = 'intersects',
        debug: bool = False,
) -> tuple[dict[str, list], GeoDataFrame]:
    """
    Generate adaptive geohash coverage with refinement at boundaries.

    Parameters
    ----------
    country_geom : MultiPolygon
        Country geometry
    min_level : int
        Starting geohash level
    max_level : int
        Maximum refinement level
    coverage_threshold : float
        Threshold for considering a tile "fully covered" (0-1)
    use_strtree : bool
        Use spatial index for performance
    predicate : str
        Spatial predicate for filtering
    debug : bool
        Enable debug logging

    Returns
    -------
    tuple : (geohash_dict, tiles_gdf)
        - geohash_dict: Dictionary with levels as keys
        - tiles_gdf: GeoDataFrame with all tiles and their levels
    """
    san = _sanitize_country_geometry(country_geom, debug=debug)
    if san is None:
        return {}, GeoDataFrame(columns=['geohash', 'geometry', 'level'], geometry='geometry')
    country_geom, (lon_min, lat_min, lon_max, lat_max) = san

    prepared_country_geom = prep(country_geom)

    result = defaultdict(list)

    initial_geos = candidate_geohashes_covering_bbox(
        lon_min, lat_min, lon_max, lat_max, min_level
    )
    initial_geohashes = [gh for gh, lon, lat in initial_geos]
    initial_gdf = geohashes_to_gdf(initial_geohashes)

    initial_gdf = initial_gdf[initial_gdf.geometry.is_valid].copy()

    candidates = None
    if use_strtree:
        tree = STRtree(initial_gdf.geometry)
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore', category=RuntimeWarning)
            candidate_indices = tree.query(country_geom, predicate=predicate)
        candidates = initial_gdf.iloc[candidate_indices]
    else:
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore', category=RuntimeWarning)
            candidates = initial_gdf[initial_gdf.intersects(country_geom)]

    assert candidates is not None
    queue = deque([(gh, min_level) for gh in candidates['geohash'].values])
    processed = set()

    if debug:
        logger.debug(f"Processing {len(queue)} initial tiles...")
        logger.debug(f"Adaptive refinement: L{min_level} → L{max_level}")

    geom_cache = {}

    with warnings.catch_warnings():
        warnings.filterwarnings('ignore', category=RuntimeWarning)

        while queue:
            current_gh, current_level = queue.popleft()

            if current_gh in processed:
                continue
            processed.add(current_gh)

            if current_gh in geom_cache:
                tile_geom = geom_cache[current_gh]
            else:
                tile_geom = geohash_to_polygon(current_gh)
                if not tile_geom.is_valid:
                    tile_geom = tile_geom.buffer(0)
                geom_cache[current_gh] = tile_geom

            if not prepared_country_geom.intersects(tile_geom):
                continue

            coverage = check_tile_coverage_with_prepared(
                tile_geom,
                country_geom,
                prepared_country_geom,
                threshold=coverage_threshold
            )

            if coverage == 'none':
                continue
            elif coverage == 'full':
                result[current_level].append(current_gh)
            elif coverage == 'partial':
                if current_level < max_level:
                    children = get_geohash_children(current_gh)
                    for child in children:
                        queue.append((child, current_level + 1))
                else:
                    result[current_level].append(current_gh)

    result = dict(sorted(result.items()))

    if debug:
        total_tiles = sum(len(tiles) for tiles in result.values())
        logger.debug(f"Adaptive coverage complete:")
        logger.debug(f"   Total tiles: {total_tiles}")
        for level, tiles in result.items():
            logger.debug(f"   Level {level}: {len(tiles)} tiles")

    all_geohashes = []
    all_levels = []
    for level, tiles in result.items():
        all_geohashes.extend(tiles)
        all_levels.extend([level] * len(tiles))

    final_gdf = geohashes_to_gdf(all_geohashes)
    final_gdf['level'] = all_levels

    return result, final_gdf


if __name__ == '__main__':
    ISO3 = "BEL"
    MIN_LEVEL = 2
    MAX_LEVEL = 5
    CACHE_DIR = './gadm_cache'

    country_dataframe = download_gadm_country(ISO3, cache_dir=CACHE_DIR)
    country_geometry = build_single_multipolygon(country_dataframe)

    logger.info("=== TESTING ADAPTIVE COVERAGE ===")
    geohash_dict, tiles_gdf = adaptive_geohash_coverage(
        country_geometry,
        min_level=MIN_LEVEL,
        max_level=MAX_LEVEL,
        use_strtree=True,
        debug=True
    )

    logger.info("=== MIN-MAX LEVEL RESULTS ===")
    for key in sorted(geohash_dict.keys()):
        logger.info(f"Level {key}: {len(geohash_dict[key])} tiles")
    logger.info(f"Total tiles: {sum(len(v) for v in geohash_dict.values())}")

    logger.info("\n=== TESTING SINGLE LEVEL COVERAGE ===")
    geohash_dict_single_level = geohash_coverage(
        country_geometry,
        level=2,
        use_strtree=True,
        debug=True
    )

    logger.info("=== SINGLE LEVEL RESULTS ===")
    for key in sorted(geohash_dict_single_level.keys()):
        logger.info(f"Level {key}: {len(geohash_dict_single_level[key])} tiles")
