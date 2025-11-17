from shapely import MultiPolygon, Polygon

from sigmap.polygeohasher import download_gadm_country, build_single_multipolygon, adaptive_geohash_coverage, \
    plot_geohash_coverage, geohash_coverage
from sigmap.polygeohasher.plot_geohash_coverage import plot_level_statistics

from sigmap.logger import logging
logger = logging.getLogger(__name__)

def plot_adaptative_geohash_coverage(geom: MultiPolygon | Polygon,
                                     map_save_path='../generated_plot/adaptive_coverage.png',
                                     stat_save_path='../generated_plot/'):
    geohash_dict, tiles_gdf = adaptive_geohash_coverage(geom, 2, 6)

    logger.info(f"Generated coverage: {geohash_dict}")
    # Plot the map
    plot_geohash_coverage(
        geom, geohash_dict, tiles_gdf,
        style='adaptive',
        save_path=map_save_path,
    )

    # Plot tile repartition (bar or pie)
    plot_level_statistics(
        geohash_dict,
        style='bar',
        save_path=stat_save_path+'level_stats_bar.png'
    )
    plot_level_statistics(
        geohash_dict,
        style='pie',
        save_path=stat_save_path+'level_stats_pie.png'
    )

def plot_single_geohash_coverage(geom: MultiPolygon| Polygon, map_save_path='../generated_plot/single_coverage.png'):
    geohash_dict = geohash_coverage(geom, 4)

    # Plot the map
    plot_geohash_coverage(
        geom, geohash_dict,
        style='single',
        save_path=map_save_path,
    )

def custom_polygon_creation() -> Polygon:
    # L-shaped
    vertex = [
        (0, 0), (2, 0), (2, 1), (1, 1),
        (1, 3), (0, 3), (0, 0)
    ]
    return Polygon(vertex)

if __name__ == '__main__':
    country_gdf = download_gadm_country("BEL", cache_dir='../gadm_cache')

    # Geometry
    country_geom = build_single_multipolygon(country_gdf)
    custom_geom = custom_polygon_creation()

    # Country
    ## Adaptive coverage
    plot_adaptative_geohash_coverage(country_geom)
    ## Single level
    plot_single_geohash_coverage(country_geom)

    # Custom
    ## Adaptive coverage
    plot_adaptative_geohash_coverage(custom_geom,
                                     map_save_path='../generated_plot/CUSTOM_adaptive_coverage.png',
                                     stat_save_path='../generated_plot/CUSTOM_')
    # Note, you should see on the inside corner of the L-shape a tile with a corner off the polygon.
    # This is due to the fact that if we count the area of the tile (level 4)
    # using what we see on the neighbors at the next level (level 5), we can approximate that the part 'out' represent 1 over 32 tiles.
    # The default threshold to consider a fully contained tile is 95%, since (1 - 1/32) > 95%; then this tile is considered "fully contains".
    # This behavior can be avoided by tweaking the threshold value, for instance at 100%, like so:
    # geohash_dict, tiles_gdf = adaptive_geohash_coverage(geom, 2, 6, coverage_threshold=1)

    # I advise to be cautious with the threshold, since the more you increase it to accurately match your geometry,
    # the more tiles the algorithm has to check.
    # From one level to another, you increase the number of tiles to check by 'nbr_partial_tiles * 32' recursively until you reach the max level.

    ## Single level
    plot_single_geohash_coverage(custom_geom, map_save_path='../generated_plot/CUSTOM_single_coverage.png')