# v12 — When do private movement histories become group-level ecological niches?

**Date: 2026-10-27. Status: EXPLORATORY, SYNTHETIC, known generative rules.**
This version advances `boids` beyond v11's imposed individual- and pseudo-species-specific habitat targets. It does **not** establish a species-general biological mechanism, true Boids social-force coefficients, or a measured resource competition effect. All prior v4/v6/v8 observed forecasting gates, especially the unsupported actual-partner-vs-negative-control contrasts, remain untouched.

## 1. Scientific question and identification boundary

Previously the model could generate 3D individual and species niches only by assigning each model animal a preferred resource location. That was a sufficient generative demonstration, but it did not explain *where different preferences came from*. The new question is:

> Under identical initial habitat preferences and identical decision-learning rules, can private reward histories and the connectivity of social information cause persistent individual niches or persistent group-specific niche organization? Which components survive on unseen days, which disappear with resource depletion, and how does social connectivity change the level where information is predictive?

The important distinction is between three levels:

1. **Locomotor Boids:** a trajectory-generating component containing same-dyad separation/cohesion and alignment.
2. **Adaptive choice policy:** an *explicitly modeled* private reward/habit memory plus an optional socially observed preceding patch-choice fraction among specified contacts; social-choice imitation is **not** a Reynolds steering force.
3. **Emergent distribution and forecast:** records of synthetic 3D space utilization and independent simulated-day patch use; assessed with within-guild individual and between-guild conditional information.

We did **not** construct an ecological species divergence experiment: labels `s=1,2` designate equally capable synthetic **social guilds** that differ only in the identity of their social connections. Neither guild has imposed habitat preferences, flight capacities, or resource-access asymmetries.

## 2. Algorithm, including what is imposed

There are 2 guilds of 6 agents, 4 symmetric resource patches at horizontal \(x=\pm 12\) and altitude \(z=\pm 13\) (all have \(y=0\)). All agents begin with **identical \(Q_{ik}=0\)**, identical initial-location distributions, motor constants and innate patch probabilities. Each of 8 model days contains 24 decisions (3 initial blocks excluded from state-use scoring). Position/velocity are reset at each day's start, while private memory persists unless it is explicitly removed by a negative control.

At each decision, \(k\in\{1,2,3,4\}\) is chosen from a softmax with \(T=0.72\):

\[
P_i(k,t)\propto\exp\!\left\{\frac{3.6Q_{ik}(t)+0.5R_k(t)-0.006\,d(x_i,x_k)
+\lambda F_{g(i),k}(t-1)}{0.72}\right\}.
\]

\(F_{g(i),k}(t-1)\) is the fraction of **other connected conspecific-guild agents** choosing patch \(k\) at the preceding decision, when social-choice feedback is enabled. For the mixed-network negative control, it instead counts all other agents regardless of guild. Private memory is discounted by `0.94` and the rewarded chosen patch gets a fixed learning update of weight `0.45`; unchosen patches are discounted. These memory/temperature/update settings are **hypotheses built into the simulator**, not fitted biological mechanisms. Uniform patches without consumption have reward 1 everywhere. Under the resource-consumption scenario, reward is diminished by concurrent consumers and stocks update symmetrically as

\[
R_k(t+1)=\operatorname{clip}_{[0.04,1]}
\bigl[R_k(t)+0.13(1-R_k(t))-0.043\,n_k(t)\bigr].
\]

The 3D locomotion step includes a common target-patch acceleration, drag, independent noise, and optionally the same-dyad Reynolds-like component

\[
\mathbf a_{i,\mathrm{social}}=
\left(\gamma-\frac{\alpha}{d_{ij}^3}\right)
(\mathbf x_j-\mathbf x_i)+0.065(\mathbf v_j-\mathbf v_i),\qquad
\gamma=-0.003+\frac{\alpha}{10^3}.
\]

Candidates \(\alpha\in\{0,1,2\}\) are algebraically **identical at separation 10 m**, as in v9–v11. This is only a demonstration of finite source-equivalent candidate sets, not a fitted or exhaustive parameter confidence set.

## 3. Prediction targets and controls

**Prediction split: first 4 days train; last 4 days test.** Same held-out patch choices/3D fixes are scored under the model conditioned on the focal individual's history versus the pooled guild, and under the guild history versus both guilds pooled. A categorical Dirichlet prior is **0.5 pseudo-observations per state per contributing training individual**, so predictions using 1, 6 or 12 training individuals receive the same prior strength per unit data. This correction was made during method development after a unit test detected misleading pseudocount behavior for category shifts; the final dataset was completely regenerated. All held-out XY cells are scored, including previously unobserved ones; the fraction supported by personal training data is reported separately.

Observed/simulated use is binned to 3D \((X,Y,Z)\); the primary coarse cutpoints are \(X,Z=(-7,7)\) and \(Y=(0)\), and a fine-grain negative control has extra cutpoints. Group and individual information are separately estimated as

\[
I(G;X,Y),\quad I(G;Z\mid X,Y),\quad I(i;Z\mid X,Y,G).
\]

These are probability-distribution descriptors, **not measures of competition or causal social learning**. Eight-day descriptive information and held-out-four-day log scores are not interchangeable. All uncertainty intervals below resample 30 independent **simulator seeds**, preserving matched-seed pairs between models; they are not field-species confidence intervals.

| Synthetic condition | Individual patch forecast (nats/choice) | Guild patch forecast (nats/choice) | Individual held-out Z\|XY (nats/fix) | Guild held-out Z\|XY (nats/fix) | \(I(G;XY)\) (nats) |
|---|---:|---:|---:|---:|---:|
| Neutral — no reinforcement, no social force | −0.015 | −0.002 | −0.079 | −0.007 | 0.003 |
| Boids locomotor force only | −0.015 | −0.002 | −0.078 | −0.005 | 0.003 |
| Private habit reinforcement only | **+0.428** | +0.029 | **+0.242** | +0.015 | 0.035 |
| Private reinforcement + Boids movement | **+0.432** | +0.028 | **+0.245** | +0.011 | 0.035 |
| Private reinforcement + assortative social choice (without Boids movement) | −0.024 | **+0.592** | −0.016 | **+0.183** | **0.402** |
| Private reinforcement + assortative social choice + Boids | −0.024 | **+0.592** | −0.023 | **+0.183** | **0.403** |
| Above plus resource consumption/replenishment | −0.028 | −0.053 | −0.163 | −0.051 | 0.009 |
| Assortative condition, reshuffle private Q *within* guild each day | −0.007 | **+0.592** | −0.008 | +0.204 | 0.384 |
| Assortative condition, reset all Q to zero each day | −0.427 | −0.241 | −0.292 | −0.171 | 0.021 |
| Assortative condition, mix social connections across both guilds | −0.100 | −0.004 | −0.047 | −0.002 | 0.011 |

**Crucial negative control:** most of the guild-level effect is created by **private reinforcement × assortative social-choice imitation**. Switching Boids locomotor force on or off scarcely changes \(I(G;XY)\) (0.4025 vs 0.4026). This experiment does **not** show that Reynolds separation/alignment/cohesion alone produces species niche segregation.

## 4. Replicate-paired synthetic uncertainty and controls

Representative differences across exactly matched simulator seeds, with 5,000 resamples of the 30 complete seed worlds:

| Paired contrast | Mean difference | RNG-seed bootstrap 95% |
|---|---:|---:|
| Private reinforcement vs no learning, personal patch forecast | +0.443 nats/choice | [+0.365,+0.522] |
| Private reinforcement vs no learning, personal 3D Z\|XY forecast | +0.321 nats/fix | [+0.238,+0.404] |
| Add assortative social choice to private reinforcement+Boids, guild patch forecast | **+0.564** | **[+0.476,+0.638]** |
| Same change, guild 3D Z\|XY forecast | +0.171 | [+0.077,+0.279] |
| Same change, descriptive horizontal guild information | +0.368 | [+0.267,+0.462] |
| Remove Boids motor force from learned assortative choice, guild patch forecast | +0.0005 for motor-OFF relative to ON | approximately zero |
| Add consumption to the learned assortative condition, guild patch forecast | −0.645 | [−0.707,−0.565] |
| Mix social connectivity between guilds, guild patch forecast | −0.596 | [−0.661,−0.516] |
| Reset private reward memory each day, guild patch forecast | −0.833 | [−0.933,−0.732] |
| Permute private memory within same guild each day, guild patch forecast | +0.001 | [−0.005,+0.005] |

A second negative control preserves the six 2-agent Boids dyads but reassigns **three dyads per group** in all \(\binom63=20\) possible ways. For learned assortative choice the actual held-out grouping carried mean \(I(G;XY)=0.463\), and the average alternative group assignment 0.083, giving **+0.380 nats** (independent-seed bootstrap interval **[+0.285,+0.475]**). Neutral controls show no corresponding excess. Because complementary labels yield the same mutual information, the **minimum possible per-seed exact group-partition p is 0.10**. The seed-level contrast is descriptive evidence **in the generating model**; no wild-group hypothesis test is claimed.

### Where does the group occupy space?

When assortative choice is learned, the held-out horizontal group-center separation averaged **15.99 m in absolute value**, but its sign was positive in 13/30 simulated worlds and negative in 17/30. The *presence/strength* of a split can be predictable from a specified interaction network; the identity of which guild selects the left vs right patch is **not determined without observing its early history**. One must not imply fixed species-specific sides or ancestral resource preferences.

### Robustness and spatial resolution

At the five candidate scenarios examined on both grains, learned assortative group \(Z\mid XY\) held-out predictive gain was **+0.183** (coarse) and **+0.190** (fine), whereas mixed-network group gain was −0.002 and −0.009 respectively. The absolute entropy/information values depend on grain and the 3D observation model; directions of the main group-vs-mixed comparison were preserved in these two preselected grains. The \(\alpha\in\{0,1,2\}\) separation/cohesion candidate sensitivity also leaves main group horizontal information near **0.4025** under assortative choice, unlike the much stronger effect of changing the social-choice network.

## 5. Exploratory information-level crossover, not a universal threshold

A later **exploratory** ten-point scan varied only assortative social-choice strength \(\lambda\in\{0,0.25,0.5,0.75,1,1.25,1.5,1.75,2,2.5\}\). The held-out resource-choice information carried by the individual and group crossed at **\(\lambda\simeq0.443\)** by linear interpolation. Thirty matched RNG worlds resampled as complete seeds gave a **[0.349,0.535]** numerical-bootstrap range. This depends on the stipulated softmax temperature, learning/forgetting rules, resource layout and forecast horizon. **It is not a bifurcation, ecological tipping point, competitive exclusion threshold, or biological critical coefficient.**

## 6. Connection to existing ecology programmes, without overstating them

- **batter:** stable individual altitude profiles without necessary spatial partition could be consistent with learned private policies, but current wild data do not identify memory, learning or the social-choice mechanism in this model. A direct test needs repeated behavioral state and environment measurements.
- **ODSP:** the level carrying held-out niche information can shift from `individual` to `social guild`. Future ODSP-style tests must condition on shared geographic support and avoid pooled reference/label leakage, and should compare an individual label against an independently measured social network/community assignment.
- **louis:** reward stock/renewal may alter which environmental states are available to be buffered, but v12 does *not* implement louis's time-matched available-versus-used hydrology experiment, so there is no new empirical claim about King Rail habitat tracking.
- **mina:** private, group and resource processes may change site-use concentration, but this short-term movement model has **no breeding substrate, annual demography or observation-error null**; it does not explain the observed penguin population decline or breeding-component contraction.

## 7. What would falsify the model in independent data?

1. Observe an animal's patch choice, reward/resource availability, and measured social-network partners across **repeated independent sessions**. Fit a policy with *identical prior preference states* and separately predict held-out individual identities and social-group membership. A model with no individual-specific initial resource targets should predict new sessions; its success is not guaranteed by these synthetic tests.
2. Change the social network or environmental opportunity **independently of the outcome**, rather than labeling animals by a posteriori spatial overlap. If individual historical preference persists through partner mixing despite model predictions, this specific mechanism is insufficient.
3. With instrument-specific localization uncertainty, test whether the 3D distribution and conditional-height profile forecast wins against simpler habitat-only and shared-guild policies on held-out sites, seasons and species.
4. Test resource-consumption versus crowding cues with independently measured replenishment rates and true prey/patch supply. Artificial reward laws alone cannot establish competition-driven partitioning.

## Reproduction

```bash
python -m pip install 'numpy>=1.26,<3' 'matplotlib>=3.7,<4'
PYTHONPATH=validation_v12 python -m unittest discover -s validation_v12 -p 'test_*.py' -v
PYTHONPATH=validation_v12 python validation_v12/emergent_preferences.py --seeds 30 --out validation_v12/results/endogenous_policy_v12.json
PYTHONPATH=validation_v12 python validation_v12/species_partition_null.py --seeds 30 --out validation_v12/results/guild_relabel_null_v12.json
PYTHONPATH=validation_v12 python validation_v12/social_influence_scan.py --seeds 30 --out validation_v12/results/social_influence_scan_v12.json
PYTHONPATH=validation_v12 python validation_v12/grain_audit_v12.py --seeds 30 --out validation_v12/results/grain_audit_v12.json
PYTHONPATH=validation_v12 python validation_v12/crossover_audit_v12.py
PYTHONPATH=validation_v12 python validation_v12/audit_v12.py
PYTHONPATH=validation_v12 python validation_v12/plot_v12.py
```

The accompanying `force_family_sensitivity_v12.json` replays the three source-equivalent \(\alpha\) values for the private+Boids, assortative choice, and depletion conditions. No raw animal data are redistributed. The GitHub repository contains the previous observed-data freezes intact; **nothing in v12 overrides their unsupported primary social interaction forecasts**.
