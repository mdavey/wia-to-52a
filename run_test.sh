#!/usr/bin/env bash
set -euo pipefail
rm /tmp/w52a_tmp.csv
uv run main.py testfiles/Repeater\ Directory\ 250925.csv --prepend testfiles/repeaters_to_prepend.csv /tmp/w52a_tmp.csv
diff -s /tmp/w52a_tmp.csv testfiles/output\ 52a.csv
