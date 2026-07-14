from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

from PIL import Image

from .color_names import closest_color_name


@dataclass
class ColorInfo:
    rgb: Tuple[int, int, int]
    hex: str
    count: int
    percentage: float
    name: str

    def __str__(self):
        return f"{self.hex}  {self.name:<20} {self.percentage:5.2f}%  ({self.count} px)"


def extract_colors(
    image_path,
    num_colors: int = 32,
    top_n: Optional[int] = None,
    resize_max: Optional[int] = 400,
    group_similar: bool = True,
) -> List[ColorInfo]:
    """Extract the dominant colors from an image, sorted most to least common.

    Args:
        image_path: path to the image file.
        num_colors: size of the palette to quantize down to before counting.
        top_n: if set, only return the N most common colors.
        resize_max: if set, downscale the image so its longest side is at
            most this many pixels before processing (keeps large photos fast).
        group_similar: if True, merge quantized shades that share the same
            nearest color name (e.g. several near-white shades all named
            "white") into a single entry with combined counts.
    """
    path = Path(image_path)
    if not path.exists():
        raise FileNotFoundError(f"Image not found: {path}")

    try:
        img = Image.open(path).convert("RGB")
    except Image.UnidentifiedImageError as exc:
        raise ValueError(f"Could not read '{path}' as an image") from exc

    if resize_max and max(img.size) > resize_max:
        img.thumbnail((resize_max, resize_max))

    quantized = img.quantize(colors=num_colors)
    palette = quantized.getpalette()
    color_counts = quantized.getcolors()

    total_pixels = sum(count for count, _ in color_counts)

    results = []
    for count, index in color_counts:
        r, g, b = palette[index * 3: index * 3 + 3]
        rgb = (r, g, b)
        results.append(
            ColorInfo(
                rgb=rgb,
                hex=f"#{r:02x}{g:02x}{b:02x}",
                count=count,
                percentage=(count / total_pixels) * 100,
                name=closest_color_name(rgb),
            )
        )

    if group_similar:
        results = _group_by_name(results)

    results.sort(key=lambda c: c.count, reverse=True)

    if top_n:
        results = results[:top_n]

    return results


def _group_by_name(results: List[ColorInfo]) -> List[ColorInfo]:
    """Merge entries that share the same nearest color name, using a
    count-weighted average RGB as the representative swatch."""
    groups = {}
    for r in results:
        groups.setdefault(r.name, []).append(r)

    grouped = []
    for name, items in groups.items():
        total_count = sum(i.count for i in items)
        total_percentage = sum(i.percentage for i in items)
        r = round(sum(i.rgb[0] * i.count for i in items) / total_count)
        g = round(sum(i.rgb[1] * i.count for i in items) / total_count)
        b = round(sum(i.rgb[2] * i.count for i in items) / total_count)
        grouped.append(
            ColorInfo(
                rgb=(r, g, b),
                hex=f"#{r:02x}{g:02x}{b:02x}",
                count=total_count,
                percentage=total_percentage,
                name=name,
            )
        )
    return grouped
