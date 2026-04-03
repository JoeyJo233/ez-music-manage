from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("usage: round_icon.py <input> <output>")

    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])

    with Image.open(input_path).convert("RGBA") as image:
        size = min(image.size)
        if image.size[0] != image.size[1]:
            left = (image.size[0] - size) // 2
            top = (image.size[1] - size) // 2
            image = image.crop((left, top, left + size, top + size))

        radius = int(size * 0.225)
        mask = Image.new("L", (size, size), 0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle((0, 0, size, size), radius=radius, fill=255)

        rounded = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        rounded.alpha_composite(image, (0, 0))
        rounded.putalpha(mask)
        rounded.save(output_path)


if __name__ == "__main__":
    main()
