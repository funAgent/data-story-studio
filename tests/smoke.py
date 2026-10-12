#!/usr/bin/env python3
"""Real dashboard → snapshot → PNG/MP4 smoke. Does not install dependencies."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / 'plugins/data-story-studio'
MOTION = PLUGIN / 'runtime/motion/cli.js'


def run(*args):
    result = subprocess.run([str(a) for a in args], text=True, capture_output=True, timeout=300)
    if result.returncode:
        raise RuntimeError(f'Command failed: {args}\n{result.stdout}\n{result.stderr}')
    return result.stdout


def main():
    with tempfile.TemporaryDirectory(prefix='data-story-smoke-') as temporary:
        workspace = Path(temporary) / 'workspace'
        run(sys.executable, PLUGIN / 'scripts/studio.py', 'init', '--workspace', workspace)
        dashboard = workspace / 'dashboard'
        run(sys.executable, workspace / '.data-story-runtime/dashboard.py', 'build', '--source', workspace / 'examples/sales.csv', '--spec', workspace / 'examples/dashboard-spec.json', '--output', dashboard)
        run('node', ROOT / 'tests/test_dashboard_dom.js', dashboard / 'index.html')
        project = workspace / 'motion'
        run('node', MOTION, 'init', '--project-dir', project)
        run('node', MOTION, 'import-snapshot', '--project-dir', project, '--input', dashboard / 'snapshot.json', '--chart', 1, '--duration-seconds', 3)
        scene = json.loads((project / 'snapshot-project.json').read_text())
        assert sorted(row[1] for row in scene['source']['rows']) == [33700, 42700]
        run('node', MOTION, 'render', '--project-dir', project, '--project', 'snapshot-project.json', '--format', 'png', '--frame', 45)
        assert (project / 'preview.png').read_bytes()[:8] == b'\x89PNG\r\n\x1a\n'
        run('node', MOTION, 'render', '--project-dir', project, '--project', 'snapshot-project.json', '--format', 'mp4')
        probe = json.loads(run('ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=codec_name,width,height,nb_frames:format=duration', '-of', 'json', project / 'preview.mp4'))
        stream = probe['streams'][0]
        assert (stream['codec_name'], stream['width'], stream['height'], int(stream['nb_frames'])) == ('h264', 1280, 720, 90), probe
        assert abs(float(probe['format']['duration']) - 3) < .01, probe
        run('ffmpeg', '-v', 'error', '-i', project / 'preview.mp4', '-f', 'null', '-')
        print(json.dumps({'result': 'passed', 'probe': probe, 'expected_totals': [33700, 42700], 'checks': ['generated DOM behavior', 'snapshot aggregates', 'PNG signature', 'real H.264 encode', 'full video decode'], 'limits': 'No real-browser layout/accessibility or visual PNG inspection in this automated check.'}, indent=2))


if __name__ == '__main__':
    main()
