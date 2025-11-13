"""
Pytest configuration and shared fixtures for polygeohasher tests
"""
import pytest
import tempfile
import shutil
from pathlib import Path
import geopandas as gpd
from shapely.geometry import box, Polygon, MultiPolygon


# ==================== Directory Fixtures ====================

@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests"""
    tmpdir = tempfile.mkdtemp()
    yield tmpdir
    shutil.rmtree(tmpdir, ignore_errors=True)


@pytest.fixture
def cache_dir(temp_dir):
    """Create a cache directory for GADM files"""
    cache = Path(temp_dir) / 'gadm_cache'
    cache.mkdir(exist_ok=True)
    return str(cache)


# ==================== Geometry Fixtures ====================

@pytest.fixture
def simple_square():
    """Simple square geometry for testing"""
    return box(0, 0, 1, 1)


@pytest.fixture
def large_square():
    """Larger square for testing"""
    return box(0, 0, 10, 10)


@pytest.fixture
def small_square():
    """Very small square for edge case testing"""
    return box(0, 0, 0.1, 0.1)


@pytest.fixture
def rectangle():
    """Rectangle for testing non-square shapes"""
    return box(0, 0, 5, 2)


@pytest.fixture
def l_shaped_polygon():
    """L-shaped polygon for complex shape testing"""
    coords = [
        (0, 0), (2, 0), (2, 2), (1, 2),
        (1, 3), (0, 3), (0, 0)
    ]
    return Polygon(coords)


@pytest.fixture
def concave_polygon():
    """Concave polygon (C-shape)"""
    coords = [
        (0, 0), (4, 0), (4, 1), (1, 1),
        (1, 3), (4, 3), (4, 4), (0, 4), (0, 0)
    ]
    return Polygon(coords)


@pytest.fixture
def polygon_with_hole():
    """Polygon with interior hole"""
    outer = [(0, 0), (10, 0), (10, 10), (0, 10), (0, 0)]
    hole = [(2, 2), (2, 8), (8, 8), (8, 2), (2, 2)]
    return Polygon(outer, [hole])


@pytest.fixture
def multipolygon_islands():
    """MultiPolygon representing islands"""
    island1 = box(0, 0, 1, 1)
    island2 = box(3, 3, 4, 4)
    island3 = box(6, 6, 7, 7)
    return MultiPolygon([island1, island2, island3])


@pytest.fixture
def overlapping_polygons():
    """Two overlapping polygons"""
    poly1 = box(0, 0, 2, 2)
    poly2 = box(1, 1, 3, 3)
    return [poly1, poly2]


@pytest.fixture
def invalid_polygon():
    """Self-intersecting (invalid) polygon"""
    return Polygon([(0, 0), (2, 2), (2, 0), (0, 2), (0, 0)])


# ==================== GeoDataFrame Fixtures ====================

@pytest.fixture
def simple_gdf(simple_square):
    """Simple GeoDataFrame with one polygon"""
    return gpd.GeoDataFrame(
        {'id': [1], 'name': ['Test']},
        geometry=[simple_square],
        crs='EPSG:4326'
    )


@pytest.fixture
def multi_polygon_gdf():
    """GeoDataFrame with multiple polygons"""
    polygons = [box(i, i, i+1, i+1) for i in range(5)]
    return gpd.GeoDataFrame(
        {'id': range(5), 'name': [f'Poly_{i}' for i in range(5)]},
        geometry=polygons,
        crs='EPSG:4326'
    )


@pytest.fixture
def tiles_gdf():
    """GeoDataFrame representing geohash tiles"""
    tiles = [box(i, j, i+1, j+1) for i in range(3) for j in range(3)]
    geohashes = [f'tile_{i}_{j}' for i in range(3) for j in range(3)]
    return gpd.GeoDataFrame(
        {'geohash': geohashes, 'level': [2] * 9},
        geometry=tiles,
        crs='EPSG:4326'
    )


# ==================== Geohash Fixtures ====================

@pytest.fixture
def sample_geohashes():
    """Sample geohash strings for testing"""
    return ['u09tv', 'u09tw', 'u09ty', 'u09tz']


@pytest.fixture
def geohash_hierarchy():
    """Parent-child geohash hierarchy"""
    parent = 'u09'
    children = [parent + c for c in '0123456789bcdefghjkmnpqrstuvwxyz']
    return {'parent': parent, 'children': children}


# ==================== Test Data Fixtures ====================

@pytest.fixture
def sample_country_data():
    """Sample country-like data for testing"""
    return {
        'iso3': 'TST',
        'name': 'Test Country',
        'geometry': box(0, 0, 5, 5)
    }


@pytest.fixture
def france_like_data():
    """France-like geometry data"""
    coords = [
        (0, 0), (2, -1), (4, 0), (5, 2),
        (4, 4), (2, 5), (0, 4), (-1, 2), (0, 0)
    ]
    return {
        'iso3': 'FRA',
        'name': 'France',
        'geometry': Polygon(coords)
    }


# ==================== Mock File Fixtures ====================

@pytest.fixture
def mock_shapefile(temp_dir, simple_gdf):
    """Create a mock shapefile for testing"""
    shp_path = Path(temp_dir) / 'test.shp'
    simple_gdf.to_file(shp_path)
    return str(shp_path)


@pytest.fixture
def mock_gadm_files(cache_dir):
    """Create mock GADM files structure"""
    files = {
        'FRA': f'gadm41_FRA_0.shp',
        'USA': f'gadm41_USA_0.shp',
        'DEU': f'gadm41_DEU_0.shp'
    }
    
    created = {}
    for iso3, filename in files.items():
        filepath = Path(cache_dir) / filename
        # Create minimal shapefile structure
        gdf = gpd.GeoDataFrame(
            {'NAME': [iso3]},
            geometry=[box(0, 0, 1, 1)],
            crs='EPSG:4326'
        )
        gdf.to_file(filepath)
        created[iso3] = str(filepath)
    
    return created


# ==================== Configuration Fixtures ====================

@pytest.fixture
def default_coverage_params():
    """Default parameters for coverage testing"""
    return {
        'min_level': 2,
        'max_level': 4,
        'coverage_threshold': 0.95,
        'use_strtree': True,
        'predicate': 'intersects',
        'debug': False
    }


@pytest.fixture
def high_precision_params():
    """High precision parameters"""
    return {
        'min_level': 4,
        'max_level': 7,
        'coverage_threshold': 0.99,
        'use_strtree': True,
        'predicate': 'intersects',
        'debug': False
    }


@pytest.fixture
def low_precision_params():
    """Low precision parameters"""
    return {
        'min_level': 1,
        'max_level': 3,
        'coverage_threshold': 0.85,
        'use_strtree': True,
        'predicate': 'intersects',
        'debug': False
    }


# ==================== Pytest Markers ====================

def pytest_configure(config):
    """Register custom markers"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "network: marks tests that require network access"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )


# ==================== Test Helpers ====================

@pytest.fixture
def assert_valid_geodataframe():
    """Helper to assert valid GeoDataFrame"""
    def _assert(gdf, expected_columns=None):
        assert isinstance(gdf, gpd.GeoDataFrame)
        assert 'geometry' in gdf.columns
        assert len(gdf) >= 0
        assert all(gdf.geometry.is_valid)
        
        if expected_columns:
            for col in expected_columns:
                assert col in gdf.columns
        
        return True
    return _assert


@pytest.fixture
def assert_geohash_valid():
    """Helper to assert valid geohash"""
    def _assert(geohash, expected_length=None):
        valid_chars = set("0123456789bcdefghjkmnpqrstuvwxyz")
        assert isinstance(geohash, str)
        assert set(geohash).issubset(valid_chars)
        
        if expected_length:
            assert len(geohash) == expected_length
        
        return True
    return _assert


@pytest.fixture
def assert_coverage_result():
    """Helper to assert valid coverage result"""
    def _assert(result_dict, result_gdf, min_level, max_level):
        # Check dictionary
        assert isinstance(result_dict, dict)
        for level, geohashes in result_dict.items():
            assert min_level <= level <= max_level
            assert isinstance(geohashes, list)
            assert all(isinstance(gh, str) for gh in geohashes)
        
        # Check GeoDataFrame
        assert isinstance(result_gdf, gpd.GeoDataFrame)
        assert 'geohash' in result_gdf.columns
        assert 'level' in result_gdf.columns
        assert 'geometry' in result_gdf.columns
        assert all(result_gdf.geometry.is_valid)
        
        # Check consistency
        dict_total = sum(len(tiles) for tiles in result_dict.values())
        assert len(result_gdf) == dict_total
        
        return True
    return _assert


# ==================== Session Fixtures ====================

@pytest.fixture(scope='session')
def test_data_dir():
    """Test data directory (session scope)"""
    return Path(__file__).parent / 'test_data'


# ==================== Cleanup ====================

@pytest.fixture(autouse=True)
def cleanup_temp_files():
    """Automatically cleanup temp files after each test"""
    yield
    # Cleanup code runs after test
    import gc
    gc.collect()

