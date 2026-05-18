import argparse
import sys
from pathlib import Path

from wiato52a import filter_repeaters, read_repeater_directory, write_52a_csv


def main():
    parser = argparse.ArgumentParser(
        description="Convert WIA repeater directory CSV to Icom IC-52A programming CSV format.",
        epilog="Download the WIA Repeater Directory from "
        "https://www.wia.org.au/members/repeaters/data/",
    )
    parser.add_argument(
        "input",
        type=Path,
        metavar="input_wia.csv",
        help="WIA repeater directory CSV file",
    )
    parser.add_argument(
        "output",
        type=Path,
        metavar="output.csv",
        help="Output CSV file for Icom 52A programming",
    )
    parser.add_argument(
        "--prepend",
        type=Path,
        metavar="favorites.csv",
        help="Custom channels CSV in 52A format to include as Group 00 "
        "(e.g. favorites and simplex channels)",
    )
    args = parser.parse_args()

    if not args.input.is_file():
        print(f"Error: Input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    if args.prepend and not args.prepend.is_file():
        print(f"Error: Prepend file not found: {args.prepend}", file=sys.stderr)
        sys.exit(1)

    repeaters = read_repeater_directory(args.input)
    print(f"Loaded {len(repeaters)} repeaters from {args.input.name}\n")

    groups = [
        (name, sorted(repeaters, key=lambda r: r.call.upper()))
        for name, repeaters in [
            ("VK3 FM 2M", filter_repeaters(repeaters, "vk3", "fm", "2m")),
            ("VK3 FM 70CM", filter_repeaters(repeaters, "vk3", "fm", "70cm")),
            ("VK3 DStar", filter_repeaters(repeaters, "vk3", "dstar")),
            ("VK1", filter_repeaters(repeaters, "vk1")),
            ("VK2 FM 2M", filter_repeaters(repeaters, "vk2", "fm", "2m")),
            ("VK2 FM 70CM", filter_repeaters(repeaters, "vk2", "fm", "70cm")),
            ("VK2 DStar", filter_repeaters(repeaters, "vk2", "dstar")),
            ("VK4 FM 2M", filter_repeaters(repeaters, "vk4", "fm", "2m")),
            ("VK4 FM 70CM", filter_repeaters(repeaters, "vk4", "fm", "70cm")),
            ("VK4 DStar", filter_repeaters(repeaters, "vk4", "dstar")),
            ("VK5", filter_repeaters(repeaters, "vk5")),
            ("VK6", filter_repeaters(repeaters, "vk6")),
            ("VK7", filter_repeaters(repeaters, "vk7")),
            ("VK8", filter_repeaters(repeaters, "vk8")),
        ]
    ]

    for i, (name, group) in enumerate(groups, start=1):
        print(f"Group {i:02d}: {name:<25s} {len(group)} repeaters")

    total = sum(len(g) for _, g in groups)
    print(f"\nTotal: {total} repeaters across {len(groups)} groups")

    write_52a_csv(args.output, groups, args.prepend)
    print(f"\nWritten to {args.output}")


if __name__ == "__main__":
    main()
