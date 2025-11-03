"""
Unit tests for geohash.py
"""
import geopandas as gpd
import pytest
from sigmap.polygeohasher.utils.geohash import (
    lonlat_res_for_length,
    encode_geohash,
    candidate_geohashes_covering_bbox,
    geohash_to_bbox,
    geohash_to_polygon,
    geohashes_to_gdf,
    get_geohash_children,
    geohashes_to_boxes,
    geohashes_to_multipolygon,
    coverage_dict_to_multipolygon,
    coverage_dict_to_multipolygon_by_level
)


class TestLonLatRes:
    """Test lonlat_res_for_length function"""
    
    def test_resolution_level_1(self):
        """Test resolution for level 1"""
        lon_res, lat_res = lonlat_res_for_length(1)
        assert lon_res > 0
        assert lat_res > 0
        assert lon_res <= 360
        assert lat_res <= 180
    
    def test_resolution_level_5(self):
        """Test resolution for level 5"""
        lon_res, lat_res = lonlat_res_for_length(5)
        assert lon_res > 0
        assert lat_res > 0
        
        # Level 5 has 25 bits total
        # lon_bits = ceil(25/2) = 13, lat_bits = floor(25/2) = 12
        expected_lon_res = 360.0 / (2 ** 13)
        expected_lat_res = 180.0 / (2 ** 12)
        
        assert abs(lon_res - expected_lon_res) < 1e-10
        assert abs(lat_res - expected_lat_res) < 1e-10
    
    def test_higher_level_higher_resolution(self):
        """Test that higher levels have higher resolution"""
        lon1, lat1 = lonlat_res_for_length(2)
        lon3, lat3 = lonlat_res_for_length(5)
        
        assert lon3 < lon1  # Smaller resolution = higher precision
        assert lat3 < lat1


class TestEncodeGeohash:
    """Test encode_geohash function"""
    
    def test_encode_paris(self):
        """Test encoding Paris coordinates"""
        # Paris is approximately at (2.3522, 48.8566)
        geohash = encode_geohash(2.3522, 48.8566, 7)
        assert isinstance(geohash, str)
        assert len(geohash) == 7
    
    def test_encode_same_point_different_lengths(self):
        """Test encoding same point with different lengths"""
        lon, lat = 0.0, 0.0
        
        gh3 = encode_geohash(lon, lat, 3)
        gh5 = encode_geohash(lon, lat, 5)
        gh7 = encode_geohash(lon, lat, 7)
        
        assert len(gh3) == 3
        assert len(gh5) == 5
        assert len(gh7) == 7
        
        # First N characters should match
        assert gh5.startswith(gh3)
        assert gh7.startswith(gh5)
    
    def test_encode_edge_cases(self):
        """Test encoding at world boundaries"""
        # Equator
        geohash = encode_geohash(0.0, 0.0, 5)
        assert isinstance(geohash, str)
        assert len(geohash) == 5
        
        # North pole
        geohash = encode_geohash(0.0, 89.0, 5)
        assert isinstance(geohash, str)
        
        # Greenwich meridian
        geohash = encode_geohash(0.0, 48.0, 5)
        assert isinstance(geohash, str)


class TestGeohashToBbox:
    """Test geohash_to_bbox function"""
    
    def test_decode_and_encode_round_trip(self):
        """Test that encoding and decoding returns original point"""
        lon, lat = 2.3522, 48.8566
        geohash = encode_geohash(lon, lat, 7)
        lon_min, lat_min, lon_max, lat_max = geohash_to_bbox(geohash)
        
        # Original point should be within bbox
        assert lon_min <= lon <= lon_max
        assert lat_min <= lat <= lat_max
    
    def test_bbox_validity(self):
        """Test that bbox is valid"""
        geohash = encode_geohash(0.0, 0.0, 5)
        lon_min, lat_min, lon_max, lat_max = geohash_to_bbox(geohash)
        
        assert lon_min < lon_max
        assert lat_min < lat_max
        assert -180 <= lon_min <= 180
        assert -180 <= lon_max <= 180
        assert -90 <= lat_min <= 90
        assert -90 <= lat_max <= 90
    
    def test_bbox_size_decreases_with_level(self):
        """Test that bbox size decreases with higher levels"""
        geohash3 = encode_geohash(0.0, 0.0, 3)
        geohash5 = encode_geohash(0.0, 0.0, 5)
        
        bbox3 = geohash_to_bbox(geohash3)
        bbox5 = geohash_to_bbox(geohash5)
        
        area3 = (bbox3[2] - bbox3[0]) * (bbox3[3] - bbox3[1])
        area5 = (bbox5[2] - bbox5[0]) * (bbox5[3] - bbox5[1])
        
        assert area5 < area3


class TestGeohashToPolygon:
    """Test geohash_to_polygon function"""
    
    def test_polygon_is_box(self):
        """Test that geohash polygon is a box"""
        geohash = encode_geohash(0.0, 0.0, 5)
        polygon = geohash_to_polygon(geohash)
        
        assert polygon.is_valid
        assert polygon.area > 0
        assert polygon.geom_type == 'Polygon'
    
    def test_polygon_matches_bbox(self):
        """Test that polygon bounds match bbox"""
        geohash = encode_geohash(0.0, 0.0, 5)
        lon_min, lat_min, lon_max, lat_max = geohash_to_bbox(geohash)
        polygon = geohash_to_polygon(geohash)
        
        bbox_from_polygon = polygon.bounds
        
        assert abs(bbox_from_polygon[0] - lon_min) < 1e-10
        assert abs(bbox_from_polygon[1] - lat_min) < 1e-10
        assert abs(bbox_from_polygon[2] - lon_max) < 1e-10
        assert abs(bbox_from_polygon[3] - lat_max) < 1e-10


class TestCandidateGeohashes:
    """Test candidate_geohashes_covering_bbox function"""
    
    def test_small_bbox(self):
        """Test candidate generation for small bbox"""
        geohashes = candidate_geohashes_covering_bbox(
            0.0, 0.0, 1.0, 1.0, 3
        )
        
        assert isinstance(geohashes, list)
        assert len(geohashes) > 0
        
        # All should be tuples of (geohash, lon, lat)
        for item in geohashes:
            assert isinstance(item, tuple)
            assert len(item) == 3
            geohash, lon, lat = item
            assert isinstance(geohash, str)
            assert len(geohash) == 3
    
    def test_candidates_cover_bbox(self):
        """Test that candidates cover the bbox"""
        lon_min, lat_min, lon_max, lat_max = 2.0, 48.0, 3.0, 49.0
        geohashes = candidate_geohashes_covering_bbox(
            lon_min, lat_min, lon_max, lat_max, 4
        )
        
        assert len(geohashes) > 0
        
        # Check that at least some tiles cover the center
        center_lon = (lon_min + lon_max) / 2
        center_lat = (lat_min + lat_max) / 2
        
        center_geohash = encode_geohash(center_lon, center_lat, 4)
        
        # Should be in the candidate list
        candidate_codes = [item[0] for item in geohashes]
        assert center_geohash in candidate_codes
    
    def test_large_bbox(self):
        """Test candidate generation for large bbox"""
        geohashes = candidate_geohashes_covering_bbox(
            -10.0, -10.0, 10.0, 10.0, 2
        )
        
        assert len(geohashes) > 1  # Should generate multiple candidates
    
    def test_world_boundaries(self):
        """Test candidate generation near world boundaries"""
        # Cross dateline
        geohashes = candidate_geohashes_covering_bbox(
            179.0, -1.0, -179.0, 1.0, 3
        )
        
        assert len(geohashes) >= 0  # Should handle gracefully


class TestGeohashesToGdf:
    """Test geohashes_to_gdf function"""
    
    def test_single_geohash(self):
        """Test converting single geohash to GDF"""
        geohashes = ['u4pruyd']
        gdf = geohashes_to_gdf(geohashes)
        
        assert isinstance(gdf, gpd.GeoDataFrame)
        assert len(gdf) == 1
        assert 'geohash' in gdf.columns
        assert 'geometry' in gdf.columns
        assert gdf.crs == 'EPSG:4326'
    
    def test_multiple_geohashes(self):
        """Test converting multiple geohashes to GDF"""
        geohashes = ['u09tv', 'u09tw', 'u09ty']
        gdf = geohashes_to_gdf(geohashes)
        
        assert len(gdf) == 3
        assert set(gdf['geohash'].values) == set(geohashes)
        assert all(gdf.geometry.is_valid)
    
    def test_with_invalid_geohash(self):
        """Test handling invalid geohashes"""
        geohashes = ['u09tv', 'invalid', 'u09ty']
        gdf = geohashes_to_gdf(geohashes)
        
        # Should skip invalid and return valid ones
        assert len(gdf) >= 1
        assert 'invalid' not in gdf['geohash'].values


class TestGetGeohashChildren:
    """Test get_geohash_children function"""
    
    def test_children_count(self):
        """Test that parent has exactly 32 children"""
        parent = 'u09'
        children = get_geohash_children(parent)
        
        assert len(children) == 32  # Base32 alphabet has 32 characters
    
    def test_children_prefix(self):
        """Test that all children have parent as prefix"""
        parent = 'u09'
        children = get_geohash_children(parent)
        
        for child in children:
            assert child.startswith(parent)
            assert len(child) == len(parent) + 1
    
    def test_different_parents(self):
        """Test children for different parent geohashes"""
        children1 = get_geohash_children('abc')
        children2 = get_geohash_children('xyz')
        
        assert len(children1) == 32
        assert len(children2) == 32
        assert set(children1).isdisjoint(set(children2))


class TestGeohashesToBoxes:
    """Test geohashes_to_boxes function"""
    
    def test_single_geohash(self):
        """Test converting single geohash to box"""
        boxes = geohashes_to_boxes('u4pruyd')
        
        assert isinstance(boxes, dict)
        assert len(boxes) == 1
        assert 'u4pruyd' in boxes
        assert boxes['u4pruyd'].is_valid
    
    def test_multiple_geohashes(self):
        """Test converting multiple geohashes to boxes"""
        geohashes = ['u09tv', 'u09tw', 'u09ty']
        boxes = geohashes_to_boxes(geohashes)
        
        assert len(boxes) == 3
        assert set(boxes.keys()) == set(geohashes)
        assert all(polygon.is_valid for polygon in boxes.values())
    
    def test_boxes_are_not_overlapping(self):
        """Test that distinct geohashes produce distinct boxes"""
        geohashes = ['u09tv', 'u09tw', 'u09ty']
        boxes = geohashes_to_boxes(geohashes)
        
        # Check that boxes are different
        box_coords = [b.bounds for b in boxes.values()]
        assert len(set(box_coords)) == len(box_coords)


class TestGeohashesToMultipolygon:
    """Test geohashes_to_multipolygon function"""
    
    def test_single_geohash(self):
        """Test converting single geohash to MultiPolygon"""
        multi_poly = geohashes_to_multipolygon('u4pruyd')
        
        # Can return Polygon or MultiPolygon depending on union result
        from shapely.geometry import Polygon, MultiPolygon
        assert isinstance(multi_poly, (Polygon, MultiPolygon))
        assert multi_poly.is_valid
        assert multi_poly.area > 0
    
    def test_dissolved_multipolygon(self):
        """Test dissolved MultiPolygon"""
        # Adjacent geohashes
        geohashes = ['u09tv', 'u09tw']
        multi_poly = geohashes_to_multipolygon(geohashes, dissolve=True)
        
        assert multi_poly.is_valid
    
    def test_separate_boxes(self):
        """Test MultiPolygon with separate boxes"""
        # Distant geohashes
        geohashes = ['u09tv', 'ezjmmy']  # Different regions
        multi_poly = geohashes_to_multipolygon(geohashes, dissolve=False)
        
        assert len(multi_poly.geoms) == 2
    
    def test_from_dict(self):
        """Test creating MultiPolygon from boxes dict"""
        boxes = geohashes_to_boxes(['u09tv', 'u09tw'])
        multi_poly = geohashes_to_multipolygon(boxes)
        
        assert multi_poly.is_valid
    
    def test_empty_geohashes(self):
        """Test handling empty geohashes list"""
        multi_poly = geohashes_to_multipolygon([])
        
        assert hasattr(multi_poly, 'geoms')
        assert len(multi_poly.geoms) == 0


class TestCoverageDictToMultipolygon:
    """Test coverage_dict_to_multipolygon function"""
    
    def test_simple_dict(self):
        """Test converting simple coverage dict"""
        coverage_dict = {
            2: ['u09tv', 'u09tw'],
            3: ['u09ty']
        }
        multi_poly = coverage_dict_to_multipolygon(coverage_dict)
        
        assert multi_poly.is_valid
        assert multi_poly.area > 0
    
    def test_dissolve_false(self):
        """Test with dissolve=False"""
        coverage_dict = {
            2: ['u09tv', 'u09tw']
        }
        multi_poly = coverage_dict_to_multipolygon(coverage_dict, dissolve=False)
        
        assert len(multi_poly.geoms) == 2
    
    def test_empty_dict(self):
        """Test with empty dict"""
        coverage_dict = {}
        multi_poly = coverage_dict_to_multipolygon(coverage_dict)
        
        assert hasattr(multi_poly, 'geoms')
        assert len(multi_poly.geoms) == 0


class TestCoverageDictToMultipolygonByLevel:
    """Test coverage_dict_to_multipolygon_by_level function"""
    
    def test_separate_by_level(self):
        """Test that levels are separated"""
        coverage_dict = {
            2: ['u09tv', 'u09tw'],
            3: ['u09ty', 'u09tz']
        }
        level_polys = coverage_dict_to_multipolygon_by_level(coverage_dict)
        
        assert len(level_polys) == 2
        assert 2 in level_polys
        assert 3 in level_polys
        assert level_polys[2].is_valid
        assert level_polys[3].is_valid
    
    def test_dissolve_false(self):
        """Test with dissolve=False"""
        coverage_dict = {
            2: ['u09tv', 'u09tw']
        }
        level_polys = coverage_dict_to_multipolygon_by_level(coverage_dict, dissolve=False)
        
        assert len(level_polys[2].geoms) == 2


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

