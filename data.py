from __future__ import annotations

import re
from typing import Literal
import pyperclip

from text_extract import TextExtractor


class DataExtractor(TextExtractor):
    use_clipboard = True

    def __init__(self):
        super().__init__()
        self.position = 0, 0, 0
        self.angle = 0, 0
        self.dimension: Literal[
            "overworld", "the_nether", "the_end"
        ] = "overworld"

    def capture(self):
        if self.use_clipboard:
            text = pyperclip.paste()
            data = re.match(
                r"^\/execute in minecraft:(overworld|the_nether|the_end) run tp @s (-?\d+\.\d\d) (-?\d+\.\d\d) (-?\d+\.\d\d) (-?\d+\.\d\d) (-?\d+\.\d\d$)",
                text,
            )
            if not data:
                return
            data = data.groups()
            dimension: Literal["overworld", "the_nether", "the_end"] = data[
                0
            ]  # type: ignore
            self.dimension = dimension
            self.position = (float(data[1]), float(data[2]), float(data[3]))
            self.angle = (float(data[4]), float(data[5]))
            return

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
        coordinates = coordinates.groups()
        return (
            float(coordinates[0]),
            float(coordinates[1]),
            float(coordinates[2]),
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
        angles = angles.groups()
        return (float(angles[0]), float(angles[1]))

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
