from __future__ import annotations

import re
from typing import Literal

from text_extract import TextExtractor


class DataExtractor(TextExtractor):
    def __init__(self):
        super().__init__()
        self.position = 0, 0, 0
        self.angle = 0, 0
        self.dimension: Literal[
            "overworld", "the_nether", "the_end"
        ] = "overworld"

    def capture(self):
        super().capture()
        self.position = self._get_position() or self.position
        self.angle = self._get_angle() or self.angle
        self.dimension = self._get_dimension() or self.dimension

    def _get_position(self):
        text = self._get_text(11)
        if not text:
            return None
        coordinates = re.match(
            r"XYZ: (-?\d+\.\d+) \/ (-?\d+\.\d+) \/ (-?\d+\.\d+)",
            text,
        )
        if not coordinates:
            return None
        return (
            float(coordinates[1]),
            float(coordinates[2]),
            float(coordinates[3]),
        )

    def _get_angle_text(self):
        return (
            self._get_text(14, 174)
            or self._get_text(14, 178)
            or self._get_text(14, 180)
            or self._get_text(14, 184)
        )

    def _get_angle(self):
        text = self._get_angle_text()
        if not text:
            return None
        angles = re.match(r"(-?\d+\.\d+) \/ (-?\d+\.\d+)", text)
        if not angles:
            return None
        return float(angles[1]), float(angles[2])

    def _get_dimension(self):
        text = self._get_text(9, 49)
        if not text:
            return None
        if text.startswith("o"):
            return "overworld"
        if text.startswith("the_n"):
            return "the_nether"
        if text.startswith("the_e"):
            return "the_end"
        return None
