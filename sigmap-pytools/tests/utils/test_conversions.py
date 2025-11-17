import pytest
from shapely.geometry import Polygon, MultiPolygon, Point

from sigmap.utils.conversion import geojson_to_shape, shape_to_geojson


# --- Fixtures -----------------------------------------------------------------

@pytest.fixture
def single_polygon_geojson():
    """Simple square polygon"""
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]
                    ]
                }
            }
        ]
    }


@pytest.fixture
def polygon_with_hole_geojson():
    """Polygon with an interior hole"""
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        # Exterior ring
                        [[0, 0], [10, 0], [10, 10], [0, 10], [0, 0]],
                        # Interior hole
                        [[2, 2], [8, 2], [8, 8], [2, 8], [2, 2]]
                    ]
                }
            }
        ]
    }


@pytest.fixture
def two_separate_polygons_geojson():
    """Two non-touching polygons"""
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]]
                }
            },
            {
                "type": "Feature",
                "properties": {},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[3, 3], [4, 3], [4, 4], [3, 4], [3, 3]]]
                }
            }
        ]
    }


@pytest.fixture
def two_touching_polygons_geojson():
    """Two polygons that share an edge"""
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]]
                }
            },
            {
                "type": "Feature",
                "properties": {},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[1, 0], [2, 0], [2, 1], [1, 1], [1, 0]]]
                }
            }
        ]
    }


@pytest.fixture
def overlapping_polygons_geojson():
    """Two polygons that overlap"""
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[0, 0], [2, 0], [2, 2], [0, 2], [0, 0]]]
                }
            },
            {
                "type": "Feature",
                "properties": {},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[1, 1], [3, 1], [3, 3], [1, 3], [1, 1]]]
                }
            }
        ]
    }


@pytest.fixture
def multipolygon_feature_geojson():
    """Single feature containing a MultiPolygon"""
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {},
                "geometry": {
                    "type": "MultiPolygon",
                    "coordinates": [
                        [[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]],
                        [[[3, 3], [4, 3], [4, 4], [3, 4], [3, 3]]]
                    ]
                }
            }
        ]
    }


@pytest.fixture
def complex_multifeature_geojson():
    """Mix of Polygon and MultiPolygon features"""
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]]
                }
            },
            {
                "type": "Feature",
                "properties": {},
                "geometry": {
                    "type": "MultiPolygon",
                    "coordinates": [
                        [[[3, 3], [4, 3], [4, 4], [3, 4], [3, 3]]],
                        [[[5, 5], [6, 5], [6, 6], [5, 6], [5, 5]]]
                    ]
                }
            }
        ]
    }


# --- Basic Conversion Tests ---------------------------------------------------

def test_single_polygon_returns_polygon(single_polygon_geojson):
    geom = geojson_to_shape(single_polygon_geojson)
    assert isinstance(geom, Polygon)
    assert geom.is_valid


def test_polygon_with_hole_preserved(polygon_with_hole_geojson):
    geom = geojson_to_shape(polygon_with_hole_geojson)
    assert isinstance(geom, Polygon)
    assert len(geom.interiors) == 1
    assert geom.is_valid


def test_multipolygon_feature_returns_multipolygon(multipolygon_feature_geojson):
    geom = geojson_to_shape(multipolygon_feature_geojson)
    assert isinstance(geom, MultiPolygon)
    assert len(geom.geoms) == 2


# --- Multiple Feature Merging Tests -------------------------------------------

def test_two_separate_polygons_merge_to_multipolygon(two_separate_polygons_geojson):
    geom = geojson_to_shape(two_separate_polygons_geojson, merge_features=True)
    assert isinstance(geom, MultiPolygon)
    assert len(geom.geoms) == 2


def test_two_touching_polygons_merge_to_single_polygon(two_touching_polygons_geojson):
    """Touching polygons should merge into one Polygon"""
    geom = geojson_to_shape(two_touching_polygons_geojson, merge_features=True)
    assert isinstance(geom, Polygon)
    assert geom.is_valid


def test_overlapping_polygons_merge_to_single_polygon(overlapping_polygons_geojson):
    """Overlapping polygons should merge into one Polygon"""
    geom = geojson_to_shape(overlapping_polygons_geojson, merge_features=True)
    assert isinstance(geom, Polygon)
    assert geom.area < 8  # Less than sum of both original areas


def test_no_merge_returns_multipolygon(two_separate_polygons_geojson):
    geom = geojson_to_shape(two_separate_polygons_geojson, merge_features=False)
    assert isinstance(geom, MultiPolygon)
    assert len(geom.geoms) == 2


def test_complex_multifeature_no_merge(complex_multifeature_geojson):
    """Should flatten all polygons into a single MultiPolygon"""
    geom = geojson_to_shape(complex_multifeature_geojson, merge_features=False)
    assert isinstance(geom, MultiPolygon)
    assert len(geom.geoms) == 3  # 1 Polygon + 2 from MultiPolygon


# --- Shape to GeoJSON Tests ---------------------------------------------------

def test_polygon_to_geojson(single_polygon_geojson):
    poly = geojson_to_shape(single_polygon_geojson)
    geo = shape_to_geojson(poly)

    assert len(geo["features"]) == 1
    assert geo["features"][0]["geometry"]["type"] == "Polygon"


def test_multipolygon_to_geojson_no_split(two_separate_polygons_geojson):
    geom = geojson_to_shape(two_separate_polygons_geojson, merge_features=True)
    geo = shape_to_geojson(geom, split_multipolygons=False)

    assert len(geo["features"]) == 1
    assert geo["features"][0]["geometry"]["type"] == "MultiPolygon"


def test_multipolygon_to_geojson_split(two_separate_polygons_geojson):
    geom = geojson_to_shape(two_separate_polygons_geojson, merge_features=True)
    geo = shape_to_geojson(geom, split_multipolygons=True)

    assert len(geo["features"]) == 2
    assert all(f["geometry"]["type"] == "Polygon" for f in geo["features"])


def test_polygon_with_hole_to_geojson(polygon_with_hole_geojson):
    poly = geojson_to_shape(polygon_with_hole_geojson)
    geo = shape_to_geojson(poly)

    coords = geo["features"][0]["geometry"]["coordinates"]
    assert len(coords) == 2  # Exterior + 1 hole
    assert len(coords[0]) == 5  # Exterior ring
    assert len(coords[1]) == 5  # Interior ring


# --- Round Trip Tests ---------------------------------------------------------

def test_round_trip_simple_polygon(single_polygon_geojson):
    geom1 = geojson_to_shape(single_polygon_geojson)
    geo = shape_to_geojson(geom1)
    geom2 = geojson_to_shape(geo)

    assert geom2.equals(geom1)


def test_round_trip_polygon_with_hole(polygon_with_hole_geojson):
    geom1 = geojson_to_shape(polygon_with_hole_geojson)
    geo = shape_to_geojson(geom1)
    geom2 = geojson_to_shape(geo)

    assert geom2.equals(geom1)
    assert len(geom2.interiors) == len(geom1.interiors)


def test_round_trip_multipolygon_no_split(two_separate_polygons_geojson):
    geom1 = geojson_to_shape(two_separate_polygons_geojson, merge_features=True)
    geo = shape_to_geojson(geom1, split_multipolygons=False)
    geom2 = geojson_to_shape(geo)

    assert geom2.equals(geom1)


def test_round_trip_multipolygon_split(two_separate_polygons_geojson):
    geom1 = geojson_to_shape(two_separate_polygons_geojson, merge_features=True)
    geo = shape_to_geojson(geom1, split_multipolygons=True)
    geom2 = geojson_to_shape(geo, merge_features=False)

    assert geom2.equals(geom1)


# --- Error Handling Tests -----------------------------------------------------

def test_empty_features_raises_error():
    with pytest.raises(ValueError, match="GeoJSON has no features"):
        geojson_to_shape({"type": "FeatureCollection", "features": []})


def test_invalid_geometry_type_raises_error():
    invalid_geojson = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {},
                "geometry": {
                    "type": "Point",
                    "coordinates": [0, 0]
                }
            }
        ]
    }
    with pytest.raises(ValueError, match="Feature must be Polygon or MultiPolygon"):
        geojson_to_shape(invalid_geojson)


def test_shape_to_geojson_invalid_type_raises_error():
    point = Point(0, 0)
    with pytest.raises(ValueError, match="Input geometry must be Polygon or MultiPolygon"):
        shape_to_geojson(point)


def test_missing_features_key():
    with pytest.raises(ValueError):
        geojson_to_shape({"type": "FeatureCollection"})


# --- Area and Validity Tests --------------------------------------------------

def test_merged_polygon_area_correct(overlapping_polygons_geojson):
    """Test that merged overlapping polygons have correct area"""
    geom = geojson_to_shape(overlapping_polygons_geojson, merge_features=True)
    # Two 2x2 squares overlapping by 1x1 = 4 + 4 - 1 = 7
    assert abs(geom.area - 7.0) < 0.001


def test_all_geometries_valid(complex_multifeature_geojson):
    """Ensure all converted geometries are valid"""
    geom = geojson_to_shape(complex_multifeature_geojson, merge_features=False)
    assert geom.is_valid
    assert all(poly.is_valid for poly in geom.geoms)


# --- Properties Preservation Tests --------------------------------------------

def test_feature_count_preserved_no_merge(two_separate_polygons_geojson):
    """Verify feature count matches when not merging"""
    original_count = len(two_separate_polygons_geojson["features"])
    geom = geojson_to_shape(two_separate_polygons_geojson, merge_features=False)
    geo = shape_to_geojson(geom, split_multipolygons=True)

    assert len(geo["features"]) == original_count


def test_coordinate_precision_preserved(single_polygon_geojson):
    """Test that coordinate precision is maintained through conversion"""
    geom = geojson_to_shape(single_polygon_geojson)
    geo = shape_to_geojson(geom)

    original_coords = single_polygon_geojson["features"][0]["geometry"]["coordinates"][0]
    result_coords = geo["features"][0]["geometry"]["coordinates"][0]

    assert len(original_coords) == len(result_coords)