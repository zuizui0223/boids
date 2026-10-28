# v17-A2 — Observable individual, source clock and wind-schema audit (before movement targets)

**Amendment recorded after v17-A source integrity only and BEFORE opening any v17 heading, route or response outcome.** The source was checksum-verified in [v17-A](V17_INDEPENDENT_WIND_SOCIAL_ADMISSION.md); this amendment does not alter a forecast model or its eligibility to obtain a favorable result.

## Fixed new evidence available from original archive inventory

- Taylor et al. 2019 Zenodo 5026107: **458 original GPS CSV files** all with the same 18-column Qstarz schema (`VALID, UTC DATE, UTC TIME, MS, LATITUDE, LONGITUDE, SPEED, HEADING, ALTITUDE`, etc). Archive MD5 and SHA256 verified before any model.
- Original weather CSV is **11,529,364 bytes**, MD5 `1a8c56601ed982a7f2968f1348831317`, SHA256 `45885ce19954fd99397b92847421d3e11a6ea2c8d22d1a1d6220ea4940fa2917`, **152,226 physical rows after the first line**. Its first line has three numeric-like fields, **not an identified named column header**. Publication describes source columns as date/timestamp, wind speed, wind bearing. Do not silently assign units/time zone from guesswork.

## Stage A2 permissible reads — no GPS coordinates, courses, weather values, or prediction

1. Parse original GPS filenames using explicit `<bird>_<phase>_<within_phase_release>_GPS.csv` grammar, where bird is a leading letter + 2 digits and phase in 1..4, release in 1..6. Count unique bird IDs, releases per phase, duplicate `bird×phase×release`, unknown filename shapes and repeated bird sessions. Bird identity in the name is NOT proof that partner networks are independent.
2. For at most 32 filename-evenly sampled original GPS tracks, read the **first 100** records using only `VALID`, UTC date/time and milliseconds. Count missingness/validity and token shapes; do not export exact dates or times; GPS drift/cofix precision is **not yet verified**. Do not read latitude, longitude, course, speed, altitude or target outcomes.
3. Weather CSV: treat first line as **data** when its tokens are not a supported named header. Sample up to 4,096 evenly-spaced source physical records for the **format, numeric type and finite/range validity** of columns 2/3, but never output values or weather–movement relationships. Count all source lines and header interpretation exactly. If parsing date/time is ambiguous, report the candidate formats as UNKNOWN.
4. Before any weather × GPS join require fixed timezone from source metadata, cross-bird recorded UTC precision in the GPS, and a separate published original pair/phase/release schedule. Date/time token-shape matching does not prove a correct timezone.

**Admission criterion for next structural phase:** source filename parser recognizes all original biological GPS entries with no duplicates; all 4 nominal phases and recurrent identities observed; weather record is physically readable with three consistent columns and finite values. This is **only an eligibility for further raw-source timing validation, not a permit to fit interaction outcomes**.

Stop/UNKNOWN where any source metadata is ambiguous. It is not allowed to choose an offset/time convention based on which one maximizes an observed turn-forecast gain.
