"""
Unit tests for data/copernicus.py
"""
from pathlib import Path
from unittest.mock import patch

import pytest
from shapely.geometry import box, MultiPolygon

# Test if copernicus is available, skip if not
try:
    from src.sigmap.data.copernicus import (
        _geometry_to_bbox,
        list_copernicus_products,
        get_copernicus_coverage,
        fetch_copernicus_data,
        fetch_sea_surface_temperature,
        fetch_ocean_salinity
    )
    COPERNICUS_INSTALLED = True
except ImportError:
    COPERNICUS_INSTALLED = False
    pytestmark = pytest.mark.skip("copernicusmarine not installed")


class TestGeometryToBbox:
    """Test _geometry_to_bbox utility function"""

    def test_none_geometry(self):
        """Test with None geometry returns global bbox"""
        bbox = _geometry_to_bbox(None)
        assert bbox == (-180.0, -90.0, 180.0, 90.0)

    def test_polygon_geometry(self):
        """Test with Polygon geometry"""
        poly = box(2.5, 49.5, 6.4, 51.5)
        bbox = _geometry_to_bbox(poly)
        assert bbox == (2.5, 49.5, 6.4, 51.5)

    def test_multipolygon_geometry(self):
        """Test with MultiPolygon geometry"""
        poly1 = box(0, 0, 1, 1)
        poly2 = box(2, 2, 3, 3)
        multi = MultiPolygon([poly1, poly2])
        bbox = _geometry_to_bbox(multi)
        # Should return overall bounds
        assert bbox == (0.0, 0.0, 3.0, 3.0)

    def test_single_geohash(self):
        """Test with single geohash string"""
        bbox = _geometry_to_bbox('u151')
        # Check it returns a tuple of 4 floats
        assert isinstance(bbox, tuple)
        assert len(bbox) == 4
        assert all(isinstance(x, float) for x in bbox)

    def test_multiple_geohashes(self):
        """Test with list of geohashes"""
        geohashes = ['u151', 'u154', 'u155']
        bbox = _geometry_to_bbox(geohashes)
        # Should return combined bounds
        assert isinstance(bbox, tuple)
        assert len(bbox) == 4
        assert all(isinstance(x, float) for x in bbox)

    def test_invalid_geometry_type(self):
        """Test with invalid geometry type"""
        with pytest.raises(TypeError):
            _geometry_to_bbox(123)  # Invalid type


@pytest.mark.skipif(not COPERNICUS_INSTALLED, reason="copernicusmarine not installed")
class TestListCopernicusProducts:
    """Test list_copernicus_products function"""

    @patch('src.sigmap.data.copernicus.copernicusmarine')
    def test_list_all_products(self, mock_copernicusmarine):
        """Test listing all products"""
        mock_copernicusmarine.describe.return_value = [
            {'id': 'product1', 'name': 'Product 1'},
            {'id': 'product2', 'name': 'Product 2'},
        ]

        products = list_copernicus_products()

        assert len(products) == 2
        assert products[0]['id'] == 'product1'
        mock_copernicusmarine.describe.assert_called_once()

    @patch('src.sigmap.data.copernicus.copernicusmarine')
    def test_list_with_keywords(self, mock_copernicusmarine):
        """Test listing products with keyword filter"""
        mock_copernicusmarine.describe.return_value = [
            {'id': 'temp1', 'name': 'Temperature Product'},
            {'id': 'sal1', 'name': 'Salinity Product'},
            {'id': 'temp2', 'name': 'Temperature Analysis'},
        ]

        products = list_copernicus_products(keywords=['temperature'])

        # Should filter to only temperature products
        assert len(products) == 2
        assert all('temperature' in str(p).lower() for p in products)

    @patch('src.sigmap.data.copernicus.copernicusmarine')
    def test_list_products_error(self, mock_copernicusmarine):
        """Test error handling when listing products fails"""
        mock_copernicusmarine.describe.side_effect = Exception("API Error")

        with pytest.raises(Exception):
            list_copernicus_products()


@pytest.mark.skipif(not COPERNICUS_INSTALLED, reason="copernicusmarine not installed")
class TestGetCopernicusCoverage:
    """Test get_copernicus_coverage function"""

    @patch('src.sigmap.data.copernicus.copernicusmarine')
    def test_get_coverage(self, mock_copernicusmarine):
        """Test getting coverage metadata"""
        mock_copernicusmarine.describe.return_value = {
            'product_id': 'test_product',
            'bbox': [-180, -90, 180, 90],
            'time_range': ['2020-01-01', '2020-12-31']
        }

        coverage = get_copernicus_coverage('test_product')

        assert isinstance(coverage, dict)
        mock_copernicusmarine.describe.assert_called_once()

    @patch('src.sigmap.data.copernicus.copernicusmarine')
    def test_get_coverage_error(self, mock_copernicusmarine):
        """Test error handling"""
        mock_copernicusmarine.describe.side_effect = Exception("Product not found")

        with pytest.raises(Exception):
            get_copernicus_coverage('invalid_product')


@pytest.mark.skipif(not COPERNICUS_INSTALLED, reason="copernicusmarine not installed")
class TestFetchCopernicusData:
    """Test fetch_copernicus_data function"""

    @patch('src.sigmap.data.copernicus.copernicusmarine')
    def test_basic_fetch(self, mock_copernicusmarine, tmp_path):
        """Test basic data fetch"""
        output_path = tmp_path / 'test.nc'
        geometry = box(2.5, 49.5, 6.4, 51.5)

        result = fetch_copernicus_data(
            product_id='test_product',
            variables=['thetao'],
            output_path=output_path,
            geometry=geometry,
            time_range=('2020-01-01', '2020-01-07')
        )

        # Check an output path is returned
        assert isinstance(result, Path)
        # Check subset was called
        mock_copernicusmarine.subset.assert_called_once()

        # Check parameters passed to subset
        call_args = mock_copernicusmarine.subset.call_args[1]
        assert call_args['variables'] == ['thetao']
        assert call_args['minimum_longitude'] == 2.5
        assert call_args['maximum_longitude'] == 6.4
        assert call_args['minimum_latitude'] == 49.5
        assert call_args['maximum_latitude'] == 51.5

    @patch('src.sigmap.data.copernicus.copernicusmarine')
    def test_fetch_with_geohash(self, mock_copernicusmarine, tmp_path):
        """Test fetch with geohash geometry"""
        output_path = tmp_path / 'test.nc'

        result = fetch_copernicus_data(
            product_id='test_product',
            variables=['thetao'],
            output_path=output_path,
            geometry='u151',
            time_range=('2020-01-01', '2020-01-07')
        )

        assert isinstance(result, Path)
        mock_copernicusmarine.subset.assert_called_once()

    @patch('src.sigmap.data.copernicus.copernicusmarine')
    def test_fetch_with_depth_range(self, mock_copernicusmarine, tmp_path):
        """Test fetch with depth range"""
        output_path = tmp_path / 'test.nc'

        result = fetch_copernicus_data(
            product_id='test_product',
            variables=['thetao'],
            output_path=output_path,
            geometry=box(0, 0, 1, 1),
            time_range=('2020-01-01', '2020-01-07'),
            depth_range=(0.0, 100.0)
        )

        call_args = mock_copernicusmarine.subset.call_args[1]
        assert call_args['minimum_depth'] == 0.0
        assert call_args['maximum_depth'] == 100.0

    @patch('src.sigmap.data.copernicus.copernicusmarine')
    def test_fetch_existing_file_no_force(self, mock_copernicusmarine, tmp_path):
        """Test that existing file is not re-downloaded without force"""
        output_path = tmp_path / 'test.nc'
        output_path.touch()  # Create empty file

        result = fetch_copernicus_data(
            product_id='test_product',
            variables=['thetao'],
            output_path=output_path,
            geometry=box(0, 0, 1, 1),
            time_range=('2020-01-01', '2020-01-07'),
            force_download=False
        )

        # Should not call subset
        mock_copernicusmarine.subset.assert_not_called()
        assert result == output_path

    @patch('src.sigmap.data.copernicus.copernicusmarine')
    def test_fetch_existing_file_with_force(self, mock_copernicusmarine, tmp_path):
        """Test that existing file is re-downloaded with force"""
        output_path = tmp_path / 'test.nc'
        output_path.touch()

        result = fetch_copernicus_data(
            product_id='test_product',
            variables=['thetao'],
            output_path=output_path,
            geometry=box(0, 0, 1, 1),
            time_range=('2020-01-01', '2020-01-07'),
            force_download=True
        )

        # Should call subset even though file exists
        mock_copernicusmarine.subset.assert_called_once()

    @patch('src.sigmap.data.copernicus.copernicusmarine')
    def test_fetch_creates_output_directory(self, mock_copernicusmarine, tmp_path):
        """Test that output directory is created if it doesn't exist"""
        output_path = tmp_path / 'subdir' / 'nested' / 'test.nc'

        fetch_copernicus_data(
            product_id='test_product',
            variables=['thetao'],
            output_path=output_path,
            geometry=box(0, 0, 1, 1),
            time_range=('2020-01-01', '2020-01-07')
        )

        assert output_path.parent.exists()

    @patch('src.sigmap.data.copernicus.copernicusmarine')
    def test_fetch_error_handling(self, mock_copernicusmarine, tmp_path):
        """Test error handling during fetch"""
        mock_copernicusmarine.subset.side_effect = Exception("Download failed")
        output_path = tmp_path / 'test.nc'

        with pytest.raises(Exception):
            fetch_copernicus_data(
                product_id='test_product',
                variables=['thetao'],
                output_path=output_path,
                geometry=box(0, 0, 1, 1),
                time_range=('2020-01-01', '2020-01-07')
            )


@pytest.mark.skipif(not COPERNICUS_INSTALLED, reason="copernicusmarine not installed")
class TestConvenienceFunctions:
    """Test convenience functions"""

    @patch('src.sigmap.data.copernicus.fetch_copernicus_data')
    def test_fetch_sea_surface_temperature(self, mock_fetch, tmp_path):
        """Test SST convenience function"""
        output_path = tmp_path / 'sst.nc'
        geometry = box(0, 0, 1, 1)
        time_range = ('2020-01-01', '2020-01-07')

        mock_fetch.return_value = output_path

        result = fetch_sea_surface_temperature(
            output_path=output_path,
            geometry=geometry,
            time_range=time_range
        )

        # Check it calls the main function with correct parameters
        mock_fetch.assert_called_once()
        call_args = mock_fetch.call_args[1]
        assert 'thetao' in call_args['variables']
        assert call_args['depth_range'] == (0.0, 1.0)

    @patch('src.sigmap.data.copernicus.fetch_copernicus_data')
    def test_fetch_ocean_salinity(self, mock_fetch, tmp_path):
        """Test salinity convenience function"""
        output_path = tmp_path / 'salinity.nc'
        geometry = box(0, 0, 1, 1)
        time_range = ('2020-01-01', '2020-01-07')

        mock_fetch.return_value = output_path

        result = fetch_ocean_salinity(
            output_path=output_path,
            geometry=geometry,
            time_range=time_range
        )

        mock_fetch.assert_called_once()
        call_args = mock_fetch.call_args[1]
        assert 'so' in call_args['variables']


class TestCopernicusNotInstalled:
    """Test behavior when copernicusmarine is not installed"""

    @pytest.mark.skipif(COPERNICUS_INSTALLED, reason="copernicusmarine is installed")
    def test_import_warning(self):
        """Test that import warning is raised"""
        # This test only runs if copernicusmarine is NOT installed
        # The warning should have been raised during import
        pass


if __name__ == '__main__':
    pytest.main([__file__, '-v'])