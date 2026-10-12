# Verification report

OSS preparation for plugin 0.1.0 · 2026-10-12 · Linux x86-64 · Python 3.12.14 · Node 24.19.0 · npm 11.9.0 · FFmpeg 7.1.5

## Reproduced in this preparation

- Six packaging tests: manifest/skill consistency, diagnostics, workspace isolation, path rejection, deterministic source ZIP/fresh extraction, plugin-root ZIP and license inclusion.
- Thirteen Python dashboard tests: parsing, refresh/provenance, editable specs, aggregation/null handling, schema/numeric validation, path safety and tampered outputs.
- Twenty-six Node motion tests: scene validation, aggregation, bounds, inert labels, path safety, exclusive outputs, actual PNG data and retained snapshot.
- Eight generated-JavaScript behavior checks through the minimal DOM adapter: startup, panels/cards, filtering, empty results, reset, dimension selection, metric selection and repeated reset.
- Registry-backed npm lockfile generated for Canvas 0.1.100; `npm ci --omit=dev --ignore-scripts --no-audit --no-fund` succeeded using a fresh empty npm cache and no preexisting runtime node_modules. Three applicable runtime/native packages installed. The lockfile also records optional packages for other platforms; those platforms were not tested.
- Fresh source ZIP extraction followed by a second clean-cache `npm ci` and the full smoke test also passed.
- Real CSV → dashboard → selected region/revenue snapshot → PNG and MP4. Expected grouped totals 42,700 / 33,700 checked against project data. ffprobe verified H.264, 1280×720, 90 frames and 3.000000 seconds. FFmpeg decoded the complete video without errors.
- ZIP packaging fixes filenames/timestamps/permissions; repeated builds from identical source bytes match SHA-256. Both hidden marketplace and compatibility manifests are retained. Source artifacts contain no dependencies, generated media or caches.
- Private-data/source scan found no credentials, personal email addresses, user-local paths or downloaded proprietary assets in distributed project source. Retained original prototype hashes match their provenance record. The implementation and prototype were independently authored for this project and MIT publication was approved by the owner; external components retain separate licenses.

## Boundaries

- No public GitHub remote, release or hosted CI result is claimed by these local checks.
- No installation in the user's real ChatGPT/Codex account, private portal import, public catalog submission or automatic GUI routing was performed.
- No new real-browser visual/accessibility pass or manual PNG inspection was performed in this preparation. The DOM adapter is not a browser.
- Only this Linux environment and installed Python/Node/FFmpeg versions were tested locally. CI is configured for Python 3.10/3.13 and Node 22/24 on Ubuntu; results require an actual CI run.
- Font coverage and pixel-level output vary by operating system. Inspect a PNG on the destination machine.
- Historical isolated CLI 0.159.2 registration/install/discovery/uninstall and earlier visual tests are preserved separately in [QA-HISTORY.md](QA-HISTORY.md); they are not a claim of present user installation.

## Reproduce

Follow [CONTRIBUTING.md](../CONTRIBUTING.md) for clean dependency installation, then:

```sh
python3 -m unittest discover -s tests -v
python3 -m unittest discover -s plugins/data-story-studio/tests -v
node plugins/data-story-studio/runtime/motion/test.js
python3 tests/smoke.py
```

Dependency installation and system prerequisite setup are separate from tests. Tests do not change client configuration.
