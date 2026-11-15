# Reproduction gate: Mazar & Yovel 2026 cave-exit clustering source completeness

**2026-11-08 — source authenticity / execution-eligibility ONLY. No new bat observations, no original numerical model output opened.** Prior eLife `10.7554/eLife.105571` already demonstrated that confusion can sharply reduce simulated cave exits and multi-call clustering partly restores success. Those are original authors' findings.

### Why this check is necessary

Original MIT source `omermazar/Colony-Exit-Bat-Simulation`, pinned Git commit `a74fb61a8efb57ca37693893c3bd7b35fa94fa89`: `BatFlightForGui.m` calls `BatManueverDecision_FullConfusion_ver08Aug24` when `AllParams.BatSonarParams.ObsClusterFlag` is true (the original no-cluster fallback calls `BatManueverDecision`). A full 268-object Git source-tree inventory did not show the `BatManueverDecision_FullConfusion_ver08Aug24.m` file. This makes the clustering path apparently nonexecutable AS DISTRIBUTED, subject to checking other official archives.

Official publication source [eLife 105571](https://elifesciences.org/articles/105571) also cites Zenodo DOI `10.5281/zenodo.16992617`. This is a second official source candidate, not an unauthorized mirror.

### Frozen procedures BEFORE any source result

1. Checkout original GitHub pinned SHA via Actions in separate `upstream/` ephemeral directory, verify original SHA and all original paths. Do not commit raw original source files or data.
2. Inspect original `BatFlightForGui.m` and `Experiments Code/CaveExit_Experiment_Confusion.m` for the clustered-vs-unclustered branch and original source expected implementation symbols. Record verified source line numbers and SHA, and actual existence of the target function. Do not infer missing function from grep only.
3. Parse original parameter workbook `DATA/DefaultParamsTable_CaveExit_FInal_withConfusion_PK.xlsx` `BatSonar` sheet with stdlib OOXML to check `ObsClusterFlag` parameter cell content. Read only public model parameters, no original bat observations. Note original experiment overrides exactly and source default=5 in `readme.txt` but `Confusion.m` overrides `ObsMemorySize=10`; no silently identifying these as the same parameter.
4. Query official Zenodo `https://zenodo.org/api/records/16992617` for file metadata. If a single archive is <=80 MB, download transiently from its *exact provider-supplied* file URL to list member basenames and check for missing `.m` function, without opening simulated animal values. If files are too large, inaccessible or metadata lacks download URLs, SOURCE STOP for Zenodo member coverage. No bypass/guess of private file paths. Record source archive hash/license.
5. **No MATLAB numerical replay claimed** unless the exact original clustering function and all runtime dependencies are available and a separate outcome-independent execution protocol is established.
6. A later question about memory on static walls versus moving prey requires source-exact acoustic physics or an openly labeled toy; the 310-cell Gaussian model from Nov 7 remains an external theory and is not original source code.

Acceptance: original clustering code path fully present in at least one author source => source eligibility PASS for dependency testing, not performance replication. Else output **SOURCE_IMPLEMENTATION_GAP** with two archive statuses. Keep PR #36 Draft and original batter manuscript frozen.
