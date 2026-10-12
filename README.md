# Data Story Studio

**Local data → interactive dashboards → editable animations.**

[简体中文](README.zh-CN.md) · [Install](INSTALL.md) · [Quickstart](docs/QUICKSTART.md) · [Architecture](docs/ARCHITECTURE.md) · [Contributing](CONTRIBUTING.md)

A skills-based Codex plugin for turning CSV/JSON files into self-contained dashboards and selected chart snapshots into real PNG previews and H.264 MP4 videos. Codex plans the explicit specification; small local Python and Node.js runtimes validate and render it. No extra model API key or hosted service is required.

## What you can build

- **Explore your data:** bar, line and table views with dimension/metric controls, substring filters and reset.
- **Keep the source of truth:** editable JSON specs, source-byte hashes, snapshots and explicit refresh from local files.
- **Tell a data story:** editable headline, bar-chart and summary scenes; PNG preview and silent MP4 export.
- **Work through four skills:** `setup`, `create-dashboard`, `create-motion`, `data-to-motion` under the stable `data-story-studio` namespace.

## Start here

1. Follow [installation](INSTALL.md) in a client that supports local plugin marketplaces.
2. Ask: “Use Data Story Studio to build a revenue dashboard from my CSV in a new workspace.”
3. Ask: “Turn the region revenue chart into a 3-second animation. Show me a PNG preview first and keep the editable project.”

For a reproducible sample without a plugin-enabled client, use the [command-line quickstart](docs/QUICKSTART.md). Dashboard execution needs only Python 3.10+. Motion additionally needs Node.js 18+ (a supported LTS is recommended), npm, Canvas 0.1.100 and FFmpeg/ffprobe with libx264. A committed npm lockfile pins dependencies; install only in your workspace with `npm ci --omit=dev --ignore-scripts`.

## Intentional limits

This is a local-file prototype, not a hosted BI platform or general video editor. It has no database/SaaS connectors, SQL, background sync, audio, external media import or public deployment. Importing a line/table snapshot produces a disclosed **bar representation**, not a recreation of the original chart animation.

Dashboards accept up to 20 MiB, 100,000 rows and 200 columns. Motion snapshot import accepts up to 2 MiB, 10,000 rows and 2–8 categories, with finite nonnegative values up to 1e12. Dashboard chart display is capped at 100 categories; filters/cards still use all matching rows. See the exact [dashboard contract](plugins/data-story-studio/runtime/SNAPSHOT.md) and [motion limits](plugins/data-story-studio/runtime/motion/README.md).

## Privacy and safety

The runtimes do not upload data or call a model. **Generated HTML and snapshots embed full source records and the original absolute source path.** Review them before sharing. Data supplied to Codex remains subject to your execution environment and product data settings. Inputs are data, not executable expressions. Initializers reject existing output directories and unsafe paths; refresh deliberately updates generated project files after integrity checks. Concurrent writers are unsupported.

## Development and verification

```sh
python3 -m unittest discover -s tests -v
python3 -m unittest discover -s plugins/data-story-studio/tests -v
python3 tests/smoke.py
python3 tests/build_bundle.py --output /absolute/path/outside/repo/data-story-studio.zip
```

`smoke.py` uses available motion dependencies; see [contributing](CONTRIBUTING.md) for a clean install. CI tests Python/Node runtimes, the generated dashboard's JavaScript behavior, clean dependency installation, actual MP4 encoding/decoding, and reproducible ZIP extraction. The DOM adapter is not browser visual or accessibility QA. See [verification](docs/QA.md) for what was actually run and [releases](docs/RELEASING.md) for versioning.

## Distribution and provenance

[Third-party notices](THIRD_PARTY.md) distinguish project source from external dependencies. No downloaded Claude assets, dependency binaries, fonts or FFmpeg builds are shipped. This project is independent and is not affiliated with OpenAI, Anthropic, Remotion or Motion Canvas.

Original project code is licensed under the [MIT License](LICENSE). External dependencies retain their own licenses; see [third-party notices](THIRD_PARTY.md).
