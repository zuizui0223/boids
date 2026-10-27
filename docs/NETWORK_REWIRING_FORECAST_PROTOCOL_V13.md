# v13 frozen protocol — Social-network rewiring and transfer of learned niche hierarchy

**Registered 2026-10-28; exploratory, simulator-only. No biological observation outcomes.**
Code lives in `validation_v13/network_transfer.py`. The archived v4/v6/v8 observed endpoints and the v12 30-seed results are not amended or re-scored.

## Primary question

When initially symmetric agents have learned resource preferences through private reinforcement and within-group choice imitation, is **current social-network membership** more predictive of future resource choice than the *pre-perturbation* guild membership, after a mid-experiment rewiring?

The v12 guilds are artificial six-agent networks, **not species**. The result is a test of a specified adaptive-choice policy, **not Reynolds steering alone**.

## Fixed generative design (before outcome opening)

- Reuse v12 `sample_categorical`, `move`, four 3D patch coordinates, memory and reward update, eight days × 24 decisions, first three decisions/day excluded, six agents in each of two artificial guilds.
- All start with equal `Q=0`; stochastic seed worlds `20270101..20270130` (30 independent RNG worlds, same seed for each condition), `alpha=1`.
- Original network: agents 0–5 versus 6–11. Orthogonal, pre-fixed rewired network: `[0,1,2,6,7,8]` versus `[3,4,5,9,10,11]`, exactly 3 agents from each original guild. Change social-choice contacts **before the first choice on day 5**. Identity labels never come from fitted trajectories.
- Motor-Boids force is **OFF in the primary test** to isolate social *choice* imitation; v12 Reynolds-alignment motor physics remains common in the reused motion code. An on-force sensitivity (fixed original dyadic motor partners) is separately reported and must not be interpreted as observed social forces.
- The standard world has four equal rewards and the v12 `Q` update, decay, choice temperature and imitation strength `2.0`. A later environmental perturbation changes the day-5-onward patch reward/cue vector identically for all agents to `[0.25,0.25,1,1]`; no prey counts or depletion dynamics are claimed.

### Eight pre-fixed conditions

1. `stable_uniform`: original social network all eight days; learned policies.
2. `rewired_uniform`: original days 1–4, orthogonal social network days 5–8; learned policies.
3. `mixed_uniform`: original days 1–4, all-to-all social-choice information days 5–8; learned policies.
4. `rewired_no_learning`: same rewire, **private reward updating disabled all days**, to test whether within-day social imitation alone yields across-day group forecast.
5. `rewired_reset`: reset private memory once at start of day 5, then resume reinforcement under new network.
6. `stable_gradient`: original network, common reward gradient from day 5.
7. `rewired_gradient`: rewired network, common reward gradient from day 5.
8. `rewired_boids`: same as `rewired_uniform` but original v12 dyad-level Boids motor interaction ON.

A null can fail, and such failures will not be tuned away by changing network memberships, time windows, learning coefficients or seeds.

## Prediction protocol: prohibit post-outcome regrouping

**All outcomes are synthetic and held out in time.** Training is simulation days 5–6; test is days 7–8, for each of the fixed two groupings. All 12 agents and all 4 resource classes are scored, with `0.5 × number-of-training-agents` Dirichlet pseudo-count per class, exactly the prior-mass convention of v12.

The focal measure is mean held-out agent-balanced log-score advantage (nats/choice):

`A = score(P(patch | active network guild)) - score(P(patch | counterfactual orthogonal guild))`.

`active` is original membership under stable, new membership under rewired, and (arbitrarily) original membership under mixed (the mixed condition has no true two-guild partition). The compared group models have the **same number of members, same training volume, same prior and identical test events**.

Secondary outcomes: guild-versus-population patch score, self-versus-active-guild patch score, conditional vertical-height score `P(Z|XY,guild)` on the *fixed v12 coarse grain*, old-network trained days 1–4 → scored days 5–6, and habitat-gradient/motor sensitivity. No claims about feeding competition or realized species niches follow from spatial occupancy alone.

### Registered interpretive gate

Claim **synthetic support for membership transfer after rewiring** only if all of:
- `rewired_uniform` mean focal advantage > 0, its seed-bootstrap percentile 95% CI lower bound > 0;
- the seed-paired `rewired_uniform − rewired_no_learning` focal advantage also has CI lower bound > 0;
- `stable_uniform` has positive focal advantage with CI lower bound > 0 (the initial network actually carries persistent information).

All 30 seed worlds are the statistical replicates. Use fixed 5,000 whole-seed bootstrap resamples; never bootstrap individual decisions as independent samples. Report the results even if the gate fails; gradient, reset and motor controls are exploratory and not rescue conditions. Report positive-seed counts and unconditional estimates including negative effects. These are Monte Carlo seed-bootstrap intervals, **not biological confidence intervals**.

## Stop and evidence boundaries

- v13 does not fit any wild bat, bird, penguin, prey or environmental records.
- A post-rewire prediction benefit would identify only **the constructed learning/imitation mechanism within the simulator**, not the mechanism operating in nature or a species-level law.
- A failure may reflect slow private-memory turnover under the *fixed* eight-day protocol; do not alter the window after opening outcomes.
- The observed v6 bat and v8 pigeon primary same-time social forecasting contrasts remain unsupported and unchanged.
- The intended next step after v13 is an **outcome-blind independent multiday 3D data validation** with measured network and reward changes plus calibrated observation error.

## Reproduction

```bash
python -m pip install 'numpy>=1.26,<3'
PYTHONPATH=validation_v12:validation_v13 python -m unittest discover -s validation_v13 -p 'test_*.py' -v
python validation_v13/network_transfer.py --seeds 30 --out validation_v13/results/network_transfer_v13.json
```
