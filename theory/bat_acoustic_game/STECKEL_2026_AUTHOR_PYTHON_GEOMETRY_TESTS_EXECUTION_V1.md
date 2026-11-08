# Original Steckel 2026 bat3d Python geometry smoke tests — 2026-11-08

**Execution eligibility locked AFTER author original source outcomes were published and inspected.** This is original published-code software verification, NOT new bat tracking, real bat learning, or source author complete trained model reproduction.

Previous source preflight: official Zenodo `10.5281/zenodo.23537553` 988MB package, source verified `code.zip` SHA256 `a5b951abf5cda1ebe2e783c06d193fd9a09cb3fc36c02a265dcc7ac72bab7ae8`. Source `pyproject.toml` project `batworld`, Python>=3.10, declared dependencies `torch>=2.1,numpy,scipy,matplotlib,tensorboard`. Source AST compile passed all 29 bat3d/*.py and tests/*.py paths (Actions `42446857141`). Ten original test modules contain numerous source-author tests. No original full model has yet been run.

Freeze **exact three SOURCE-ORIGINAL geometry and motion test modules** before execution:
- `tests/test_3d_flow_ode.py`: 3 original author tests of 3D rigid-motion differential equations, finite differences.
- `tests/test_3d_warp.py`: 7 original author tests of rotations, translation and source echo warping.
- `tests/test_3d_axis_sym.py`: 6 original author tests of head pan-roll and symmetric source worlds.
There are **16 original author tests** total, not 16 biological bats. Do not select passing tests after observing other tests; run all 16 as one fixed suite. If one test fails, report exact failing test and original source runtime; no source code modification. Do not substitute rewritten tests.

Execution environment: ephemeral GitHub Actions Python3.11, source original 2026 `code.zip` exact byte range + SHA and CRC. Extract only original `bat3d/**/*.py`, `tests/**/*.py`, `pyproject.toml` to a temporary runner directory, never GitHub commit or artifact, refuse absolute/traversal paths. Install CPU-only `torch==2.6.0` from official PyTorch CPU index (source code requires >=2.1) and bounded `numpy==2.2.6`, `scipy==1.15.3`, `matplotlib==3.10.7`, `pytest==8.4.2`. Only if these dependencies install; no arbitrary fallback to GPU. Source's original 16MB HRTF mat, model weights, source training datasets and 28 source performance-run values are not part of this smoke test; do not load or fabricate them.

A pass means original geometry/motion TESTS are executable in source-verified Python runtime; it does NOT mean source original 3D self-calibration, trained model performance or any novel simulated bat ecology result was reproduced. A stop/failure is a reproducibility issue, not a negative biological finding. Keep Draft PR #36 and frozen batter intact.
