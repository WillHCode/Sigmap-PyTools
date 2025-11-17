import math

import geopandas as gpd
from shapely.geometry import box

from ..logger import logging

logger = logging.getLogger(__name__)

__BASE32 = "0123456789bcdefghjkmnpqrstuvwxyz"
_base32_map = {c: i for i, c in enumerate(__BASE32)}


def lonlat_res_for_length(L: int):
    """
    Calculate longitude and latitude resolution for given geohash length.
    
    Parameters
    ----------
    L : int
        Geohash string length
    
    Returns
    -------
    tuple
        (lon_res, lat_res) in degrees
    """
    total_bits = 5 * L
    lon_bits = math.ceil(total_bits / 2.0)
    lat_bits = math.floor(total_bits / 2.0)
    lon_res = 360.0 / (2 ** lon_bits)
    lat_res = 180.0 / (2 ** lat_bits)
    return lon_res, lat_res


def encode_geohash(lon: float, lat: float, L: int):
    """
    Encode longitude and latitude to geohash string.
    
    Parameters
    ----------
    lon : float
        Longitude in degrees [-180, 180]
    lat : float
        Latitude in degrees [-90, 90]
    L : int
        Desired geohash string length
    
    Returns
    -------
    str
        Geohash string of length L
    """
    lon_interval = [-180.0, 180.0]
    lat_interval = [-90.0, 90.0]
    bits = []
    total_bits = 5 * L
    is_lon = True
    for _ in range(total_bits):
        if is_lon:
            mid = (lon_interval[0] + lon_interval[1]) / 2.0
            if lon >= mid:
                bits.append(1)
                lon_interval[0] = mid
            else:
                bits.append(0)
                lon_interval[1] = mid
        else:
            mid = (lat_interval[0] + lat_interval[1]) / 2.0
            if lat >= mid:
                bits.append(1)
                lat_interval[0] = mid
            else:
                bits.append(0)
                lat_interval[1] = mid
        is_lon = not is_lon

    geohash = []
    for i in range(0, total_bits, 5):
        v = 0
        for b in bits[i:i + 5]:
            v = (v << 1) | b
        geohash.append(__BASE32[v])
    return "".join(geohash)


def candidate_geohashes_covering_bbox(lon_min, lat_min, lon_max, lat_max, L):
    """
    Generate candidate geohashes that could intersect a bounding box.
    
    Parameters
    ----------
    lon_min : float
        Minimum longitude of bbox
    lat_min : float
        Minimum latitude of bbox
    lon_max : float
        Maximum longitude of bbox
    lat_max : float
        Maximum latitude of bbox
    L : int
        Geohash length
    
    Returns
    -------
    list
        List of tuples (geohash, lon, lat)
    """
    lon_res, lat_res = lonlat_res_for_length(L)

    lon_cells_min = int((lon_min + 180.0) / lon_res)
    lon_cells_max = int((lon_max + 180.0) / lon_res) + 1

    lat_cells_min = int((lat_min + 90.0) / lat_res)
    lat_cells_max = int((lat_max + 90.0) / lat_res) + 1

    geos = []
    seen = set()

    for i in range(lon_cells_min, lon_cells_max + 1):
        lon = -180.0 + (i + 0.5) * lon_res
        # Ensure longitude is in valid range
        if lon < -180 or lon > 180:
            continue

        for j in range(lat_cells_min, lat_cells_max + 1):
            lat = -90.0 + (j + 0.5) * lat_res
            # Ensure latitude is in valid range
            if lat < -90 or lat > 90:
                continue

            if (lon_min - lon_res <= lon <= lon_max + lon_res and
                    lat_min - lat_res <= lat <= lat_max + lat_res):
                gh = encode_geohash(lon, lat, L)
                if gh not in seen:
                    seen.add(gh)
                    geos.append((gh, lon, lat))

    return geos


def geohash_to_bbox(gh: str):
    """
    Decode geohash string to bounding box coordinates.
    
    Parameters
    ----------
    gh : str
        Geohash string to decode
    
    Returns
    -------
    tuple
        (lon_min, lat_min, lon_max, lat_max) in degrees
    """
    lon_min, lon_max = -180.0, 180.0
    lat_min, lat_max = -90.0, 90.0
    is_lon = True

    bits = []
    for c in gh:
        v = _base32_map[c]
        # each base32 char -> 5 bits (16,8,4,2,1)
        for i in (16, 8, 4, 2, 1):
            bits.append(1 if (v & i) else 0)

    for b in bits:
        if is_lon:
            mid = (lon_min + lon_max) / 2.0
            if b:
                lon_min = mid
            else:
                lon_max = mid
        else:
            mid = (lat_min + lat_max) / 2.0
            if b:
                lat_min = mid
            else:
                lat_max = mid
        is_lon = not is_lon

    return lon_min, lat_min, lon_max, lat_max


def geohash_to_polygon(gh: str):
    """
    Convert geohash to shapely box polygon.
    
    Parameters
    ----------
    gh : str
        Geohash string
    
    Returns
    -------
    shapely.geometry.Polygon
        Box polygon representing the geohash cell
    """
    lon_min, lat_min, lon_max, lat_max = geohash_to_bbox(gh)
    return box(lon_min, lat_min, lon_max, lat_max)


def geohashes_to_gdf(geos, crs='EPSG:4326'):
    """
    Convert geohashes to GeoDataFrame.
    
    Parameters
    ----------
    geos : list or str
        List of geohashes or tuples (geohash, lon, lat), or single geohash
    crs : str, default 'EPSG:4326'
        Coordinate reference system
    
    Returns
    -------
    gpd.GeoDataFrame
        GeoDataFrame with geohash codes and polygon geometries
    """
    polys = []
    codes = []
    for item in geos:
        # Handle both string and tuple inputs
        if isinstance(item, tuple):
            gh = item[0]
        else:
            gh = item

        try:
            p = geohash_to_polygon(gh)
        except Exception as e:
            logger.error(f"Failed to convert geohash {gh}: {e}")
            continue
        polys.append(p)
        codes.append(gh)

    gdf = gpd.GeoDataFrame({'geohash': codes, 'geometry': polys}, crs=crs)
    return gdf


def get_geohash_children(parent_geohash: str):
    """
    Generate all child geohashes for a given parent geohash.
    
    Each parent geohash has exactly 32 children (one for each base32 character).
    Each child adds one character of precision.
    
    Parameters
    ----------
    parent_geohash : str
        Parent geohash string
    
    Returns
    -------
    list
        List of 32 child geohash strings
    """
    children = []
    for char in __BASE32:
        children.append(parent_geohash + char)
    return children


def geohashes_to_boxes(geohashes):
    """
    Convert geohash(es) to a dictionary mapping geohash strings to box polygons.

    Parameters
    ----------
    geohashes : str or list of str
        Single geohash string or list of geohash strings

    Returns
    -------
    dict : Dictionary mapping geohash string to shapely box polygon
        {geohash: box_polygon, ...}

    Examples
    --------
    >>> # Single geohash
    >>> boxes = geohashes_to_boxes("u4pruyd")
    >>> print(boxes)
    {'u4pruyd': <Box polygon>}

    >>> # Multiple geohashes
    >>> boxes = geohashes_to_boxes(["u4pru", "u4prv", "u4prw"])
    >>> print(len(boxes))
    3

    >>> # Access a specific box
    >>> box_poly = boxes["u4pru"]
    >>> print(box_poly.bounds)  # (lon_min, lat_min, lon_max, lat_max)
    """
    # Handle single string input
    if isinstance(geohashes, str):
        geohashes = [geohashes]

    result = {}
    for gh in geohashes:
        try:
            lon_min, lat_min, lon_max, lat_max = geohash_to_bbox(gh)
            result[gh] = box(lon_min, lat_min, lon_max, lat_max)
        except Exception as e:
            logger.error(f"Failed to convert geohash {gh} to box: {e}")
            continue

    return result


def geohashes_to_multipolygon(geohashes_or_dict, dissolve=True):
    """
    Convert geohashes to a MultiPolygon by unioning all box polygons.

    Parameters
    ----------
    geohashes_or_dict : str, list of str, or dict
        - Single geohash string
        - List of geohash strings
        - Dictionary from geohashes_to_boxes() {geohash: box_polygon}
    dissolve : bool, default True
        If True, dissolve overlapping/adjacent boxes into single polygons
        If False, keep as separate polygons in MultiPolygon

    Returns
    -------
    MultiPolygon or Polygon : Union of all geohash boxes
        Returns Polygon if union results in single polygon,
        MultiPolygon if multiple disjoint regions

    Examples
    --------
    >>> # From list of geohashes
    >>> geohashes = ["u4pru", "u4prv", "u4prw"]
    >>> multi_poly = geohashes_to_multipolygon(geohashes)
    >>> print(multi_poly.area)

    >>> # From dictionary
    >>> boxes = geohashes_to_boxes(geohashes)
    >>> multi_poly = geohashes_to_multipolygon(boxes)

    >>> # Without dissolving (keep separate)
    >>> multi_poly = geohashes_to_multipolygon(geohashes, dissolve=False)
    """
    from shapely.geometry import MultiPolygon, Polygon
    from shapely.ops import unary_union

    # If input is a dictionary, extract the box polygons
    if isinstance(geohashes_or_dict, dict):
        boxes = list(geohashes_or_dict.values())
    else:
        # Convert geohashes to boxes
        boxes_dict = geohashes_to_boxes(geohashes_or_dict)
        boxes = list(boxes_dict.values())

    if not boxes:
        logger.warning("No valid boxes to convert to MultiPolygon")
        return MultiPolygon([])  # Empty MultiPolygon

    if dissolve:
        # Use unary_union to merge overlapping/adjacent polygons
        result = unary_union(boxes)

        # Ensure result is a MultiPolygon or Polygon
        if isinstance(result, Polygon):
            return result  # Single polygon is fine
        elif isinstance(result, MultiPolygon):
            return result
        else:
            # Fallback for unexpected geometry types
            logger.warning(f"Union resulted in unexpected geometry type: {type(result)}")
            return MultiPolygon([result]) if hasattr(result, '__geo_interface__') else MultiPolygon([])
    else:
        # Keep as separate polygons
        return MultiPolygon(boxes)


# Convenience functions for common operations
def coverage_dict_to_multipolygon(geohash_dict, dissolve=True):
    """
    Convert a coverage dictionary to a MultiPolygon.

    Useful for converting the output of adaptive_geohash_coverage() or
    geohash_coverage() directly to a polygon.

    Parameters
    ----------
    geohash_dict : dict
        Dictionary with level as keys and list of geohashes as values
        (output from coverage functions)
    dissolve : bool, default True
        Whether to dissolve adjacent polygons

    Returns
    -------
    MultiPolygon or Polygon : Union of all geohashes in the dict

    Example
    -------
    >>> geohash_dict, tiles_gdf = adaptive_geohash_coverage(country_geom, 3, 5)
    >>> coverage_polygon = coverage_dict_to_multipolygon(geohash_dict)
    """
    all_geohashes = []
    for level, geohashes in geohash_dict.items():
        all_geohashes.extend(geohashes)

    return geohashes_to_multipolygon(all_geohashes, dissolve=dissolve)


def coverage_dict_to_multipolygon_by_level(geohash_dict, dissolve=True):
    """
    Convert a coverage dictionary to separate MultiPolygons per level.

    Parameters
    ----------
    geohash_dict : dict
        Dictionary with level as keys and list of geohashes as values
    dissolve : bool, default True
        Whether to dissolve adjacent polygons

    Returns
    -------
    dict : Dictionary mapping level to MultiPolygon/Polygon
        {level: MultiPolygon, ...}

    Example
    -------
    >>> geohash_dict, tiles_gdf = adaptive_geohash_coverage(country_geom, 3, 5)
    >>> level_polygons = coverage_dict_to_multipolygon_by_level(geohash_dict)
    >>> print(level_polygons[3].area)  # Area covered by level 3 tiles
    """
    result = {}
    for level, geohashes in geohash_dict.items():
        result[level] = geohashes_to_multipolygon(geohashes, dissolve=dissolve)
    return result