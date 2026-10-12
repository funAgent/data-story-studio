# Architecture

## Execution flow

1. A skill asks Codex to interpret the user's goal and write an explicit dashboard or scene specification.
2. `scripts/studio.py` checks prerequisites and copies runtime sources/fixtures into a new private workspace.
3. `runtime/dashboard.py` parses local CSV/JSON, validates the spec, records source provenance and emits HTML, snapshot, spec and manifest.
4. `runtime/dashboard.html` renders the embedded data locally using browser controls; it never writes to disk.
5. `runtime/motion/cli.js` validates a selected snapshot, aggregates a chart and writes an editable scene project.
6. `runtime/motion/motion.js` renders frames with Canvas; the CLI invokes FFmpeg without a shell for H.264 MP4.

The source format is versioned separately from plugin version. See `runtime/SNAPSHOT.md` (snapshot schema 1) and `runtime/motion/project.schema.json`. Runtime validation adds semantic constraints beyond JSON Schema.

## Repository layout

- `.agents/plugins/marketplace.json`: local marketplace, stable identity `data-story-local`.
- `plugins/data-story-studio/plugin.json`: primary plugin manifest.
- `plugins/data-story-studio/.codex-plugin/plugin.json`: compatibility manifest.
- `plugins/data-story-studio/skills/`: four skill entry points.
- `plugins/data-story-studio/runtime/`: copied execution sources and locked motion dependency description.
- `plugins/data-story-studio/fixtures/`: synthetic demonstration data.
- `tests/` and plugin `tests/`: packaging, dashboard, DOM-adapter and integration coverage.

## Trust boundaries

Plugin/cache files are read-only during normal use. User projects live outside the runtime. Data fields never become evaluated code, SQL or shell fragments. Source paths and rows are retained for provenance, so output is sensitive when input is sensitive. There are no connectors, background workers, remote analytics or model calls inside the runtime. The host assistant's data policy and permissions still apply. A hostile process swapping paths concurrently is outside this single-user CLI's threat model.
