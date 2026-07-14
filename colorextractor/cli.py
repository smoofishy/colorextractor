import argparse
import json
import sys

from .extractor import extract_colors


def swatch(rgb):
    r, g, b = rgb
    return f"\x1b[48;2;{r};{g};{b}m  \x1b[0m"


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="List the dominant colors in an image, most to least common."
    )
    parser.add_argument("image", help="path to the image file")
    parser.add_argument(
        "-c", "--colors", type=int, default=32,
        help="palette size to quantize down to before counting (default: 32)",
    )
    parser.add_argument(
        "-n", "--top", type=int, default=None,
        help="only show the top N colors (default: show all)",
    )
    parser.add_argument(
        "--resize", type=int, default=400,
        help="downscale the image so its longest side is at most this many pixels "
             "before processing, 0 to disable (default: 400)",
    )
    parser.add_argument(
        "--json", action="store_true",
        help="output results as JSON instead of a formatted table",
    )
    parser.add_argument(
        "--no-swatch", action="store_true",
        help="disable ANSI color swatches in table output",
    )
    parser.add_argument(
        "--no-group", action="store_true",
        help="don't merge quantized shades that share the same nearest color name",
    )
    args = parser.parse_args(argv)

    try:
        results = extract_colors(
            args.image,
            num_colors=args.colors,
            top_n=args.top,
            resize_max=args.resize or None,
            group_similar=not args.no_group,
        )
    except (FileNotFoundError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps([r.__dict__ for r in results], indent=2))
        return 0

    print(f"{'':3}{'HEX':<9}{'NAME':<20}{'PERCENT':>8}   COUNT")
    for r in results:
        prefix = "" if args.no_swatch else swatch(r.rgb)
        print(f"{prefix} {r.hex:<8}{r.name:<20}{r.percentage:7.2f}%   {r.count}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
