# v29 publication provenance

The user authorized publication of the completed v29 research branch and creation of a draft pull request on **2026-10-30 JST**. The work is published in [draft PR #29](https://github.com/zuizui0223/boids/pull/29), targeting `main` from `analysis/v29-duck-persistence`. The base remains `47cf12b51553c865027961ae5c162f1b479f5c8c`.

Local Git HTTPS authentication was unavailable, so the connected GitHub Git-data API recreated the four reviewed local commits in their original order. The API assigns new commit metadata, and the recreated commits consequently have different commit identities. **Each corresponding Git tree is identical**, verified both from the API's returned tree hashes and after fetching the published commits into the local repository. This establishes byte-for-byte equality of each repository snapshot, including the implementation and original saved results.

## Local execution and published snapshots

| Stage | Original local commit | Published commit | Identical Git tree |
|---|---|---|---|
| Protocol | `744ae6598aa96d5132da2b2fa3b1d4344f506851` | [`f17ca9d0b434aa6a0b628d04741a97da4a72f871`](https://github.com/zuizui0223/boids/commit/f17ca9d0b434aa6a0b628d04741a97da4a72f871) | `4b175a059e3f077592ba1b4db2f8ce0a8774d0e1` |
| Implementation used for scoring | `a4dc841369b80ad0994435fe17ffe2aef197fd2a` | [`18672bd513ab430ecfea83bd5f21f351c43ef683`](https://github.com/zuizui0223/boids/commit/18672bd513ab430ecfea83bd5f21f351c43ef683) | `39cf555a23f51bdfc35a6cbced08e58cea59271b` |
| Results and synthesis | `045d88261b5684717146152ba2b2f9b2b967d5ef` | [`a48ac66bcb71a76999d8f85b219fe2b1b7798d8e`](https://github.com/zuizui0223/boids/commit/a48ac66bcb71a76999d8f85b219fe2b1b7798d8e) | `eda1d9cad2d137c752cd1f201f36e51a67c0c278` |
| Final reviewed wording | `e0efa1b3c7f9546d6f154bf31bedca5e3ecf24a4` | [`e52f0f212e9c1941abad96946a90ea6171ae3cb4`](https://github.com/zuizui0223/boids/commit/e52f0f212e9c1941abad96946a90ea6171ae3cb4) | `bb97732ae9d4ea23b1a647e072e651d48b6aacfe` |

The original [v29 numerical receipt](../validation_v29/results/duck_persistence_v29.json) remains unchanged, with SHA256 `2055a07f9cda4963789f84d43558dec66ae64f454139ddb00fec6d07ce4bbf95`. Its `code_base_sha` correctly identifies the **local implementation commit used for the original scoring run**, `a4dc841369b80ad0994435fe17ffe2aef197fd2a`; the corresponding public implementation snapshot is `18672bd513ab430ecfea83bd5f21f351c43ef683`. A subsequent CI artifact naturally records the CI checkout's commit instead.

The [v13 fixed-code replay](../validation_v29/results/v13_replay_2026-10-30.json) also remains unchanged, with SHA256 `c7e34840d91306045cbad7f0bf350cc68067a564b95135f0f28010b84f3e8e85`.

## Chronology and interpretation

The v29 protocol was committed **locally before the new persistence errors were calculated**, with v23's positive results already known. This GitHub publication took place after the completed analysis. Neither the recreated remote commit dates nor this mapping establishes public preregistration. The analysis remains a same-source exploratory extension, and CI reproduces its computation rather than providing an independent biological replication.

Publication-status documentation was added after the four identical-tree snapshots above. Those later documentation changes do not alter the analysis code or numerical receipts.

## GitHub verification

The first published-code source replay, [GitHub Actions run 41033755223](https://github.com/zuizui0223/boids/actions/runs/41033755223), **passed** and completed at **2026-10-30 18:29:47 JST**. Its head was `e52f0f212e9c1941abad96946a90ea6171ae3cb4`; the pull-request merge checkout used by Actions was `a985a88ed25b9966d8b883c9220fe07cf0c815f0`.

- The unchanged v23 suite passed all 17 tests; the new v29 suite passed all 12 tests.
- The original-source replay completed and returned `V23_FROZEN_RECEIPT_MATCH`, with the same 49 birds, 2,664 targets and `1e-12` receipt tolerance.
- All four fixed comparisons, including their mean gains, bootstrap intervals, sign probabilities and positive-bird counts, matched the original saved result within `1e-12`. The maximum numerical difference was `2.7755575615628914e-17`.
- The anonymous aggregate was archived as [artifact 12967525495](https://github.com/zuizui0223/boids/actions/runs/41033755223/artifacts/12967525495). Its ZIP hash is separate from the unchanged original receipt hash above.

The [v29 result note](V29_OBSERVED_DUCK_PERSISTENCE_RESULT.md#artifacts-and-verification) and the PR's verification section link this completed computational replay. Later documentation-only updates are not new statistical analyses.
