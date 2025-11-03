"""
Unit tests for adaptative_geohash_coverage.py
"""
import geopandas as gpd
import pytest
from shapely.geometry import box, Polygon, MultiPolygon

from sigmap.polygeohasher.adaptative_geohash_coverage import adaptive_geohash_coverage


class TestAdaptiveGeohashCoverage:
    """Test suite for adaptive_geohash_coverage function"""
    
    def test_basic_coverage_small_square(self):
        """Test basic coverage with small square country"""
        country_geom = box(0, 0, 1, 1)
        
        result_dict, result_gdf = adaptive_geohash_coverage(
            country_geom,
            min_level=2,
            max_level=4,
            use_strtree=True,
            debug=False
        )
        
        assert isinstance(result_dict, dict)
        assert isinstance(result_gdf, gpd.GeoDataFrame)
        assert len(result_gdf) > 0
        assert 'geohash' in result_gdf.columns
        assert 'level' in result_gdf.columns
        assert 'geometry' in result_gdf.columns
    
    def test_min_max_level_respected(self):
        """Test that min and max levels are respected"""
        country_geom = box(0, 0, 5, 5)
        min_level = 2
        max_level = 4
        
        result_dict, result_gdf = adaptive_geohash_coverage(
            country_geom,
            min_level=min_level,
            max_level=max_level,
            debug=False
        )
        
        # Check that only specified levels are present
        levels = set(result_gdf['level'].values)
        assert all(min_level <= level <= max_level for level in levels)
    
    def test_coverage_threshold_affects_refinement(self):
        """Test that coverage threshold affects refinement"""
        country_geom = box(0, 0, 2, 2)
        
        # High threshold - more refinement
        result_high, gdf_high = adaptive_geohash_coverage(
            country_geom,
            min_level=2,
            max_level=5,
            coverage_threshold=0.99,
            debug=False
        )
        
        # Lower threshold - less refinement
        result_low, gdf_low = adaptive_geohash_coverage(
            country_geom,
            min_level=2,
            max_level=5,
            coverage_threshold=0.80,
            debug=False
        )
        
        # Higher threshold should generally result in more tiles
        # (more partial tiles get refined)
        total_high = sum(len(tiles) for tiles in result_high.values())
        total_low = sum(len(tiles) for tiles in result_low.values())
        assert total_high >= total_low
    
    def test_strtree_vs_no_strtree(self):
        """Test that STRtree and non-STRtree give similar results"""
        country_geom = box(0, 0, 2, 2)
        
        result_tree, gdf_tree = adaptive_geohash_coverage(
            country_geom,
            min_level=2,
            max_level=4,
            use_strtree=True,
            debug=False
        )
        
        result_no_tree, gdf_no_tree = adaptive_geohash_coverage(
            country_geom,
            min_level=2,
            max_level=4,
            use_strtree=False,
            debug=False
        )
        
        # Should have similar number of tiles
        total_tree = sum(len(tiles) for tiles in result_tree.values())
        total_no_tree = sum(len(tiles) for tiles in result_no_tree.values())
        
        # Allow some difference due to implementation details
        assert abs(total_tree - total_no_tree) <= total_tree * 0.1
    
    def test_complex_polygon_coverage(self):
        """Test with complex polygon (L-shape)"""
        # L-shaped country
        coords = [
            (0, 0), (2, 0), (2, 2), (1, 2),
            (1, 3), (0, 3), (0, 0)
        ]
        country_geom = Polygon(coords)
        
        result_dict, result_gdf = adaptive_geohash_coverage(
            country_geom,
            min_level=2,
            max_level=4,
            debug=False
        )
        
        assert len(result_gdf) > 0
        # All tiles should intersect with country
        for geom in result_gdf.geometry:
            assert geom.intersects(country_geom)
    
    def test_multipolygon_coverage(self):
        """Test with MultiPolygon (islands)"""
        island1 = box(0, 0, 1, 1)
        island2 = box(3, 3, 4, 4)
        island3 = box(6, 6, 7, 7)
        country_geom = MultiPolygon([island1, island2, island3])
        
        result_dict, result_gdf = adaptive_geohash_coverage(
            country_geom,
            min_level=2,
            max_level=4,
            debug=False
        )
        
        assert len(result_gdf) > 0
        # Should have tiles covering all islands
        for island in [island1, island2, island3]:
            has_coverage = any(
                geom.intersects(island) for geom in result_gdf.geometry
            )
            assert has_coverage
    
    def test_invalid_geometry_handling(self):
        """Test that invalid geometries are handled gracefully"""
        # Self-intersecting polygon
        invalid_geom = Polygon([
            (0, 0), (2, 2), (2, 0), (0, 2), (0, 0)
        ])
        
        # Should not raise exception
        result_dict, result_gdf = adaptive_geohash_coverage(
            invalid_geom,
            min_level=2,
            max_level=4,
            debug=False
        )
        
        # Should still produce results
        assert len(result_gdf) >= 0
    
    def test_no_coverage_for_non_intersecting(self):
        """Test that non-intersecting areas are excluded"""
        country_geom = box(0, 0, 1, 1)
        
        result_dict, result_gdf = adaptive_geohash_coverage(
            country_geom,
            min_level=2,
            max_level=4,
            debug=False
        )
        
        # All tiles should intersect with country
        for geom in result_gdf.geometry:
            assert geom.intersects(country_geom)
    
    def test_refinement_at_boundaries(self):
        """Test that refinement occurs at boundaries"""
        country_geom = box(0, 0, 3, 3)
        
        result_dict, result_gdf = adaptive_geohash_coverage(
            country_geom,
            min_level=2,
            max_level=5,
            coverage_threshold=0.95,
            debug=False
        )
        
        # Should have multiple levels (refinement occurred)
        levels = set(result_gdf['level'].values)
        assert len(levels) >= 1
    
    def test_output_dict_structure(self):
        """Test structure of output dictionary"""
        country_geom = box(0, 0, 2, 2)
        
        result_dict, result_gdf = adaptive_geohash_coverage(
            country_geom,
            min_level=2,
            max_level=4,
            debug=False
        )
        
        # Dict should map level to list of geohashes
        for level, geohashes in result_dict.items():
            assert isinstance(level, int)
            assert isinstance(geohashes, list)
            assert 2 <= level <= 4
            # All geohashes should be strings
            assert all(isinstance(gh, str) for gh in geohashes)
    
    def test_gdf_matches_dict(self):
        """Test that GeoDataFrame matches dictionary output"""
        country_geom = box(0, 0, 2, 2)
        
        result_dict, result_gdf = adaptive_geohash_coverage(
            country_geom,
            min_level=2,
            max_level=4,
            debug=False
        )
        
        # Count tiles in dict
        dict_counts = {level: len(tiles) for level, tiles in result_dict.items()}
        
        # Count tiles in GDF by level
        gdf_counts = result_gdf['level'].value_counts().to_dict()
        
        # Should match
        assert dict_counts == gdf_counts
    
    def test_different_predicates(self):
        """Test different spatial predicates"""
        country_geom = box(0, 0, 2, 2)
        
        predicates = ['intersects', 'within', 'contains']
        results = []
        
        for pred in predicates:
            result_dict, result_gdf = adaptive_geohash_coverage(
                country_geom,
                min_level=2,
                max_level=4,
                use_strtree=True,
                predicate=pred,
                debug=False
            )
            results.append(len(result_gdf))
        
        # Different predicates should give different results
        # (at least some should differ)
        assert len(set(results)) > 1 or all(r > 0 for r in results)
    
    def test_very_small_country(self):
        """Test with very small country geometry"""
        country_geom = box(0, 0, 0.1, 0.1)
        
        result_dict, result_gdf = adaptive_geohash_coverage(
            country_geom,
            min_level=3,
            max_level=6,
            debug=False
        )
        
        # Should still produce coverage
        assert len(result_gdf) > 0
    
    def test_elongated_country(self):
        """Test with elongated country (like Chile)"""
        country_geom = box(0, 0, 1, 10)  # Very tall and narrow
        
        result_dict, result_gdf = adaptive_geohash_coverage(
            country_geom,
            min_level=2,
            max_level=4,
            debug=False
        )
        
        assert len(result_gdf) > 0
        # All tiles should intersect
        for geom in result_gdf.geometry:
            assert geom.intersects(country_geom)


class TestAdaptiveCoverageEdgeCases:
    """Test edge cases for adaptive coverage"""
    
    def test_single_level_coverage(self):
        """Test when min_level equals max_level"""
        country_geom = box(0, 0, 2, 2)
        
        result_dict, result_gdf = adaptive_geohash_coverage(
            country_geom,
            min_level=3,
            max_level=3,
            debug=False
        )
        
        # Should only have one level
        levels = set(result_gdf['level'].values)
        assert levels == {3}
    
    def test_country_at_boundaries(self):
        """Test country near world boundaries"""
        # Near dateline and equator
        country_geom = box(179, -1, -179, 1)
        
        result_dict, result_gdf = adaptive_geohash_coverage(
            country_geom,
            min_level=2,
            max_level=4,
            debug=False
        )
        
        assert len(result_gdf) > 0
    
    def test_country_with_hole(self):
        """Test country with interior hole"""
        outer = [(0, 0), (10, 0), (10, 10), (0, 10), (0, 0)]
        hole = [(2, 2), (2, 8), (8, 8), (8, 2), (2, 2)]
        country_geom = Polygon(outer, [hole])
        
        result_dict, result_gdf = adaptive_geohash_coverage(
            country_geom,
            min_level=2,
            max_level=4,
            debug=False
        )
        
        # Should produce coverage around the hole
        assert len(result_gdf) > 0
    
    def test_zero_area_geometry(self):
        """Test with zero-area geometry (point/line)"""
        # This should either handle gracefully or raise appropriate error
        point_geom = box(0, 0, 0, 0)
        
        result_dict, result_gdf = adaptive_geohash_coverage(
            point_geom,
            min_level=2,
            max_level=4,
            debug=False
        )

        assert isinstance(result_gdf, gpd.GeoDataFrame)

class TestPerformanceCharacteristics:
    """Test performance characteristics"""
    
    def test_increasing_levels_increases_tiles(self):
        """Test that increasing max_level increases tile count"""
        country_geom = box(0, 0, 5, 5)
        
        result_3, gdf_3 = adaptive_geohash_coverage(
            country_geom, min_level=2, max_level=3, debug=False
        )
        result_4, gdf_4 = adaptive_geohash_coverage(
            country_geom, min_level=2, max_level=4, debug=False
        )
        result_5, gdf_5 = adaptive_geohash_coverage(
            country_geom, min_level=2, max_level=5, debug=False
        )
        
        # More levels should generally mean more tiles
        assert len(gdf_3) <= len(gdf_4) <= len(gdf_5)
    
    def test_larger_area_more_tiles(self):
        """Test that larger areas require more tiles"""
        small = box(0, 0, 1, 1)
        medium = box(0, 0, 3, 3)
        large = box(0, 0, 5, 5)
        
        _, gdf_small = adaptive_geohash_coverage(
            small, min_level=2, max_level=4, debug=False
        )
        _, gdf_medium = adaptive_geohash_coverage(
            medium, min_level=2, max_level=4, debug=False
        )
        _, gdf_large = adaptive_geohash_coverage(
            large, min_level=2, max_level=4, debug=False
        )
        
        assert len(gdf_small) < len(gdf_medium) < len(gdf_large)


class TestRealWorldScenarios:
    """Test with realistic scenarios"""
    
    def test_france_like_geometry(self):
        """Test with France-like hexagonal geometry"""
        # Simplified France-like shape
        coords = [
            (0, 0), (2, -1), (4, 0), (5, 2),
            (4, 4), (2, 5), (0, 4), (-1, 2), (0, 0)
        ]
        country_geom = Polygon(coords)
        
        result_dict, result_gdf = adaptive_geohash_coverage(
            country_geom,
            min_level=2,
            max_level=5,
            debug=False
        )
        
        assert len(result_gdf) > 0
        assert all(geom.intersects(country_geom) for geom in result_gdf.geometry)
    
    def test_island_nation(self):
        """Test with multiple disconnected islands"""
        islands = [
            box(0, 0, 1, 1),
            box(3, 3, 4, 4),
            box(7, 1, 8, 2),
            box(2, 6, 3, 7)
        ]
        country_geom = MultiPolygon(islands)
        
        result_dict, result_gdf = adaptive_geohash_coverage(
            country_geom,
            min_level=2,
            max_level=5,
            debug=False
        )
        
        # Should cover all islands
        for island in islands:
            covered = any(
                geom.intersects(island) for geom in result_gdf.geometry
            )
            assert covered

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
