"""
Unit tests for plot_geohash_coverage.py

Note: These tests use non-interactive matplotlib backend to avoid opening windows
"""
import matplotlib
import pytest

matplotlib.use('Agg')  # Non-interactive backend

import geopandas as gpd
from shapely.geometry import box

from sigmap.polygeohasher.plot_geohash_coverage import (
    plot_geohash_coverage,
    plot_geohash_comparison,
    plot_level_statistics
)


class TestPlotGeohashCoverage:
    """Test plot_geohash_coverage function"""
    
    def test_basic_plot(self, simple_square, sample_geohashes):
        """Test basic plotting functionality"""
        geohash_dict = {2: sample_geohashes}
        tiles_gdf = gpd.GeoDataFrame(
            {'geohash': sample_geohashes, 'level': [2] * len(sample_geohashes)},
            geometry=[box(i, i, i+1, i+1) for i in range(len(sample_geohashes))],
            crs='EPSG:4326'
        )
        
        fig, ax = plot_geohash_coverage(
            simple_square, geohash_dict, tiles_gdf,
            show_stats=False
        )
        
        assert fig is not None
        assert ax is not None
    
    def test_plot_with_save(self, simple_square, sample_geohashes, temp_dir):
        """Test plotting with save_path"""
        geohash_dict = {2: sample_geohashes}
        tiles_gdf = gpd.GeoDataFrame(
            {'geohash': sample_geohashes, 'level': [2] * len(sample_geohashes)},
            geometry=[box(i, i, i+1, i+1) for i in range(len(sample_geohashes))],
            crs='EPSG:4326'
        )
        
        save_path = temp_dir + '/test_plot.png'
        
        fig, ax = plot_geohash_coverage(
            simple_square, geohash_dict, tiles_gdf,
            save_path=save_path,
            show_stats=False
        )
        
        assert fig is not None
        assert ax is not None
    
    def test_adaptive_style_plot(self, simple_square, sample_geohashes):
        """Test plotting with adaptive style"""
        geohash_dict = {2: sample_geohashes}
        tiles_gdf = gpd.GeoDataFrame(
            {'geohash': sample_geohashes, 'level': [2] * len(sample_geohashes)},
            geometry=[box(i, i, i+1, i+1) for i in range(len(sample_geohashes))],
            crs='EPSG:4326'
        )
        
        fig, ax = plot_geohash_coverage(
            simple_square, geohash_dict, tiles_gdf,
            style='adaptive',
            show_stats=False
        )
        
        assert fig is not None
        assert ax is not None
    
    def test_simple_style_plot(self, simple_square, sample_geohashes):
        """Test plotting with simple style"""
        geohash_dict = {2: sample_geohashes}
        tiles_gdf = gpd.GeoDataFrame(
            {'geohash': sample_geohashes, 'level': [2] * len(sample_geohashes)},
            geometry=[box(i, i, i+1, i+1) for i in range(len(sample_geohashes))],
            crs='EPSG:4326'
        )
        
        fig, ax = plot_geohash_coverage(
            simple_square, geohash_dict, tiles_gdf,
            style='simple',
            show_stats=False
        )
        
        assert fig is not None
        assert ax is not None
    
    def test_heatmap_style_plot(self, simple_square, sample_geohashes):
        """Test plotting with heatmap style"""
        geohash_dict = {2: sample_geohashes}
        tiles_gdf = gpd.GeoDataFrame(
            {'geohash': sample_geohashes, 'level': [2] * len(sample_geohashes)},
            geometry=[box(i, i, i+1, i+1) for i in range(len(sample_geohashes))],
            crs='EPSG:4326'
        )
        
        fig, ax = plot_geohash_coverage(
            simple_square, geohash_dict, tiles_gdf,
            style='heatmap',
            show_stats=False
        )
        
        assert fig is not None
        assert ax is not None
    
    def test_no_tiles_raises_error(self, simple_square):
        """Test that empty geohash dict raises error"""
        geohash_dict = {}
        
        with pytest.raises(ValueError):
            plot_geohash_coverage(simple_square, geohash_dict, show_stats=False)
    
    def test_custom_title(self, simple_square, sample_geohashes):
        """Test custom title"""
        geohash_dict = {2: sample_geohashes}
        tiles_gdf = gpd.GeoDataFrame(
            {'geohash': sample_geohashes, 'level': [2] * len(sample_geohashes)},
            geometry=[box(i, i, i+1, i+1) for i in range(len(sample_geohashes))],
            crs='EPSG:4326'
        )
        
        fig, ax = plot_geohash_coverage(
            simple_square, geohash_dict, tiles_gdf,
            title="Custom Title",
            show_stats=False
        )
        
        assert fig is not None
        assert ax is not None
    
    def test_multipolygon_country(self, multipolygon_islands, sample_geohashes):
        """Test plotting with MultiPolygon country"""
        geohash_dict = {2: sample_geohashes}
        tiles_gdf = gpd.GeoDataFrame(
            {'geohash': sample_geohashes, 'level': [2] * len(sample_geohashes)},
            geometry=[box(i, i, i+1, i+1) for i in range(len(sample_geohashes))],
            crs='EPSG:4326'
        )
        
        fig, ax = plot_geohash_coverage(
            multipolygon_islands, geohash_dict, tiles_gdf,
            show_stats=False
        )
        
        assert fig is not None
        assert ax is not None
    
    def test_no_bbox_drawing(self, simple_square, sample_geohashes):
        """Test with bbox drawing disabled"""
        geohash_dict = {2: sample_geohashes}
        tiles_gdf = gpd.GeoDataFrame(
            {'geohash': sample_geohashes, 'level': [2] * len(sample_geohashes)},
            geometry=[box(i, i, i+1, i+1) for i in range(len(sample_geohashes))],
            crs='EPSG:4326'
        )
        
        fig, ax = plot_geohash_coverage(
            simple_square, geohash_dict, tiles_gdf,
            draw_bbox=False,
            show_stats=False
        )
        
        assert fig is not None
        assert ax is not None
    
    def test_no_country_drawing(self, simple_square, sample_geohashes):
        """Test with country drawing disabled"""
        geohash_dict = {2: sample_geohashes}
        tiles_gdf = gpd.GeoDataFrame(
            {'geohash': sample_geohashes, 'level': [2] * len(sample_geohashes)},
            geometry=[box(i, i, i+1, i+1) for i in range(len(sample_geohashes))],
            crs='EPSG:4326'
        )
        
        fig, ax = plot_geohash_coverage(
            simple_square, geohash_dict, tiles_gdf,
            draw_country=False,
            show_stats=False
        )
        
        assert fig is not None
        assert ax is not None


class TestPlotGeohashComparison:
    """Test plot_geohash_comparison function"""
    
    def test_basic_comparison(self, simple_square):
        """Test basic comparison plot"""
        geohashes1 = ['u09tv', 'u09tw']
        geohashes2 = ['u09ty', 'u09tz']
        
        tiles1 = gpd.GeoDataFrame(
            {'geohash': geohashes1, 'level': [3] * 2},
            geometry=[box(i, i, i+1, i+1) for i in range(2)],
            crs='EPSG:4326'
        )
        tiles2 = gpd.GeoDataFrame(
            {'geohash': geohashes2, 'level': [4] * 2},
            geometry=[box(i+2, i+2, i+3, i+3) for i in range(2)],
            crs='EPSG:4326'
        )
        
        results_list = [
            ({3: geohashes1}, tiles1),
            ({4: geohashes2}, tiles2)
        ]
        
        fig, axes = plot_geohash_comparison(
            simple_square, results_list, ['Level 3', 'Level 4']
        )
        
        assert fig is not None
        assert axes is not None
    
    def test_three_way_comparison(self, simple_square):
        """Test three-way comparison"""
        results_list = [
            ({2: ['u09tv']}, gpd.GeoDataFrame(
                {'geohash': ['u09tv'], 'level': [2]},
                geometry=[box(0, 0, 1, 1)],
                crs='EPSG:4326'
            )),
            ({3: ['u09tw']}, gpd.GeoDataFrame(
                {'geohash': ['u09tw'], 'level': [3]},
                geometry=[box(1, 1, 2, 2)],
                crs='EPSG:4326'
            )),
            ({4: ['u09ty']}, gpd.GeoDataFrame(
                {'geohash': ['u09ty'], 'level': [4]},
                geometry=[box(2, 2, 3, 3)],
                crs='EPSG:4326'
            ))
        ]
        
        fig, axes = plot_geohash_comparison(
            simple_square, results_list, ['L2', 'L3', 'L4']
        )
        
        assert fig is not None
        assert len(axes) == 3
    
    def test_save_comparison(self, simple_square, temp_dir):
        """Test saving comparison plot"""
        results_list = [
            ({2: ['u09tv']}, gpd.GeoDataFrame(
                {'geohash': ['u09tv'], 'level': [2]},
                geometry=[box(0, 0, 1, 1)],
                crs='EPSG:4326'
            ))
        ]
        
        save_path = temp_dir + '/comparison.png'
        
        fig, axes = plot_geohash_comparison(
            simple_square, results_list, ['Level 2'],
            save_path=save_path
        )
        
        assert fig is not None
        assert axes is not None


class TestPlotLevelStatistics:
    """Test plot_level_statistics function"""
    
    def test_bar_chart(self):
        """Test bar chart style"""
        geohash_dict = {
            2: ['u09tv', 'u09tw'],
            3: ['u09ty', 'u09tz', 'u09t0'],
            4: ['u09t1']
        }
        
        fig, ax = plot_level_statistics(
            geohash_dict,
            style='bar'
        )
        
        assert fig is not None
        assert ax is not None
    
    def test_pie_chart(self):
        """Test pie chart style"""
        geohash_dict = {
            2: ['u09tv', 'u09tw'],
            3: ['u09ty']
        }
        
        fig, ax = plot_level_statistics(
            geohash_dict,
            style='pie'
        )
        
        assert fig is not None
        assert ax is not None
    
    def test_save_statistics(self, temp_dir):
        """Test saving statistics plot"""
        geohash_dict = {
            2: ['u09tv'],
            3: ['u09tw']
        }
        
        save_path = temp_dir + '/stats.png'
        
        fig, ax = plot_level_statistics(
            geohash_dict,
            save_path=save_path
        )
        
        assert fig is not None
        assert ax is not None
    
    def test_empty_dict(self):
        """Test with empty dictionary"""
        geohash_dict = {}
        
        fig, ax = plot_level_statistics(geohash_dict)
        
        assert fig is not None
        assert ax is not None
    
    def test_single_level(self):
        """Test with single level"""
        geohash_dict = {2: ['u09tv', 'u09tw', 'u09ty']}
        
        fig, ax = plot_level_statistics(
            geohash_dict,
            style='bar'
        )
        
        assert fig is not None
        assert ax is not None
    
    def test_multiple_levels(self):
        """Test with multiple levels"""
        geohash_dict = {
            1: ['u09'],
            2: ['u09t', 'u09w'],
            3: ['u09tv', 'u09tw', 'u09ty', 'u09tz'],
            4: ['u09tv0', 'u09tv1'],
            5: ['u09tv02']
        }
        
        fig, ax = plot_level_statistics(
            geohash_dict,
            style='pie'
        )
        
        assert fig is not None
        assert ax is not None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
