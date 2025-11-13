# Data Collection Subpackage

The `sigmap.data` subpackage provides unified wrappers for collecting geospatial data from multiple sources. It integrates seamlessly with the `polygeohasher` functionality to support area-of-interest filtering using polygons, bounding boxes, or geohash tiles.

## Supported Data Sources

### 1. **Copernicus Marine Service**
- **Type**: Ocean and marine data
- **Coverage**: Global oceans
- **Resolution**: Varies by product (~0.08° typical)
- **Temporal**: Daily to monthly
- **Variables**: Temperature, salinity, currents, sea level, waves, ice

### 2. **ERA5 (Copernicus Climate Data Store)**
- **Type**: Climate reanalysis
- **Coverage**: Global
- **Resolution**: 0.25° x 0.25°
- **Temporal**: Hourly (1940-present)
- **Variables**: Temperature, precipitation, wind, pressure, radiation, humidity

### 3. **CHELSA**
- **Type**: High-resolution climate data
- **Coverage**: Global land areas
- **Resolution**: ~1 km (30 arc-seconds)
- **Temporal**: 1981-2010 baseline, future projections 2011-2100
- **Variables**: Temperature, precipitation, bioclimatic variables

## Installation

Install the base package plus data dependencies:

```bash
# Base installation
pip install sigmap-pytools

# For Copernicus Marine
pip install copernicusmarine

# For ERA5
pip install cdsapi

# For CHELSA
pip install chelsa-cmip6

# Optional: For raster processing
pip install rasterio
```

## Setup & Authentication

### Copernicus Marine Service
1. Register at [Copernicus Marine](https://marine.copernicus.eu/)
2. Configure credentials (handled by copernicusmarine package)

### ERA5 (CDS API)
1. Register at [Climate Data Store](https://cds.climate.copernicus.eu/)
2. Create `~/.cdsapirc`:
```
url: https://cds.climate.copernicus.eu/api/v2
key: {uid}:{api-key}
```

### CHELSA
No authentication required - data is openly accessible.

## Quick Start

```python
from shapely.geometry import box
from sigmap.data import fetch_era5_temperature

# Define area of interest
belgium = box(2.5, 49.5, 6.4, 51.5)

# Download temperature data
path = fetch_era5_temperature(
    output_path='temperature.nc',
    geometry=belgium,
    time_range=('2020-01-01', '2020-01-31')
)
```

## Usage Patterns

### 1. Using Polygons/Bounding Boxes

```python
from shapely.geometry import box, Polygon
from sigmap.data import fetch_copernicus_data

# Method 1: Bounding box
belgium = box(2.5, 49.5, 6.4, 51.5)

# Method 2: Custom polygon
custom_area = Polygon([
    (2.5, 49.5), (6.4, 49.5),
    (6.4, 51.5), (2.5, 51.5), (2.5, 49.5)
])

# Download data
path = fetch_copernicus_data(
    product_id='cmems_mod_glo_phy_my_0.083deg_P1D-m',
    variables=['thetao'],
    output_path='ocean_temp.nc',
    geometry=belgium,
    time_range=('2020-01-01', '2020-01-07')
)
```

### 2. Using Geohash Tiles

```python
from sigmap.data import fetch_era5_data

# Single geohash
data = fetch_era5_data(
    variables=['2m_temperature'],
    output_path='temp.nc',
    geometry='u151',  # Single geohash
    time_range=('2020-01-01', '2020-01-07')
)

# Multiple geohashes
geohashes = ['u151', 'u154', 'u155']
data = fetch_era5_data(
    variables=['2m_temperature', 'total_precipitation'],
    output_path='climate.nc',
    geometry=geohashes,
    time_range=('2020-01-01', '2020-01-31')
)
```

### 3. Combining with Adaptive Coverage

```python
from sigmap.polygeohasher import (
    download_gadm_country,
    build_single_multipolygon,
    adaptive_geohash_coverage
)
from sigmap.data import fetch_chelsa_temperature

# Get country geometry
country_gdf = download_gadm_country('BEL')
country_geom = build_single_multipolygon(country_gdf)

# Generate adaptive geohash coverage
geohash_dict, tiles_gdf = adaptive_geohash_coverage(
    country_geom,
    min_level=3,
    max_level=5
)

# Use level 3 tiles for data download
level_3_tiles = geohash_dict[3]

# Download data for these tiles
path = fetch_chelsa_temperature(
    output_path='chelsa_temp.tif',
    geometry=level_3_tiles,
    month=1
)
```

## API Reference

### Copernicus Marine

```python
from sigmap.data import (
    fetch_copernicus_data,
    fetch_sea_surface_temperature,
    fetch_ocean_salinity,
    list_copernicus_products,
    get_copernicus_coverage
)

# Main function
fetch_copernicus_data(
    product_id: str,
    variables: List[str],
    output_path: Path,
    geometry: Union[Polygon, str, List[str], None] = None,
    time_range: Tuple[str, str] = None,
    depth_range: Tuple[float, float] = None,
    **kwargs
) -> Path

# Convenience functions
fetch_sea_surface_temperature(output_path, geometry, time_range)
fetch_ocean_salinity(output_path, geometry, time_range)

# Discovery
list_copernicus_products(keywords=None, contains_bbox=None)
get_copernicus_coverage(product_id)
```

### ERA5

```python
from sigmap.data import (
    fetch_era5_data,
    fetch_era5_temperature,
    fetch_era5_precipitation,
    fetch_era5_wind,
    list_era5_variables,
    get_era5_coverage
)

# Main function
fetch_era5_data(
    variables: List[str],
    output_path: Path,
    geometry: Union[Polygon, str, List[str], None] = None,
    time_range: Tuple[str, str] = None,
    hours: List[str] = None,
    dataset: str = 'reanalysis-era5-single-levels',
    **kwargs
) -> Path

# Convenience functions
fetch_era5_temperature(output_path, geometry, time_range)
fetch_era5_precipitation(output_path, geometry, time_range)
fetch_era5_wind(output_path, geometry, time_range)

# Discovery
list_era5_variables(dataset='reanalysis-era5-single-levels')
get_era5_coverage(dataset='reanalysis-era5-single-levels')
```

### CHELSA

```python
from sigmap.data import (
    fetch_chelsa_data,
    fetch_chelsa_temperature,
    fetch_chelsa_precipitation,
    fetch_chelsa_bioclim,
    list_chelsa_variables,
    get_chelsa_coverage
)

# Main function
fetch_chelsa_data(
    variable: str,
    output_path: Path,
    geometry: Union[Polygon, str, List[str], None] = None,
    time_period: str = '1981-2010',
    scenario: str = None,
    model: str = None,
    month: int = None,
    **kwargs
) -> Path

# Convenience functions
fetch_chelsa_temperature(output_path, geometry, time_period, month)
fetch_chelsa_precipitation(output_path, geometry, time_period, month)
fetch_chelsa_bioclim(bioclim_variable, output_path, geometry, time_period)

# Discovery
list_chelsa_variables(dataset='climatologies')
get_chelsa_coverage(dataset='climatologies')
```

## Common Variables

### ERA5 Variables
- **Temperature**: `2m_temperature`, `skin_temperature`, `sea_surface_temperature`
- **Precipitation**: `total_precipitation`, `convective_precipitation`
- **Wind**: `10m_u_component_of_wind`, `10m_v_component_of_wind`
- **Pressure**: `surface_pressure`, `mean_sea_level_pressure`
- **Radiation**: `surface_solar_radiation_downwards`, `surface_thermal_radiation_downwards`

### CHELSA Variables
- **Temperature**: `tas` (mean), `tasmin` (minimum), `tasmax` (maximum)
- **Precipitation**: `pr`
- **Bioclimatic**: `bio1` to `bio19` (WorldClim-style bioclimatic variables)

### Copernicus Marine Variables
- **Temperature**: `thetao`
- **Salinity**: `so`
- **Currents**: `uo` (eastward), `vo` (northward)
- **Sea level**: `zos`

## Examples

See `exemples/data_collection_example.py` for comprehensive examples including:

1. Downloading Copernicus data for a country
2. Using geohash tiles with ERA5
3. Downloading CHELSA with bounding boxes
4. Combining adaptive coverage with data downloads
5. Listing available variables and products
6. Comparing data from different sources
7. Batch downloading for multiple areas
8. Future climate projections

## Best Practices

### Area Selection
- **Small areas** (<1000 km²): Use precise polygons or single geohashes
- **Medium areas** (countries): Use adaptive geohash coverage at level 3-5
- **Large areas** (continents): Use coarser geohashes or bounding boxes

### Time Ranges
- **ERA5**: Best for hourly to daily data, historical analysis
- **CHELSA**: Best for monthly climatologies, future projections
- **Copernicus**: Best for ocean data, operational oceanography

### Resolution Considerations
- **ERA5**: 0.25° (~25 km) - good for regional climate
- **CHELSA**: ~1 km - excellent for local terrain effects
- **Copernicus**: Varies by product, typically 0.08° (~8 km) for ocean

### File Formats
- **NetCDF** (.nc): Multi-dimensional data (time, lat, lon, depth)
  - Best for time series, multiple variables
  - Supported by: ERA5, Copernicus
  
- **GeoTIFF** (.tif): Raster data (2D)
  - Best for spatial analysis, GIS integration
  - Supported by: CHELSA
  
- **GRIB** (.grib): Meteorological standard
  - Alternative format for ERA5

## Troubleshooting

### Authentication Issues
```python
# ERA5: Check ~/.cdsapirc exists and has correct format
# Copernicus: Ensure copernicusmarine credentials are configured
```

### Download Failures
```python
# Check available disk space
# Verify internet connection
# For ERA5: Check CDS API status
# For Copernicus: Verify product availability
```

### Area Selection
```python
# Ensure geometry is valid
from shapely.geometry import box
geom = box(lon_min, lat_min, lon_max, lat_max)
assert geom.is_valid

# Check geohash validity
from sigmap.polygeohasher import geohash_to_bbox
try:
    bbox = geohash_to_bbox('u151')
except:
    print("Invalid geohash")
```

## Performance Tips

1. **Batch Downloads**: Group requests to minimize API calls
2. **Geohash Level**: Use appropriate level (3-5 typically optimal)
3. **Time Chunking**: Download large time ranges in smaller chunks
4. **Caching**: Set `force_download=False` to reuse existing files
5. **Parallel Downloads**: Use multiple processes for independent areas

## Future Enhancements

Planned additions to the data subpackage:

- Additional data sources (Sentinel, Landsat, MODIS)
- Automatic data format conversion
- Built-in data validation and quality checks
- Temporal aggregation utilities
- Spatial interpolation helpers
- Integration with xarray for data analysis
- Progress bars for large downloads
- Automatic retry logic for failed downloads

## Contributing

To add a new data source:

1. Create a new module in `sigmap/data/` (e.g., `sentinel.py`)
2. Implement core functions:
   - `fetch_<source>_data()`: Main download function
   - `list_<source>_variables()`: Variable discovery
   - `get_<source>_coverage()`: Coverage metadata
3. Add convenience functions for common use cases
4. Update `__init__.py` exports
5. Add examples to `exemples/data_collection_example.py`
6. Update this README

## License

BSD 3-Clause License (same as sigmap-pytools)