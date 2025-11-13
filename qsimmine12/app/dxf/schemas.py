import re
from typing import Literal

from pydantic import field_validator, Field, BaseModel


class SimpleStyleProperties(BaseModel):
    """ https://github.com/mapbox/simplestyle-spec/tree/master/1.1.0 """

    """
    OPTIONAL: default ""
    A title to show when this item is clicked or
    hovered over

    "title": "A title",
    """
    title: str = Field(default='')

    """
    OPTIONAL: default ""
    A description to show when this item is clicked or
    hovered over

    "description": "A description",
    """
    description: str = Field(default='')

    """
    OPTIONAL: default "medium"
    specify the size of the marker. sizes
    can be different pixel sizes in different
    implementations
    Value must be one of
    "small"
    "medium"
    "large"

    "marker-size": "medium",
    """
    marker_size: Literal['small', 'medium', 'large'] = Field(default='medium')

    """
    OPTIONAL: default ""
    a symbol to position in the center of this icon
    if not provided or "", no symbol is overlaid
    and only the marker is shown
    Allowed values include
    - Icon ID
    - An integer 0 through 9
    - A lowercase character "a" through "z"

    "marker-symbol": "bus",
    """
    marker_symbol: str = Field(default='bus')

    """
    OPTIONAL: default "7e7e7e"
    the marker's color

    value must follow COLOR RULES

    "marker-color": "#fff",
    """
    marker_color: str = Field(default='7e7e7e')

    """
    OPTIONAL: default "555555"
    the color of a line as part of a polygon, polyline, or
    multigeometry

    value must follow COLOR RULES

    "stroke": "#555555",
    """
    stroke: str = Field(default='#555555')

    """
    OPTIONAL: default 1.0
    the opacity of the line component of a polygon, polyline, or
    multigeometry

    value must be a floating point number greater than or equal to
    zero and less or equal to than one

    "stroke-opacity": 1.0,
    """
    stroke_opacity: float = Field(default=1.0)

    """
    OPTIONAL: default 2
    the width of the line component of a polygon, polyline, or
    multigeometry

    value must be a floating point number greater than or equal to 0

    "stroke-width": 2,
    """
    stroke_width: float = Field(default=2)

    """
    OPTIONAL: default "555555"
    the color of the interior of a polygon

    value must follow COLOR RULES

    "fill": "#555555",
    """
    fill: str = Field(default='#555555')

    """
    OPTIONAL: default 0.6
    the opacity of the interior of a polygon. Implementations
    may choose to set this to 0 for line features.

    value must be a floating point number greater than or equal to
    zero and less or equal to than one

    "fill-opacity": 0.5
    """
    fill_opacity: float = Field(default=0.6)

    @field_validator('marker_size')
    @classmethod
    def validate_marker_size(cls, v: str) -> str:
        allowed_values = ('small', 'medium', 'large')

        if v not in allowed_values:
            raise ValueError(f'marker_size must be one of {allowed_values}, got {v}')

        return v

    @field_validator('marker_symbol')
    @classmethod
    def validate_marker_symbol(cls, v: str) -> str:
        if v == "":
            return v

        pattern = r'^[a-z0-9]+$'
        is_valid = bool(re.match(pattern, v))

        if not is_valid:
            raise Exception(f'marker_symbol must be in {pattern}')

        return v

    @field_validator('marker_color', 'stroke', 'fill')
    @classmethod
    def validate_color(cls, v: str) -> str:
        color_without_hash = v.lstrip('#')

        if len(color_without_hash) not in {3, 6}:
            raise ValueError(f'color must be a valid hex color (3 or 6 hex digits), got {v}')

        if not all(color_char in '0123456789abcdefABCDEF' for color_char in color_without_hash):
            raise ValueError(f'color must contain only hex digits, got {v}')

        return color_without_hash

    @field_validator('stroke_opacity', 'fill_opacity')
    @classmethod
    def validate_opacity(cls, v: float) -> float:
        if not (0 <= v <= 1):
            raise ValueError(f'opacity must be between 0 and 1 (inclusive), got {v}')
        return v

    @field_validator('stroke_width')
    @classmethod
    def validate_stroke_width(cls, v: float) -> float:
        if v < 0:
            raise ValueError(f'stroke_width must be >= 0, got {v}')
        return v
