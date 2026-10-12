# Contributing

Please start with a focused issue describing the problem, expected behavior and a minimal synthetic example. Do not attach private datasets, credentials or generated HTML containing real records. For vulnerabilities, read [SECURITY.md](SECURITY.md).

## Local checks

Python uses the standard library. Install a supported Node LTS, npm and FFmpeg/ffprobe with libx264. Install the locked Canvas dependency only in a disposable workspace or development checkout (never an installed plugin cache):

```sh
(cd plugins/data-story-studio/runtime/motion && npm ci --omit=dev --ignore-scripts)
python3 -m unittest discover -s tests -v
python3 -m unittest discover -s plugins/data-story-studio/tests -v
node plugins/data-story-studio/runtime/motion/test.js
python3 tests/smoke.py
```

The smoke check uses temporary projects, checks generated DOM behavior, creates PNG/MP4, verifies codec/dimensions/frame count/duration and decodes the MP4. It does not install packages, change client configuration or prove visual accessibility. Test relevant browser behavior manually for UI changes and state exactly what you checked.

## Pull requests

Keep changes small and explain the user-visible effect. Add regression coverage for validators and every safety boundary you change. Do not weaken path checks, silently drop categories or conceal unsupported chart conversions. Maintain both manifests and preserve installation identities. Keep English and Chinese user-facing documentation consistent. Never commit `node_modules`, private input data, credentials or generated videos.

Include test commands/results, compatibility implications and known limitations. Dependency updates must regenerate the lockfile with npm and pass a clean `npm ci`; do not edit integrity hashes manually. No CLA or extra contributor agreement is configured. Original project code is MIT-licensed; preserve applicable third-party notices.
