"""Reproducible ZIP and fresh-extraction checks; no dependencies downloaded."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]


class Archive(unittest.TestCase):
    def test_plugin_archive_root_and_license(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / 'plugin.zip'
            subprocess.run([sys.executable, str(ROOT / 'tests/build_bundle.py'), '--output', str(output), '--plugin-only'], check=True, capture_output=True)
            with zipfile.ZipFile(output) as archive:
                self.assertIn('plugin.json', archive.namelist())
                self.assertIn('LICENSE', archive.namelist())
                self.assertIn('THIRD_PARTY.md', archive.namelist())
                self.assertIn('.codex-plugin/plugin.json', archive.namelist())
                self.assertNotIn('.agents/plugins/marketplace.json', archive.namelist())
                self.assertEqual(json.loads(archive.read('plugin.json'))['name'], 'data-story-studio')

    def test_reproducible_archive_and_extracted_workspace(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            archives = [base / 'a.zip', base / 'b.zip']
            for archive in archives:
                subprocess.run([sys.executable, str(ROOT / 'tests/build_bundle.py'), '--output', str(archive)], check=True, capture_output=True)
            self.assertEqual(hashlib.sha256(archives[0].read_bytes()).digest(), hashlib.sha256(archives[1].read_bytes()).digest())
            with zipfile.ZipFile(archives[0]) as archive:
                names = archive.namelist()
                self.assertIn('data-story-studio/.agents/plugins/marketplace.json', names)
                self.assertIn('data-story-studio/plugins/data-story-studio/.codex-plugin/plugin.json', names)
                self.assertIn('data-story-studio/plugins/data-story-studio/runtime/motion/package-lock.json', names)
                self.assertFalse(any('node_modules' in n or '__pycache__' in n or '/.git/' in n for n in names))
                archive.extractall(base / 'extracted')
            root = base / 'extracted/data-story-studio'
            plugin = root / 'plugins/data-story-studio'
            workspace = base / 'workspace'
            subprocess.run([sys.executable, str(plugin / 'scripts/studio.py'), 'init', '--workspace', str(workspace)], check=True, capture_output=True)
            subprocess.run([sys.executable, str(workspace / '.data-story-runtime/dashboard.py'), 'build', '--source', str(workspace / 'examples/sales.csv'), '--spec', str(workspace / 'examples/dashboard-spec.json'), '--output', str(workspace / 'dashboard')], check=True, capture_output=True)
            snapshot = json.loads((workspace / 'dashboard/snapshot.json').read_text())
            self.assertEqual(snapshot['schema_version'], 1)
            self.assertEqual(snapshot['provenance']['row_count'], len(snapshot['rows']))
            self.assertTrue((workspace / '.data-story-runtime/motion/package-lock.json').is_file())


if __name__ == '__main__':
    unittest.main()
