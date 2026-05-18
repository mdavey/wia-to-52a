import csv
from pathlib import Path

from wiato52a.models import Repeater, Section


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


def read_prepend_lines(path: Path) -> list[str]:
    with path.open(newline="", encoding="utf-8") as f:
        lines = f.readlines()
    return [line for line in lines[1:] if line.strip()]
