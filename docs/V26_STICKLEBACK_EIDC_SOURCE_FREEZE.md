# v26 frozen source gate: independent 2021 stickleback fish tracks

**2026-11-24 JST; frozen before opening any EIDC original movement outcomes. SOURCE-ONLY.**

## Independent original source
MacGregor, H. E. A. & Ioannou, C. C. (2021), EIDC dataset DOI https://doi.org/10.5285/08305a43-79b5-432f-ad20-2ddffe0d1077. Original *Gasterosteus aculeatus* eight-fish XY pixel time series, recorded 25fps, with explicitly flagged missed tracks and repeated food rewards. Linked published paper DOI https://doi.org/10.1098/rsos.210655 studied 12 shoals of eight fish through time. Public original EIDC index https://catalogue.ceh.ac.uk/datastore/eidchub/08305a43-79b5-432f-ad20-2ddffe0d1077/ lists numbered TXT files, typically ~7–12MB, and __README.html. The directory does not itself identify the relationship between file number, shoal ID, day and trial, so **do not assume one file = one independent fish group**.

The dataset uses the Open Government Licence v3 and requires source citation and the attribution “Contains data supplied by UK Centre for Ecology & Hydrology.”

## Predeclared source-only v26 gates

1. Fetch no more than 2 MiB of the *official EIDC index* and parse only TXT filename / public byte-count pairs (names must match two/three-digit base and .txt extension). Reject changed/unknown table schema, more than 200 files, fewer than three, duplicated filenames, redirects to other hosts, unbounded sizes or zero sizes. Hash exact index bytes with SHA256.
2. Authenticate exactly THREE preselected original source-format probes: 01.txt, 02.txt, 105.txt; each bounded to 15 MiB and matching directory size, compute original full-file SHA256. Check *schema only*: 3 first nonempty lines, delimiter character frequencies, token count, numeric fraction, length/line count, possible header flag. Do NOT save numeric XY, fish speed, stimulus times, prediction outcomes, within-school effects, plots, or raw bytes to GitHub.
3. Verify that source columns can be mapped unambiguously to an individual fish and native clock; school identity remains UNKNOWN unless original source includes an explicit map. Structural metadata success = SOURCE_STRUCTURE_ONLY_NOT_ECOLOGY_ADMITTED. Any failed checksum, source download, schema, access or time mapping = SOURCE_ACCESS_OR_SCHEMA_STOP. No third taxon ecological evidence is scored.
4. Synthetic known-truth fixtures validate valid source listing, malicious redirect, corrupted file lengths, missing field structure, false biological school ID inference, and text/plain numerical header ambiguity.
5. Separate biological admission requires original author-verifiable file-to-school and repeated-trial mapping and at least three **distinct original shoals** with complete train/test ID separation, not merely three numbered text files.

## Follow-on primary forecast only after source gate, not executed in this step

At original 25 Hz, compare other-fish velocity *measurement ages* 0, 0.2, 0.4, 1, 2 seconds (exact lags 0,5,10,25,50 frames) without interpolating 0.1 or 0.5 seconds. Keep current focal own motion and current group geometry identical across each arm. Use frozen Ridge alpha=10 with train-only scaling, leave-whole-shoal-out, original finite tracking mask, shared prediction cohorts: future mean velocity 0–0.2 s as primary, future 0.6–0.8 s as secondary. Compare in squared source pixels/sec; never pool with tetra cm/sec or ayu unknown source units. Do not tune the cohort/clock or infer group IDs after seeing outcomes. No animal calling observations in this dataset, hence no test of fish chorus or feedback.

**No new original field fish scores in v26 source-only step.** Keep PR #248 Draft and main unchanged.