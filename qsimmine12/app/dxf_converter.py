import logging
import pathlib
import re

from ezdxf.entities.dxfgfx import DXFGraphic
from ezdxf.entities.line import Line
from ezdxf.entities.lwpolyline import LWPolyline
from ezdxf.entities.polyline import Polyline
from ezdxf.filemanagement import readfile as ezdxf_readfile

from app.geo_utils import local_to_global

__all__ = (
    'DXFConverter',
)

logger = logging.getLogger(__name__)


class DXFConverter:

    def __init__(self, anchor_lat: float, anchor_lon: float, anchor_height: float | None) -> None:
        self.anchor_lat = anchor_lat
        self.anchor_lon = anchor_lon
        self.anchor_height = anchor_height

    def convert_coords(self, x: float, y: float, z: float | None = None) -> tuple[float, float, float | None]:
        lat, lon, alt = local_to_global(
            x, y, z, self.anchor_lat, self.anchor_lon, self.anchor_height
        )
        return lat, lon, alt

    def safe_geojson_coords(
            self,
            x: float,
            y: float,
            z: float | None
    ) -> tuple[float, float] | tuple[float, float, float]:
        if z is None:
            return (y, x)
        return (y, x, z)

    def extract_elevation_from_str(self, layer_name: str) -> float | None:
        """Extract elevation from layer name"""
        # Look for elevation patterns like "Горизонт_100м", "205м", etc.
        elevation_match = re.search(r'(\d+)м', layer_name)
        if elevation_match:
            elevation = float(elevation_match.group(1))
            return elevation
        return None

    def process_line(self, line: Line, layer_name: str, elevation: float | None) -> dict:
        """Process LINE entity"""

        start_coords = self.convert_coords(*line.dxf.start.xyz)
        start_coords_safe = self.safe_geojson_coords(*start_coords)
        end_coords = self.convert_coords(*line.dxf.end.xyz)
        end_coords_safe = self.safe_geojson_coords(*end_coords)

        feature = {
            'type': 'Feature',
            'properties': {
                'name': layer_name,
                'elevation': elevation
            },
            'geometry': {
                'type': 'LineString',
                'coordinates': [start_coords_safe, end_coords_safe]
            }
        }
        return feature

    def process_polyline(self, polyline: Polyline, layer_name: str, elevation: float | None) -> dict | None:
        """Process POLYLINE entity"""

        coords_list = []
        for vertex in polyline.vertices:
            coords = self.convert_coords(*vertex.dxf.location.xyz)
            coords_safe = self.safe_geojson_coords(*coords)
            coords_list.append(coords_safe)
        if len(coords_list) < 2:
            return

        feature = {
            'type': 'Feature',
            'properties': {
                'name': layer_name,
                'elevation': elevation
            },
            'geometry': {
                'type': 'LineString',
                'coordinates': coords_list
            }
        }
        return feature

    def process_lwpolyline(self, lwpolyline: LWPolyline, layer_name: str, elevation: float | None) -> dict | None:
        """Process LWPOLYLINE entity"""

        coords_list = []
        for point in lwpolyline.get_points():
            coords = self.convert_coords(point[0], point[1], lwpolyline.dxf.elevation)
            coords_safe = self.safe_geojson_coords(*coords)
            coords_list.append(coords_safe)
        if len(coords_list) < 2:
            return

        feature = {
            'type': 'Feature',
            'properties': {
                'name': layer_name,
                'elevation': elevation
            },
            'geometry': {
                'type': 'LineString',
                'coordinates': coords_list
            }
        }
        return feature

    def convert_dxf_to_geojson(self, dxf_file: pathlib.Path) -> dict:
        """Convert DXF file to GeoJSON format"""

        logger.info('Loading DXF-file for conversion to GeoJSON: %s', dxf_file)

        # Try different encodings
        for encoding in ('cp1251', 'utf-8', 'latin1'):
            try:
                doc = ezdxf_readfile(dxf_file, encoding=encoding, errors='strict')
                logger.info('Loaded DXF-file with encoding: %s', encoding)
                break
            except Exception:
                logger.exception('Failed to load DXF-file with encoding: %s', encoding)
                continue
        else:
            raise Exception('Failed to load DXF-file with any encoding')

        model_space = doc.modelspace()

        layer_entities: dict[str, list[DXFGraphic]] = {}
        total_entities = 0

        # Group entities by layer
        for entity in model_space:
            layer_name = entity.dxf.layer
            if layer_name not in layer_entities:
                layer_entities[layer_name] = []
            layer_entities[layer_name].append(entity)
            total_entities += 1

        logger.info('Found %s objects within %s layers', total_entities, len(layer_entities))

        features = []
        feature_collection = {
            'type': 'FeatureCollection',
            'features': features
        }

        # Process entities by layer
        for layer_name, entities in layer_entities.items():
            logger.info('Processing layer: %s (%s objects)', layer_name, len(entities))
            elevation = self.extract_elevation_from_str(layer_name)

            for entity in entities:
                dxf_type = entity.dxftype()
                match dxf_type:
                    case 'LINE':
                        features.append(self.process_line(entity, layer_name, elevation))
                    case 'POLYLINE':
                        features.append(self.process_polyline(entity, layer_name, elevation))
                    case 'LWPOLYLINE':
                        features.append(self.process_lwpolyline(entity, layer_name, elevation))
                    case _:
                        logger.warning('Skipping entity with type: %s', dxf_type)

        logger.info('Finished conversion of DXF-file: %s (total features %s)', dxf_file, len(features))
        return feature_collection
