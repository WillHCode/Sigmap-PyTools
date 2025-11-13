"""
Pytest fixtures for data subpackage tests.
"""
import pytest
from shapely.geometry import box, Polygon


# ==================== Geometry Fixtures ====================

@pytest.fixture
def belgium_bbox():
    """Belgium bounding box"""
    return box(2.5, 49.5, 6.4, 51.5)


@pytest.fixture
def small_test_area():
    """Small test area for quick tests"""
    return box(4.0, 50.0, 4.5, 50.5)


@pytest.fixture
def geohash_test_tiles():
    """Sample geohash tiles for Belgium area"""
    return ['u151', 'u154', 'u155', 'u156']


@pytest.fixture
def coastal_polygon():
    """Coastal polygon for ocean data tests"""
    return Polygon([
        (2.5, 51.0), (3.5, 51.0),
        (3.5, 51.7), (2.5, 51.7), (2.5, 51.0)
    ])


# ==================== Time Range Fixtures ====================

@pytest.fixture
def test_time_range_week():
    """One week time range for testing"""
    return '2020-01-01', '2020-01-07'


@pytest.fixture
def test_time_range_month():
    """One month time range for testing"""
    return '2020-01-01', '2020-01-31'


# ==================== Output Path Fixtures ====================

@pytest.fixture
def data_output_dir(tmp_path):
    """Create a data output directory"""
    output_dir = tmp_path / 'data_output'
    output_dir.mkdir(exist_ok=True)
    return output_dir


@pytest.fixture
def netcdf_output_path(data_output_dir):
    """NetCDF output path"""
    return data_output_dir / 'test_output.nc'


@pytest.fixture
def geotiff_output_path(data_output_dir):
    """GeoTIFF output path"""
    return data_output_dir / 'test_output.tif'


# ==================== Helper Fixtures ====================

@pytest.fixture
def assert_valid_bbox():
    """Helper to assert valid bounding box"""
    def _assert(bbox):
        assert isinstance(bbox, tuple), "Bbox must be a tuple"
        assert len(bbox) == 4, "Bbox must have 4 elements"
        
        lon_min, lat_min, lon_max, lat_max = bbox
        
        assert -180 <= lon_min <= 180, f"Invalid lon_min: {lon_min}"
        assert -180 <= lon_max <= 180, f"Invalid lon_max: {lon_max}"
        assert lon_min < lon_max, "lon_min must be less than lon_max"
        
        assert -90 <= lat_min <= 90, f"Invalid lat_min: {lat_min}"
        assert -90 <= lat_max <= 90, f"Invalid lat_max: {lat_max}"
        assert lat_min < lat_max, "lat_min must be less than lat_max"
        
        return True
    return _assert
