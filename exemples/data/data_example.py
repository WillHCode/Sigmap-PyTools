"""
Examples for using the data collection subpackage.

This script demonstrates how to:
1. Download data from different sources (Copernicus, ERA5, CHELSA)
2. Use geohash tiles for area selection
3. Use polygon geometries for filtering
4. Combine with polygeohasher functionality
"""

from pathlib import Path
from shapely.geometry import box

from sigmap.polygeohasher import (
    download_gadm_country,
    build_single_multipolygon,
    adaptive_geohash_coverage,
)
from sigmap.data import (
    # Copernicus
    fetch_copernicus_data,
    list_copernicus_products,
    # ERA5
    fetch_era5_data,
    fetch_era5_temperature,
    list_era5_variables,
    # CHELSA
    fetch_chelsa_data,
    fetch_chelsa_temperature,
    list_chelsa_variables,
)
from sigmap.logger import logging

logger = logging.getLogger(__name__)


def example_1_copernicus_with_country():
    """
    Example 1: Download Copernicus ocean data for a country.
    """
    logger.info("\n" + "=" * 60)
    logger.info("Example 1: Copernicus Data for Belgium Coast")
    logger.info("=" * 60)
    
    # Download country geometry
    belgium_gdf = download_gadm_country('BEL', cache_dir='../gadm_cache')
    belgium_geom = build_single_multipolygon(belgium_gdf)
    
    # Fetch sea surface temperature
    output_path = Path('data/copernicus_sst_belgium.nc')
    
    try:
        # Note: This requires Copernicus Marine credentials
        path = fetch_copernicus_data(
            product_id='cmems_mod_glo_phy_my_0.083deg_P1D-m',
            variables=['thetao'],  # Temperature
            output_path=output_path,
            geometry=belgium_geom,
            time_range=('2020-01-01', '2020-01-07'),
            depth_range=(0.0, 1.0)
        )
        logger.info(f"Downloaded to: {path}")
    except Exception as e:
        logger.error(f"Download failed: {e}")
        logger.info("Make sure you have Copernicus Marine credentials configured")


def example_2_era5_with_geohash():
    """
    Example 2: Download ERA5 data using geohash tiles.
    """
    logger.info("\n" + "=" * 60)
    logger.info("Example 2: ERA5 Data with Geohash Selection")
    logger.info("=" * 60)
    
    # Define area using geohash tiles
    # These cover parts of Belgium
    geohash_tiles = ['u151', 'u154', 'u155', 'u156']
    
    logger.info(f"Using geohash tiles: {geohash_tiles}")
    
    # Fetch temperature and precipitation
    output_path = Path('data/era5_belgium_jan2020.nc')
    
    try:
        # Note: This requires CDS API credentials in ~/.cdsapirc
        path = fetch_era5_data(
            variables=['2m_temperature', 'total_precipitation'],
            output_path=output_path,
            geometry=geohash_tiles,
            time_range=('2020-01-01', '2020-01-07'),
            hours=['00:00', '12:00']  # Only 00:00 and 12:00
        )
        logger.info(f"Downloaded to: {path}")
    except Exception as e:
        logger.error(f"Download failed: {e}")
        logger.info("Make sure you have CDS API credentials configured")


def example_3_chelsa_with_bbox():
    """
    Example 3: Download CHELSA data using bounding box.
    """
    logger.info("\n" + "=" * 60)
    logger.info("Example 3: CHELSA Data with Bounding Box")
    logger.info("=" * 60)
    
    # Define area using bounding box
    belgium_bbox = box(2.5, 49.5, 6.4, 51.5)
    
    logger.info(f"Using bbox: {belgium_bbox.bounds}")
    
    # Fetch temperature for January
    output_path = Path('data/chelsa_temp_jan.tif')
    
    try:
        path = fetch_chelsa_temperature(
            output_path=output_path,
            geometry=belgium_bbox,
            time_period='1981-2010',
            month=1  # January
        )
        logger.info(f"Downloaded to: {path}")
    except Exception as e:
        logger.error(f"Download failed: {e}")


def example_4_adaptive_coverage_then_data():
    """
    Example 4: Use adaptive geohash coverage to select data area.
    """
    logger.info("\n" + "=" * 60)
    logger.info("Example 4: Adaptive Coverage + Data Download")
    logger.info("=" * 60)
    
    # Get country geometry
    belgium_gdf = download_gadm_country('BEL', cache_dir='../gadm_cache')
    belgium_geom = build_single_multipolygon(belgium_gdf)
    
    # Generate adaptive geohash coverage
    geohash_dict, tiles_gdf = adaptive_geohash_coverage(
        belgium_geom,
        min_level=3,
        max_level=5
    )
    
    logger.info(f"Generated {sum(len(v) for v in geohash_dict.values())} geohash tiles")
    
    # Use level 3 tiles for data download (larger tiles = less files)
    level_3_tiles = geohash_dict.get(3, [])
    
    if level_3_tiles:
        logger.info(f"Using {len(level_3_tiles)} level-3 tiles for data download")
        
        # Download ERA5 data for these tiles
        output_path = Path('data/era5_adaptive_coverage.nc')
        
        try:
            path = fetch_era5_temperature(
                output_path=output_path,
                geometry=level_3_tiles,
                time_range=('2020-01-01', '2020-01-07')
            )
            logger.info(f"Downloaded to: {path}")
        except Exception as e:
            logger.error(f"Download failed: {e}")


def example_5_list_available_data():
    """
    Example 5: List available variables and products.
    """
    logger.info("\n" + "=" * 60)
    logger.info("Example 5: List Available Data")
    logger.info("=" * 60)
    
    # List ERA5 variables
    logger.info("\nERA5 Variables:")
    era5_vars = list_era5_variables()
    for category, variables in era5_vars.items():
        logger.info(f"  {category}: {variables[:3]}...")  # Show first 3
    
    # List CHELSA variables
    logger.info("\nCHELSA Variables:")
    chelsa_vars = list_chelsa_variables()
    for category, variables in chelsa_vars.items():
        logger.info(f"  {category}: {variables[:3]}...")
    
    # List Copernicus products
    try:
        logger.info("\nCopernicus Products (searching for 'temperature'):")
        products = list_copernicus_products(keywords=['temperature'])
        logger.info(f"  Found {len(products)} products")
    except Exception as e:
        logger.error(f"  Could not list products: {e}")


def example_6_compare_data_sources():
    """
    Example 6: Compare data from different sources for the same area.
    """
    logger.info("\n" + "=" * 60)
    logger.info("Example 6: Compare Data Sources")
    logger.info("=" * 60)
    
    # Define area of interest
    test_area = box(4.0, 50.5, 4.5, 51.0)  # Small area in Belgium
    time_range = ('2020-01-01', '2020-01-07')
    
    logger.info(f"Area: {test_area.bounds}")
    logger.info(f"Time: {time_range}")
    
    # 1. ERA5 (reanalysis, ~0.25° resolution)
    logger.info("\n1. Downloading ERA5 data...")
    try:
        era5_path = fetch_era5_temperature(
            output_path='data/compare_era5.nc',
            geometry=test_area,
            time_range=time_range
        )
        logger.info(f"   ERA5: {era5_path}")
    except Exception as e:
        logger.error(f"   ERA5 failed: {e}")
    
    # 2. CHELSA (high-resolution climatology, ~1 km)
    logger.info("\n2. Downloading CHELSA data...")
    try:
        chelsa_path = fetch_chelsa_temperature(
            output_path='data/compare_chelsa.tif',
            geometry=test_area,
            time_period='1981-2010',
            month=1
        )
        logger.info(f"   CHELSA: {chelsa_path}")
    except Exception as e:
        logger.error(f"   CHELSA failed: {e}")
    
    logger.info("\nNote: Compare resolution and accuracy of different sources")


def example_7_batch_download():
    """
    Example 7: Batch download data for multiple areas.
    """
    logger.info("\n" + "=" * 60)
    logger.info("Example 7: Batch Download for Multiple Areas")
    logger.info("=" * 60)
    
    # Define multiple areas using geohashes
    areas = {
        'belgium_north': ['u155', 'u156'],
        'belgium_center': ['u151', 'u154'],
        'belgium_south': ['u14p', 'u14r'],
    }
    
    time_range = ('2020-01-01', '2020-01-03')
    
    for area_name, geohashes in areas.items():
        logger.info(f"\nDownloading data for {area_name}...")
        logger.info(f"  Geohashes: {geohashes}")
        
        output_path = Path(f'data/batch_{area_name}.nc')
        
        try:
            path = fetch_era5_temperature(
                output_path=output_path,
                geometry=geohashes,
                time_range=time_range
            )
            logger.info(f"  Downloaded to: {path}")
        except Exception as e:
            logger.error(f"  Failed: {e}")


def example_8_future_climate_projection():
    """
    Example 8: Download future climate projections from CHELSA.
    """
    logger.info("\n" + "=" * 60)
    logger.info("Example 8: Future Climate Projections")
    logger.info("=" * 60)
    
    belgium = box(2.5, 49.5, 6.4, 51.5)
    
    # Download projections for different scenarios
    scenarios = {
        'ssp126': 'Low emissions (optimistic)',
        'ssp370': 'Medium-high emissions (intermediate)',
        'ssp585': 'High emissions (worst-case)',
    }
    
    for scenario, description in scenarios.items():
        logger.info(f"\nDownloading {description}...")
        
        output_path = Path(f'data/chelsa_future_{scenario}.tif')
        
        try:
            path = fetch_chelsa_data(
                variable='tas',
                output_path=output_path,
                geometry=belgium,
                time_period='2041-2070',  # Mid-century
                scenario=scenario,
                model='GFDL-ESM4'
            )
            logger.info(f"  Downloaded to: {path}")
        except Exception as e:
            logger.error(f"  Failed: {e}")


def run_all_examples():
    """Run all examples in sequence."""
    examples = [
        example_1_copernicus_with_country,
        example_2_era5_with_geohash,
        example_3_chelsa_with_bbox,
        example_4_adaptive_coverage_then_data,
        example_5_list_available_data,
        example_6_compare_data_sources,
        example_7_batch_download,
        example_8_future_climate_projection,
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
    # Create data directory
    Path('').mkdir(exist_ok=True)
    
    # Run specific example or all
    example_num = '5'  # Change this to run different examples
    
    match example_num:
        case '1':
            example_1_copernicus_with_country()
        case '2':
            example_2_era5_with_geohash()
        case '3':
            example_3_chelsa_with_bbox()
        case '4':
            example_4_adaptive_coverage_then_data()
        case '5':
            example_5_list_available_data()
        case '6':
            example_6_compare_data_sources()
        case '7':
            example_7_batch_download()
        case '8':
            example_8_future_climate_projection()
        case 'all':
            run_all_examples()
        case _:
            logger.info(f"Unknown example: {example_num}")
            logger.info("Available examples: 1-8, or 'all'")
