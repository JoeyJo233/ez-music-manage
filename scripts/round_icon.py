from __future__ import annotations

import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw


def _squircle_mask(size: int) -> Image.Image:
    """Generate a macOS-style squircle mask (superellipse, n=5).

    Apple's Big Sur squircle is a superellipse with exponent ~5,
    which produces smoother corner transitions than a simple rounded rect.
    """
    mask = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(mask)
    n = 5.0
    r = size / 2.0
    cx = cy = r
    # Approximate the superellipse with a polygon of many vertices
    points: list[tuple[float, float]] = []
    steps = 2048
    for i in range(steps):
        angle = 2 * math.pi * i / steps
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        x = cx + r * math.copysign(abs(cos_a) ** (2 / n), cos_a)
        y = cy + r * math.copysign(abs(sin_a) ** (2 / n), sin_a)
        points.append((x, y))
    draw.polygon(points, fill=255)
    return mask


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

        mask = _squircle_mask(size)
        result = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        result.alpha_composite(image)
        result.putalpha(mask)
        result.save(output_path)


if __name__ == "__main__":
    main()
