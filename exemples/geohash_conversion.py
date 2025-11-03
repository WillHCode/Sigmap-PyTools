from sigmap.polygeohasher.utils.gadm_download import download_gadm_country
from sigmap.polygeohasher.utils.geohash import (
    geohashes_to_boxes,
    geohashes_to_multipolygon,
    get_geohash_children
)
from sigmap.polygeohasher.utils.polygons import build_single_multipolygon
from sigmap.polygeohasher.adaptative_geohash_coverage import (
    adaptive_geohash_coverage,
    geohash_coverage
)

from sigmap.polygeohasher.logger import logging

logger = logging.getLogger(__name__)

def example_1_single_geohash():
    """Example 1: Convert a single geohash to box."""
    logger.info("\n" + "=" * 60)
    logger.info("Example 1: Single Geohash to Box")
    logger.info("=" * 60)

    # Single geohash
    geohash = "u4pruyd"

    # Convert to box
    boxes = geohashes_to_boxes(geohash)

    logger.info(f"\nGeohash: {geohash}")
    logger.info(f"Box polygon: {boxes[geohash]}")
    logger.info(f"Bounds (lon_min, lat_min, lon_max, lat_max): {boxes[geohash].bounds}")
    logger.info(f"Area: {boxes[geohash].area:.10f} square degrees")


def example_2_multiple_geohashes():
    """Example 2: Convert multiple geohashes to boxes."""
    logger.info("\n" + "=" * 60)
    logger.info("Example 2: Multiple Geohashes to Boxes")
    logger.info("=" * 60)

    # Multiple geohashes (neighboring tiles)
    geohashes = ["u4pru", "u4prv", "u4prw", "u4pry"]

    # Convert to boxes
    boxes = geohashes_to_boxes(geohashes)

    logger.info(f"\nNumber of geohashes: {len(geohashes)}")
    logger.info(f"Number of boxes: {len(boxes)}")

    for gh, box in boxes.items():
        logger.info(f"  {gh}: bounds = {box.bounds}")


def example_3_from_coverage_result():
    """Example 3: Convert coverage results to boxes."""
    logger.info("\n" + "=" * 60)
    logger.info("Example 3: From Coverage Results")
    logger.info("=" * 60)

    # Load country
    country_gdf = download_gadm_country("LUX", cache_dir='./gadm_cache')  # Luxembourg (small)
    country_geom = build_single_multipolygon(country_gdf)

    # Generate single-level coverage
    geohash_dict = geohash_coverage(country_geom, level=4)

    # Get list of geohashes from result
    geohashes_list = []
    for level, geohashes in geohash_dict.items():
        geohashes_list.extend(geohashes)

    logger.info(f"\nCoverage generated {len(geohashes_list)} geohashes")

    # Convert to boxes
    boxes = geohashes_to_boxes(geohashes_list)

    logger.info(f"Created {len(boxes)} box polygons")
    logger.info(f"First 5 geohashes: {list(boxes.keys())[:5]}")


def example_4_multipolygon_dissolved():
    """Example 4: Create dissolved MultiPolygon from geohashes."""
    logger.info("\n" + "=" * 60)
    logger.info("Example 4: MultiPolygon (Dissolved)")
    logger.info("=" * 60)

    # Create some adjacent geohashes
    parent = "u4pr"
    children = get_geohash_children(parent)[:8]  # First 8 children

    logger.info(f"\nParent geohash: {parent}")
    logger.info(f"Using {len(children)} children: {children}")

    # Create dissolved MultiPolygon
    multi_poly = geohashes_to_multipolygon(children, dissolve=True)

    logger.info(f"\nResult type: {type(multi_poly).__name__}")
    logger.info(f"Number of polygons: {len(multi_poly.geoms) if hasattr(multi_poly, 'geoms') else 1}")
    logger.info(f"Total area: {multi_poly.area:.10f} square degrees")
    logger.info(f"Is valid: {multi_poly.is_valid}")


def example_5_multipolygon_separate():
    """Example 5: Create MultiPolygon keeping boxes separate."""
    logger.info("\n" + "=" * 60)
    logger.info("Example 5: MultiPolygon (Separate Boxes)")
    logger.info("=" * 60)

    # Create some geohashes
    geohashes = ["u4pru", "u4prv", "u4prw"]

    # Create MultiPolygon without dissolving
    multi_poly = geohashes_to_multipolygon(geohashes, dissolve=False)

    logger.info(f"\nInput geohashes: {geohashes}")
    logger.info(f"Result type: {type(multi_poly).__name__}")
    logger.info(f"Number of separate polygons: {len(multi_poly.geoms)}")
    logger.info(f"Total area: {multi_poly.area:.10f} square degrees")


def example_6_from_dict():
    """Example 6: Create MultiPolygon from boxes dictionary."""
    logger.info("\n" + "=" * 60)
    logger.info("Example 6: From Boxes Dictionary")
    logger.info("=" * 60)

    geohashes = ["u4pru", "u4prv", "u4prw", "u4pry"]

    # First convert to boxes
    boxes = geohashes_to_boxes(geohashes)
    logger.info(f"\nCreated boxes dictionary with {len(boxes)} entries")

    # Then convert to MultiPolygon
    multi_poly = geohashes_to_multipolygon(boxes, dissolve=True)

    logger.info(f"Result type: {type(multi_poly).__name__}")
    logger.info(f"Area: {multi_poly.area:.10f} square degrees")


def example_7_coverage_to_multipolygon():
    """Example 7: Full workflow - coverage to MultiPolygon."""
    logger.info("\n" + "=" * 60)
    logger.info("Example 7: Full Workflow - Coverage to MultiPolygon")
    logger.info("=" * 60)

    # Load country
    country_gdf = download_gadm_country("LUX", cache_dir='./gadm_cache')
    country_geom = build_single_multipolygon(country_gdf)

    # Generate coverage
    geohash_dict = geohash_coverage(country_geom, level=5)

    # Extract geohashes
    all_geohashes = []
    for level, geohashes in geohash_dict.items():
        all_geohashes.extend(geohashes)

    logger.info(f"\nGenerated {len(all_geohashes)} geohashes for Luxembourg (level 5)")

    # Convert to MultiPolygon
    coverage_polygon = geohashes_to_multipolygon(all_geohashes, dissolve=True)

    logger.info(f"\nCoverage polygon:")
    logger.info(f"  Type: {type(coverage_polygon).__name__}")
    logger.info(f"  Area: {coverage_polygon.area:.6f} square degrees")
    logger.info(f"  Bounds: {coverage_polygon.bounds}")

    # Compare with original country
    logger.info(f"\nOriginal country:")
    logger.info(f"  Area: {country_geom.area:.6f} square degrees")
    logger.info(f"  Coverage ratio: {(coverage_polygon.area / country_geom.area * 100):.2f}%")


def example_8_adaptive_coverage_by_level():
    """Example 8: Create separate MultiPolygons for each level."""
    logger.info("\n" + "=" * 60)
    logger.info("Example 8: Adaptive Coverage - MultiPolygons by Level")
    logger.info("=" * 60)

    # Load country
    country_gdf = download_gadm_country("LUX", cache_dir='./gadm_cache')
    country_geom = build_single_multipolygon(country_gdf)

    # Generate adaptive coverage
    geohash_dict, tiles_gdf = adaptive_geohash_coverage(
        country_geom,
        min_level=3,
        max_level=5
    )

    logger.info(f"\nAdaptive coverage results:")

    # Create MultiPolygon for each level
    level_polygons = {}
    for level, geohashes in geohash_dict.items():
        multi_poly = geohashes_to_multipolygon(geohashes, dissolve=True)
        level_polygons[level] = multi_poly

        logger.info(f"\nLevel {level}:")
        logger.info(f"  Geohashes: {len(geohashes)}")
        logger.info(f"  Area: {multi_poly.area:.6f} square degrees")
        logger.info(f"  Polygons: {len(multi_poly.geoms) if hasattr(multi_poly, 'geoms') else 1}")

    # Calculate total coverage
    all_geohashes = []
    for geohashes in geohash_dict.values():
        all_geohashes.extend(geohashes)

    total_coverage = geohashes_to_multipolygon(all_geohashes, dissolve=True)
    logger.info(f"\nTotal coverage:")
    logger.info(f"  Total geohashes: {len(all_geohashes)}")
    logger.info(f"  Total area: {total_coverage.area:.6f} square degrees")


def example_9_visualize_boxes():
    """Example 9: Visualize boxes vs MultiPolygon."""
    logger.info("\n" + "=" * 60)
    logger.info("Example 9: Visualize Boxes vs MultiPolygon")
    logger.info("=" * 60)

    try:
        import matplotlib.pyplot as plt
        import geopandas as gpd
        from shapely.geometry import mapping

        # Create some geohashes
        geohashes = ["u0gnu", "u0gnv", "u0gnw", "u0gny",
                     "u0gnz", "u0gnx", "u0gnq", "u0gnm"]

        # Get boxes
        boxes = geohashes_to_boxes(geohashes)

        # Create MultiPolygons (dissolved and separate)
        multi_poly_dissolved = geohashes_to_multipolygon(geohashes, dissolve=True)
        multi_poly_separate = geohashes_to_multipolygon(geohashes, dissolve=False)

        # Create plot
        fig, axes = plt.subplots(1, 3, figsize=(18, 6))

        # Plot 1: Individual boxes
        gdf1 = gpd.GeoDataFrame({'geohash': list(boxes.keys())},
                                geometry=list(boxes.values()), crs='EPSG:4326')
        gdf1.plot(ax=axes[0], facecolor='lightblue', edgecolor='navy', alpha=0.6)
        axes[0].set_title(f'Individual Boxes\n{len(boxes)} separate polygons', fontweight='bold')
        axes[0].set_axis_off()

        # Plot 2: Separate MultiPolygon
        gdf2 = gpd.GeoDataFrame({'geometry': [multi_poly_separate]}, crs='EPSG:4326')
        gdf2.plot(ax=axes[1], facecolor='lightgreen', edgecolor='darkgreen', alpha=0.6)
        axes[1].set_title(f'MultiPolygon (Separate)\n{len(multi_poly_separate.geoms)} polygons',
                          fontweight='bold')
        axes[1].set_axis_off()

        # Plot 3: Dissolved MultiPolygon
        gdf3 = gpd.GeoDataFrame({'geometry': [multi_poly_dissolved]}, crs='EPSG:4326')
        gdf3.plot(ax=axes[2], facecolor='lightcoral', edgecolor='darkred', alpha=0.6)
        n_polys = len(multi_poly_dissolved.geoms) if hasattr(multi_poly_dissolved, 'geoms') else 1
        axes[2].set_title(f'MultiPolygon (Dissolved)\n{n_polys} polygon(s)', fontweight='bold')
        axes[2].set_axis_off()

        plt.tight_layout()
        plt.savefig('./generated_plot/geohash_boxes_comparison.png', dpi=200, bbox_inches='tight')
        logger.info("Visualization saved to: geohash_boxes_comparison.png")

    except ImportError:
        logger.warning("Matplotlib not available. Skipping visualization.")


def example_10_isolated_polygons():
    """Example 10: Behavior with isolated (disjoint) polygons."""
    logger.info("\n" + "=" * 60)
    logger.info("Example 10: Isolated (Disjoint) Polygons")
    logger.info("=" * 60)

    try:
        import matplotlib.pyplot as plt
        import geopandas as gpd

        # Create geohashes with distinct groups:
        # Group 1: Adjacent tiles (will merge when dissolved)
        group1 = ["u0gnb", "u0gnc", "u0gnf", "u0gn9"]

        # Group 2: Adjacent tiles in different location (will merge separately)
        group2 = ["u0gns", "u0gnt"]

        # Group 3: Single isolated tile far away
        group3 = ["u0gn0"]  # Completely isolated

        # Group 4: Another isolated tile
        group4 = ["u0gnp"]  # Completely isolated in different area

        all_geohashes = group1 + group2 + group3 + group4

        logger.info(f"\nTest setup:")
        logger.info(f"  Group 1 (adjacent): {group1}")
        logger.info(f"  Group 2 (adjacent): {group2}")
        logger.info(f"  Group 3 (isolated): {group3}")
        logger.info(f"  Group 4 (isolated): {group4}")
        logger.info(f"  Total geohashes: {len(all_geohashes)}")

        # Get boxes
        boxes = geohashes_to_boxes(all_geohashes)

        # Create MultiPolygons
        multi_poly_separate = geohashes_to_multipolygon(all_geohashes, dissolve=False)
        multi_poly_dissolved = geohashes_to_multipolygon(all_geohashes, dissolve=True)

        # Analyze dissolved result
        logger.info(f"\nResults:")
        logger.info(f"  Separate: {len(multi_poly_separate.geoms)} polygons")
        logger.info(
            f"  Dissolved: {len(multi_poly_dissolved.geoms) if hasattr(multi_poly_dissolved, 'geoms') else 1} polygon(s)")

        if hasattr(multi_poly_dissolved, 'geoms'):
            logger.info(f"\n  Dissolved polygon breakdown:")
            for i, geom in enumerate(multi_poly_dissolved.geoms, 1):
                logger.info(f"    Polygon {i}: area = {geom.area:.10f} sq degrees")

        # Create visualization
        fig, axes = plt.subplots(2, 2, figsize=(16, 16))

        # Plot 1: Individual boxes with labels
        gdf1 = gpd.GeoDataFrame({'geohash': list(boxes.keys())},
                                geometry=list(boxes.values()), crs='EPSG:4326')
        gdf1.plot(ax=axes[0, 0], facecolor='lightblue', edgecolor='navy', alpha=0.6, linewidth=2)
        axes[0, 0].set_title(f'Individual Boxes\n{len(boxes)} separate boxes',
                             fontweight='bold', fontsize=14)

        # Add labels to show groups
        for gh, box in boxes.items():
            centroid = box.centroid
            color = 'red' if gh in group1 else 'blue' if gh in group2 else 'green' if gh in group3 else 'purple'
            axes[0, 0].plot(centroid.x, centroid.y, 'o', color=color, markersize=8, zorder=5)
        axes[0, 0].set_axis_off()

        # Plot 2: Separate MultiPolygon
        gdf2 = gpd.GeoDataFrame({'geometry': [multi_poly_separate]}, crs='EPSG:4326')
        gdf2.plot(ax=axes[0, 1], facecolor='lightgreen', edgecolor='darkgreen',
                  alpha=0.6, linewidth=2)
        axes[0, 1].set_title(f'MultiPolygon (Separate)\n{len(multi_poly_separate.geoms)} polygons (no merging)',
                             fontweight='bold', fontsize=14)
        axes[0, 1].set_axis_off()

        # Plot 3: Dissolved MultiPolygon
        gdf3 = gpd.GeoDataFrame({'geometry': [multi_poly_dissolved]}, crs='EPSG:4326')
        gdf3.plot(ax=axes[1, 0], facecolor='lightcoral', edgecolor='darkred',
                  alpha=0.6, linewidth=2)
        n_polys = len(multi_poly_dissolved.geoms) if hasattr(multi_poly_dissolved, 'geoms') else 1
        axes[1, 0].set_title(f'MultiPolygon (Dissolved)\n{n_polys} polygon(s) (adjacent merged)',
                             fontweight='bold', fontsize=14)
        axes[1, 0].set_axis_off()

        # Plot 4: Dissolved with different colors per polygon
        if hasattr(multi_poly_dissolved, 'geoms'):
            colors = plt.cm.Set3(range(len(multi_poly_dissolved.geoms)))
            for i, (geom, color) in enumerate(zip(multi_poly_dissolved.geoms, colors)):
                gdf_part = gpd.GeoDataFrame({'id': [i]}, geometry=[geom], crs='EPSG:4326')
                gdf_part.plot(ax=axes[1, 1], facecolor=color, edgecolor='black',
                              alpha=0.7, linewidth=2, label=f'Region {i + 1}')
            axes[1, 1].legend(loc='upper right', fontsize=10)
        else:
            gdf3.plot(ax=axes[1, 1], facecolor='lightcoral', edgecolor='darkred',
                      alpha=0.6, linewidth=2)

        axes[1, 1].set_title(f'Dissolved - Colored by Region\nEach color = separate polygon',
                             fontweight='bold', fontsize=14)
        axes[1, 1].set_axis_off()

        plt.tight_layout()
        plt.savefig('./generated_plot/geohash_isolated_polygons.png', dpi=200, bbox_inches='tight')
        logger.info("Visualization saved to: geohash_isolated_polygons.png")

        # Additional analysis
        logger.info(f"\nKey Insights:")
        logger.info(f"   - When dissolve=False: All {len(all_geohashes)} boxes remain separate")
        logger.info(f"   - When dissolve=True: Adjacent boxes merge, isolated stay separate")
        logger.info(f"   - Result: {n_polys} distinct region(s)")
        logger.info(f"   - Each isolated geohash becomes its own polygon in the MultiPolygon")
        logger.info(f"   - Adjacent geohashes merge into single polygons")

    except ImportError:
        logger.warning("Matplotlib not available. Skipping visualization.")


def run_all_examples():
    """Run all examples in sequence."""
    examples = [
        example_1_single_geohash,
        example_2_multiple_geohashes,
        example_3_from_coverage_result,
        example_4_multipolygon_dissolved,
        example_5_multipolygon_separate,
        example_6_from_dict,
        example_7_coverage_to_multipolygon,
        example_8_adaptive_coverage_by_level,
        example_9_visualize_boxes,
        example_10_isolated_polygons
    ]

    for i, example_func in enumerate(examples, 1):
        try:
            example_func()
        except Exception as e:
            logger.error(f"Error in example {i}: {e}")
            import traceback
            traceback.print_exc()

    logger.info("\n" + "=" * 60)
    logger.info("ALL EXAMPLES COMPLETE")
    logger.info("=" * 60)


if __name__ == '__main__':
    example_num = 'all'

    match example_num:
        case '1':
            example_1_single_geohash()
        case '2':
            example_2_multiple_geohashes()
        case '3':
            example_3_from_coverage_result()
        case '4':
            example_4_multipolygon_dissolved()
        case '5':
            example_5_multipolygon_separate()
        case '6':
            example_6_from_dict()
        case '7':
            example_7_coverage_to_multipolygon()
        case '8':
            example_8_adaptive_coverage_by_level()
        case '9':
            example_9_visualize_boxes()
        case '10':
            example_10_isolated_polygons()
        case 'all':
            run_all_examples()
        case _:
            print(f"Unknown example: {example_num}")
            print("Available examples: 1-10, or 'all'")
