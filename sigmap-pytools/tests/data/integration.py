"""
Integration tests for data subpackage.

These tests require:
1. API credentials to be configured
2. Network access
3. Longer timeout (actual data downloads)

Run with: pytest tests/test_data_integration.py -v -m integration
Skip with: pytest -m "not integration"
"""
import pytest
from pathlib import Path
from shapely.geometry import box

# These tests are marked as integration and will be skipped by default
pytestmark = [
    pytest.mark.integration,
    pytest.mark.network,
    pytest.mark.slow
]


class TestCopernicusIntegration:
    """Integration tests for Copernicus Marine Service"""
    
    @pytest.mark.copernicus
    @pytest.mark.requires_credentials
    @pytest.mark.skip(reason="Requires Copernicus credentials - run manually")
    def test_download_real_sst_data(self, tmp_path, belgium_bbox):
        """Test downloading real SST data (MANUAL TEST)"""
        from sigmap.data import fetch_sea_surface_temperature
        
        output_path = tmp_path / 'copernicus_sst.nc'
        
        result = fetch_sea_surface_temperature(
            output_path=output_path,
            geometry=belgium_bbox,
            time_range=('2020-01-01', '2020-01-03')  # Just 3 days for testing
        )
        
        assert result.exists()
        assert result.stat().st_size > 0
    
    @pytest.mark.copernicus
    def test_list_products_real(self):
        """Test listing real Copernicus products"""
        try:
            from sigmap.data import list_copernicus_products
            
            # This might work without credentials
            products = list_copernicus_products(keywords=['temperature'])
            
            assert isinstance(products, list)
            # May or may not have results depending on API access
        except ImportError:
            pytest.skip("copernicusmarine not installed")
        except Exception as e:
            pytest.skip(f"API not accessible: {e}")


class TestERA5Integration:
    """Integration tests for ERA5/CDS API"""
    
    @pytest.mark.era5
    @pytest.mark.requires_credentials
    @pytest.mark.skip(reason="Requires CDS credentials - run manually")
    def test_download_real_temperature_data(self, tmp_path, small_test_area):
        """Test downloading real ERA5 temperature data (MANUAL TEST)"""
        from sigmap.data import fetch_era5_temperature
        
        output_path = tmp_path / 'era5_temp.nc'
        
        result = fetch_era5_temperature(
            output_path=output_path,
            geometry=small_test_area,
            time_range=('2020-01-01', '2020-01-02'),  # Just 2 days
            hours=['00:00', '12:00']  # Only 2 hours per day
        )
        
        assert result.exists()
        assert result.stat().st_size > 0
    
    @pytest.mark.era5
    def test_list_variables_real(self):
        """Test listing ERA5 variables"""
        try:
            from sigmap.data import list_era5_variables
            
            variables = list_era5_variables()
            
            assert isinstance(variables, dict)
            assert 'temperature' in variables
            assert '2m_temperature' in variables['temperature']
        except ImportError:
            pytest.skip("cdsapi not installed")


class TestCHELSAIntegration:
    """Integration tests for CHELSA"""
    
    @pytest.mark.chelsa
    @pytest.mark.skip(reason="Requires long download time - run manually")
    def test_download_real_temperature_data(self, tmp_path, small_test_area):
        """Test downloading real CHELSA temperature data (MANUAL TEST)"""
        from sigmap.data import fetch_chelsa_temperature
        
        output_path = tmp_path / 'chelsa_temp.tif'
        
        result = fetch_chelsa_temperature(
            output_path=output_path,
            geometry=small_test_area,
            time_period='1981-2010',
            month=1
        )
        
        assert result.exists()
        assert result.stat().st_size > 0
    
    @pytest.mark.chelsa
    def test_list_variables_real(self):
        """Test listing CHELSA variables"""
        try:
            from sigmap.data import list_chelsa_variables
            
            variables = list_chelsa_variables()
            
            assert isinstance(variables, dict)
            assert 'temperature' in variables
            assert 'tas' in variables['temperature']
        except ImportError:
            pytest.skip("chelsa-cmip6 not installed")


class TestCombinedWorkflow:
    """Integration tests for combined workflows"""
    
    @pytest.mark.skip(reason="Requires all data sources - run manually")
    def test_compare_temperature_sources(self, tmp_path, small_test_area):
        """Compare temperature from different sources (MANUAL TEST)"""
        from sigmap.data import (
            fetch_era5_temperature,
            fetch_chelsa_temperature
        )
        
        # ERA5 data
        era5_path = tmp_path / 'era5_temp.nc'
        era5_result = fetch_era5_temperature(
            output_path=era5_path,
            geometry=small_test_area,
            time_range=('2020-01-01', '2020-01-01')
        )
        
        # CHELSA data
        chelsa_path = tmp_path / 'chelsa_temp.tif'
        chelsa_result = fetch_chelsa_temperature(
            output_path=chelsa_path,
            geometry=small_test_area,
            time_period='1981-2010',
            month=1
        )
        
        # Both should exist
        assert era5_result.exists()
        assert chelsa_result.exists()
    
    @pytest.mark.skip(reason="Requires polygeohasher integration - run manually")
    def test_adaptive_coverage_with_data(self, tmp_path):
        """Test using adaptive coverage for data download (MANUAL TEST)"""
        from sigmap.polygeohasher import (
            download_gadm_country,
            build_single_multipolygon,
            adaptive_geohash_coverage
        )
        from sigmap.data import fetch_era5_temperature
        
        # Get country geometry
        belgium_gdf = download_gadm_country('LUX', cache_dir=tmp_path / 'gadm')
        belgium_geom = build_single_multipolygon(belgium_gdf)
        
        # Generate adaptive coverage
        geohash_dict, tiles_gdf = adaptive_geohash_coverage(
            belgium_geom,
            min_level=3,
            max_level=4
        )
        
        # Use level 3 tiles for data download
        level_3_tiles = geohash_dict.get(3, [])
        
        if level_3_tiles:
            output_path = tmp_path / 'era5_coverage.nc'
            result = fetch_era5_temperature(
                output_path=output_path,
                geometry=level_3_tiles,
                time_range=('2020-01-01', '2020-01-01')
            )
            
            assert result.exists()


class TestErrorHandling:
    """Integration tests for error handling"""
    
    def test_invalid_product_id(self, tmp_path, small_test_area):
        """Test error handling for invalid product ID"""
        try:
            from sigmap.data import fetch_copernicus_data
            
            output_path = tmp_path / 'test.nc'
            
            with pytest.raises(Exception):
                fetch_copernicus_data(
                    product_id='invalid_product_id_xyz',
                    variables=['thetao'],
                    output_path=output_path,
                    geometry=small_test_area,
                    time_range=('2020-01-01', '2020-01-01')
                )
        except ImportError:
            pytest.skip("copernicusmarine not installed")
    
    def test_invalid_variable_name(self, tmp_path, small_test_area):
        """Test error handling for invalid variable name"""
        try:
            from sigmap.data import fetch_era5_data
            
            output_path = tmp_path / 'test.nc'
            
            # CDS API should reject invalid variable names
            with pytest.raises(Exception):
                fetch_era5_data(
                    variables=['invalid_variable_xyz'],
                    output_path=output_path,
                    geometry=small_test_area,
                    time_range=('2020-01-01', '2020-01-01')
                )
        except ImportError:
            pytest.skip("cdsapi not installed")


class TestPerformance:
    """Performance tests for data operations"""
    
    @pytest.mark.slow
    @pytest.mark.skip(reason="Performance test - run manually")
    def test_geohash_vs_bbox_performance(self, tmp_path, belgium_bbox):
        """Compare performance of geohash vs bbox filtering"""
        import time
        from sigmap.polygeohasher import adaptive_geohash_coverage
        from sigmap.data import fetch_era5_temperature
        
        # Test with bbox
        start = time.time()
        bbox_path = tmp_path / 'bbox_test.nc'
        fetch_era5_temperature(
            output_path=bbox_path,
            geometry=belgium_bbox,
            time_range=('2020-01-01', '2020-01-01')
        )
        bbox_time = time.time() - start
        
        # Test with geohash
        geohash_dict, _ = adaptive_geohash_coverage(
            belgium_bbox,
            min_level=3,
            max_level=3
        )
        level_3_tiles = geohash_dict[3]
        
        start = time.time()
        geohash_path = tmp_path / 'geohash_test.nc'
        fetch_era5_temperature(
            output_path=geohash_path,
            geometry=level_3_tiles,
            time_range=('2020-01-01', '2020-01-01')
        )
        geohash_time = time.time() - start
        
        print(f"\nBbox download time: {bbox_time:.2f}s")
        print(f"Geohash download time: {geohash_time:.2f}s")
        
        # Both should succeed
        assert bbox_path.exists()
        assert geohash_path.exists()


# ==================== Fixtures for Integration Tests ====================

@pytest.fixture
def skip_if_no_cds_credentials():
    """Skip test if CDS credentials are not configured"""
    cdsapirc = Path.home() / '.cdsapirc'
    if not cdsapirc.exists():
        pytest.skip("CDS API credentials not configured")


@pytest.fixture
def small_test_area():
    """Very small area for quick integration tests"""
    return box(4.0, 50.0, 4.1, 50.1)  # ~10x10 km area


@pytest.fixture
def integration_timeout():
    """Timeout for integration tests"""
    return 600  # 10 minutes


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-m', 'integration'])
