# Dependencies and provenance

- @napi-rs/canvas 0.1.100 declares MIT: https://github.com/Brooooooklyn/canvas . It includes platform-specific native components whose notices must be reviewed when redistributed. No package binaries are included here.
- FFmpeg is an external executable: https://ffmpeg.org/legal.html . The tested build supports libx264 and GPL components. Redistributing FFmpeg carries separate licensing/source obligations; codec licensing may also apply. It is not included.
- Node.js and system fonts are external. Font availability affects appearance; no fonts are bundled.
- provenance/original-motion.js and original-project.json retain the exact supplied independently reconstructed prototype inputs. SOURCE.json records their hashes and adaptations. This is not source code from Claude, Remotion or Motion Canvas.
- Original project code and the retained independently authored prototype are covered by the repository root MIT LICENSE. External dependencies retain their own licenses. See the repository root THIRD_PARTY.md.
