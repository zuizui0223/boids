# v33: Origin-anchored 2023 Zenodo multi-bat flight-source reconstruction preflight

**Date:** 2026-11-19 JST. Stage: structural and provenance only; **no predictive model or source-wide numerical behavioral effect fitted**. 
**Connection:** continuation of v32 Dryad original CSV transport STOP; **not** an independent field population or independent scientific replication because the 2025 Delmotte Dryad paper explicitly reuses Barré et al 2024 field records.

## Original source and fixed integrity

Barré et al. "Insectivorous bats alter their flight and feeding behaviour at ground-mounted solar farms". Official Zenodo record **10149959**, DOI 10.5281/zenodo.10149959, 2023-11-17/18 v2. The publicly linked original file \`data_bats_barre et al 2023.csv\`, about 3.2MB, has author-published **MD5 60ce63b79fd8a5b9bc4771997de97839**. Direct official URL:
\`https://zenodo.org/records/10149959/files/data_bats_barre%20et%20al%202023.csv?download=1\`.
Check downloaded complete bytes against exact MD5 before even structural parsing. Record SHA256. Do not redistribute raw position/time data in our GitHub artifacts.

## Source structure known from public header

Original semicolon-separated CSV (French comma numeric separator) includes:
\`id_site,typeSite,date,time,Trajectory_identifier,Species_corrected,guild,x (m),y (m),z (m),Speed,sinuosity,Imprecision,buzz_proba,mean_buzz_proba\` plus uncertainty margins.

Each row is one author-derived acoustic localization point; multiple source rows belong to a trajectory. Some author values such as \`999\` are invalid/sentinel (observed in public preview), not real 999 m/s flight. Reconstructed 3D points and speed are not independent sensors; GPS/trajectory-level individual IDs are absent, and acoustic call time is displayed at seconds resolution. This is not a true synchronized multi-animal tag dataset.

## Only source-structure questions at this stage

1. Confirm exact bytes, header, delimiter, dates, location site tokens, total event rows, source trajectory (id_site×date×Trajectory_identifier×Species_corrected) counts, 3D column presence and missingness **without evaluating behavioral speed/buzz/coordinate numbers**.
2. Test whether \`id_site\` contains a date-coded session and is therefore not automatically a spatial site. Count a date-stripped nominal locality stem, its repeats across days and \`typeSite\` \`C\`/\`S\`; do not assert the stem is a mapped independently sampled physical location.
3. Count timestamp string resolution and duplicate timestamp entries, whole-trajectory time intervals, and **possible structural overlaps between different trajectory IDs** within the same named source session. An equal timestamp may reflect rounding; it is not proof of simultaneous independent bats, direct interaction, or social information transfer.
4. If no verifiable ID-disjoint *overlapping* tracks in independently identified recording windows exist, STOP on a contact-based primary. If source lacks validated trajectory identities or synchrony beyond second resolution, any co-occurrence is explicitly *opportunity proxy*, not observed individual proximity or interaction.
5. The 2023 raw-derived archive does not contain the 2025 derived \`Conspecific_sp\` or \`Heterospecific_intraMRE\` fields; do not fabricate them or equate a same-minute species presence proxy with authors' derived cooccurrence.

## Scientific boundary and next decision

A positive 2023 source-structure audit can enable a new, separately frozen **site/recording-context transfer** study, only after establishing independent recording windows and the correct site grain. This would be one landscape/field campaign, not a cross-region ecological law. It **cannot** independently validate the 2025 co-occurrence finding, because it is the underlying source; it cannot repair the v32 original 2025 Dryad outcome-blind file stop. If a genuine independent non-Rhône source is not identified, publish no universal behavior rule.

## Provenance of previous evidence

- v30 Carollia bat-heldout acoustic incremental advantage: negative, unchanged.
- v31 Rhinopoma official public API: 401, no behavioral result.
- v32 Dryad official raw: public file endpoint returned bot \`Validating...\` HTML and REST 401; no numerical \`meanBuzz\` or \`meanVfinal\` results were fitted.
- v33 Zenodo reanalysis receives separate sample and provenance labels and cannot be counted as a new species/site independent study.
