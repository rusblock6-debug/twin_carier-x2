import math

from pyproj import Geod

__all__ = (
    'calc_distance',
    'local_to_global',
)


def calc_distance(
        coord0: tuple[float, float, float | None],
        coord1: tuple[float, float, float | None],
        geod: Geod | None = None
) -> float:
    if geod is None:
        geod = Geod(ellps='WGS84')
    # distance 2d
    az_f, az_b, distance = geod.inv(coord0[0], coord0[1], coord1[0], coord1[1])
    if coord0[2] is not None and coord1[2] is not None:
        # distance 3d
        distance = math.hypot(distance, coord1[2] - coord0[2])
    return distance


def local_to_global(
        x: float,
        y: float,
        z: float | None,
        lat0: float,
        lon0: float,
        alt0: float | None
) -> tuple[float, float, float | None]:
    rad = 0 * math.pi / 180
    cos_r = math.cos(rad)
    sin_r = math.sin(rad)
    rx = x * cos_r - y * sin_r
    ry = x * sin_r + y * cos_r

    metersPerDegree = 111000
    delta_lat = ry / metersPerDegree
    delta_lon = rx / (metersPerDegree * math.cos(lat0 * math.pi / 180))

    if z is not None and alt0 is not None:
        alt = alt0 + z
    else:
        alt = None

    return lat0 + delta_lat, lon0 + delta_lon, alt
