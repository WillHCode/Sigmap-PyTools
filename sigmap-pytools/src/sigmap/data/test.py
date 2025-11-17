from shapely.geometry import shape, Polygon, MultiPolygon, mapping
from shapely.ops import unary_union
from typing import Union


def geojson_to_shape(
        geojson: dict,
        merge_features: bool = True
) -> Union[Polygon, MultiPolygon]:
    """
    Convert a GeoJSON FeatureCollection to a Shapely Polygon or MultiPolygon.

    Args:
        geojson: A GeoJSON dict with a 'features' key
        merge_features: If True, merge overlapping/touching polygons using unary_union

    Returns:
        Polygon if single feature or merged into one shape
        MultiPolygon if multiple separate features

    Raises:
        ValueError: If GeoJSON is invalid or contains no polygon features
    """
    features = geojson.get("features", [])
    if not features:
        raise ValueError("GeoJSON has no features")

    # Convert feature geometries to Shapely objects
    shapes = []
    for f in features:
        geom = shape(f["geometry"])
        if isinstance(geom, (Polygon, MultiPolygon)):
            shapes.append(geom)
        else:
            raise ValueError(
                f"Feature must be Polygon or MultiPolygon, got {geom.geom_type}"
            )

    if not shapes:
        raise ValueError("No valid polygon features found")

    # Single feature case
    if len(shapes) == 1:
        return shapes[0]

    # Multiple features
    if merge_features:
        merged = unary_union(shapes)

        # Handle different return types from unary_union
        if isinstance(merged, (Polygon, MultiPolygon)):
            return merged

        # Extract polygons from GeometryCollection
        polys = [g for g in merged.geoms if isinstance(g, Polygon)]
        if not polys:
            raise ValueError("No polygons found after merging")

        return MultiPolygon(polys) if len(polys) > 1 else polys[0]

    # No merging: collect all polygons
    polygons = []
    for g in shapes:
        if isinstance(g, Polygon):
            polygons.append(g)
        elif isinstance(g, MultiPolygon):
            polygons.extend(g.geoms)

    return MultiPolygon(polygons) if len(polygons) > 1 else polygons[0]


def shape_to_geojson(
        geom: Union[Polygon, MultiPolygon],
        split_multipolygons: bool = False
) -> dict:
    """
    Convert a Shapely Polygon or MultiPolygon to a GeoJSON FeatureCollection.

    Args:
        geom: A Shapely Polygon or MultiPolygon
        split_multipolygons: If True, split MultiPolygon into separate features
                            If False, keep MultiPolygon as single feature

    Returns:
        GeoJSON FeatureCollection dict

    Raises:
        ValueError: If input is not a Polygon or MultiPolygon
    """
    if isinstance(geom, Polygon):
        return {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {},
                    "geometry": mapping(geom)
                }
            ],
        }

    if isinstance(geom, MultiPolygon):
        if split_multipolygons:
            # Create separate features for each polygon
            features = [
                {
                    "type": "Feature",
                    "properties": {},
                    "geometry": mapping(poly)
                }
                for poly in geom.geoms
            ]
        else:
            # Keep as single MultiPolygon feature
            features = [
                {
                    "type": "Feature",
                    "properties": {},
                    "geometry": mapping(geom)
                }
            ]

        return {
            "type": "FeatureCollection",
            "features": features
        }

    raise ValueError(
        f"Input geometry must be Polygon or MultiPolygon, got {geom.geom_type}"
    )


# Example usage
if __name__ == '__main__':
    geojson = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {},
                "geometry": {
                    "coordinates": [
                        [
                            [119.54, 37.98],
                            [120.07, 37.44],
                            [118.46, 37.41],
                            [115.82, 40.59],
                            [119.54, 37.98]
                        ]
                    ],
                    "type": "Polygon"
                }
            }
        ]
    }

    geom = geojson_to_shape(geojson)
    print(f"Geometry type: {geom.geom_type}")

    geo = shape_to_geojson(geom)
    print(f"Features: {len(geo['features'])}")