# wia-to-52a

Converts the [WIA](https://www.wia.org.au) repeater directory into a CSV file suitable for programming an Icom IC-52A handheld radio.

## Usage

```bash
uv run main.py
```

This reads `Repeater Directory 250925.csv` and `repeaters_to_prepend.csv` and writes `output 52a.csv`.

## Files

| File | Description |
|------|-------------|
| `Repeater Directory 250925.csv` | WIA repeater directory (input) |
| `repeaters_to_prepend.csv` | Manual favorites/simplex channels to include as Group 00 |
| `output 52a.csv` | Icom 52A programming file (output) |

## What it does

- Parses the WIA repeater directory CSV
- Filters to 2M and 70CM bands, FM and DStar modes
- Excludes portable repeaters
- Groups by state and mode, sorted by callsign
- Outputs an Icom 52A-compatible CSV with correct duplex, offset, tone, and DStar settings

---

This project was 100% vibe coded with [Crush](https://charm.land) and GLM-5-Turbo.
