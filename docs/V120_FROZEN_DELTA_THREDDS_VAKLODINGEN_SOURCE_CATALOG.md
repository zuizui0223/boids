# v120 | Deltares THREDDS Vaklodingen historical seabed catalog: frozen source audit

2026-11-10 JST. AFTER original v119 verified that two genuine 2019/2020 Borndiep bathymetry NetCDFs lie OUTSIDE the Oosterschelde source study; BEFORE examining any new Deltares catalog spatial/temporal output. This is a SOURCE-ONLY feasibility audit, no bird time-niche effect.

Two pre-declared original native first-party THREDDS public catalogs:
- Deltares wiki identifies a 2020 release at https://opendap.deltares.nl/thredds/catalog/opendap/rijkswaterstaat/vaklodingen_new/catalog.html . Query native XML https://opendap.deltares.nl/thredds/catalog/opendap/rijkswaterstaat/vaklodingen_new/catalog.xml.
- Older THREDDS tiles at https://opendap.deltares.nl/thredds/catalog/opendap/rijkswaterstaat/vaklodingen/catalog.html ; native XML https://opendap.deltares.nl/thredds/catalog/opendap/rijkswaterstaat/vaklodingen/catalog.xml.
- A small native index file catalog.nc appears in older provider catalog (~41 KB): official source https://opendap.deltares.nl/thredds/fileServer/opendap/rijkswaterstaat/vaklodingen/catalog.nc . The index is NOT bathymetric sediment or survey date itself.

Original source frame is ALL tiles in both original catalogs, identified by authoritative XML dataset name/path/size or source metadata, never by measured habitat outcome. Preserve source SHA and catalog identity, publisher server modification timestamps and source failures separately. The THREDDS published updated date is NOT bathymetric survey date, and older interpolated Vaklodingen NetCDF may lack any actual 2019/2020 sounding. A 2020 release label is not necessarily a 2020 observation. Never map 2014 carry-forward data to the 2020 gull year as real observations.

First original audit checks both native XML catalogs under 3 MB cap each, verifies XML vs HTML errors; extracts complete original NetCDF tile filenames and official source metadata/time/spatial fields when present. Also inspect the optional catalog.nc only if official HTTP HEAD content length <=2MB, verify native NetCDF magic and original SHA; list native CF variables/attrs and georeferencing. If any source is inaccessible, report SOURCE_UNAVAILABLE, no fabricated local tile.

**Geographic membership must be demonstrated by native CRS plus native spatial coordinates (not by a filename).** Four fixed Zeeland sites from v116 original RD source x roughly 36,912–44,592 m and y 401,844–409,562 m (Roggenplaat, Neeltje Jans, Roompotsluis Buiten and Marina); only physically georeferenced original source grid with **actual valid cells** at these sites can fill previous 2019 lidar masked ground. Native vertical NAP datum and true bathymetric survey date must also be verified, before any 2020 bird accessibility score. This catalog-only run cannot establish that.

Context source stop: original v118 2020 two-gull May–July actual GPS 45,133 moves and seven equal-step geodesic rotated alternative points had full original 2019 lidar DTM z for only 41.71% (L. argentatus) and 57.80% (L. fuscus), below frozen 90% each-taxon completeness gate. This remains NOT_ESTIMATED for tide-dependent bird habitat selection, regardless of new catalogs.
