import argparse
import csv
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Section:
    band: str
    mode: str
    region: str


@dataclass
class Repeater:
    output_mhz: float
    input_mhz: float
    call: str
    mnemonic: str
    location: str
    service_area: str
    latitude: str
    longitude: str
    status: str
    erp: str
    hasl: str
    timeout: str
    sponsor: str
    tone: str
    notes: str
    section: Section


def parse_section_marker(value: str) -> Section | None:
    value = value.strip()
    if value.startswith("{{") and value.endswith("}}"):
        inner = value[2:-2]
        parts = inner.split(";")
        if len(parts) >= 3:
            return Section(band=parts[0], mode=parts[1], region=parts[2])
    return None


def read_repeater_directory(path: Path) -> list[Repeater]:
    repeaters: list[Repeater] = []
    current_section: Section | None = None

    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            notes = row.get("Notes", "")
            section = parse_section_marker(notes)
            if section:
                current_section = section
                continue

            output = row.get("Output", "").strip()
            input_val = row.get("Input", "").strip()
            if not output or not input_val:
                continue

            try:
                output_mhz = float(output)
                input_mhz = float(input_val)
            except ValueError:
                continue

            repeaters.append(
                Repeater(
                    output_mhz=output_mhz,
                    input_mhz=input_mhz,
                    call=row["Call"],
                    mnemonic=row["mNemonic"],
                    location=row["Location"],
                    service_area=row["Service Area"],
                    latitude=row["Latitude"],
                    longitude=row["Longitude"],
                    status=row["S"],
                    erp=row["ERP"],
                    hasl=row["HASL"],
                    timeout=row["T/O"],
                    sponsor=row["Sp"],
                    tone=row["Tone"],
                    notes=notes,
                    section=current_section,
                )
            )

    return repeaters


HEADER = [
    "Group No", "Group Name", "CH No", "Name", "Frequency", "Dup", "Offset",
    "TS", "Mode", "SKIP", "TONE", "Repeater Tone", "TSQL Frequency",
    "DTCS Code", "DTCS Polarity", "DV SQL", "DV CSQL Code",
    "Your Call Sign", "RPT1 Call Sign", "RPT2 Call Sign",
]


def get_band(repeater: Repeater) -> str | None:
    if repeater.section and repeater.section.band not in ("*", ""):
        return repeater.section.band

    freq = repeater.output_mhz
    if 144 <= freq <= 148:
        return "2M"
    if 430 <= freq <= 450:
        return "70CM"
    if 50 <= freq <= 54:
        return "6M"
    if 28 <= freq <= 30:
        return "10M"
    if 1240 <= freq <= 1300:
        return "23CM"
    return None


def filter_repeaters(
    repeaters: list[Repeater],
    region: str,
    mode: str | None = None,
    band: str | None = None,
) -> list[Repeater]:
    region_prefix = region.upper()
    allowed_modes = {mode.upper()} if mode else {"FM", "DSTAR"}
    allowed_bands = {band.upper()} if band else {"2M", "70CM"}

    return [
        r for r in repeaters
        if r.call.upper().startswith(region_prefix)
        and r.location.lower() != "portable"
        and r.section
        and r.section.mode in allowed_modes
        and get_band(r) in allowed_bands
    ]


def format_tone(tone_raw: str) -> tuple[str, str]:
    tone_val = tone_raw.strip()
    if tone_val and tone_val != "-":
        return "TONE", f"{float(tone_val)}Hz"
    return "OFF", "88.5Hz"


def repeater_to_row(repeater: Repeater, group_no: int, group_name: str, ch_no: int) -> dict:
    diff = repeater.output_mhz - repeater.input_mhz
    if abs(diff) < 0.0001:
        dup = "OFF"
    elif diff > 0:
        dup = "DUP-"
    else:
        dup = "DUP+"

    is_dstar = repeater.section.mode == "DSTAR"
    mode = "DV" if is_dstar else "FM"
    tone_col, repeater_tone = format_tone(repeater.tone)

    return {
        "Group No": f"{group_no:02d}",
        "Group Name": group_name,
        "CH No": f"{ch_no:02d}",
        "Name": f"{repeater.call} {repeater.location}",
        "Frequency": f"{repeater.output_mhz:.6f}",
        "Dup": dup,
        "Offset": f"{abs(diff):.6f}",
        "TS": "12.5kHz",
        "Mode": mode,
        "SKIP": "OFF",
        "TONE": tone_col,
        "Repeater Tone": repeater_tone,
        "TSQL Frequency": "88.5Hz",
        "DTCS Code": "023",
        "DTCS Polarity": "BOTH N",
        "DV SQL": "",
        "DV CSQL Code": "",
        "Your Call Sign": "CQCQCQ" if is_dstar else "",
        "RPT1 Call Sign": repeater.call if is_dstar else "",
        "RPT2 Call Sign": "",
    }


def read_prepend_lines(path: Path) -> list[str]:
    with path.open(newline="", encoding="utf-8") as f:
        lines = f.readlines()
    return [line for line in lines[1:] if line.strip()]


def write_52a_csv(path: Path, groups: list[tuple[str, list[Repeater]]], prepend_path: Path | None = None):
    prepend_lines = read_prepend_lines(prepend_path) if prepend_path else []

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=HEADER)
        writer.writeheader()

        for line in prepend_lines:
            f.write(line)

        for group_no, (group_name, repeaters) in enumerate(groups, start=1):
            for ch_no, repeater in enumerate(repeaters):
                writer.writerow(repeater_to_row(repeater, group_no, group_name, ch_no))


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
