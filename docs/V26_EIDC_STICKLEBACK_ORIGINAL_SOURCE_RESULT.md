# v26 original stickleback source diagnosis — 84 files, last-column frame clock, complete XY blocks

**2026-11-24 JST — SOURCE ONLY, NO new observed movement prediction**. Dataset: MacGregor & Ioannou 2021, original EIDC DOI https://doi.org/10.5285/08305a43-79b5-432f-ad20-2ddffe0d1077, *Gasterosteus aculeatus*, nominal 25fps and 8 fish. Original EIDC uses Open Government Licence v3; cite data/paper and include attribution "Contains data supplied by UK Centre for Ecology & Hydrology."

[Source directory and 3 original files #45333264730](https://github.com/zuizui0223/boids/actions/runs/45333264730): PASS, **84** original numbered .txt files in published directory; no school/time labels in listing. All three preregistered file SHA256 and bytes independently verified; no fish outcomes computed.

An initial [v26b source semantic run #45333428558](https://github.com/zuizui0223/boids/actions/runs/45333428558) correctly STOPPED on **incorrect schema expectation** that original first column was a nearly complete frame ID. It was NOT; our source-only preflight refused to fit movement models. Synthetic fixtures passed but real source had column0 finite fraction below 0.99 (as low as 0.908), so scientific source admission failed as intended. We did not revise v26b outcome or rescue its predeclared clock rule.

A follow-up source-only exploratory [v26c original audit #45333543614](https://github.com/zuizui0223/boids/actions/runs/45333543614) identified original 17-column header order:
`x.1,x.9,x.2,x.10,x.3,x.11,x.4,x.12,x.5,x.13,x.6,x.14,x.7,x.15,x.8,x.16,frame`.
Thus **the last (17th) column is labeled frame**, and the first 16 alternate position coordinate members. The first 16 original source columns have the same finite fraction in each inspected file; the last column is 100% numeric. The non-numeric/missing source label in the first sixteen is `NA`. Original frame increment (+1) still requires independent numeric audit before treating 25fps as exact native clock.

| Original EIDC source | Verified original byte size | Raw data rows, excluding one header | Complete 16-coordinate rows | Complete share | NA rows |
| --- | ---: | ---: | ---: | ---: | ---: |
| 01.txt | 9,422,363 | 37,605 | 35,075 | **93.2722%** | 2,530 |
| 02.txt | 8,144,030 | 40,569 | 40,223 | **99.1471%** | 346 |
| 105.txt | 8,734,098 | 35,445 | 32,173 | **90.7688%** | 3,272 |

The three original hashes are respectively SHA256 657872348cdf31b90e01c9f087df64937cb435f14d92eb1b1b9c3bc59a4b314a, 552f766d2a72926d041df8316caf8a0e2454aee64746ca837ad60e83973d10ed, and 541617d6458a07c22bedeca43636c76e59e4dc30cfb12eedfa038d168cec0336.

This resolves the **column-order source schema** but **does not establish the 84 numbered file → 12 original shoal identities/day mapping**, individual tracking corrections, actual environmental co-stimuli, or time-aligned call events. It does not establish 84 independent school replicates. Under a separately frozen exploratory protocol, a 3-recording model may be scored as recording-heldout *within this one published third fish taxon*, but never as whole-independent-shoal validation until original group IDs are available. No new 0.2s biological response claim, no 3-species formal meta-analysis, and no fish chorus/Boids causal mechanism established here.

Main remains unchanged, PR #248 Draft.
