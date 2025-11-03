"""
Unit tests for algorithms.py
"""
import pytest
from shapely.geometry import box, Polygon
from shapely.prepared import prep
import geopandas as gpd
from sigmap.polygeohasher.utils.algorithms import check_tile_coverage_with_prepared, SRTree

class TestCheckTileCoverage:
    """Test suite for check_tile_coverage_with_prepared function"""
    
    def test_full_coverage(self):
        """Test when tile is fully inside country"""
        tile = box(0, 0, 1, 1)
        country = box(-1, -1, 2, 2)
        prepared_country = prep(country)
        result = check_tile_coverage_with_prepared(tile, country, prepared_country, threshold=0.95)
        assert result == 'full'
    
    def test_no_coverage(self):
        """Test when tile doesn't intersect country"""
        tile = box(0, 0, 1, 1)
        country = box(5, 5, 6, 6)
        prepared_country = prep(country)
        result = check_tile_coverage_with_prepared(tile, country, prepared_country, threshold=0.95)
        assert result == 'none'
    
    def test_partial_coverage(self):
        """Test when tile is partially inside country"""
        tile = box(0, 0, 2, 2)
        country = box(1, 1, 3, 3)
        prepared_country = prep(country)
        result = check_tile_coverage_with_prepared(tile, country, prepared_country, threshold=0.95)
        assert result == 'partial'
    
    def test_threshold_boundary(self):
        """Test coverage at threshold boundary"""
        tile = box(0, 0, 10, 10)
        # Cover exactly 95% of tile
        country = box(0, 0, 10, 9.5)
        prepared_country = prep(country)
        result = check_tile_coverage_with_prepared(tile, country, prepared_country, threshold=0.95)
        assert result == 'full'
        
        # Cover slightly less than 95%
        country = box(0, 0, 10, 9.4)
        prepared_country = prep(country)
        result = check_tile_coverage_with_prepared(tile, country, prepared_country, threshold=0.95)
        assert result == 'partial'
    
    def test_invalid_geometries(self):
        """Test handling of invalid geometries"""
        # Create invalid geometry (self-intersecting polygon)
        invalid_tile = Polygon([(0, 0), (2, 2), (2, 0), (0, 2), (0, 0)])
        country = box(-1, -1, 3, 3)
        prepared_country = prep(country)
        # Should not raise exception, handle gracefully
        result = check_tile_coverage_with_prepared(invalid_tile, country, prepared_country)
        assert result in ['full', 'partial', 'none']
    
    def test_zero_area_tile(self):
        """Test handling of zero-area tile"""
        tile = box(0, 0, 0, 0)  # Point
        country = box(-1, -1, 1, 1)
        prepared_country = prep(country)
        result = check_tile_coverage_with_prepared(tile, country, prepared_country)
        assert result == 'none'
    
    def test_custom_threshold(self):
        """Test with custom threshold values"""
        tile = box(0, 0, 10, 10)
        country = box(0, 0, 10, 8)  # 80% coverage
        prepared_country = prep(country)
        
        result = check_tile_coverage_with_prepared(tile, country, prepared_country, threshold=0.75)
        assert result == 'full'
        
        result = check_tile_coverage_with_prepared(tile, country, prepared_country, threshold=0.85)
        assert result == 'partial'
    
    def test_touching_geometries(self):
        """Test when geometries only touch at boundary"""
        tile = box(0, 0, 1, 1)
        country = box(1, 0, 2, 1)  # Shares edge
        prepared_country = prep(country)
        result = check_tile_coverage_with_prepared(tile, country, prepared_country)
        # Touching is not intersection in terms of area
        assert result == 'none'
    
    def test_complex_polygon(self):
        """Test with complex polygon shapes"""
        tile = box(0, 0, 4, 4)
        # L-shaped country
        country = Polygon([
            (0, 0), (2, 0), (2, 2), (4, 2), 
            (4, 4), (0, 4), (0, 0)
        ])
        prepared_country = prep(country)
        result = check_tile_coverage_with_prepared(tile, country, prepared_country, threshold=0.95)
        assert result in ['full', 'partial']


class TestSRTree:
    """Test suite for SRTree function"""
    
    def test_basic_intersection(self):
        """Test basic spatial tree query"""
        # Create test tiles
        tiles = [
            box(0, 0, 1, 1),
            box(1, 1, 2, 2),
            box(5, 5, 6, 6)
        ]
        tiles_gdf = gpd.GeoDataFrame(
            {'id': [1, 2, 3]},
            geometry=tiles,
            crs='EPSG:4326'
        )
        
        country = box(0.5, 0.5, 1.5, 1.5)
        result = SRTree(tiles_gdf, country)
        
        assert len(result) == 2  # Should find first two tiles
        assert 3 not in result['id'].values
    
    def test_no_intersection(self):
        """Test when no tiles intersect"""
        tiles = [box(0, 0, 1, 1), box(1, 1, 2, 2)]
        tiles_gdf = gpd.GeoDataFrame(
            geometry=tiles,
            crs='EPSG:4326'
        )
        
        country = box(10, 10, 11, 11)
        result = SRTree(tiles_gdf, country)
        
        assert len(result) == 0
    
    def test_all_tiles_intersect(self):
        """Test when all tiles intersect"""
        tiles = [box(i, i, i+1, i+1) for i in range(3)]
        tiles_gdf = gpd.GeoDataFrame(
            geometry=tiles,
            crs='EPSG:4326'
        )
        
        country = box(-1, -1, 5, 5)
        result = SRTree(tiles_gdf, country)
        
        assert len(result) == 3
    
    def test_invalid_geometries_filtered(self):
        """Test that invalid geometries are filtered out"""
        # Mix of valid and invalid geometries
        tiles = [
            box(0, 0, 1, 1),
            Polygon([(0, 0), (2, 2), (2, 0), (0, 2), (0, 0)]),  # Invalid
            box(2, 2, 3, 3)
        ]
        tiles_gdf = gpd.GeoDataFrame(
            geometry=tiles,
            crs='EPSG:4326'
        )
        
        country = box(-1, -1, 4, 4)
        result = SRTree(tiles_gdf, country)
        
        # Should only process valid geometries
        assert len(result) >= 1
    
    def test_empty_geodataframe(self):
        """Test with empty GeoDataFrame"""
        tiles_gdf = gpd.GeoDataFrame(
            geometry=[],
            crs='EPSG:4326'
        )
        
        country = box(0, 0, 1, 1)
        result = SRTree(tiles_gdf, country)
        
        assert len(result) == 0
    
    def test_preserves_attributes(self):
        """Test that non-geometry attributes are preserved"""
        tiles = [box(i, i, i+1, i+1) for i in range(3)]
        tiles_gdf = gpd.GeoDataFrame({
            'id': [1, 2, 3],
            'name': ['A', 'B', 'C'],
            'geometry': tiles
        }, crs='EPSG:4326')
        
        country = box(0.5, 0.5, 1.5, 1.5)
        result = SRTree(tiles_gdf, country)
        
        assert 'id' in result.columns
        assert 'name' in result.columns
        assert 'geometry' in result.columns
    
    def test_large_dataset_performance(self):
        """Test with larger dataset to verify spatial index efficiency"""
        # Create grid of 100 tiles
        tiles = [box(i%10, i//10, (i%10)+1, (i//10)+1) for i in range(100)]
        tiles_gdf = gpd.GeoDataFrame(
            {'id': range(100)},
            geometry=tiles,
            crs='EPSG:4326'
        )
        
        country = box(2, 2, 4, 4)
        result = SRTree(tiles_gdf, country)
        
        # Should efficiently find only intersecting tiles
        assert 0 < len(result) < 100
        # Verify results are actually intersecting
        for geom in result.geometry:
            assert geom.intersects(country)


class TestCoverageEdgeCases:
    """Test edge cases for coverage calculations"""
    
    def test_multipolygon_country(self):
        """Test with MultiPolygon country (e.g., islands)"""
        from shapely.geometry import MultiPolygon
        
        tile = box(0, 0, 5, 5)
        island1 = box(1, 1, 2, 2)
        island2 = box(3, 3, 4, 4)
        country = MultiPolygon([island1, island2])
        prepared_country = prep(country)
        
        result = check_tile_coverage_with_prepared(tile, country, prepared_country, threshold=0.95)
        assert result == 'partial'
    
    def test_very_small_intersection(self):
        """Test with very small intersection area"""
        tile = box(0, 0, 100, 100)
        country = box(99.9, 99.9, 100.1, 100.1)
        prepared_country = prep(country)
        
        result = check_tile_coverage_with_prepared(tile, country, prepared_country, threshold=0.95)
        assert result == 'partial'
    
    def test_concave_polygon(self):
        """Test with concave polygon"""
        tile = box(0, 0, 4, 4)
        # C-shaped polygon
        country = Polygon([
            (0, 0), (4, 0), (4, 1), (1, 1),
            (1, 3), (4, 3), (4, 4), (0, 4), (0, 0)
        ])
        prepared_country = prep(country)
        
        result = check_tile_coverage_with_prepared(tile, country, prepared_country)
        assert result in ['full', 'partial']


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
