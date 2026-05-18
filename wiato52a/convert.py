import csv
from pathlib import Path

from wiato52a.models import Repeater


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


def write_52a_csv(path: Path, groups: list[tuple[str, list[Repeater]]], prepend_path: Path | None = None):
    from wiato52a.readers import read_prepend_lines

    prepend_lines = read_prepend_lines(prepend_path) if prepend_path else []

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=HEADER)
        writer.writeheader()

        for line in prepend_lines:
            f.write(line)

        for group_no, (group_name, repeaters) in enumerate(groups, start=1):
            for ch_no, repeater in enumerate(repeaters):
                writer.writerow(repeater_to_row(repeater, group_no, group_name, ch_no))
