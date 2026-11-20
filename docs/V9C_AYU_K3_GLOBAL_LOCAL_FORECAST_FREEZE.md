# v9c: independent Ayu species, fixed k-nearest group/global/local motor test

This protocol is frozen **after v9b source-only numeric formats and clock diagnostics, before any fish motor prediction outcomes**.

Original Niizato et al. 2024 *Scientific Reports* (doi:10.1038/s41598-024-79232-2), 7 separate original 10-fish *Plecoglossus altivelis* recordings from source pinned `158e8d7ebdef73752da63192ee36e3a099dd5dfa`, repository https://github.com/t-niizato/Information-structure-of-heterogeneous-criticality. Author's original `Compute_IIT/fish_revised/data_import.m` explicitly maps `D(:,3:12)` to 10 X and `D(:,13:22)` to 10 Y. Original source-only v9b Actions #44759606259 verified all files complete (10,101–13,861 rows), no missing XY, frame index +1 and **elapsed-time column showing 30fps native series**. This is different from the 20Hz downstream sampling used in the paper's analysis. We must **not** use 20fps when measuring fish native velocities; selected native 30Hz source clock is independently supported before outcomes.

## Main novel ecological test

In the Puy 2024 black neon tetra original series, nearly 94% of individual-time observations had all 7 other fish within the imposed 25cm neighborhood. Local alignment and global other-seven average then coincide algebraically. To avoid this identifiable-set saturation in independent ayu, define a **fixed topological 3-nearest-fish** neighborhood in the ayu source (out of nine others), and compare its incremental predictive information over whole-group relative velocity.

Seven whole original files retained as separate holdouts. Predictor features at t are:
- G: focal x,y, own last two 0.1s velocity segments, own velocity change and speed, mean relative displacement of 3 nearest fish, mean nearest-3 distance, displacement toward group centroid. Feature standardization fitted only on six other recordings.
- G+Global: G plus the two-component mean relative velocity of all **other nine fish**.
- G+Local3: G plus mean relative velocity of **three nearest fish** in the fixed topological neighborhood.
- G+Both: G + both global and local.
- G+RotatedLocal: G+Global plus same 3 selected neighbors receiving a fixed one-place rotation of the nine other-fish velocity vectors within a focal fish/time. This preserves *all* original positions, focal own movement, other-nine velocity multiset and global average, but misassigns which fish swims at which source location. No social causation or permutation p claimed.

Fixed `Ridge(alpha=10)`, training-only StandardScaler, 30fps original frame check, one source sample every 6 frames (0.2s), 10 fish each, same recorded target positions across models; no post-outcome tuning. Primary endpoint: **0.2s future mean Cartesian velocity** (t→t+6 frame). Delayed (separate) from t+15→t+21 frames, i.e. 0.5–0.7s ahead.

Primary comparison MSE(G+Global)−MSE(G+Both), recording-equal average + 7 recording signs, bootstrap descriptive uncertainty with 5000 whole-recording draws. Secondary: global beyond G, global beyond local3, correct local3 vs fixed velocity crosswalk, repeated for delayed endpoint. Score units are original coordinate units per second squared, **do not pool with black neon tetra original (cm/s)^2**; only percent improvements or signs can be compared cautiously. These are 7 recordings of one additional species, not 7 independent species or confirmed independent fish populations.

No additional fish call or hydrophone data are time-matched to these Ayu trajectories; the fish-school→chorus mechanism remains untested. Source originality and temporal interpolation uncertainty may limit causal interpretation. Any failed source author column/frame/MD5 git blob gate stops without score.

**No merge to main. All original v5–v8 findings preserved.**
