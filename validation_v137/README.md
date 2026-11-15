# v137 genuine supplement acquisition audit

Target: Raposa et al. (2026) doi:10.1002/ece3.72872, PMCID PMC12805223, published Appendix S1 (66.7kB XLSX). Original source URLs via NCBI, EuropePMC, then publisher.

This stage retrieves and fingerprints the actual XLSX from a networked GitHub Actions runner. It uses only Python's standard library ZIP/XML to inventory sheet titles, counts, and the first eight row headings, writing a small human-reviewable manifest. The original workbook bytes are not redistributed or committed. The provenance SHA-256 is computed only after downloading the actual bytes.

**A workbook containing animal-photo rows or per-station total camera days is NOT sufficient to estimate tide x diel per-hour rates.** Admission additionally requires flooded/dry x day/night no-event camera hours or reconstructable station uptime, water-level-at-station labels and observation detection rules.

The workflow fails closed if download or source file structure verification does not succeed; artifact is uploaded even on failure. No ecological effect or meta-analysis is claimed by inventory alone.
