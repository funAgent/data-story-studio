"""No client configuration or internet required. Run: python3 -m unittest discover -s tests -v"""
import json,pathlib,subprocess,sys,tempfile,unittest,os
ROOT=pathlib.Path(__file__).resolve().parents[1];PLUGIN=ROOT/'plugins/data-story-studio';SCRIPT=PLUGIN/'scripts/studio.py'
class Packaging(unittest.TestCase):
 def runcli(self,*args):return subprocess.run([sys.executable,str(SCRIPT),*map(str,args)],capture_output=True,text=True)
 def test_manifest_and_components(self):
  root=json.loads((PLUGIN/'plugin.json').read_text());overlay=json.loads((PLUGIN/'.codex-plugin/plugin.json').read_text());catalog=json.loads((ROOT/'.agents/plugins/marketplace.json').read_text())
  self.assertEqual(root['name'],overlay['name']);self.assertEqual(root['version'],overlay['version']);self.assertEqual(root['$schema'],'https://agent-plugins.org/schemas/1.0.0/plugin.schema.json')
  self.assertEqual((ROOT/catalog['plugins'][0]['source']['path']).resolve(),PLUGIN)
  self.assertEqual(catalog['name'],'data-story-local'); self.assertTrue((PLUGIN/root['extensions']['com.openai']['onboardingSkill']).is_file())
  for name in ['setup','create-dashboard','create-motion','data-to-motion']:
   t=(PLUGIN/'skills'/name/'SKILL.md').read_text();self.assertTrue(t.startswith('---\nname: '+name+'\n'));self.assertIn('description:',t)
  self.assertFalse((PLUGIN/'mcp.json').exists());self.assertFalse((PLUGIN/'hooks').exists())
  interface=root['extensions']['com.openai']['interface']
  self.assertLessEqual(len(interface['shortDescription']),30);self.assertLessEqual(len(interface['displayName']),30)
  self.assertTrue(interface['longDescription']);self.assertEqual(root['license'],'MIT')
  for field in ['composerIcon','logo']: self.assertTrue((PLUGIN/interface[field]).is_file())
 def test_doctor_no_mutation(self):
  r=self.runcli('doctor');self.assertEqual(r.returncode,0,r.stderr);self.assertTrue(json.loads(r.stdout)['dashboard_ready']['ok'])
 def test_workspace_copy_and_existing_rejection(self):
  with tempfile.TemporaryDirectory() as tmp:
   p=pathlib.Path(tmp)/'user workspace';r=self.runcli('init','--workspace',p);self.assertEqual(r.returncode,0,r.stderr)
   self.assertTrue((p/'.data-story-runtime/dashboard.py').is_file());self.assertTrue((p/'.data-story-runtime/motion/cli.js').is_file());self.assertTrue((p/'data-story-workspace.json').is_file())
   self.assertNotEqual(self.runcli('init','--workspace',p).returncode,0)
   self.assertFalse(list(p.rglob('node_modules')))
 def test_unsafe_workspace_paths(self):
  self.assertNotEqual(self.runcli('init','--workspace','relative').returncode,0)
  self.assertNotEqual(self.runcli('init','--workspace',PLUGIN/'evil-output').returncode,0)
  with tempfile.TemporaryDirectory() as tmp:
   p=pathlib.Path(tmp);(p/'real').mkdir();(p/'link').symlink_to(p/'real',target_is_directory=True)
   self.assertNotEqual(self.runcli('init','--workspace',p/'link'/'output').returncode,0)
   self.assertNotEqual(self.runcli('init','--workspace',str(p/'real')+'/../output').returncode,0)
   self.assertFalse((p/'real/output').exists())
if __name__=='__main__':unittest.main()
