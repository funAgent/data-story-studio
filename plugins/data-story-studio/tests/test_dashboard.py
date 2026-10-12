import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

MODULE = Path(__file__).resolve().parents[1] / 'runtime' / 'dashboard.py'
spec = importlib.util.spec_from_file_location('dashboard', MODULE)
d = importlib.util.module_from_spec(spec)
spec.loader.exec_module(d)

class DashboardTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.source = self.root / 'data.csv'
        self.source.write_text('region,revenue\nEast,10\nWest,20\nEast,5\n', encoding='utf-8')
        self.spec = self.root / 'spec.json'
        self.definition = {'title':'A dashboard', 'dimensions':['region'], 'metrics':[{'field':'revenue','aggregation':'sum'}], 'charts':[{'type':'bar','dimension':'region','metric':'sum:revenue'}, {'type':'line','dimension':'region','metric':'sum:revenue'}, {'type':'table','dimension':'region','metric':'sum:revenue'}]}
        self.spec.write_text(json.dumps(self.definition))
        self.output = self.root / 'output'
    def tearDown(self):
        self.temp.cleanup()
    def build(self):
        return d.build(self.source,self.spec,self.output)
    def test_build_provenance_and_refresh(self):
        self.build()
        snapshot=json.loads((self.output/'snapshot.json').read_text())
        self.assertEqual(snapshot['rows'][0]['revenue'],10)
        self.assertEqual(snapshot['metrics'][0]['id'],'sum:revenue')
        self.assertEqual(snapshot['provenance']['sha256'],d.digest(self.source.read_bytes()))
        (self.output/'notes.txt').write_text('Keep me')
        self.source.write_text('region,revenue\nNorth,42\n')
        d.refresh(self.output)
        self.assertEqual(json.loads((self.output/'snapshot.json').read_text())['rows'][0]['revenue'],42)
        self.assertEqual((self.output/'notes.txt').read_text(),'Keep me')
    def test_existing_output_refused(self):
        self.output.mkdir()
        (self.output/'unrelated.txt').write_text('untouched')
        with self.assertRaises(d.DashboardError): self.build()
        self.assertEqual((self.output/'unrelated.txt').read_text(),'untouched')
    def test_tampered_project_refused(self):
        self.build()
        (self.output/'index.html').write_text('user work')
        with self.assertRaises(d.DashboardError): d.refresh(self.output)
        self.assertEqual((self.output/'index.html').read_text(),'user work')
    def test_symlinks_refused(self):
        link=self.root/'link';link.symlink_to(self.root,target_is_directory=True)
        with self.assertRaises(d.DashboardError): d.build(self.source,self.spec,link/'other')
        self.build();(self.output/'index.html').unlink();(self.output/'index.html').symlink_to(self.spec)
        with self.assertRaises(d.DashboardError):d.refresh(self.output)
    def test_plugin_and_root_refused(self):
        for target in [d.PLUGIN_ROOT/'bad-output',Path('/'),Path.home()]:
            with self.assertRaises(d.DashboardError):d.safe_target(target)
    def test_script_payload_is_inert(self):
        attack='</script><script>alert("x")</script><img src=x onerror=alert(1)>'
        self.definition['title']=attack
        self.spec.write_text(json.dumps(self.definition))
        self.source.write_text('region,revenue\n'+json.dumps(attack)+',10\n')
        # JSON avoids CSV quoting ambiguity for a deliberate HTML payload.
        self.source=self.root/'data.json';self.source.write_text(json.dumps([{'region':attack,'revenue':10}]))
        self.build();html=(self.output/'index.html').read_text()
        self.assertNotIn(attack,html)
        self.assertIn('\\u003c/script\\u003e',html)
        self.assertNotIn('innerHTML',html)
        self.assertIn("connect-src 'none'",html)
    def test_invalid_sources(self):
        for payload in ['[{"region":"A","revenue":NaN}]','[{"region":"A","revenue":1e999}]','[{"region":"A","revenue":{}}]','[{"region":"A","region":"B","revenue":2}]','[{"region":"A","revenue":9007199254740992}]','[{"a":1},{"b":2}]']:
            source=self.root/'bad.json';source.write_text(payload)
            with self.subTest(payload=payload),self.assertRaises(d.DashboardError):d.source_data(source)
        for payload in ['region,revenue\nA,NaN\n','region,region\nA,2\n','a,b\n1,2,3\n','a,b\n1\n']:
            self.source.write_text(payload)
            with self.subTest(payload=payload),self.assertRaises(d.DashboardError):d.source_data(self.source)
    def test_invalid_specs(self):
        rows,fields,_=d.source_data(self.source)
        for definition in [None,{}, {'dimensions':['missing'],'metrics':[]},dict(self.definition,query='DELETE'),dict(self.definition,metrics=[{'field':'region','aggregation':'sum'}]),dict(self.definition,metrics=[{'field':'revenue','aggregation':'exec'}]),dict(self.definition,charts=[{'type':'pie','dimension':'region','metric':'sum:revenue'}])]:
            with self.subTest(definition=definition),self.assertRaises(d.DashboardError):d.validate_spec(definition,rows,fields)
    def test_editable_spec_refresh(self):
        self.build()
        spec_file=self.output/'spec.json'
        changed=json.loads(spec_file.read_text());changed['title']='Updated title'
        spec_file.write_text(json.dumps(changed))
        d.refresh(self.output)
        self.assertEqual(json.loads((self.output/'snapshot.json').read_text())['title'],'Updated title')
    def test_group_overflow_and_traversal_rejected(self):
        rows=[{'region':'A','revenue':1e308},{'region':'A','revenue':1e308},{'region':'B','revenue':-1e308},{'region':'B','revenue':-1e308}]
        with self.assertRaises(d.DashboardError):d.validate_spec(self.definition,rows,['region','revenue'])
        with self.assertRaises(d.DashboardError):d.no_symlinks(self.root/'child'/'..'/'output')
    def test_invalid_manifest_files_shape(self):
        self.build()
        path=self.output/'manifest.json';manifest=json.loads(path.read_text())
        manifest['files']=['index.html','snapshot.json'];path.write_text(json.dumps(manifest))
        with self.assertRaises(d.DashboardError):d.refresh(self.output)
    def test_unsafe_csv_and_json_integer_values(self):
        for token in ['9007199254740993', '"9007199254740993"', '9007199254740993.0', '9.007199254740993e15', '-9007199254740993']:
            self.source.write_text('region,revenue\nA,'+token+'\n')
            with self.subTest(token=token),self.assertRaises(d.DashboardError):d.source_data(self.source)
        source=self.root/'unsafe.json'
        for token in ['9007199254740993', '9007199254740993.0', '9.007199254740993e15']:
            source.write_text('[{"region":"A","revenue":'+token+'}]')
            with self.subTest(token=token),self.assertRaises(d.DashboardError):d.source_data(source)
        self.source.write_text('region,revenue\n09007199254740993,1\n')
        self.assertEqual(d.source_data(self.source)[0][0]['region'],'09007199254740993')
        source.write_text('[{"region":"9007199254740993","revenue":1}]')
        self.assertEqual(d.source_data(source)[0][0]['region'],'9007199254740993')
    def test_count_and_null(self):
        rows=[{'a':None},{'a':'x'}]
        normalized=d.validate_spec({'dimensions':['a'],'metrics':[{'field':'a','aggregation':'count'}]},rows,['a'])
        self.assertEqual(normalized['metrics'][0]['id'],'count:a')

if __name__=='__main__':unittest.main()
