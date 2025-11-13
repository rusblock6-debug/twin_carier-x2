import pathlib
from typing import Union

import pytest

from app.dxf.dxf_converter import DXFConverter


class TestDXFConverter:
    test_files_dir = pathlib.Path(__file__).parent / 'files'

    @pytest.mark.parametrize('filename', [
        '3D_модель_ОГОК.dxf',
        'PV_351_№51с_разворотом_кабиной_на_север.dxf',
        'PV-351 №51.dxf',
        'u_300916_2_280.dxf',
        'voids1.dxf',
        'vst_12122016 - копия.dxf',
        'y_test0712_1_290.dxf',
        'поверхность съезда3.dxf',
        'РС1250-08.dxf',
        'ю_210716_1_290.dxf',
    ])
    def test_geojson_structure(self, filename: str) -> None:
        converter = DXFConverter(0, 0, 0)
        file_path = self.test_files_dir / filename

        geojson_result = converter.convert_dxf_to_geojson(file_path)

        assert isinstance(geojson_result, dict)
        assert 'type' in geojson_result
        assert geojson_result['type'] == 'FeatureCollection'
        assert 'features' in geojson_result
        assert isinstance(geojson_result['features'], list)

        for feature in geojson_result['features']:
            assert isinstance(feature, dict)

            assert 'type' in feature
            assert feature['type'] == 'Feature'

            assert 'properties' in feature
            assert isinstance(feature['properties'], dict)

            assert 'geometry' in feature
            assert isinstance(feature['geometry'], dict)

            properties = feature['properties']
            assert 'name' in properties
            assert isinstance(properties['name'], str)

            geometry = feature['geometry']
            assert 'type' in geometry
            assert geometry['type'] == 'LineString'

            assert 'coordinates' in geometry
            assert isinstance(geometry['coordinates'], list)
            assert len(geometry['coordinates']) >= 2

            for coordinate_pack in geometry['coordinates']:
                assert isinstance(coordinate_pack, (list, tuple))
                assert 2 <= len(coordinate_pack) <= 3

                for coord in coordinate_pack:
                    assert isinstance(coord, Union[int, float])
