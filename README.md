# sigmap-pytools

[![Documentation](https://img.shields.io/badge/DOC-purple.svg)](https://sigmap-pytools.readthedocs.io/en/latest/)
[![PyPI version](https://img.shields.io/badge/PyPi-green.svg)](https://badge.fury.io/py/sigmap-pytools)
[![Python Version](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-BSD--3--Clause-red.svg)](LICENSE)

[Documentation](https://sigmap-pytools.readthedocs.io/en/latest/) | [GitHub Repository](https://github.com/WillHCode/Sigmap-PyTools) | [PyPI](https://pypi.org/project/sigmap-pytools/)

A Python package for downloading and manipulating geometries by subdividing them using geohash. This package provides efficient tools for spatial processing, geohash-based polygon subdivision, and visualization.

## 🚀 Features

- **Geohash-based Polygon Subdivision**: Generate adaptive or fixed-level geohash coverage for any polygon geometry
- **GADM Integration**: Download country geometries directly from the GADM database
- **Coordinate Encoding**: Convert coordinates to geohash strings and vice versa
- **Flexible Coverage Algorithms**: 
  - Adaptive coverage with multi-level refinement
  - Single-level coverage for uniform tiling
- **Visualization Tools**: Plot geohash coverage with customizable styling
- **Efficient Processing**: Uses spatial indexes (STRtree) for fast intersection checks
- **Geohash Utilities**: Comprehensive set of tools for geohash manipulation and conversion

## 📦 Installation

### From PyPI

```bash
pip install sigmap-pytools
```

## 🏃 Quick Start

```python
import sigmap.polygeohasher as polygeohasher
from shapely.geometry import box, MultiPolygon

# Download a country geometry from GADM
country_gdf = polygeohasher.download_gadm_country('BEL', cache_dir='./gadm_cache')

# Build a single multipolygon from the GeoDataFrame
country_geom = polygeohasher.build_single_multipolygon(country_gdf)

# Generate adaptive geohash coverage (refines at boundaries)
geohash_dict, tiles_gdf = polygeohasher.adaptive_geohash_coverage(
    country_geom,
    min_level=2,
    max_level=5,
    coverage_threshold=0.95
)

print(f"Generated {sum(len(v) for v in geohash_dict.values())} geohashes")
```

## 📊 Visual Examples

### Coverage Comparison

The package supports two coverage strategies. Here's a visual comparison showing how each approach covers the same geometry:

| Adaptive Coverage | Single-Level Coverage |
|------------------|----------------------|
| ![Adaptive Coverage](exemples/generated_plot/adaptive_coverage.png) | ![Single-Level Coverage](exemples/generated_plot/single_coverage.png) |
| *Multi-level refinement: larger tiles in interior, smaller at boundaries* | *Uniform tile size across entire geometry* |

### Statistics & Analysis

Additional visualization capabilities include level distribution statistics and geometric comparisons:

| Level Statistics | Geohash Comparison |
|-----------------|-------------------|
| ![Level Statistics](exemples/generated_plot/level_stats_bar.png) | ![Boxes Comparison](exemples/generated_plot/geohash_boxes_comparison.png) |
| *Distribution of tiles across geohash levels* | *Geohash boxes vs actual polygon boundaries* |

## 📚 Main Features

### 1. Geohash Coverage Generation

#### Adaptive Coverage
Adaptive coverage automatically refines geohash tiles at polygon boundaries, using finer resolution where needed. This results in fewer tiles overall while maintaining high accuracy at boundaries:

```python
geohash_dict, tiles_gdf = polygeohasher.adaptive_geohash_coverage(
    geometry,
    min_level=2,        # Starting geohash level
    max_level=5,         # Maximum refinement level
    coverage_threshold=0.95,  # Threshold for considering a tile "fully covered"
    use_strtree=True,    # Use spatial index for performance
    debug=False
)

# Access results
for level, geohashes in geohash_dict.items():
    print(f"Level {level}: {len(geohashes)} tiles")
```

**Visual Example:**
![Adaptive Coverage](exemples/generated_plot/adaptive_coverage.png)
*Adaptive coverage uses multi-level refinement: large tiles in the interior, smaller tiles at boundaries for optimal coverage with fewer total tiles.*

#### Single-Level Coverage
Generate uniform geohash coverage at a specific level. All tiles have the same size, providing consistent resolution across the entire geometry:

```python
geohash_dict = polygeohasher.geohash_coverage(
    geometry,
    level=3,            # Geohash level (1-12, typically 3-6)
    use_strtree=True,
    debug=False
)
```

**Visual Example:**
![Single-Level Coverage](exemples/generated_plot/single_coverage.png)
*Single-level coverage uses uniform tile sizes across the entire geometry. All tiles are at the same geohash level.*

#### Comparison

**Adaptive Coverage** (recommended for most cases):
- ✅ Fewer tiles needed for good coverage
- ✅ Automatically optimizes resolution at boundaries
- ✅ Better performance with large geometries
- ✅ More efficient storage and processing

**Single-Level Coverage**:
- ✅ Consistent resolution everywhere
- ✅ Simpler to understand and debug
- ✅ Predictable tile count
- ⚠️ May require more tiles for accurate boundary coverage

### 2. GADM Country Data Download

Download country geometries from the GADM database:

```python
# Download Belgium geometry
belgium_gdf = polygeohasher.download_gadm_country(
    'BEL',                    # ISO3 country code
    cache_dir='./gadm_cache'  # Cache directory
)

# Convert to single geometry
belgium_geom = polygeohasher.build_single_multipolygon(belgium_gdf)
```

### 3. Geohash Encoding and Decoding

```python
# Encode coordinates to geohash
geohash = polygeohasher.encode_geohash(lon=6.1, lat=49.6, L=5)
print(geohash)  # 'u0u64'

# Convert geohash to polygon
polygon = polygeohasher.geohash_to_polygon('u0u64')
print(polygon.bounds)  # (5.625, 49.21875, 7.03125, 50.625)

# Get geohash resolution
lon_res, lat_res = polygeohasher.lonlat_res_for_length(5)
print(f"Level 5: {lon_res:.4f}° longitude, {lat_res:.4f}° latitude")
```

### 4. Geohash Conversion Utilities

```python
# Convert multiple geohashes to boxes
boxes = polygeohasher.geohashes_to_boxes(['u0u', 'u0v', 'u0w'])
# Returns: {'u0u': <Polygon>, 'u0v': <Polygon>, ...}

# Convert geohashes to a single multipolygon
multipolygon = polygeohasher.geohashes_to_multipolygon(
    ['u0u', 'u0v', 'u0w'],
    dissolve=True  # Union all geohashes into one geometry
)

# Convert to GeoDataFrame
gdf = polygeohasher.geohashes_to_gdf(['u0u', 'u0v', 'u0w'])

# Get children of a geohash
children = polygeohasher.get_geohash_children('u0u')
# Returns: ['u0u0', 'u0u1', 'u0u2', ...] (32 children)
```

### 5. Visualization

The package includes powerful visualization tools to understand your geohash coverage:

```python
from sigmap.polygeohasher import plot_geohash_coverage

# Plot coverage results with customizable styling
fig, ax = plot_geohash_coverage(
    country_geom=country_geom,
    geohash_dict=geohash_dict,
    tiles_gdf=tiles_gdf,
    style='adaptive',        # 'adaptive', 'simple', or 'heatmap'
    save_path='coverage.png',
    show_stats=True,
    color_by_level=True,
    title='Geohash Coverage Visualization'
)
```

**Additional Visualizations:**

The plotting function can also generate statistics visualizations:

![Level Statistics Bar Chart](exemples/generated_plot/level_stats_bar.png)
*Bar chart showing tile distribution across geohash levels*

![Geohash Boxes Comparison](exemples/generated_plot/geohash_isolated_polygons.png)
*Visualisation on how tiles can be represent and manipulated as (Multi)Polygons, and how the merging affects the geometry.*

For more visualization examples, check the `exemples/plot_geohash_coverage.py` and `exemples/geohash_conversion.py` scripts.

## 🔧 API Reference

### Core Coverage Functions

- `adaptive_geohash_coverage(geometry, min_level, max_level, ...)` - Generate adaptive multi-level geohash coverage
- `geohash_coverage(geometry, level, ...)` - Generate single-level geohash coverage

### Geohash Utilities

- `encode_geohash(lon, lat, L)` - Encode coordinates to geohash string
- `geohash_to_polygon(geohash)` - Convert geohash to polygon geometry
- `geohashes_to_boxes(geohashes)` - Convert geohashes to dictionary of box polygons
- `geohashes_to_multipolygon(geohashes, dissolve=True)` - Union geohashes into a multipolygon
- `geohashes_to_gdf(geohashes, crs='EPSG:4326')` - Convert geohashes to GeoDataFrame
- `get_geohash_children(parent_geohash)` - Get all children of a geohash
- `lonlat_res_for_length(L)` - Get spatial resolution for a geohash length
- `candidate_geohashes_covering_bbox(lon_min, lat_min, lon_max, lat_max, L)` - Find candidate geohashes for a bounding box

### Data Download

- `download_gadm_country(iso3, cache_dir=None)` - Download country geometry from GADM
- `clear_gadm_temp_files(dirs=None, patterns=None, dry_run=False)` - Clean up temporary GADM files

### Visualization

- `plot_geohash_coverage(country_geom, geohash_dict, tiles_gdf=None, ...)` - Plot geohash coverage with various styles
- `quick_plot(country_geom, geohash_dict, tiles_gdf=None)` - Quick visualization helper

### Polygon Utilities

- `build_single_multipolygon(gdf)` - Build a single MultiPolygon from a GeoDataFrame

## 📖 Examples

See the `exemples/` directory for complete usage examples:

- **geohash_coverage_simple.py** - Basic coverage generation workflow
- **geohash_conversion.py** - Comprehensive geohash conversion examples
- **plot_geohash_coverage.py** - Visualization examples

### Example: Covering a Custom Polygon

```python
import sigmap.polygeohasher as polygeohasher
from shapely.geometry import Polygon

# Create a custom L-shaped polygon
polygon = Polygon([
    (0, 0), (2, 0), (2, 2), (1, 2),
    (1, 3), (0, 3), (0, 0)
])

# Generate adaptive coverage
geohash_dict, tiles_gdf = polygeohasher.adaptive_geohash_coverage(
    polygon,
    min_level=3,
    max_level=6
)

# Visualize
polygeohasher.plot_geohash_coverage(
    polygon,
    geohash_dict,
    tiles_gdf,
    save_path='custom_coverage.png'
)
```

## 📋 Requirements

- Python >= 3.12
- geopandas >= 1.1.1
- shapely >= 2.1.2
- numpy >= 2.3.3
- pandas >= 2.3.3
- requests >= 2.32.5
- matplotlib

## 📦 Project Structure

```
Geohash/
├── docs/
├── exemples/
│   ├── generated_plot/
│   ├── geohash_conversion.py
│   ├── geohash_coverage_simple.py
│   └── plot_geohash_coverage.py
│
├── sigmap-pytools/
│   ├── src/sigmap/polygeohasher/
│   │   ├── adaptative_geohash_coverage.py
│   │   ├── plot_geohash_coverage.py
│   │   ├── logger.py
│   │   └── utils/
│   ├── tests/
│   └── pyproject.toml
├── LICENSE
├── CODE_OF_CONDUCT.md
├── CONTRIBUTING.md
└── README.md
```

## 📝 License

This project is licensed under the BSD 3-Clause License - see the [LICENSE](LICENSE) file for details.

## 👤 Author

**William Hubaux**

## 📚 Related Resources

- [Geohash Specification](https://en.wikipedia.org/wiki/Geohash)
- [GADM Database](https://gadm.org/)
- [Shapely Documentation](https://shapely.readthedocs.io/) ([GitHub](https://github.com/shapely/shapely))
- [GeoPandas Documentation](https://geopandas.org/)

## 🤝 Support

Questions about using sigmap-pytools may be asked by opening a discussion.

Bugs may be reported at the [GitHub issues page](https://github.com/WillHCode/Sigmap-PyTools/issues).

Contributions are welcome! Please see our [Contributing Guide](CONTRIBUTING.md) and [Code of Conduct](CODE_OF_CONDUCT.md).
