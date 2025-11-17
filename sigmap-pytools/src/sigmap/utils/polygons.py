from typing import Union, List

import geopandas as gpd
from shapely import Polygon, MultiPolygon
from shapely import unary_union, GeometryCollection

from sigmap.utils.geohash import geohash_to_bbox, geohashes_to_boxes

def geometry_to_bbox(
        geometry: Union[Polygon, MultiPolygon, str, List[str], None]
) -> tuple[float, float, float, float] | tuple :
    """
    Convert various geometry inputs to bounding box (lon_min, lat_min, lon_max, lat_max).

    Parameters
    ----------
    geometry : Polygon, MultiPolygon, str, list of str, or None
        - Shapely Polygon/MultiPolygon
        - Single geohash string
        - List of geohash strings
        - None (returns global bbox)

    Returns
    -------
    tuple: (lon_min, lat_min, lon_max, lat_max)
    """
    if geometry is None:
        return -180.0, -90.0, 180.0, 90.0

    if isinstance(geometry, str):
        # Single geohash
        return geohash_to_bbox(geometry)

    if isinstance(geometry, list):
        # List of geohashes
        boxes = geohashes_to_boxes(geometry)
        all_bounds = [poly.bounds for poly in boxes.values()]
        lon_min = min(b[0] for b in all_bounds)
        lat_min = min(b[1] for b in all_bounds)
        lon_max = max(b[2] for b in all_bounds)
        lat_max = max(b[3] for b in all_bounds)
        return lon_min, lat_min, lon_max, lat_max

    if isinstance(geometry, (Polygon, MultiPolygon)):
        # Shapely geometry
        return geometry.bounds

    raise TypeError(
        f"Unsupported geometry type: {type(geometry)}. "
        "Expected Polygon, MultiPolygon, geohash string, or list of geohashes."
    )

def build_single_multipolygon(gdf: gpd.GeoDataFrame) -> MultiPolygon:
    """
    Build a single MultiPolygon from a GeoDataFrame of geometries.
    
    Converts all geometries in the GeoDataFrame into a single unified MultiPolygon.
    Handles invalid geometries, GeometryCollections, and mixed geometry types.

    Parameters
    ----------
    gdf : gpd.GeoDataFrame
        GeoDataFrame containing geometries to unite

    Returns
    -------
    MultiPolygon
        Unified MultiPolygon geometry
    """
    geom = unary_union(gdf.geometry.values)

    if isinstance(geom, GeometryCollection):
        polys = [p for p in geom.geoms if isinstance(p, (Polygon, MultiPolygon))]
        if not polys:
            raise RuntimeError("No polygonal geometry could be extracted from the Country geometries.")
        geom = unary_union(polys)

    if isinstance(geom, Polygon):
        geom = MultiPolygon([geom])
    elif isinstance(geom, MultiPolygon):
        pass
    else:
        # try to coerce to multipolygon by taking polygons within
        poly_parts = []
        for part in geom:
            if isinstance(part, Polygon):
                poly_parts.append(part)
            elif isinstance(part, MultiPolygon):
                poly_parts.extend(list(part))
        if not poly_parts:
            raise RuntimeError("Geometry type is not polygonal and could not be converted.")
        geom = MultiPolygon(poly_parts)

    if not geom.is_valid:
        geom = geom.buffer(0)

    return geom