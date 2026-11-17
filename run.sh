#!/bin/sh
# Jedna komenda: środowisko -> zbiór syntetyczny -> bazowy detektor -> ocena FP/FN.
# Parametry generatora można dopisać: ./run.sh --czyste 50 --dodatki 50 --szer 2400 --wys 800
set -e
cd "$(dirname "$0")"
if [ ! -x .venv/bin/python ]; then
  if command -v uv >/dev/null 2>&1; then uv venv -q .venv && uv pip install -q -p .venv -r requirements.txt
  else python3 -m venv .venv && .venv/bin/pip install -q -r requirements.txt; fi
fi
PY=.venv/bin/python
$PY -m rtg.generuj --wyjscie dane/syntetyczne "$@"
$PY -m rtg.bazowy --zbior dane/syntetyczne --wynik wyniki/bazowy.json
$PY -m rtg.ocena --zbior dane/syntetyczne --predykcje wyniki/bazowy.json --json wyniki/ocena_bazowy.json
