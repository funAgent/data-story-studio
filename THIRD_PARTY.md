# Distribution and third-party notices

This repository contains local dashboard/motion implementation, synthetic fixtures, tests and skill instructions. Motion retains an independently reconstructed prototype and its hash record in `plugins/data-story-studio/runtime/motion/provenance/`. This is not proprietary Claude, Remotion or Motion Canvas source. The dashboard, motion prototype and plugin implementation were independently authored for this project. Original project source, including retained prototype files, is covered by the root MIT LICENSE. This grant does not relicense external dependencies.

External software is installed separately and is not included in the source ZIP:

- `@napi-rs/canvas` 0.1.100: upstream package declares MIT; see [upstream](https://github.com/Brooooooklyn/canvas) and the installed package's license/notices. Platform-specific native packages and bundled native components may carry additional notices. Preserve/review those when redistributing binaries.
- FFmpeg: see [FFmpeg legal guidance](https://ffmpeg.org/legal.html). libx264-enabled distributions may be GPL builds and have separate source/redistribution obligations; codec patents may apply. This repository invokes an existing executable and does not ship it.
- Node.js, Python and system fonts: installed independently under their respective licenses. No font files are bundled.

No OpenAI or Anthropic affiliation, endorsement or ownership is implied by compatibility references. Do not remove applicable third-party notices when making your own distribution.
