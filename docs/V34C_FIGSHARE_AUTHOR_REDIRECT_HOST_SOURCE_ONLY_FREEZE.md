# v34c SOURCE-ONLY official Figshare CDN redirect-provenance probe (no original bytes)

**Frozen 2026-11-24 JST before inspecting the original small file redirect LOCATION header values or original file contents.** Following successful [v34 original 2026 Figshare article metadata](v34_verification/FOUR_2026_CONTROLLED_FISH_FIGSHARE_ORIGINAL_SOURCE_ONLY_MANIFEST.json), v34b small-source job [#45368053292](https://github.com/zuizui0223/boids/actions/runs/45368053292) correctly returned SOURCE_ACCESS_STOP for all three author records because Figshare official `ndownloader.figshare.com` links redirected to an **unregistered external CDN host**. No original author file was opened, no fish result exists in v34b.

Only inspect redirect metadata for exactly these FOUR previously source-pinned small files:
- 31378621 Figs.zip, provider bytes 1,863,466 / MD5 4514391ae74d0715969159b9eda9c11a.
- 31386349 Model code.zip, provider bytes 181,872 / MD5 4e6cf4d167c6204d4f557ae456ed5ba1.
- 30539666 Model3D-VR.py, 44,263 / MD5 fdb679b5bb70f654eb569b7b45a54e9c.
- 30539666 Parameters-Input.txt, 2,409 / MD5 ee85f780cd248dfda38a4438a581d8a3.

For each original provider record, reauthenticate its EXACT article ID, DOI, author-provided download_url, file bytes/MD5. Send HTTPS HEAD, or bounded GET Range bytes=0-0 if HEAD is unsupported, to the **unchanged ORIGINAL provider link** with automatic redirects DISABLED. Record only HTTP status, `Location` URL scheme + host, whether it is HTTPS and whether the original request was at the figshare original provider; never follow a Location, never log signed URLs, query tokens, original user credentials, any source file bytes, original code, or fish data. If the source returns HTTP200, record `NO_REDIRECT_SOURCE_DIRECT` with no body read, else `ORIGINAL_PROVIDER_REDIRECT_METADATA_ONLY` if status 301/302/303/307/308 and exactly one HTTPS Location host. Any other status or error STOP.

The resulting host may be a legitimate source-provider-signed object storage CDN, but it is NOT automatically trusted by merely appearing in a redirect. After verifying a consistently supplied host, and before opening any fish-associated file, a separate source-only v34d amendment may allow that **exact observed HTTPS CDN host** *solely through a single redirect from the pinned official original Figshare file URL*, retaining strict original provider file MD5/byte size and caps. No broad unverified redirect trust, no unlimited traversal or headers leaked.

No fish experimental treatments/positions/code values read or results fitted in v34c, no acoustic source, no change to v33 original data or effects. Draft PR #248, main untouched.
