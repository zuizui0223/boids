# v7 — independent high-resolution pigeon-pair source gate

**Date:** 2026-10-26. **Status:** source-schema preflight only; no pigeon GPS position outcomes or fitted Boids parameters have been examined.

## Source

- Independent of the Roy & Abaid bat-pair archive v6: Pettit et al. 2012/2013, *Not just passengers: Pigeons, Columba livia, can learn homing routes while flying with a more experienced conspecific.*
- Public archived copy Zenodo [record 5010830](https://zenodo.org/records/5010830), DOI `10.5061/dryad.53f4b`, CC0. Original compressed GPS data ZIP is 35,052,731 bytes, MD5 `8c8e95641182363ea7ad6d0a9a50a3b1`. File download endpoint `https://zenodo.org/api/records/5010830/files/GPS_tracks.zip/content`.
- Archived README indicates two sites; demonstrator and observer, training/control, twelve releases per pair, and CSV filenames of the form `H32H79_6.csv` (tracked bird H32 flying with H79, flight 6). Critically, both sides of the pair may exist as distinct files, *not independent episodes*.

## Predeclared pre-numeric admission

1. Check byte count and MD5; mismatch → `STOP_SOURCE_SIZE_CHANGED` / `STOP_SOURCE_MD5_CHANGED`.
2. Examine only archive filenames and first-line CSV headers, no coordinates or timestamp values.
3. Pair episodes require **both directions** of the same two bird IDs for the same site and paired-release number, recognized by the specified filename grammar. Require >=8 paired episodes for numerical preregistration; otherwise stop.
4. Do not infer that paired files share timestamps, even if pairing structure is present. The next fixed numeric preflight must assess within-episode temporal overlap and plausible original 5 Hz cadence before computing any directional/Boids model output.
5. No retuning of the above primary admission rule after opening source data. If an archive structural rule fails, report the reason and prefer a new independently selected source over rescuing the old source by changing gates.
6. Public raw tracks are **not redistributed** in boids or GitHub workflow artifacts. Only schemas and aggregate observations can be committed.

## Next prospective study (separate contract after schema)

If the source passes: predeclare exact timestamp field interpretation, geodesic-to-metric transformation with height field semantics, a same-record-time matching tolerance and smallest acceptable number of simultaneous 3D pairs. Then compare held-out next-vector probabilities or squared errors for own-inertia, self+environment and self+true-neighbor versus a ghost/shifted-neighbor negative control. Reserve different **flights and bird identities** for external generalization, and keep BirdID and PairID across flights grouped; otherwise repeated releases contaminate held-outs. Evaluate 3D niche distributions and their temporal/vertical partition only if repeated individuals, spatial vertical resolution, and observation error support genuinely ecological state forecasting.

Prior comparison: [v6 bat-pair result](OBSERVED_BAT_PAIR_RESULT_V6.md) yielded 28 eligible flight pair episodes but no robust actual-versus-ghost directional forecast. This result will not be reopened or tuned as a consequence of the pigeon analysis.
