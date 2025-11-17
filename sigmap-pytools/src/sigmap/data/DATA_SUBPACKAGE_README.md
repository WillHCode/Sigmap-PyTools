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

## Examples

See `exemples/data/notebooks` for comprehensive examples using different data sources.

## Best Practices
**BE AWARE OF THE FILE SIZES !**
The more variables you select, the bigger time range is, the higher the resolution is, and so on... Considerably increase the downloaded file sizes.\
To have an precise value please go to the website of the datasource, for instance Copernicus and ERA5 make you fulfill a form that give you the .zip total size of your request.

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
4. **Caching**: Keep `force_download=False` to reuse existing files
5. **Parallel Downloads**: Use multiple processes for independent areas

## Future Enhancements

Planned additions to the data subpackage:

- Additional data sources (Sentinel, Landsat, MODIS)
- Automatic data format conversion
- Built-in data validation and quality checks
- Temporal aggregation utilities
- Spatial interpolation helpers

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