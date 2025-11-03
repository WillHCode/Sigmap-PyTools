"""
Unit tests for gadm_download.py
"""
import io
import os
import shutil
import tempfile
import zipfile
from unittest.mock import patch

import geopandas as gpd
import pytest
from shapely.geometry import box

from sigmap.polygeohasher.utils.gadm_download import (
    check_already_exist,
    load_country_from_path,
    clear_gadm_temp_files,
    download_gadm_country
)


class TestCheckAlreadyExist:
    """Test check_already_exist function"""
    
    def test_file_exists_exact_match(self, temp_dir):
        """Test when exact file exists"""
        cache_dir = os.path.join(temp_dir, 'cache')
        os.makedirs(cache_dir, exist_ok=True)
        
        # Create mock shapefile
        test_file = os.path.join(cache_dir, 'gadm41_FRA_0.shp')
        
        # Create a minimal shapefile
        gdf = gpd.GeoDataFrame({'NAME': ['France']}, geometry=[box(0, 0, 10, 10)], crs='EPSG:4326')
        gdf.to_file(test_file)
        
        result = check_already_exist('FRA', level=0, cache_dir=cache_dir)
        
        assert result == test_file
    
    def test_file_not_exists(self, temp_dir):
        """Test when file doesn't exist"""
        cache_dir = os.path.join(temp_dir, 'cache')
        os.makedirs(cache_dir, exist_ok=True)
        
        result = check_already_exist('BEL', level=0, cache_dir=cache_dir)
        
        assert result is None
    
    def test_no_cache_dir(self):
        """Test when cache_dir is None"""
        result = check_already_exist('FRA', level=0, cache_dir=None)
        
        assert result is None
    
    def test_cache_dir_does_not_exist(self):
        """Test when cache_dir doesn't exist"""
        result = check_already_exist('FRA', level=0, cache_dir='/nonexistent/path')
        
        assert result is None
    
    def test_finds_first_matching_level(self, temp_dir):
        """Test finds first available level when exact level not found"""
        cache_dir = os.path.join(temp_dir, 'cache')
        os.makedirs(cache_dir, exist_ok=True)
        
        # Create file for level 1 but check for level 0
        test_file = os.path.join(cache_dir, 'gadm41_FRA_1.shp')
        gdf = gpd.GeoDataFrame({'NAME': ['France']}, geometry=[box(0, 0, 10, 10)], crs='EPSG:4326')
        gdf.to_file(test_file)
        
        result = check_already_exist('FRA', level=0, cache_dir=cache_dir)
        
        # Should find level 1 file
        assert result is not None
    
    def test_uppercase_iso3(self, temp_dir):
        """Test that ISO3 is case-insensitive"""
        cache_dir = os.path.join(temp_dir, 'cache')
        os.makedirs(cache_dir, exist_ok=True)
        
        test_file = os.path.join(cache_dir, 'gadm41_FRA_0.shp')
        gdf = gpd.GeoDataFrame({'NAME': ['France']}, geometry=[box(0, 0, 10, 10)], crs='EPSG:4326')
        gdf.to_file(test_file)
        
        # Test with lowercase
        result1 = check_already_exist('fra', level=0, cache_dir=cache_dir)
        # Test with uppercase
        result2 = check_already_exist('FRA', level=0, cache_dir=cache_dir)
        
        assert result1 == test_file
        assert result2 == test_file


class TestLoadCountryFromPath:
    """Test load_country_from_path function"""
    
    def test_load_valid_shapefile(self, temp_dir):
        """Test loading valid shapefile"""
        shp_path = os.path.join(temp_dir, 'test.shp')
        
        gdf = gpd.GeoDataFrame({'NAME': ['Test']}, geometry=[box(0, 0, 1, 1)], crs='EPSG:4326')
        gdf.to_file(shp_path)
        
        result = load_country_from_path(shp_path)
        
        assert isinstance(result, gpd.GeoDataFrame)
        assert len(result) == 1
        assert result.crs == 'EPSG:4326'
    
    def test_file_not_found_raises_error(self):
        """Test that missing file raises FileNotFoundError"""
        with pytest.raises(FileNotFoundError):
            load_country_from_path('/nonexistent/file.shp')
    
    def test_non_shapefile_raises_error(self, temp_dir):
        """Test that non-shapefile raises error"""
        # Create empty file
        test_file = os.path.join(temp_dir, 'not_a_shapefile.txt')
        with open(test_file, 'w') as f:
            f.write('not a shapefile')
        
        with pytest.raises(Exception):  # geopandas will raise an error
            load_country_from_path(test_file)
    
    def test_load_multiple_features(self, temp_dir):
        """Test loading shapefile with multiple features"""
        shp_path = os.path.join(temp_dir, 'test.shp')
        
        # Create with multiple polygons
        gdf = gpd.GeoDataFrame(
            {'NAME': ['A', 'B', 'C']},
            geometry=[box(i, i, i+1, i+1) for i in range(3)],
            crs='EPSG:4326'
        )
        gdf.to_file(shp_path)
        
        result = load_country_from_path(shp_path)
        
        assert len(result) == 3
        assert isinstance(result, gpd.GeoDataFrame)


class TestClearGadmTempFiles:
    """Test clear_gadm_temp_files function"""
    
    def test_dry_run_no_deletion(self, temp_dir):
        """Test that dry_run doesn't delete files"""
        # Create test files
        test_files = [
            'gadm41_FRA_0.shp',
            'gadm41_FRA_0.shx',
            'gadm41_FRA_0.dbf',
            'gadm_other.zip'
        ]
        
        created = []
        for fname in test_files:
            full_path = os.path.join(temp_dir, fname)
            with open(full_path, 'w') as f:
                f.write('test')
            created.append(full_path)
        
        # Dry run
        candidates = clear_gadm_temp_files(
            dirs=[temp_dir],
            dry_run=True,
            verbose=False
        )
        
        # Files should still exist
        for path in created:
            assert os.path.exists(path)
        
        # Should return candidate files
        assert len(candidates) >= len(test_files)
    
    def test_actual_deletion(self, temp_dir):
        """Test that actual deletion works"""
        # Create test files
        test_files = [
            os.path.join(temp_dir, 'gadm41_FRA_0.shp'),
            os.path.join(temp_dir, 'gadm41_FRA_0.shx'),
            os.path.join(temp_dir, 'other_file.txt')
        ]
        
        for path in test_files:
            with open(path, 'w') as f:
                f.write('test')
        
        # Actual deletion
        clear_gadm_temp_files(
            dirs=[temp_dir],
            dry_run=False,
            verbose=False
        )
        
        # GADM files should be deleted
        assert not os.path.exists(test_files[0])
        assert not os.path.exists(test_files[1])
        
        # Other file should not be deleted
        assert os.path.exists(test_files[2])
    
    def test_custom_patterns(self, temp_dir):
        """Test with custom patterns"""
        # Create test files
        test_files = [
            os.path.join(temp_dir, 'custom_gadm.zip'),
            os.path.join(temp_dir, 'normal.zip'),
        ]
        
        for path in test_files:
            with open(path, 'w') as f:
                f.write('test')
        
        # Delete with custom pattern
        clear_gadm_temp_files(
            dirs=[temp_dir],
            patterns=['custom_*'],
            dry_run=False,
            verbose=False
        )
        
        assert not os.path.exists(test_files[0])
        assert os.path.exists(test_files[1])
    
    def test_verbose_mode(self, temp_dir, capsys):
        """Test verbose output"""
        # Create test file
        test_file = os.path.join(temp_dir, 'gadm_test.zip')
        with open(test_file, 'w') as f:
            f.write('test')
        
        # Note: verbose output goes to logger, not stdout, so capsys won't capture it
        # Just verify it doesn't crash
        result = clear_gadm_temp_files(
            dirs=[temp_dir],
            dry_run=True,
            verbose=True
        )
        
        assert isinstance(result, list)
    
    def test_empty_directory(self, temp_dir):
        """Test with empty directory"""
        result = clear_gadm_temp_files(
            dirs=[temp_dir],
            dry_run=False,
            verbose=False
        )
        
        assert isinstance(result, list)
        assert len(result) == 0
    
    def test_nonexistent_directory(self):
        """Test with nonexistent directory"""
        result = clear_gadm_temp_files(
            dirs=['/nonexistent/path'],
            dry_run=False,
            verbose=False
        )
        
        assert isinstance(result, list)
    
    def test_multiple_directories(self, temp_dir):
        """Test scanning multiple directories"""
        dir1 = os.path.join(temp_dir, 'dir1')
        dir2 = os.path.join(temp_dir, 'dir2')
        os.makedirs(dir1)
        os.makedirs(dir2)
        
        # Create files in both
        file1 = os.path.join(dir1, 'gadm_test.zip')
        file2 = os.path.join(dir2, 'gadm_test2.zip')
        
        with open(file1, 'w') as f:
            f.write('test')
        with open(file2, 'w') as f:
            f.write('test')
        
        result = clear_gadm_temp_files(
            dirs=[dir1, dir2],
            dry_run=True,
            verbose=False
        )
        
        assert len(result) >= 2


class TestMockDownloadGadmCountry:
    """Test download_gadm_country with mocking"""
    
    @patch('sigmap.polygeohasher.utils.gadm_download.requests.get')
    def test_download_new_country(self, mock_get, temp_dir):
        """Test downloading a new country"""

        # Mock shapefile content
        gdf = gpd.GeoDataFrame({'NAME': ['France']}, geometry=[box(0, 0, 10, 10)], crs='EPSG:4326')

        # Create proper shapefile with all necessary files
        tmp_dir = tempfile.mkdtemp()
        zip_buffer = None
        try:
            shp_path = os.path.join(tmp_dir, 'gadm41_FRA_0.shp')
            gdf.to_file(shp_path)

            # Create zip file in memory with all shapefile components
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
                for ext in ['.shp', '.shx', '.dbf', '.prj', '.cpg']:
                    file_path = shp_path.replace('.shp', ext)
                    if os.path.exists(file_path):
                        zf.write(file_path, os.path.basename(file_path))
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)

        # Mock HTTP response
        mock_response = mock_get.return_value
        mock_response.content = zip_buffer.getvalue()
        mock_response.status_code = 200
        mock_response.raise_for_status = lambda: None

        cache_dir = os.path.join(temp_dir, 'cache')

        result = download_gadm_country('FRA', cache_dir=cache_dir)

        assert isinstance(result, gpd.GeoDataFrame)
        assert len(result) > 0

    def test_load_cached_country(self, temp_dir):
        """Test loading cached country"""
        cache_dir = os.path.join(temp_dir, 'cache')
        os.makedirs(cache_dir, exist_ok=True)
        
        # Create cached shapefile
        test_file = os.path.join(cache_dir, 'gadm41_FRA_0.shp')
        gdf = gpd.GeoDataFrame({'NAME': ['France']}, geometry=[box(0, 0, 10, 10)], crs='EPSG:4326')
        gdf.to_file(test_file)
        
        # Should load from cache
        result = download_gadm_country('FRA', cache_dir=cache_dir)
        
        assert isinstance(result, gpd.GeoDataFrame)
        assert len(result) == 1


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

