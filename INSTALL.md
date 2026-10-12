# Install Data Story Studio

[简体中文](INSTALL.zh-CN.md)

This repository includes a local marketplace at `.agents/plugins/marketplace.json` and the plugin at `plugins/data-story-studio/`. Preserve hidden directories when extracting a release ZIP. The marketplace identity is `data-story-local`; the plugin identity is `data-story-studio`.

## Compatible client

```sh
codex --version
codex plugin --help
```

Local registration/install/discovery/uninstall were previously exercised with Codex CLI 0.159.2 in an isolated HOME. Client support may differ; if `plugin` is absent, follow the current official client guidance rather than editing configuration by hand. Publishing a GitHub repository does not install a plugin in ChatGPT or publish it in a catalog.

## Register and install

Place the full extracted repository in a permanent directory, then replace the example path:

```sh
codex plugin marketplace add /absolute/path/to/data-story-studio
codex plugin add data-story-studio@data-story-local
```

These commands change your local plugin configuration. Start a new conversation and use the skill selector; verified names are `$data-story-studio:setup`, `$data-story-studio:create-dashboard`, `$data-story-studio:create-motion`, and `$data-story-studio:data-to-motion`.

Run setup to diagnose dependencies and initialize a new workspace. Source is copied into `.data-story-runtime`; never install dependencies or write output into the plugin cache. Dashboard needs Python 3.10+. Motion additionally needs Node.js 18+, npm, Canvas and FFmpeg/ffprobe with libx264. Approve any software installation according to your environment's rules. Use `npm ci --omit=dev --ignore-scripts` inside the copied motion runtime. Install suitable fonts for your language and inspect a PNG preview.

## Uninstall

```sh
codex plugin remove data-story-studio@data-story-local
codex plugin marketplace remove data-story-local
```

Remove the marketplace only if you no longer need it. Uninstalling does not delete your workspaces or exported files.

## Official references

- [Package your plugin](https://developers.openai.com/plugins/build/plugins)
- [Plugins user guide](https://learn.chatgpt.com/docs/plugins)
- [Build skills](https://learn.chatgpt.com/docs/build-skills)

Actual installation in your account/client and automatic GUI skill selection must be verified separately. The repository's tests never change your real Codex configuration.
