# Original Steckel 2026 bat3d Python execution preflight (source-only)

2026-11-08. This check takes place AFTER the original published 28 simulated-run metrics were examined and all 28 values source-verified, so it is a technical reproducibility preflight rather than outcome-blind preregistration. Steckel 2026 bioRxiv DOI 10.64898/2026.10.22.760884 / original Zenodo DOI 10.5281/zenodo.23537553. No new bat measurements, no original .pt models, no HRTF values, no 3D echo data, no entire 988MB ZIP.

We verified all original 28 saved numerical run results and author code.zip SHA256 a5b951abf5cda1ebe2e783c06d193fd9a09cb3fc36c02a265dcc7ac72bab7ae8 in prior CI. Those results are AUTHOR PRIOR ART, not our independently generated model predictions.

Before proposing untested geometry/movement transfer, first inspect original code's Python test-suite and actual runnable runtime requirements:
- Select the verified code.zip by the official original Zip member path, CRC, source SHA/size, using original HTTP206 Range only; code zip stays in GitHub Action ephemeral memory, never GitHub file or artifact.
- For each original *.py file under bat3d/ and tests/, use Python ast.parse/compile for syntax validation. Do NOT import modules at first; discover top-level import dependencies and exact test names.
- Read pyproject.toml and README.md software setup sections ONLY to identify original project dependency declarations; no original numerical source outcomes, .pt, 3D samples, simulated trajectories or HRTF values read.
- Perform an original source test RUN only if declared dependencies are already on the runner or can be installed within an explicitly bounded follow-on CPU environment. No silent PyTorch model-file loading, no training, no reshaping original source tests or claiming full source figure reproduction.
- An original test syntax failure indicates source completeness/runnability issue, not that observed bats fail/learn. No novelty claim from running original code unit tests.

Keep boids PR #36 Draft and batter papers frozen. New scientific flight-geometry experiment requires real source test execution and a new fixed heldout topology/trajectory axis not among source E1–E9/C1–C5, with source-aware outcome and negative control defined before opening new numerical outcomes.
