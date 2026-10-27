# v13 result — Learned guild structure after network rewiring (synthetic)

**Status: completed 2026-10-28 (JST). This is synthetic model evidence, not wild-animal ecology.**

- Frozen protocol committed before outcomes: [NETWORK_REWIRING_FORECAST_PROTOCOL_V13.md](NETWORK_REWIRING_FORECAST_PROTOCOL_V13.md).
- Code, fixed seed worlds, scoring rules, test gates: [validation_v13](../validation_v13/).
- [Passing GitHub Actions run 40535430474](https://github.com/zuizui0223/boids/actions/runs/40535430474): **14/14 regression tests**, exact unchanged-parent v12 stable model replay; 30×8 = 240 prespecified simulator worlds, full numerical audit, artifact `network-rewiring-v13-30worlds`.
- Archived ZIP artifact SHA256 digest: `5ada394371158261f21227474e976166622874ef08d0fa885b993a6f714522d0`. This hashes the downloadable artifact ZIP, **not the JSON inside**. The artifact currently expires 2027-01-25; JSON is reproducible from pinned code and seeds.

## Registered focal result: passed within the toy world

The comparison is *held-out* mean log-score of a patch model conditioned on current two-guild social network versus an ex-ante orthogonal counterfactual two-guild grouping, **using exactly the same post-intervention days 5–6 for fitting and days 7–8 for scoring**.

| Prespecified scenario | Patch network advantage (nats/choice) | Seed-bootstrap 95% | Positive seed worlds (of 30) |
|---|---:|---:|---:|
| Original network retained (`stable_uniform`) | **+0.517823** | [+0.406906,+0.610898] | 25 |
| **Old network rewired** (`rewired_uniform`) | **+0.193495** | **[+0.102003,+0.286962]** | **21** |
| All-to-all contacts after switch (`mixed_uniform`) | +0.057316 | [−0.022136,+0.143547] | 10 |
| Rewired but no private reward learning (`rewired_no_learning`) | **−0.045278** | [−0.076316,−0.015973] | 11 |
| Rewire and Q-memory reset on day 5 (`rewired_reset`) | **+0.533434** | [+0.448940,+0.609134] | 29 |
| Original network with common post-switch reward gradient (`stable_gradient`) | +0.176325 | [+0.077231,+0.281623] | 11 |
| Rewired under reward gradient (`rewired_gradient`) | +0.092050 | [+0.022927,+0.177269] | 13 |
| Rewire with original dyad Boids motor forces ON (`rewired_boids`) | +0.193272 | [+0.102831,+0.286817] | 21 |

**Predeclared support gate: PASS (synthetic only).** Positive rewired mean and lower CI; its paired advantage over the no-learning condition is positive with lower CI; unchanged-network sanity control positive with lower CI. No threshold, seeds, labels or forecast horizons were altered after the outcomes were opened.

### Additional spatial evidence

The same grouping comparison for held-out fixed-grid conditional altitude `P(Z|X,Y)` gave:
- Stable original network: **+0.177944 nats/fix**, 95% [+0.088896,+0.282062], 26/30 positive worlds.
- Rewired current network: **+0.121808 nats/fix**, 95% [+0.066969,+0.187024], 27/30 positive worlds.
- No private learning: −0.033180 nats/fix, CI [−0.073391,+0.001239].
- Motor-Boids ON with rewire: +0.123774 nats/fix, CI [+0.068318,+0.189353].

These synthetic conditional probability forecasts measure occupancy, not feeding competition, resources actually eaten, or any real bat/bird altitude preference.

### Pre-fixed matched-world contrasts

| Contrast | Mean difference | Bootstrap 95% | Interpretation |
|---|---:|---:|---|
| Rewire learning vs no learning, patch topology | **+0.238773** | **[+0.146533,+0.333563]** | Learning required for the observed *across-day* transfer in this toy world |
| Q-memory reset at rewire vs persistent Q | **+0.339939** | **[+0.202103,+0.474227]** | Old individual reinforcement can obstruct *rapid* imprinting of the new grouping |
| Rewire with Boids motor ON minus OFF | −0.000223 | [−0.003193,+0.002111] | No meaningful extra motor contribution detected in this simulator contrast |
| Reward gradient vs uniform in rewired world | −0.101445 | [−0.210483,+0.010366] | Directionally reduced average; **paired uncertainty crosses zero**, no registered evidence for attenuation |
| Rewired vs all-to-all, guild gain above population | +0.043978 | [−0.070432,+0.159181] | This **particular** contrast does not show a reliable superiority over global mixing |

The Q-reset result is especially informative but purely mechanistic: the first four days create old learned associations; erasing those associations immediately before a new network forms accelerates the model's new collective choice structure. It is **not** a claim that real animals forget habits or that reduced memory has an evolutionary advantage.

**Important heterogeneity:** under the common spatial reward gradient, mean bootstrap intervals for some topology contrasts are positive even though **less than half of the 30 worlds have positive signs**. A skewed seed distribution can produce this. Do not describe the environmental shift outcome as universal or seed-wise reliable. Inspect the artifact's complete per-seed records if evaluating distributional robustness.

## Scientific interpretation and limits

Under the explicitly constructed reward-reinforcement and preceding-choice imitation policy, persistent differences in **which social network is informationally predictive** can reorganize even though all agents had identical innate patch preferences. This is stronger than v12's constant-guild demonstration, because network membership was changed mid-series and the new grouping was selected *prior* to observing outcomes. Within this simulator, a learned social organization influences horizontal patch choice and conditional vertical position.

What is NOT shown:
- That Reynolds separation, cohesion and alignment *generate* the learned groups; motor-force sensitivity was approximately zero.
- Any unique recovered wild Boids coefficient; no biological force inference occurred.
- Wild bat/bird individuality, species divergence, phylogenetic niche conservatism, competition, demography, or general forecast transfer.
- A phase transition at a universal social-coupling or memory threshold.

Original frozen v6 (bat pairs) and v8 (pigeon pairs) wild observational primary social forecast contrasts remain **not supported** and are unchanged.

## Reproduce exact outcome and check numerical meaning

```bash
python -m pip install 'numpy>=1.26,<3'
PYTHONPATH=validation_v12:validation_v13 python -m unittest discover -s validation_v13 -p 'test_*.py' -v
python validation_v13/network_transfer.py --seeds 30 --out validation_v13/results/network_transfer_v13.json
```

Use the run artifact for all per-seed values and other conditional forecast summaries. The next independent empirical gate and shortlisted data sources are tracked in [issue #2](https://github.com/zuizui0223/boids/issues/2); no candidate's raw animal trajectories were fetched or fitted during v13.
