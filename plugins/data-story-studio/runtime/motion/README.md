# Offline data-story motion runtime

A small editable scene renderer, adapted from the supplied independent prototype. It renders actual PNG and H.264 MP4 locally with Canvas and FFmpeg. No server, browser, API key, cloud upload, audio, external assets or arbitrary code execution from scene text is involved. It is not a general-purpose animation editor or Remotion implementation.

## Bootstrap in a user workspace

Use the plugin's workspace initializer to copy this runtime into a user-owned workspace. Never install dependencies or produce outputs in the installed plugin/cache. After approving dependency installation, from the copied runtime/motion directory:

    npm ci --omit=dev --ignore-scripts
    npm test
    node cli.js doctor

Node 18+ (a currently supported Node release is recommended) and an existing FFmpeg executable with libx264 on PATH are required. The direct Canvas dependency is pinned to 0.1.100; npm installs its platform-specific native package. A committed npm lockfile records registry integrity hashes and platform-specific optional packages. Use npm ci for reproducible dependency resolution. No node_modules, FFmpeg, fonts, or other binaries are distributed. Clean-install verification is documented in the repository QA report.

Use your real absolute paths below. PROJECT must initially be a new directory with an existing parent, separate from .data-story-runtime:

    node /ABS/workspace/.data-story-runtime/motion/cli.js init --project-dir /ABS/workspace/motion-project
    node /ABS/workspace/.data-story-runtime/motion/cli.js validate --project-dir /ABS/workspace/motion-project
    node /ABS/workspace/.data-story-runtime/motion/cli.js render --project-dir /ABS/workspace/motion-project --format png --frame 300
    node /ABS/workspace/.data-story-runtime/motion/cli.js render --project-dir /ABS/workspace/motion-project --format mp4

Edit motion-project/project.json to change scene titles, timings, metrics, palette and values. Updating values does not automatically recompute hand-authored headline/summary strings. Scene text is drawn literally onto Canvas, never executed as HTML or JavaScript. project.schema.json describes structure; motion.js additionally enforces continuity, unique scene IDs/category labels and exact duration totals.

Outputs default to preview.png / preview.mp4, with a .metadata.json sidecar recording project/output SHA-256, render time, frame count and duration. Existing files are never overwritten; pass --output another-name.png or another-name.mp4. Input/output filenames within a project cannot traverse directories. Absolute project paths, a project marker, no symlink components (including dangling symlinks), exclusive output creation, and plugin/cache/runtime restrictions prevent accidental writes outside the selected project. A hostile process concurrently swapping directories is outside this local single-user CLI's threat model.

## Dashboard snapshot → editable project → video

    node /ABS/workspace/.data-story-runtime/motion/cli.js import-snapshot --project-dir /ABS/workspace/motion-project --input /ABS/workspace/snapshot.json --chart 0 --duration-seconds 12
    node /ABS/workspace/.data-story-runtime/motion/cli.js render --project-dir /ABS/workspace/motion-project --project snapshot-project.json --format png --output dashboard.png
    node /ABS/workspace/.data-story-runtime/motion/cli.js render --project-dir /ABS/workspace/motion-project --project snapshot-project.json --format mp4 --output dashboard.mp4

Importer accepts dashboard snapshot schema_version 1: rows, dimensions, metrics, charts, provenance (sha256 and matching row_count). --chart is a zero-based chart index. Its dimension must contain nonempty strings no longer than 20 characters. Aggregation is sum, mean or count (count means non-null metric cells per category; sum and mean skip null cells; all-null sum/mean categories and missing metric fields are rejected). First-appearance category order is preserved. A selected line/table is represented as bars with an explicit warning. No category is silently dropped; 2–8 categories are required. Source/provenance, selected chart, aggregation and SHA-256 of the input file are embedded in snapshot-project.json. The source file hash in provenance is retained as a claim from the snapshot, not independently verified against the original source file. Snapshot import does not make misleading growth or margin claims; it produces a single bar scene labelled with its actual aggregation.

Limits: 2 MiB JSON input, 10,000 snapshot rows, 2–8 categories, finite nonnegative values and aggregates up to 1e12, 1–12 contiguous scenes, 30–1800 total frames, 1–60 fps, fixed 1280×720. Supported scenes are headline, barChart and summary only. Bar labels show five significant digits. MP4 rendering has a five-minute timeout and removes its temporary files on normal failure. PNG renders one selected frame. Fonts use available system Liberation Sans / Arial / Noto Sans CJK SC / sans-serif; exact cross-platform pixel/font parity is not claimed. Text scales down to fit the available width (very long strings can become small). Visually inspect PNGs, especially non-English glyph coverage, before final delivery.

## Verification

    node test.js

26 tests cover validation, invalid numeric values, unsupported scenes, inert malicious-looking text, sum/mean/count, category caps, traversal/dangling symlinks, exclusive initialization/output, actual PNG bytes and retained snapshots. This build also rendered real 30-frame and 360-frame MP4 files; ffprobe verified H.264, 1280×720, respectively 1.000000 and 12.000000 seconds. The 12-second fixture used Chinese field/category labels and sums 150/120/0; its PNG was visually inspected, and FFmpeg decoded its MP4 without errors. Preinstalled Node 24.19.0, Canvas 0.1.100 and FFmpeg were reused; clean installation on another operating system remains unverified.
