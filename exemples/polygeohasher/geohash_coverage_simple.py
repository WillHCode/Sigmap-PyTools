from shapely import Polygon
from shapely.geometry.multipolygon import MultiPolygon

from sigmap.polygeohasher import download_gadm_country, build_single_multipolygon, adaptive_geohash_coverage, \
    geohash_coverage

from sigmap.polygeohasher.logger import logging

logger = logging.getLogger(__name__)

def counting_tiles_per_coverage(geom, min_level, max_level):

    logger.info("=== TESTING ADAPTIVE COVERAGE ===")
    # Adaptative from min to max
    # if a level doesn't fully include tile defined by the threshold (default 95%) it won't appear in result.
    geohash_dict, tiles_gdf = adaptive_geohash_coverage(
        geom,
        min_level=min_level,
        max_level=max_level,
        use_strtree=True,
    )

    logger.info("=== MIN-MAX LEVEL RESULTS ===")
    for key in sorted(geohash_dict.keys()):
        logger.info(f"Level {key}: {len(geohash_dict[key])} tiles")
    logger.info(f"Total tiles: {sum(len(v) for v in geohash_dict.values())}")

    logger.info("\n=== TESTING SINGLE LEVEL COVERAGE ===")
    # Single level
    geohash_dict_single_level = geohash_coverage(
        geom,
        level=2,
        use_strtree=True,
        debug=True
    )

    logger.info("=== SINGLE LEVEL RESULTS ===")
    for key in sorted(geohash_dict_single_level.keys()):
        logger.info(f"Level {key}: {len(geohash_dict_single_level[key])} tiles")

def custom_polygon_creation() -> Polygon:
    # L-shaped
    vertex = [
        (0, 0), (2, 0), (2, 2), (1, 2),
        (1, 3), (0, 3), (0, 0)
    ]
    return Polygon(vertex)

if __name__ == '__main__':
    ISO3 = "BEL"
    MIN_LEVEL = 2
    MAX_LEVEL = 5
    CACHE_DIR = '../gadm_cache'

    country_dataframe = download_gadm_country(ISO3, cache_dir=CACHE_DIR)

    # Geometry
    country_geometry = build_single_multipolygon(country_dataframe)
    custom_geometry = custom_polygon_creation()

    # Counting the tiles per coverage type
    logger.warning("=== COUNTRY COVERAGE ===")
    counting_tiles_per_coverage(country_geometry, MIN_LEVEL, MAX_LEVEL)
    logger.warning("=== CUSTOM COVERAGE ===")
    # Note : using Polygon instead of Multipolygon should not affect the result
    counting_tiles_per_coverage(custom_geometry, MIN_LEVEL, MAX_LEVEL)
