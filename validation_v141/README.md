# v141: public independent-coast data acquisition gate

Two actual original Dryad sources, no re-use of externally reported effects:

**California** — Kim et al. 2025 fish chorus, Dryad DOI 10.5061/dryad.q2bvq83sw; nine recording sites in three sanctuaries, 2018–2023 and ~18.3 cumulative recording-years. Manual detection intervals and instrument deployment effort are provided in deployment-level XLS/XLSX files. Actual file bytes must be verified before claiming independent-hours or multi-site counts. There is **no verified physical tidal exposure** in the Dryad sheet, so no tide×diel effect.

**Kashima, Japan** — Ota et al. 2026 Methods in Ecology and Evolution DOI 10.1111/2041-210x.70230, Dryad DOI 10.5061/dryad.zkh1893qn (2025 publication). Five hydrophones in one coast, white croaker group state-space model. Source README describes q25_autoChorusDetect4.zip as *chorus-cropped* signal: this may be unsuitable for day/night risk estimation, absent true non-chorus observation effort. Tide/solar originals described in JMA/NAOJ and Zenodo, but do not assume these are present in the 842 MB Dryad package.

This step downloads bounded original exemplars and hashes them. Files exceeding size cap are not downloaded. No acoustic files are redistributed; this is **original-source inventory only**, not an estimated tide×solar ecological effect, a fish individual count, or an independent-coast meta effect.

Primary source info:
- https://datadryad.org/dataset/doi%3A10.5061/dryad.q2bvq83sw
- https://datadryad.org/dataset/doi%3A10.5061/dryad.zkh1893qn
- https://doi.org/10.3354/meps14910
- https://doi.org/10.1111/2041-210x.70230
