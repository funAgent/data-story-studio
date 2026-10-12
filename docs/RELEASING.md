# Release checklist

## Version policy

Use SemVer tags (`v0.1.0`, etc.). During 0.x, minor increments may change interfaces; patch increments are compatible fixes. Snapshot schema version is independent and must change for incompatible data contracts. Keep the primary and compatibility manifests, workspace marker version and changelog synchronized. The internal motion package has its own version and is not published to npm.

## Before the first public release

- Confirm repository ownership/access and permission to publish all included source.
- Preserve the approved MIT license for original project code and the independent prototype provenance.
- Verify third-party notices. Do not redistribute native dependencies, fonts or FFmpeg in this source release.
- Configure private vulnerability reporting if available. No private contact is assumed.
- Review repository contents for credentials, real datasets, local paths and generated artifacts.

## Validate and package

Run all CONTRIBUTING.md checks using a clean dependency installation. Inspect a PNG and test the dashboard in a real browser. Run `python3 tests/build_bundle.py --output /absolute/path/outside/repo/data-story-studio-vVERSION.zip` twice to different filenames and compare SHA-256. Extract a fresh archive and rerun checks from it. Hidden `.agents` and `.codex-plugin` directories are required.

The packer fixes archive paths/timestamps/permissions and includes source/lockfiles/documentation only. It refuses symlinks and preexisting output files. A hash-identical archive proves packaging reproducibility for identical source bytes, not identical videos across operating systems.

After authorized publication, verify the remote commit, tag and CI result for that exact commit. Attach the source ZIP and its SHA-256 to the release; do not claim a public release until verified. Plugin catalog submission and installation in a user's ChatGPT/Codex client are separate actions, with their own verification. CI does not auto-publish or auto-install.

## Private plugin import archive

Use `python3 tests/build_bundle.py --plugin-only --output /absolute/path/outside/repo/data-story-studio-plugin-vVERSION.zip` to package only the plugin, with `plugin.json` at the ZIP root, all four skills and MIT/third-party notices. This archive is for a compatible private test import, not local marketplace registration. The whole-repository ZIP remains the local-marketplace distribution. Creating either ZIP does not submit to a catalog or install it in an account. Verify the current client/portal import flow before use.

The bundled original SVG is 128×128; both logo and composerIcon reference it. The subtitle is under 30 characters. Public submission still requires a selected verified developer identity and successful automated checks; no verified identity is asserted by the package. Current field rules: https://developers.openai.com/plugins/deploy/submission .
