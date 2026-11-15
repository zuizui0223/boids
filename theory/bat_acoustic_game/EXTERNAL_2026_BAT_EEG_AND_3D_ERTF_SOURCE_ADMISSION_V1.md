# Bat 3D sensing + neural response independent archive admission — 2026-11-08

**Source-only preregistered access test BEFORE opening individual bat EEG/flight outcomes or model experiment metrics.** New field/lab measurements 0. Prior `boids` PR #36 is Draft. The 2026 Mazar/Yovel missing clustering implementation and 2024 `Molossus` known original high-crowding result remain preserved. No new conclusions inferred from missing source.

## Critical independent prior art

Teshima et al. (2026), *Proceedings of the Royal Society B* DOI **10.1098/rspb.2026.1463**, PMID 42580728, already recorded trajectories and echolocation for two different bat species across seven obstacle-rich flight arenas; their VRNN captured features across individuals and environments. Their transfer result is **ALREADY PUBLISHED**, and `boids` cannot claim a new demonstration that bat flight contains species-specific latent rules. A publishable extension must ask **where and under which geometry/sensory conditions transfer FAILS**, with source-aware holdout and a new independent estimand. No source raw data or code admission known here yet.

## Source candidate A: actual synchronised bat audio+brainstem response

Tarnovsky et al. 2026 *Proc. R. Soc. B* DOI **10.1098/rspb.2025.2988**, data Dryad DOI **10.5061/dryad.dz08kps9w** (published Jan 8 2026). Source reports 14,364 original vocalizations from **3 Eptesicus fuscus bats**, simultanous EEG and vocal sound. Original XLSX `in_flight_bat_eeg_echolocation_combined_table.xlsx` ~1.67MB (published already analyzed correlations). This is **3 biological bats**, NOT 14k independent animals. It contains auditory amplitude/latency and sound duration/intensity; NO 3D motion, actual other-bat masker or successful prey capture. Studying original acoustic-to-brainstem association is prior art, not a new finding. New source output would require untrained-bat prediction with 2 training bats only, so inferential generality is weak even if accessible.

Source gate: Query ONLY official Dryad API dataset DOI metadata, its version and actual file `stash:download` link; exact original DOI and filename required. Record provider license/digest/size, HEAD and bounded GET `Range: bytes=0-4095` only. If 401/403/no Range, mark STOP, do not bypass or infer data opened. No original EEG values, source IDs or original animal records may be committed.

## Source candidate B: recent 3D sensory self-calibration (SIMULATED)

Steckel 2026 bioRxiv preprint **10.64898/2026.10.22.760884** (Oct 23 2026), original Zenodo source **10.5281/zenodo.23537553** (Oct 22 2026), MIT original code + CC BY 4.0 simulated worlds/runs. Source simulates bat-like acoustic ERTF learning from self-motion and echoes without direction labels. Source summary ALREADY includes symmetric worlds, sparse worlds, specular-reflection room and training/relearning conditions E1–E9 / C1–C5. These prior original source tests cannot be rebranded as new conditions or real bat sensorimotor data.

Official Zenodo distributes a ~**988.3 MB** outer ZIP `2026 - Steckel - Bats Learn Echolocation.zip`. DO NOT download entire archive at this gate. Only official Zenodo API record `https://zenodo.org/api/records/23537553` metadata + HEAD and HTTP **Range** requests capped at 256 KiB for tail and 2 MiB for ZIP central directory; if original provider does not honor HTTP 206 Range, STOP without downloading 1GB. If a central directory is source-accessible, enumerate only member basenames, compressed/uncompressed sizes and original input code/runs/source_data path presence. This is metadata only: NO original training results, source figure numbers, model checkpoints or bat-like virtual sonar data extracted in this step. Do not download `HRTF_Phyllostomus_Discolor_azel.mat` or redistribute third-party permissions file.

## Next analysis gate only after admission

For real brainstem source, only if exact XLSX bytes are legally accessible, freeze biological-bat-level predictive/within-bat checks before opening outcome values; with 3 bats, no claim of species-level regularity.

For 3D simulated archive, only if exact ZIP member access is independently possible and code/test/loss/seed supported, freeze a **new geometry holdout or active movement ablation NOT already E1–E9/C1–C5**, and avoid fitting to original source results or claiming real learning. It should compare explicit movement diversity and 3D spatial identifiability (known source prior), with frozen negative controls.

Stop if source access, integrity or raw sample grain is unavailable; no substitution of synthetic model outputs as independent real-bat empirical results. Keep PR Draft and `batter` frozen releases untouched.
