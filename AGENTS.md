# AGENTS.md

## Project Overview

**wia-to-52a** converts WIA (Wireless Institute of Australia) repeater directory CSV data into Icom IC-52A (and compatible) radio programming CSV format. Single-file Python script (`main.py`), no dependencies beyond stdlib, Python 3.13+, managed with `uv`.

## Commands

```bash
uv run main.py
```

Reads `Repeater Directory 250925.csv`, writes `output 52a.csv`. No build/test/lint configured.

## Data Flow

1. `read_repeater_directory()` — parses WIA CSV into `Repeater` dataclasses, tracking section markers
2. `filter_repeaters()` — filters by region (call sign prefix), mode, and band
3. `repeater_to_row()` — maps each `Repeater` to an Icom 52A CSV row dict
4. `write_52a_csv()` — writes header, prepends `repeaters_to_prepend.csv` content (minus header), then writes all groups

## Input Files

- **`Repeater Directory 250925.csv`** — WIA repeater directory. Columns: `Output`, `Input`, `Call`, `mNemonic`, `Location`, `Service Area`, `Latitude`, `Longitude`, `S`, `ERP`, `HASL`, `T/O`, `Sp`, `Tone`, `Notes`.
- **`repeaters_to_prepend.csv`** — Manual favorites/simplex channels in 52A format (with header). Written as Group 00 before the generated groups.

## Output File

- **`output 52a.csv`** — Icom 52A programming CSV. See `HEADER` constant for column list.

## Output Group Structure

| Group | Name | Filter |
|-------|------|--------|
| 00 | Favorites | From `repeaters_to_prepend.csv` |
| 01 | VK3 FM 2M | VK3, FM, 2M |
| 02 | VK3 FM 70CM | VK3, FM, 70CM |
| 03 | VK3 DStar | VK3, DSTAR |
| 04 | VK1 | VK1, all FM/DStar, 2M/70CM |
| 05 | VK2 FM 2M | VK2, FM, 2M |
| 06 | VK2 FM 70CM | VK2, FM, 70CM |
| 07 | VK2 DStar | VK2, DSTAR |
| 08 | VK4 FM 2M | VK4, FM, 2M |
| 09 | VK4 FM 70CM | VK4, FM, 70CM |
| 10 | VK4 DStar | VK4, DSTAR |
| 11 | VK5 | VK5, all FM/DStar, 2M/70CM |
| 12 | VK6 | VK6, all FM/DStar, 2M/70CM |
| 13 | VK7 | VK7, all FM/DStar, 2M/70CM |
| 14 | VK8 | VK8, all FM/DStar, 2M/70CM |

VK3, VK2, VK4 are split by band and mode. VK1/VK5-8 combine all bands and modes. Each group is sorted A-Z by callsign.

## Key Mapping Rules

- `Frequency` = WIA `Output` (6 decimal places)
- `Dup` = `DUP-` if input < output, `DUP+` if input > output, `OFF` if equal
- `Offset` = `abs(output - input)` (always positive, 6 decimal places)
- `Mode` = `DV` for DStar, `FM` for everything else
- `Name` = `Call Location` (e.g. `VK3RML Ferny Creek`)
- `TONE`/`Repeater Tone` = `TONE` + value if tone present, `OFF` + `88.5Hz` if not (treat `-` and empty as no tone)
- `TS` always `12.5kHz`, `DTCS Code` always `023`, `DTCS Polarity` always `BOTH N`
- DStar only: `Your Call Sign` = `CQCQCQ`, `RPT1 Call Sign` = repeater callsign

## Gotchas

- WIA section markers are rows like `{{2M;FM;VK3}}` in the Notes column — all other fields empty. Must be parsed as section metadata, not data.
- When section band is `*` (e.g. DStar, DMR), band must be derived from the output frequency via `get_band()`.
- WIA `Tone` field uses `-` for no tone. Must treat both `-` and empty as "no tone".
- Repeater callsign prefix determines region (e.g. `VK3RML` → VK3). This is the primary region filter, not the section region field.
- Entries with `Location` = `portable` are filtered out.
- ATV entries have non-numeric frequency values like `Various` — must skip via `try/except` on `float()`.
- VK1 repeaters use callsign prefix `VK1` but may appear in VK2 sections geographically.
