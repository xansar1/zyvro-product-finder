#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if [ ! -d .venv ]; then
  if command -v python3.12 >/dev/null 2>&1; then py=python3.12
  elif command -v python3.11 >/dev/null 2>&1; then py=python3.11
  else py=python3; fi
  "$py" -m venv .venv
fi
. .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app.py --server.address 127.0.0.1 --server.port 8501
