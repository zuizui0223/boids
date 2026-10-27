# v12 — Learned private habit ↔ assortative social-guild niche

**Synthetic model only (2026-10-27).** No individual/species innate patch targets, no raw tracks and no inferred wild Boids steering coefficients. All model agents start with exactly equal choice preferences `Q=0`.

- `emergent_preferences.py`: 3D movement + uniform initial resource preferences + private Q updates + prior-step social patch-choice imitation + optional stock depletion. `train=4 days`, `test=4 days`, `30 simulator seeds`, 2 guilds×6 agents, fixed grain and per-individual prior mass.
- `species_partition_null.py`: all 20 pair-preserving post-simulation group relabelings; pseudogroups are artificial social communities, NOT biological species differences.
- `social_influence_scan.py` and `crossover_audit_v12.py`: known-truth social-coupling gradient and uncertainty due to simulator-seed sampling. Numeric crossing is NOT a phase transition.
- `grain_audit_v12.py`: coarse vs fine binned 3D probability, same heldout outcomes.
- `audit_v12.py`: seed-paired factor contrasts and finite 3-way alpha sensitivity.
- `plot_v12.py`: two reproducible 3D-level forecasting graphs.
- `check_replay_v12.py`: CI replay against frozen JSON receipts.

Main finding: learned private habit predicts individual-level vertical use, but strong **assortative social choice imitation** (not Reynolds motor Boids) can move predictive information to the guild level. Depletion, daily memory reset or loss of assortative connectivity can remove the group structure. Uniform innate target states do not imply the learning and imitation rules were themselves spontaneously evolved.

See [`docs/EMERGENT_NICHE_HIERARCHIES_V12.md`](../docs/EMERGENT_NICHE_HIERARCHIES_V12.md) for numeric results and field-claim boundaries.
