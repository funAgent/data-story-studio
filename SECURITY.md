# Security

## Reporting

Do not put credentials, private datasets, exploit details or private local paths in a public issue. If GitHub's **Security → Report a vulnerability** is enabled for this repository, use that private reporting channel. If it is unavailable, ask the repository maintainer to enable a private channel using a public issue containing only a request for private contact, without vulnerability details. No unverified email address is provided and no response-time guarantee is implied.

Include the affected version, a minimal synthetic reproduction, impact and environment versions. Test only systems/data you are authorized to test.

## Scope and precautions

The local parser, generated HTML, path checks, snapshot importer and renderer are in scope. Review full records and absolute paths in HTML, snapshots and render metadata before sharing. Treat downloaded datasets as untrusted. Use a supported Python/Node release and keep FFmpeg and native Canvas updated. Dependencies and system fonts are external components; their security and licensing obligations remain separate.

This initial 0.1.x project has no guaranteed long-term-support branch. Security fixes should target the latest published release. Concurrent hostile filesystem mutation and sandboxing arbitrary programs are outside the supported threat model.
