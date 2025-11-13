import logging
import pathlib
import re

from ezdxf import colors
from ezdxf.entities.dxfgfx import DXFGraphic
from ezdxf.entities.line import Line
from ezdxf.entities.lwpolyline import LWPolyline
from ezdxf.entities.polyline import Polyline
from ezdxf.filemanagement import readfile as ezdxf_readfile
from ezdxf.lldxf.const import VALID_DXF_LINEWEIGHTS

from app.dxf.exceptions import DXFConversionException
from app.dxf.schemas import SimpleStyleProperties
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

    def convert_dxf_to_geojson(self, dxf_file: pathlib.Path) -> dict:
        logger.info(f"Loading DXF-file for conversion to GeoJSON: {dxf_file}")

        doc = None
        for encoding in (None, 'cp1251', 'utf-8', 'latin1'):
            try:
                doc = ezdxf_readfile(dxf_file, encoding=encoding, errors='strict')
                logger.debug(f"Loaded DXF-file with encoding: {encoding}")
                break
            except Exception as e:
                logger.exception('Failed to load DXF-file with encoding: %s', encoding, {
                    'original_exception_message': str(e),
                })
                continue

        if doc is None:
            raise Exception('Failed to load DXF-file with any encoding')

        model_space = doc.modelspace()

        layer_entities: dict[str, list[DXFGraphic]] = {}
        total_entities = 0

        for entity in model_space:
            layer_name = entity.dxf.layer
            if layer_name not in layer_entities:
                layer_entities[layer_name] = []
            layer_entities[layer_name].append(entity)
            total_entities += 1

        logger.debug(f"Found {total_entities} objects within {len(layer_entities)} layers")

        features = []
        feature_collection = {
            'type': 'FeatureCollection',
            'features': features
        }

        skipped_entity_types = set()

        for layer_name, entities in layer_entities.items():
            logger.debug(f"Processing layer '{layer_name}' ({len(entities)} entities)")

            for entity in entities:
                dxf_type = entity.dxftype()
                match dxf_type:
                    case 'LINE':
                        entity: Line
                        features.append(self._process_line(entity, layer_name))
                    case 'POLYLINE':
                        entity: Polyline
                        features.append(self._process_polyline(entity, layer_name))
                    case 'LWPOLYLINE':
                        entity: LWPolyline
                        features.append(self._process_lwpolyline(entity, layer_name))
                    case _:
                        skipped_entity_types.add(dxf_type)

        if len(skipped_entity_types) > 0:
            logger.warning(f"Skipped entity types: {skipped_entity_types}")

        logger.info(f"Finished conversion of DXF-file: {dxf_file} (total features {len(features)})")

        return feature_collection

    def _convert_coords(self, x: float, y: float, z: float | None = None) -> tuple[float, float, float | None]:
        lat, lon, alt = local_to_global(
            x, y, z, self.anchor_lat, self.anchor_lon, self.anchor_height
        )
        return lat, lon, alt

    @staticmethod
    def _safe_geojson_coords(
            x: float,
            y: float,
            z: float | None
    ) -> tuple[float, float] | tuple[float, float, float]:
        if z is None:
            return y, x
        return y, x, z

    @staticmethod
    def _extract_elevation_from_str(layer_name: str) -> float | None:
        # Look for elevation patterns like "Горизонт_100м", "205м", etc.
        elevation_match = re.search(r'(\d+)м', layer_name)
        if elevation_match:
            elevation = float(elevation_match.group(1))
            return elevation
        return None

    def _process_line(self, line: Line, layer_name: str) -> dict:
        start_coords = self._convert_coords(*line.dxf.start.xyz)
        start_coords_safe = self._safe_geojson_coords(*start_coords)
        end_coords = self._convert_coords(*line.dxf.end.xyz)
        end_coords_safe = self._safe_geojson_coords(*end_coords)

        coordinates = [start_coords_safe, end_coords_safe]

        return self.__build_feature(line, layer_name, coordinates)

    def _process_polyline(self, polyline: Polyline, layer_name: str) -> dict | None:
        coords_list = []
        for vertex in polyline.vertices:
            coords = self._convert_coords(*vertex.dxf.location.xyz)
            coords_safe = self._safe_geojson_coords(*coords)
            coords_list.append(coords_safe)
        if len(coords_list) < 2:
            return None

        return self.__build_feature(polyline, layer_name, coords_list)

    def _process_lwpolyline(self, lwpolyline: LWPolyline, layer_name: str) -> dict | None:
        coords_list = []
        for point in lwpolyline.get_points():
            coords = self._convert_coords(point[0], point[1], lwpolyline.dxf.elevation)
            coords_safe = self._safe_geojson_coords(*coords)
            coords_list.append(coords_safe)
        if len(coords_list) < 2:
            return None

        return self.__build_feature(lwpolyline, layer_name, coords_list)

    def __build_feature(self, entity: DXFGraphic, layer_name: str, coordinates: list) -> dict:
        simple_style_properties = self.__extract_simple_style_properties(entity)
        elevation = self._extract_elevation_from_str(layer_name)

        return {
            'type': 'Feature',
            'properties': {
                'name': layer_name,
                'elevation': elevation,
                'stroke': simple_style_properties.stroke,
                'stroke-width': simple_style_properties.stroke_width,
                'stroke-opacity': simple_style_properties.stroke_opacity,
            },
            'geometry': {
                'type': 'LineString',
                'coordinates': coordinates
            }
        }

    def __extract_simple_style_properties(self, entity: DXFGraphic) -> SimpleStyleProperties:
        lineweight = self.__extract_entity_lineweight(entity)

        if lineweight not in VALID_DXF_LINEWEIGHTS:
            raise DXFConversionException(f"Line weight {lineweight} is not a valid DXF line weight")

        hex_color = self.__extract_entity_color(entity)

        opacity = 0 if (hex_color is None) else 1
        stroke_width = float(lineweight / 100)
        hex_color = hex_color or '#000000'

        return SimpleStyleProperties(
            stroke=hex_color,
            stroke_width=stroke_width,
            stroke_opacity=opacity,
        )

    @staticmethod
    def __extract_entity_lineweight(entity: DXFGraphic) -> float:
        """
        https://ezdxf.readthedocs.io/en/stable/dxfentities/dxfgfx.html#ezdxf.entities.DXFGraphic.dxf.lineweight

        DXFGraphic.dxf.lineweight
        Line weight in mm times 100 (e.g. 0.13mm = 13).
        There are fixed valid lineweights which are accepted by AutoCAD, other values prevents AutoCAD from loading the
        DXF document, BricsCAD isn’t that picky. (requires DXF R2000)

        Constants defined in ezdxf.lldxf.const
        -1 LINEWEIGHT_BYLAYER
        -2 LINEWEIGHT_BYBLOCK
        -3 LINEWEIGHT_DEFAULT

        Valid DXF lineweights stored in VALID_DXF_LINEWEIGHTS:
        0, 5, 9, 13, 15, 18, 20, 25, 30, 35, 40, 50, 53, 60, 70, 80, 90, 100, 106, 120, 140, 158, 200, 211
        """

        doc = entity.doc

        entity_lineweight = entity.dxf.lineweight
        default_lineweight = 25  # стандартное значение по умолчанию (обычно 0.25mm = 25)

        match entity_lineweight:
            case -1:  # LINEWEIGHT_BYLAYER
                try:
                    layer = doc.layers.get(entity.dxf.layer) if doc else None
                except Exception:
                    # ezdxf.lldxf.const.DXFTableEntryError: BLG$440$FAKT
                    return default_lineweight

                if layer and hasattr(layer.dxf, 'lineweight') and layer.dxf.lineweight >= 0:
                    return layer.dxf.lineweight

                return default_lineweight

            case -2:  # LINEWEIGHT_BYBLOCK
                # Толщину из блока извлечь не удалось, возможно это лишнее, пока не обрабатываем
                return default_lineweight

            case -3:  # LINEWEIGHT_DEFAULT
                return default_lineweight

        return entity_lineweight

    @staticmethod
    def __extract_entity_color(entity: DXFGraphic) -> str | None:
        doc = entity.doc
        color_code = entity.dxf.color

        match color_code:
            case 257:
                return None

            case 256:  # 256 - ByLayer (принимает цвет слоя)
                layer = entity.dxf.layer
                layer_color = doc.layers.get(layer).dxf.color
                if 0 < layer_color < 256:
                    return colors.aci2rgb(layer_color).to_hex()

            case 0:  # 0 - ByBlock (принимает цвет блока)
                # Цвет из блока извлечь не удалось, возможно это лишнее, пока не обрабатываем
                return None

            case _:
                if 0 < color_code < 256:
                    return colors.aci2rgb(color_code).to_hex()

        return None
