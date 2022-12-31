from collections.abc import Sequence
import json

from PIL import Image

from screen_capture import Capturer


with open("characters.json", encoding="utf8") as f:
    characters: dict[str, list[list[int]]] = json.load(f)


class TextExtractor(Capturer):
    scale = 3

    def _get_text(self, line: int, offset: int = 0):
        if not self.screenshot:
            return None
        image = self._get_image(
            (
                self.scale * (1 + offset),
                self.scale * ((line - 1) * 9 + 1),
                self.screenshot.size[0],
                self.scale * (line * 9 + 1),
            )
        )
        if not image:
            return None
        return self._image_to_string(image)

    def _image_to_string(self, image: Image.Image):
        offset = 1
        text = ""
        while True:
            for c, pixels in characters.items():
                if not self._check_character(image, offset, pixels):
                    continue
                text += c
                offset += len(pixels[0]) + 1
                break
            else:  # No match
                return text.rstrip()

    def _check_character(
        self,
        image: Image.Image,
        offset: int,
        pixels: Sequence[Sequence[int]],
    ):
        width = len(pixels[0])
        if offset + width >= image.size[0]:
            return False
        for y, row in enumerate(pixels):
            for x, pixel in enumerate(row):
                if image.getpixel((x + offset, y)) != pixel:
                    return False
            if image.getpixel((offset + width, y)):
                return False

        return True

    def _get_image(self, box: tuple[int, int, int, int]):
        if not self.screenshot:
            return None
        if box[0] >= box[2]:
            return None
        image = self.screenshot.crop(box)

        text = Image.new("1", (image.size[0] // 3, image.size[1] // 3))

        for x in range(1, image.size[0], 3):
            for y in range(1, image.size[1], 3):
                if image.getpixel((x, y)) == (221, 221, 221):
                    text.putpixel((x // 3, y // 3), True)

        return text
