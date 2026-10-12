#!/usr/bin/env python3
"""Create a deterministic, source-only plugin archive without configuration changes."""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
TOP_FILES = {'README.md', 'README.zh-CN.md', 'INSTALL.md', 'INSTALL.zh-CN.md',
             'LICENSE', 'THIRD_PARTY.md', 'CONTRIBUTING.md', 'SECURITY.md',
             'CHANGELOG.md', '.gitignore', '.editorconfig'}
TOP_DIRS = {'.agents', '.github', 'plugins', 'tests', 'docs'}
EXCLUDED = {'node_modules', '__pycache__', '.git', '.venv', '.pytest_cache'}


def source_files(root):
    for path in sorted(root.rglob('*')):
        rel = path.relative_to(root)
        if any(part in EXCLUDED for part in rel.parts):
            continue
        if path.is_symlink():
            raise ValueError(f'Refusing source symlink: {rel}')
        if not path.is_file() or (rel.parts[0] not in TOP_DIRS and str(rel) not in TOP_FILES):
            continue
        if path.suffix in {'.pyc', '.zip', '.mp4', '.png', '.pem', '.key'} or path.name.startswith('.env'):
            continue
        yield path, rel


def build(output, plugin_only=False):
    output = output.expanduser().absolute()
    if ROOT == output or ROOT in output.parents:
        raise ValueError('Output archive must be outside the source package')
    files = list(source_files(ROOT))
    if plugin_only:
        prefix = Path('plugins/data-story-studio')
        files = [(path, rel.relative_to(prefix)) for path, rel in files if prefix in rel.parents]
    with zipfile.ZipFile(output, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path, rel in files:
            name = rel.as_posix() if plugin_only else 'data-story-studio/' + rel.as_posix()
            info = zipfile.ZipInfo(name, date_time=(2020, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, path.read_bytes(), compresslevel=9)
    return {'archive': str(output), 'files': len(files), 'bytes': output.stat().st_size,
            'sha256': hashlib.sha256(output.read_bytes()).hexdigest()}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--plugin-only', action='store_true', help='Place plugin.json at ZIP root for private test import; not a local marketplace')
    try:
        args = parser.parse_args()
        print(json.dumps(build(args.output, args.plugin_only), indent=2))
    except (ValueError, OSError) as exc:
        parser.exit(2, str(exc) + '\n')
