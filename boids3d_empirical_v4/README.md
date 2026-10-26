# Boids → ecological prediction: real-data gate v4 (2026-10-26)

## Actual new result (not simulation)

In the archived Tadarida annotated GPS source (DOI `10.5441/001/1.52nn82r9`), complete 9,873 rows were read using an external public-data content reader. The tool-extracted text had 3,630,088 characters and exact expected row count; source archive's expected MD5 is pinned in the sister `batter` repository but raw byte checksum could **not** be reverified locally. Aggregate counts/prediction scores were computed without exporting raw tracks to this project.

- 8 bats, 16 BatDay sessions, 9,587 eligible 3-location transitions.
- Held-out-session equal-individual log score: M0 (marginal) -1.08699, M1 (last-step velocity class) -1.07316, M2 (+ annotated vertical wind class) -1.07428 nats per step.
- On unseen individual holdout M2 minus M1 = -0.00118 nats/step.
- M3 (matched individual other-night history) vs M2 **paired on 7 repeat bats**, -0.00916 nats/step. Null mean -0.01149; 199 whole-night ID permutations: one-sided p=0.32. The positive null-centered excess (~+0.00233) **does not pass** the test. Raw negative contrasts alone cannot prove absence of individuality.
- Individual-weighted bootstrap percentile 95% CIs: M1-M0 [+0.00672,+0.02113]; M2-M1 [-0.00252,+0.00012]; M3-M2 raw [-0.01898,-0.00053]. The M3 null is not zero, so its raw CI should NOT replace null-calibrated inference.
- Sensitivity: changing speed threshold ±0.5→±1.0m/s or wind threshold ±0.05→±0.15m/s did not produce a positive M2-M1 or M3-M2 average.
- Approximate 3D neighbor gate: 15,676 cross-individual GPS fix pairs within 5s, but **zero** within 100m. Under relaxed <=15s/<=500m conditions: 39 pairs. Asynchronous~30s GPS is **not suitable for recovering fast social force coefficients**; this is not evidence that bats do not socialize.
- Independent structural check for Eidolon helvum archive (DOI `10.5441/001/1.k8n02jn8`): 18,154 events / 63 bats; time-gap median 273s (10th percentile 147s, 90th percentile 1,786s), and **0 valid 15–75s triplets**. We did not relax fixed cadence rules after this gate failed.

## Biological interpretation

- The only genuinely improved observed short-horizon predictive **feature** in this benchmark was previous climb class, and its gain was small (+0.01383 nats/step vs marginal, 7/8 bats positive). This statistical persistence does NOT distinguish true physical inertia from GPS error autocorrelation or repeated unobserved behavioral states.
- Added archived wind did not outperform inertia under fixed discretization and time interval; this does not falsify the biological influence of uplift/terrain on flight, and modeled wind is not the same as measured airflow at the animal.
- Repeated centered-height *distribution* identity in the published `batter` comparative panels remains distinct from direct identification of a 30-second **movement policy** for Tadarida. Note that the Tadarida centered-shape panel itself failed in batter; no contradiction is asserted.
- A multi-taxon predictive *Boids law* has **not** been identified. The previous synthetic forecast successes remain known-truth ABM interpolation, not demonstrated empirical niche or competition forecasts.

## Reproduction

```bash
python -m pip install numpy matplotlib
python empirical_transition_benchmark.py --download --out result-from-raw-data.json --sensitivity
python boids_observability_gate.py --csv path-to-public-gps.csv --out social-preflight.json
python -m unittest discover -p 'test_*.py' -v
```

The --download option requires network access and checks the exact expected original MD5 before any statistics. The local session here had no outbound DNS, so it **was not** run locally on the complete raw CSV. It was separately executed using a public-content tool that supplied full CSV text, applying the same discrete state definitions and grouped evaluation equations. Local unit tests cover those equations using synthetic records. This provenance distinction must stay visible.

Raw animal GPS records are not redistributed in the archive. Chart is `bat_vertical_prediction_v4.png`. All aggregates and thresholds are recorded in `EMPIRICAL_RESULT_V4.json`.

## Next source gate, not additional fishing

An independent, synchronized multi-individual GPS/IMU collection with sufficient near-neighbor pairs is needed to test Reynolds separation/alignment/cohesion. Before collecting data, preregister (a) time resolution based on wingbeat / sensory response scale, (b) 3D positioning/altitude measurement error, (c) actual neighbor detection, (d) external habitat and prey availability, (e) independent held-out groups/sites/dates. Fit alternative transition kernels (inertia-only, habitat, personal, social) and test **new individual or new night** niche-distribution prediction, not just pointwise velocity. Do not reopen frozen batter, odsp, mina, or louis manuscripts.
