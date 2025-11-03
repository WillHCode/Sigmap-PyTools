import geopandas as gpd
from shapely import unary_union, GeometryCollection, Polygon, MultiPolygon

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