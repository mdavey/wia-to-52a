# wia-to-52a

Converts the [WIA](https://www.wia.org.au) repeater directory into a CSV file suitable for programming an Icom IC-52A handheld radio.

## Usage

```bash
uv run main.py input_wia.csv output.csv
uv run main.py input_wia.csv output.csv --prepend favorites.csv
```

Download the WIA repeater directory CSV from [wia.org.au/members/repeaters/data](https://www.wia.org.au/members/repeaters/data/).

### Options

| Argument | Description |
|----------|-------------|
| `input_wia.csv` | WIA repeater directory CSV file (required) |
| `output.csv` | Output CSV file for Icom 52A programming (required) |
| `--prepend favorites.csv` | Custom channels in 52A format to include as Group 00 (optional) |

A sample favorites file is provided as [`favorites_sample.csv`](favorites_sample.csv).

## What it does

- Parses the WIA repeater directory CSV
- Filters to 2M and 70CM bands, FM and DStar modes
- Excludes portable repeaters
- Groups by state and mode, sorted by callsign
- Outputs an Icom 52A-compatible CSV with correct duplex, offset, tone, and DStar settings

---

This project was 100% vibe coded with [Crush](https://charm.land) and GLM-5-Turbo.
