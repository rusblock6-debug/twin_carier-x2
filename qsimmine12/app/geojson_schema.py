__all__ = (
    'FEATURE_COLLECTION_FULL',
    'FEATURE_COLLECTION_POINT_LINESTRING',
    'FEATURE_COLLECTION_LINESTRING',
    'FEATURE_COLLECTION_POINT',
)


# https://geojson.org/schema/FeatureCollection.json
# RFC 7946 schema AS IS
FEATURE_COLLECTION_FULL = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "https://geojson.org/schema/FeatureCollection.json",
    "title": "GeoJSON FeatureCollection",
    "type": "object",
    "required": ["type", "features"],
    "properties": {
        "type": {"type": "string", "enum": ["FeatureCollection"]},
        "features": {
            "type": "array",
            "items": {
                "title": "GeoJSON Feature",
                "type": "object",
                "required": ["type", "properties", "geometry"],
                "properties": {
                    "type": {"type": "string", "enum": ["Feature"]},
                    "id": {"oneOf": [{"type": "number"}, {"type": "string"}]},
                    "properties": {"oneOf": [{"type": "null"}, {"type": "object"}]},
                    "geometry": {
                        "oneOf": [
                            {"type": "null"},
                            {
                                "title": "GeoJSON Point",
                                "type": "object",
                                "required": ["type", "coordinates"],
                                "properties": {
                                    "type": {"type": "string", "enum": ["Point"]},
                                    "coordinates": {
                                        "type": "array",
                                        "minItems": 2,
                                        "items": {"type": "number"},
                                    },
                                    "bbox": {
                                        "type": "array",
                                        "minItems": 4,
                                        "items": {"type": "number"},
                                    },
                                },
                            },
                            {
                                "title": "GeoJSON LineString",
                                "type": "object",
                                "required": ["type", "coordinates"],
                                "properties": {
                                    "type": {"type": "string", "enum": ["LineString"]},
                                    "coordinates": {
                                        "type": "array",
                                        "minItems": 2,
                                        "items": {
                                            "type": "array",
                                            "minItems": 2,
                                            "items": {"type": "number"},
                                        },
                                    },
                                    "bbox": {
                                        "type": "array",
                                        "minItems": 4,
                                        "items": {"type": "number"},
                                    },
                                },
                            },
                            {
                                "title": "GeoJSON Polygon",
                                "type": "object",
                                "required": ["type", "coordinates"],
                                "properties": {
                                    "type": {"type": "string", "enum": ["Polygon"]},
                                    "coordinates": {
                                        "type": "array",
                                        "items": {
                                            "type": "array",
                                            "minItems": 4,
                                            "items": {
                                                "type": "array",
                                                "minItems": 2,
                                                "items": {"type": "number"},
                                            },
                                        },
                                    },
                                    "bbox": {
                                        "type": "array",
                                        "minItems": 4,
                                        "items": {"type": "number"},
                                    },
                                },
                            },
                            {
                                "title": "GeoJSON MultiPoint",
                                "type": "object",
                                "required": ["type", "coordinates"],
                                "properties": {
                                    "type": {"type": "string", "enum": ["MultiPoint"]},
                                    "coordinates": {
                                        "type": "array",
                                        "items": {
                                            "type": "array",
                                            "minItems": 2,
                                            "items": {"type": "number"},
                                        },
                                    },
                                    "bbox": {
                                        "type": "array",
                                        "minItems": 4,
                                        "items": {"type": "number"},
                                    },
                                },
                            },
                            {
                                "title": "GeoJSON MultiLineString",
                                "type": "object",
                                "required": ["type", "coordinates"],
                                "properties": {
                                    "type": {"type": "string", "enum": ["MultiLineString"]},
                                    "coordinates": {
                                        "type": "array",
                                        "items": {
                                            "type": "array",
                                            "minItems": 2,
                                            "items": {
                                                "type": "array",
                                                "minItems": 2,
                                                "items": {"type": "number"},
                                            },
                                        },
                                    },
                                    "bbox": {
                                        "type": "array",
                                        "minItems": 4,
                                        "items": {"type": "number"},
                                    },
                                },
                            },
                            {
                                "title": "GeoJSON MultiPolygon",
                                "type": "object",
                                "required": ["type", "coordinates"],
                                "properties": {
                                    "type": {"type": "string", "enum": ["MultiPolygon"]},
                                    "coordinates": {
                                        "type": "array",
                                        "items": {
                                            "type": "array",
                                            "items": {
                                                "type": "array",
                                                "minItems": 4,
                                                "items": {
                                                    "type": "array",
                                                    "minItems": 2,
                                                    "items": {"type": "number"},
                                                },
                                            },
                                        },
                                    },
                                    "bbox": {
                                        "type": "array",
                                        "minItems": 4,
                                        "items": {"type": "number"},
                                    },
                                },
                            },
                            {
                                "title": "GeoJSON GeometryCollection",
                                "type": "object",
                                "required": ["type", "geometries"],
                                "properties": {
                                    "type": {"type": "string", "enum": ["GeometryCollection"]},
                                    "geometries": {
                                        "type": "array",
                                        "items": {
                                            "oneOf": [
                                                {
                                                    "title": "GeoJSON Point",
                                                    "type": "object",
                                                    "required": ["type", "coordinates"],
                                                    "properties": {
                                                        "type": {
                                                            "type": "string",
                                                            "enum": ["Point"],
                                                        },
                                                        "coordinates": {
                                                            "type": "array",
                                                            "minItems": 2,
                                                            "items": {"type": "number"},
                                                        },
                                                        "bbox": {
                                                            "type": "array",
                                                            "minItems": 4,
                                                            "items": {"type": "number"},
                                                        },
                                                    },
                                                },
                                                {
                                                    "title": "GeoJSON LineString",
                                                    "type": "object",
                                                    "required": ["type", "coordinates"],
                                                    "properties": {
                                                        "type": {
                                                            "type": "string",
                                                            "enum": ["LineString"],
                                                        },
                                                        "coordinates": {
                                                            "type": "array",
                                                            "minItems": 2,
                                                            "items": {
                                                                "type": "array",
                                                                "minItems": 2,
                                                                "items": {"type": "number"},
                                                            },
                                                        },
                                                        "bbox": {
                                                            "type": "array",
                                                            "minItems": 4,
                                                            "items": {"type": "number"},
                                                        },
                                                    },
                                                },
                                                {
                                                    "title": "GeoJSON Polygon",
                                                    "type": "object",
                                                    "required": ["type", "coordinates"],
                                                    "properties": {
                                                        "type": {
                                                            "type": "string",
                                                            "enum": ["Polygon"],
                                                        },
                                                        "coordinates": {
                                                            "type": "array",
                                                            "items": {
                                                                "type": "array",
                                                                "minItems": 4,
                                                                "items": {
                                                                    "type": "array",
                                                                    "minItems": 2,
                                                                    "items": {"type": "number"},
                                                                },
                                                            },
                                                        },
                                                        "bbox": {
                                                            "type": "array",
                                                            "minItems": 4,
                                                            "items": {"type": "number"},
                                                        },
                                                    },
                                                },
                                                {
                                                    "title": "GeoJSON MultiPoint",
                                                    "type": "object",
                                                    "required": ["type", "coordinates"],
                                                    "properties": {
                                                        "type": {
                                                            "type": "string",
                                                            "enum": ["MultiPoint"],
                                                        },
                                                        "coordinates": {
                                                            "type": "array",
                                                            "items": {
                                                                "type": "array",
                                                                "minItems": 2,
                                                                "items": {"type": "number"},
                                                            },
                                                        },
                                                        "bbox": {
                                                            "type": "array",
                                                            "minItems": 4,
                                                            "items": {"type": "number"},
                                                        },
                                                    },
                                                },
                                                {
                                                    "title": "GeoJSON MultiLineString",
                                                    "type": "object",
                                                    "required": ["type", "coordinates"],
                                                    "properties": {
                                                        "type": {
                                                            "type": "string",
                                                            "enum": ["MultiLineString"],
                                                        },
                                                        "coordinates": {
                                                            "type": "array",
                                                            "items": {
                                                                "type": "array",
                                                                "minItems": 2,
                                                                "items": {
                                                                    "type": "array",
                                                                    "minItems": 2,
                                                                    "items": {"type": "number"},
                                                                },
                                                            },
                                                        },
                                                        "bbox": {
                                                            "type": "array",
                                                            "minItems": 4,
                                                            "items": {"type": "number"},
                                                        },
                                                    },
                                                },
                                                {
                                                    "title": "GeoJSON MultiPolygon",
                                                    "type": "object",
                                                    "required": ["type", "coordinates"],
                                                    "properties": {
                                                        "type": {
                                                            "type": "string",
                                                            "enum": ["MultiPolygon"],
                                                        },
                                                        "coordinates": {
                                                            "type": "array",
                                                            "items": {
                                                                "type": "array",
                                                                "items": {
                                                                    "type": "array",
                                                                    "minItems": 4,
                                                                    "items": {
                                                                        "type": "array",
                                                                        "minItems": 2,
                                                                        "items": {"type": "number"},
                                                                    },
                                                                },
                                                            },
                                                        },
                                                        "bbox": {
                                                            "type": "array",
                                                            "minItems": 4,
                                                            "items": {"type": "number"},
                                                        },
                                                    },
                                                },
                                            ]
                                        },
                                    },
                                    "bbox": {
                                        "type": "array",
                                        "minItems": 4,
                                        "items": {"type": "number"},
                                    },
                                },
                            },
                        ]
                    },
                    "bbox": {"type": "array", "minItems": 4, "items": {"type": "number"}},
                },
            },
        },
        "bbox": {"type": "array", "minItems": 4, "items": {"type": "number"}},
    },
}


# Only Point and LineString features
FEATURE_COLLECTION_POINT_LINESTRING = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "https://geojson.org/schema/FeatureCollection.json",
    "title": "GeoJSON FeatureCollection",
    "type": "object",
    "required": ["type", "features"],
    "properties": {
        "type": {"type": "string", "enum": ["FeatureCollection"]},
        "features": {
            "type": "array",
            "items": {
                "title": "GeoJSON Feature",
                "type": "object",
                "required": ["type", "properties", "geometry"],
                "properties": {
                    "type": {"type": "string", "enum": ["Feature"]},
                    "id": {"oneOf": [{"type": "number"}, {"type": "string"}]},
                    "properties": {"oneOf": [{"type": "null"}, {"type": "object"}]},
                    "geometry": {
                        "oneOf": [
                            {
                                "title": "GeoJSON Point",
                                "type": "object",
                                "required": ["type", "coordinates"],
                                "properties": {
                                    "type": {"type": "string", "enum": ["Point"]},
                                    "coordinates": {
                                        "type": "array",
                                        "minItems": 2,
                                        "items": {"type": "number"},
                                    },
                                    "bbox": {
                                        "type": "array",
                                        "minItems": 4,
                                        "items": {"type": "number"},
                                    },
                                },
                            },
                            {
                                "title": "GeoJSON LineString",
                                "type": "object",
                                "required": ["type", "coordinates"],
                                "properties": {
                                    "type": {"type": "string", "enum": ["LineString"]},
                                    "coordinates": {
                                        "type": "array",
                                        "minItems": 2,
                                        "items": {
                                            "type": "array",
                                            "minItems": 2,
                                            "items": {"type": "number"},
                                        },
                                    },
                                    "bbox": {
                                        "type": "array",
                                        "minItems": 4,
                                        "items": {"type": "number"},
                                    },
                                },
                            },
                        ]
                    },
                    "bbox": {"type": "array", "minItems": 4, "items": {"type": "number"}},
                },
            },
        },
        "bbox": {"type": "array", "minItems": 4, "items": {"type": "number"}},
    },
}


# Only LineString feature
FEATURE_COLLECTION_LINESTRING = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "https://geojson.org/schema/FeatureCollection.json",
    "title": "GeoJSON FeatureCollection",
    "type": "object",
    "required": ["type", "features"],
    "properties": {
        "type": {"type": "string", "enum": ["FeatureCollection"]},
        "features": {
            "type": "array",
            "items": {
                "title": "GeoJSON Feature",
                "type": "object",
                "required": ["type", "properties", "geometry"],
                "properties": {
                    "type": {"type": "string", "enum": ["Feature"]},
                    "id": {"oneOf": [{"type": "number"}, {"type": "string"}]},
                    "properties": {"oneOf": [{"type": "null"}, {"type": "object"}]},
                    "geometry": {
                        "oneOf": [
                            {
                                "title": "GeoJSON LineString",
                                "type": "object",
                                "required": ["type", "coordinates"],
                                "properties": {
                                    "type": {"type": "string", "enum": ["LineString"]},
                                    "coordinates": {
                                        "type": "array",
                                        "minItems": 2,
                                        "items": {
                                            "type": "array",
                                            "minItems": 2,
                                            "items": {"type": "number"},
                                        },
                                    },
                                    "bbox": {
                                        "type": "array",
                                        "minItems": 4,
                                        "items": {"type": "number"},
                                    },
                                },
                            },
                        ]
                    },
                    "bbox": {"type": "array", "minItems": 4, "items": {"type": "number"}},
                },
            },
        },
        "bbox": {"type": "array", "minItems": 4, "items": {"type": "number"}},
    },
}


# Only Point feature
FEATURE_COLLECTION_POINT = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "https://geojson.org/schema/FeatureCollection.json",
    "title": "GeoJSON FeatureCollection",
    "type": "object",
    "required": ["type", "features"],
    "properties": {
        "type": {"type": "string", "enum": ["FeatureCollection"]},
        "features": {
            "type": "array",
            "items": {
                "title": "GeoJSON Feature",
                "type": "object",
                "required": ["type", "properties", "geometry"],
                "properties": {
                    "type": {"type": "string", "enum": ["Feature"]},
                    "id": {"oneOf": [{"type": "number"}, {"type": "string"}]},
                    "properties": {"oneOf": [{"type": "null"}, {"type": "object"}]},
                    "geometry": {
                        "oneOf": [
                            {
                                "title": "GeoJSON Point",
                                "type": "object",
                                "required": ["type", "coordinates"],
                                "properties": {
                                    "type": {"type": "string", "enum": ["Point"]},
                                    "coordinates": {
                                        "type": "array",
                                        "minItems": 2,
                                        "items": {"type": "number"},
                                    },
                                    "bbox": {
                                        "type": "array",
                                        "minItems": 4,
                                        "items": {"type": "number"},
                                    },
                                },
                            },
                        ]
                    },
                    "bbox": {"type": "array", "minItems": 4, "items": {"type": "number"}},
                },
            },
        },
        "bbox": {"type": "array", "minItems": 4, "items": {"type": "number"}},
    },
}
