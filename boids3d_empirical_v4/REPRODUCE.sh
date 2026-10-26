#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python -m unittest test_empirical_transition.py test_observability_gate.py -v
(cd boids3d_research && python -m unittest discover -p 'test_*.py' -q)
python build_receipt_and_figure.py >/dev/null
if [[ "${RUN_REMOTE_DATA:-0}" == "1" ]]; then
  python empirical_transition_benchmark.py --download --out bat_result_from_source.json --sensitivity
fi
