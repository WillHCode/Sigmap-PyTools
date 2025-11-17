"""
Copernicus Marine Service data collection wrapper.

This module provides functions to fetch ocean and marine data from Copernicus Marine Service.
Supports filtering by bounding box, geohash tiles, or polygon geometries.

Dependencies:
    pip install copernicusmarine xarray numpy shapely
"""
import warnings
from pathlib import Path
from typing import Optional, Union, List, Tuple, Dict, Any

from copernicusmarine import CopernicusMarineProduct

from ..utils.polygons import geometry_to_bbox

try:
    import copernicusmarine
    COPERNICUS_AVAILABLE = True
except ImportError:
    COPERNICUS_AVAILABLE = False
    warnings.warn(
        "copernicusmarine is not installed. Install with: pip install copernicusmarine",
        ImportWarning
    )

try:
    import xarray as xr
    import numpy as np
    XARRAY_AVAILABLE = True
except ImportError:
    XARRAY_AVAILABLE = False
    warnings.warn(
        "xarray and numpy are required for geometry masking. Install with: pip install xarray numpy",
        ImportWarning
    )

from shapely.geometry import Polygon, MultiPolygon, Point

from sigmap.logger import logging
from ..utils.polygons import geohashes_to_boxes

logger = logging.getLogger(__name__)

def _check_copernicus_available():
    """Raise error if copernicusmarine is not installed."""
    if not COPERNICUS_AVAILABLE:
        raise ImportError(
            "copernicusmarine is required for Copernicus data access. "
            "Install with: pip install copernicusmarine"
        )


def _check_xarray_available():
    """Raise error if xarray/numpy are not installed."""
    if not XARRAY_AVAILABLE:
        raise ImportError(
            "xarray and numpy are required for geometry masking. "
            "Install with: pip install xarray numpy"
        )


def _geometry_to_shapely(
        geometry: Union[Polygon, MultiPolygon, str, List[str]]
) -> Union[Polygon, MultiPolygon]:
    """
    Convert geometry input to Shapely Polygon or MultiPolygon.

    Parameters
    ----------
    geometry : Polygon, MultiPolygon, str, or list of str
        - Shapely Polygon/MultiPolygon (returned as-is)
        - Single geohash string (converted to Polygon)
        - List of geohash strings (converted to MultiPolygon)

    Returns
    -------
    Polygon or MultiPolygon
    """
    if isinstance(geometry, (Polygon, MultiPolygon)):
        return geometry

    if isinstance(geometry, str):
        # Single geohash - convert to Polygon
        boxes = geohashes_to_boxes([geometry])
        return boxes[geometry]

    if isinstance(geometry, list):
        # List of geohashes - convert to MultiPolygon
        boxes = geohashes_to_boxes(geometry)
        polygons = list(boxes.values())
        if len(polygons) == 1:
            return polygons[0]
        return MultiPolygon(polygons)

    raise TypeError(
        f"Unsupported geometry type: {type(geometry)}. "
        "Expected Polygon, MultiPolygon, geohash string, or list of geohashes."
    )


def _mask_dataset_with_geometry(
        dataset_path: Path,
        geometry: Union[Polygon, MultiPolygon, str, List[str]]
) -> None:
    """
    Mask a NetCDF dataset using a geometry, setting values outside the geometry to NaN.

    This function modifies the NetCDF file in-place.

    Parameters
    ----------
    dataset_path : Path
        Path to the NetCDF file to mask
    geometry : Polygon, MultiPolygon, str, or list of str
        Geometry to use as mask
    """
    _check_xarray_available()

    logger.info(f"Masking dataset with geometry: {dataset_path}")

    # Convert geometry to Shapely object
    shapely_geom = _geometry_to_shapely(geometry)

    # Open dataset - IMPORTANT: close it properly before writing
    ds = xr.open_dataset(dataset_path)

    # Create a copy to avoid file locking issues
    masked_ds = None

    try:
        lon_names = ['longitude', 'lon', 'x']
        lat_names = ['latitude', 'lat', 'y']

        lon_coord = None
        lat_coord = None

        for name in lon_names:
            if name in ds.coords or name in ds.dims:
                lon_coord = name
                break

        for name in lat_names:
            if name in ds.coords or name in ds.dims:
                lat_coord = name
                break

        if lon_coord is None or lat_coord is None:
            raise ValueError(
                f"Could not find longitude/latitude coordinates in dataset. "
                f"Available coords: {list(ds.coords.keys())}, dims: {list(ds.dims.keys())}"
            )

        logger.info(f"Using coordinates: lon='{lon_coord}', lat='{lat_coord}'")

        lons = ds[lon_coord].values
        lats = ds[lat_coord].values
        lon_2d, lat_2d = np.meshgrid(lons, lats)

        mask = np.zeros_like(lon_2d, dtype=bool)

        logger.info(f"Creating mask for {mask.shape[0] * mask.shape[1]} grid points...")

        points = np.column_stack([lon_2d.ravel(), lat_2d.ravel()])

        # Check which points are inside the geometry
        if isinstance(shapely_geom, MultiPolygon):
            # For MultiPolygon, check against all polygons
            mask_flat = np.zeros(len(points), dtype=bool)
            for poly in shapely_geom.geoms:
                for i, (lon, lat) in enumerate(points):
                    if not mask_flat[i]:  # Skip if already marked as inside
                        mask_flat[i] = poly.contains(Point(lon, lat))
        else:
            mask_flat = np.array([shapely_geom.contains(Point(lon, lat))
                                  for lon, lat in points])

        mask = mask_flat.reshape(lon_2d.shape)

        logger.info(f"Mask created: {mask.sum()} / {mask.size} points inside geometry "
                   f"({100 * mask.sum() / mask.size:.1f}%)")

        ds = ds.load()
        masked_ds = ds.copy()
        for var in ds.data_vars:
            if lat_coord in ds[var].dims and lon_coord in ds[var].dims:
                logger.info(f"Masking variable: {var}")

                data = ds[var].values
                dims = ds[var].dims

                if data.ndim == 2:  # 2D: (lat, lon)
                    data[~mask] = np.nan
                elif data.ndim == 3:  # 3D: e.g., (time, lat, lon) or (depth, lat, lon)
                    for i in range(data.shape[0]):
                        data[i, ~mask] = np.nan
                elif data.ndim == 4:  # 4D: e.g., (time, depth, lat, lon)
                    for i in range(data.shape[0]):
                        for j in range(data.shape[1]):
                            data[i, j, ~mask] = np.nan
                else:
                    logger.warning(f"Variable {var} has {data.ndim} dimensions, skipping mask")
                    continue

                masked_ds[var].values = data

    finally:
        ds.close()

    try:
        masked_ds.to_netcdf(dataset_path)
        logger.info(f"Masked dataset saved to: {dataset_path}")
    finally:
        if masked_ds is not None:
            masked_ds.close()


def get_meta(product: CopernicusMarineProduct) -> Dict[str, Any]:
    return {
        "title": product.title,
        "product_id": product.product_id,
        "thumbnail_url": product.thumbnail_url,
        "description": product.description,
        "digital_object_identifier": product.digital_object_identifier,
        "sources": product.sources,
        "processing_level": product.processing_level,
        "production_center": product.production_center,
        "keywords": product.keywords,
        "datasets": product.datasets,
    }

def list_copernicus_products(
        keywords: Optional[List[str]] = None,
        product_id: Optional[str] = None,
        dataset_id: Optional[str] = None,
        disable_progress_bar: Optional[bool] = True,
) -> list[CopernicusMarineProduct]:
    """
    List available Copernicus Marine products.

    Parameters
    ----------
    keywords : list of str, optional
        Keywords to filter products (e.g., ['temperature', 'ocean'])
    contains_bbox : tuple, optional
        (lon_min, lat_min, lon_max, lat_max) to filter products by coverage

    Returns
    -------
    list : List of CopernicusMarineProduct
    """
    _check_copernicus_available()

    try:
        if keywords is None:
            catalogue = copernicusmarine.describe(product_id=product_id,
                                                  dataset_id=dataset_id,
                                                  disable_progress_bar=disable_progress_bar)
        else:
            catalogue = copernicusmarine.describe(contains=keywords,
                                                  product_id=product_id,
                                                  dataset_id=dataset_id,
                                                  disable_progress_bar=disable_progress_bar)

    except Exception as e:
        logger.error(f"Failed to list Copernicus products: {e}")
        raise

    return catalogue.products


def get_copernicus_coverage(
        product_id: str,
        dataset_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get spatial and temporal coverage information for a Copernicus product.

    Parameters
    ----------
    product_id : str
        Copernicus product identifier
    dataset_id : str, optional
        Specific dataset within the product

    Returns
    -------
    dict : Coverage metadata including bbox, time range, variables
    """
    _check_copernicus_available()

    try:
        metadata = copernicusmarine.describe(
            include_datasets=True,
            include_versions=True,
            returned_value="dict"
        )

        # Extract coverage info for the specified product
        # Implementation depends on API response structure
        logger.info(f"Retrieved coverage for product: {product_id}")
        return metadata

    except Exception as e:
        logger.error(f"Failed to get coverage for {product_id}: {e}")
        raise


def fetch_copernicus_data(
        dataset_id: str,
        variables: List[str],
        output_path: Union[str, Path],
        geometry: Union[Polygon, MultiPolygon, str, List[str], None] = None,
        time_range: Optional[Tuple[str, str]] = None,
        depth_range: Optional[Tuple[float, float]] = None,
        force_download: bool = False,
        mask_using_geom: bool = False,
        **kwargs
) -> Path:
    """
    Fetch data from Copernicus Marine Service.

    Parameters
    ----------
    dataset_id : str
        Copernicus dataset identifier (e.g., 'cmems_mod_glo_phy_my_0.083deg_P1D-m')
    variables : list of str
        Variables to download (e.g., ['thetao', 'so'] for temperature and salinity)
    output_path : str or Path
        Path where downloaded file will be saved
    geometry : Polygon, MultiPolygon, str, list of str, or None
        Area of interest:
        - Shapely Polygon/MultiPolygon
        - Single geohash string
        - List of geohash strings
        - None for global coverage
    time_range : tuple of str, optional
        (start_date, end_date) in format 'YYYY-MM-DD'
        Example: ('2020-01-01', '2020-12-31')
    depth_range : tuple of float, optional
        (min_depth, max_depth) in meters
        Example: (0.0, 100.0)
    force_download : bool, default False
        If True, download even if file exists
    mask_using_geom : bool, default False
        If True, mask the downloaded data using the provided geometry.
        Values outside the geometry will be set to NaN.
        Note: This requires xarray and numpy to be installed.
    **kwargs
        Additional parameters passed to copernicusmarine.subset()

    Returns
    -------
    Path : Path to downloaded file
    """
    _check_copernicus_available()

    if mask_using_geom:
        _check_xarray_available()
        if geometry is None:
            raise ValueError("mask_using_geom=True requires a geometry to be specified")

    output_path = Path(output_path)

    # Check if file exists
    if output_path.exists():
        if force_download:
            logger.info(f"Force download enabled — removing existing file: {output_path}")
            try:
                output_path.unlink()
            except Exception as e:
                logger.warning(f"Could not delete existing file {output_path}: {e}")
        else:
            logger.info(f"File already exists (skipping download): {output_path}")
            return output_path

    # Create output directory
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Convert geometry to bbox
    bbox = geometry_to_bbox(geometry)
    lon_min, lat_min, lon_max, lat_max = bbox

    logger.info(f"Fetching Copernicus data:")
    logger.info(f"  Dataset: {dataset_id}")
    logger.info(f"  Variables: {variables}")
    logger.info(f"  Bbox: {bbox}")
    logger.info(f"  Mask using geometry: {mask_using_geom}")
    logger.info(f"  Output: {output_path}")

    try:
        # Build subset parameters
        subset_params = {
            'dataset_id': dataset_id,
            'variables': variables,
            'minimum_longitude': lon_min,
            'maximum_longitude': lon_max,
            'minimum_latitude': lat_min,
            'maximum_latitude': lat_max,
            'output_filename': str(output_path)
        }

        # Add time range if specified
        if time_range:
            start_date, end_date = time_range
            subset_params['start_datetime'] = start_date
            subset_params['end_datetime'] = end_date

        # Add depth range if specified
        if depth_range:
            min_depth, max_depth = depth_range
            subset_params['minimum_depth'] = min_depth
            subset_params['maximum_depth'] = max_depth

        # Add any additional parameters
        subset_params.update(kwargs)

        # Download data
        copernicusmarine.subset(**subset_params)

        logger.info(f"Successfully downloaded to: {output_path}")

        # Apply geometry mask if requested
        if mask_using_geom:
            _mask_dataset_with_geometry(output_path, geometry)

        return output_path

    except Exception as e:
        logger.error(f"Failed to fetch Copernicus data: {e}")
        raise


# Convenience functions

def fetch_sea_surface_temperature(
        output_path: Union[str, Path],
        geometry: Union[Polygon, MultiPolygon, str, List[str]],
        time_range: Tuple[str, str],
        dataset_id: str = 'cmems_mod_glo_phy_my_0.083deg_P1D-m',
        mask_using_geom: bool = False,
        **kwargs
) -> Path:
    """
    Fetch sea surface temperature data.

    Convenience wrapper for fetching SST data from Copernicus.

    Parameters
    ----------
    output_path : str or Path
        Where to save the data
    geometry : Polygon, MultiPolygon, str, or list of str
        Area of interest
    time_range : tuple of str
        (start_date, end_date) in 'YYYY-MM-DD' format
    dataset_id : str, optional
        Copernicus product to use
    mask_using_geom : bool, default False
        If True, mask data outside the geometry
    **kwargs
        Additional parameters

    Returns
    -------
    Path : Path to downloaded file
    """
    return fetch_copernicus_data(
        dataset_id=dataset_id,
        variables=['thetao'],  # Temperature
        output_path=output_path,
        geometry=geometry,
        time_range=time_range,
        depth_range=(0.0, 1.0),  # Surface only
        mask_using_geom=mask_using_geom,
        **kwargs
    )


def fetch_ocean_salinity(
        output_path: Union[str, Path],
        geometry: Union[Polygon, MultiPolygon, str, List[str]],
        time_range: Tuple[str, str],
        dataset_id: str = 'cmems_mod_glo_phy_my_0.083deg_P1D-m',
        mask_using_geom: bool = False,
        **kwargs
) -> Path:
    """
    Fetch ocean salinity data.

    Convenience wrapper for fetching salinity data from Copernicus.

    Parameters
    ----------
    output_path : str or Path
        Where to save the data
    geometry : Polygon, MultiPolygon, str, or list of str
        Area of interest
    time_range : tuple of str
        (start_date, end_date) in 'YYYY-MM-DD' format
    dataset_id : str, optional
        Copernicus product to use
    mask_using_geom : bool, default False
        If True, mask data outside the geometry
    **kwargs
        Additional parameters

    Returns
    -------
    Path : Path to downloaded file
    """
    return fetch_copernicus_data(
        dataset_id=dataset_id,
        variables=['so'],  # Salinity
        output_path=output_path,
        geometry=geometry,
        time_range=time_range,
        depth_range=(0.0, 1.0),  # Surface only
        mask_using_geom=mask_using_geom,
        **kwargs
    )
