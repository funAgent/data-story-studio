# Historical verification record

The following was recorded during the initial local-package development. These statements are prior-run evidence, not a new verification of a user account, client GUI or operating system. Current OSS preparation results are in [QA.md](QA.md).

# Verification report

Release candidate 0.1.0 · 2026-10-12

## Passed

- Actual Codex CLI 0.159.2 parser, local-marketplace registration, plugin installation, enabled skill discovery and uninstall in isolated HOME/CODEX_HOME. The four namespaced skills are setup, create-dashboard, create-motion and data-to-motion. Cached files matched source bytes. No real user configuration was modified.
- Four skills pass the skill-creator frontmatter validator. Manifest consistency and relative marketplace paths checked. This is actual Codex parser validation, not a claim of independent canonical JSON Schema validation.
- Four packaging tests: manifest/components, diagnostic command, isolated source copy, no-overwrite and unsafe-path rejection.
- Thirteen dashboard tests: real CSV/JSON parsing, provenance/refresh, editable spec, count/null behavior, finite values, malformed schemas, overflow, script-like labels, symlinks, traversal, existing output and tampered files.
- Twenty-six motion unit tests cover scene/data validation, aggregation, nulls, unsupported shapes, path safety, exclusive output, actual PNG bytes and retained snapshots. The test runner reports the current exact count.
- Source-only ZIP extracted into a fresh directory, workspace initialized from that copy, sample CSV built into dashboard and snapshot, selected region/revenue chart imported, PNG rendered and inspected, actual MP4 encoded and fully decoded. ffprobe: H.264, 1280×720, 30 fps, 90 frames, 3.000000 seconds. Grouped source totals 42,700 / 33,700 match the inspected preview.
- Additional runtime proof: Chinese-labelled 12-second MP4, H.264 1280×720, 360 frames, clean decoder; Chinese PNG text inspected.
- Eight generated-JavaScript behavior checks via minimal DOM adapter: initial rendering, cards/panels, filter, empty state, reset, dimension selection, metric selection and repeated reset. This is not a real browser test.

- Independent natural-language workflow with a new six-row Chinese-labelled CSV passed: dashboard with two metrics, 12-second revenue animation, Chinese title edit and a second 12-second export. Expected monthly revenue 1500 / 0 / 2100.5 / 1000 and order totals were preserved; source/snapshot/output hashes verified. Both videos decode cleanly and differ after the title edit. Malformed numeric data, all-null sum and missing metric fields reject without fabricating output. This tested packaged skills and runtime usage, not automatic GUI routing.

## Not verified / limits

- Real user Codex client/OS installation and automatic skill selection in its GUI.
- Clean dependency download on another machine. Tests reused preinstalled Node 24.19.0, canvas 0.1.100 and FFmpeg 7.1.5. Canvas direct dependency is pinned; offline npm registry metadata was unavailable, so the package does not claim a tested lockfile. First approved install occurs only in the copied user workspace and should retain its generated lockfile.
- Full dashboard browser rendering, responsive layout and browser accessibility tree. Chromium launch in the cloud execution environment failed with socket permission restrictions. No browser visual pass is claimed; template syntax, escaping and minimal DOM behavior passed.
- Some fixed animation chrome remains English; scene titles, subtitles, labels and source text can be Chinese. A single snapshot import represents one selected chart, not an automatic multi-metric movie.
- Font/pixel parity between operating systems. Install appropriate fonts and inspect a PNG on the destination machine.
- Scheduled data sync, SaaS/database connectors, arbitrary video generation, public publishing and MCP integrations are not implemented. Motion currently has headline, barChart and summary scenes; imported line/table charts become explicitly disclosed bar representations, with 2–8 categories and nonnegative values only.

## Reproduce

Run from the extracted package root:

```sh
python3 -m unittest discover -s tests -v
python3 -m unittest discover -s plugins/data-story-studio/tests -v
node plugins/data-story-studio/runtime/motion/test.js
```

The motion test requires its documented dependencies already available. For the generated dashboard logic:

```sh
node tests/test_dashboard_dom.js /absolute/path/to/dashboard/index.html
```

For actual local installation and removal, follow INSTALL.md. Follow normal approval requirements; the tests above do not install software or change Codex configuration.
