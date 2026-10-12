# Quickstart: sample CSV to MP4

Run from the repository root in a POSIX shell. Python 3.10+ is enough for steps 1–2. Choose a new absolute workspace whose parent exists; the example uses a temporary directory. These commands do not install the plugin or modify client settings.

## 1. Create a workspace

```sh
BASE="$(mktemp -d)"
WORK="$BASE/story"
python3 plugins/data-story-studio/scripts/studio.py doctor
python3 plugins/data-story-studio/scripts/studio.py init --workspace "$WORK"
```

## 2. Build the dashboard

```sh
python3 "$WORK/.data-story-runtime/dashboard.py" build \
  --source "$WORK/examples/sales.csv" \
  --spec "$WORK/examples/dashboard-spec.json" \
  --output "$WORK/dashboard"
```

Open `$WORK/dashboard/index.html` in your browser. Explore filters, dimensions and metrics; these controls do not save changes. Edit `dashboard/spec.json` and explicitly refresh to persist chart configuration or reread changed source data:

```sh
python3 "$WORK/.data-story-runtime/dashboard.py" refresh --project "$WORK/dashboard"
```

Refresh overwrites four generated project files after integrity checks. Keep historical copies separately. HTML and snapshots contain complete rows and local-path provenance.

## 3. Install motion dependencies

Ensure Node.js, npm, FFmpeg and ffprobe are installed. FFmpeg must provide libx264. The following command downloads locked native Canvas packages from npm; run it only when software installation is allowed:

```sh
(cd "$WORK/.data-story-runtime/motion" && npm ci --omit=dev --ignore-scripts)
node "$WORK/.data-story-runtime/motion/cli.js" doctor
```

## 4. Render a selected chart

```sh
MOTION="$WORK/.data-story-runtime/motion/cli.js"
node "$MOTION" init --project-dir "$WORK/motion"
node "$MOTION" import-snapshot --project-dir "$WORK/motion" \
  --input "$WORK/dashboard/snapshot.json" --chart 1 --duration-seconds 3
node "$MOTION" render --project-dir "$WORK/motion" \
  --project snapshot-project.json --format png --frame 45
node "$MOTION" render --project-dir "$WORK/motion" \
  --project snapshot-project.json --format mp4
```

Inspect `motion/preview.png`, then play `motion/preview.mp4`. Edit `motion/snapshot-project.json` and render with a new `--output revised.mp4` filename; existing exports are never overwritten. Sample chart index 1 is region revenue, with expected totals 42,700 and 33,700. Source values and editability remain in the project JSON. A rendered image does not independently verify business correctness.
