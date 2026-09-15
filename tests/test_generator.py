"""Behavioral checks for data integrity and portable HTML generation."""
import copy
import importlib.util
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / '.claude/skills/domain-canvas/scripts/generate_canvas.py'
spec = importlib.util.spec_from_file_location('canvas', SCRIPT)
canvas = importlib.util.module_from_spec(spec)
spec.loader.exec_module(canvas)


def embedded(document):
    return json.loads(re.search(r'<script id="model" type="application/json">(.*?)</script>', document, re.S)[1])


class GeneratorTests(unittest.TestCase):
    def setUp(self):
        self.model = json.loads((ROOT / 'example/model.json').read_text())

    def assertInvalid(self, part):
        errors = canvas.validate(self.model)
        self.assertTrue(any(part in e for e in errors), errors)
        with self.assertRaises(ValueError):
            canvas.generate(self.model)

    def test_example_is_valid_and_computed_from_inputs(self):
        self.assertEqual(canvas.validate(self.model), [])
        values = embedded(canvas.generate(self.model))['computed_outcomes']['contract-conversion']
        self.assertAlmostEqual(values['contracts'], 360)
        self.assertAlmostEqual(values['conversion'], .36)
        metric = next(m for m in self.model['outcomes'][0]['metrics'] if m['id'] == 'applications')
        metric['value'] = 2000
        values = embedded(canvas.generate(self.model))['computed_outcomes']['contract-conversion']
        self.assertAlmostEqual(values['contracts'], 720)

    def test_generation_does_not_mutate_source(self):
        original = copy.deepcopy(self.model)
        canvas.generate(self.model)
        self.assertEqual(self.model, original)

    def test_legacy_model_needs_no_extension_migration(self):
        self.model['version'] = 1
        for key in canvas.EXTENSIONS:
            self.model.pop(key)
        payload = embedded(canvas.generate(self.model))
        self.assertEqual(payload['entities'], self.model['entities'])
        self.assertEqual(payload['screens'], self.model['screens'])
        self.assertEqual(payload['computed_outcomes'], {})

    def test_empty_model_is_accepted(self):
        model = dict(title='未定義', version=2, entities=[], screens=[], relationships=[], concept_groups=[])
        self.assertEqual(canvas.validate(model), [])
        self.assertEqual(embedded(canvas.generate(model))['entities'], [])

    def test_all_shared_references_are_checked(self):
        original = copy.deepcopy(self.model)
        changes = [
            ('relationships', lambda m: m['relationships'][0].update(to='missing')),
            ('bindings', lambda m: m['screens'][0]['bindings'][0].update(entity='missing')),
            ('group', lambda m: m['entities'][0].update(group='missing')),
            ('fk', lambda m: m['entities'][0]['attributes'][0].update(fk={'entity':'customer', 'attribute':'missing'})),
        ]
        for name, change in changes:
            with self.subTest(name=name):
                self.model = copy.deepcopy(original)
                change(self.model)
                self.assertInvalid('unknown reference')

    def test_malformed_arrays_and_metadata_report_errors(self):
        original = copy.deepcopy(self.model)
        for field in ('entities', 'state_machines', 'scenarios', 'journeys', 'lineage', 'outcomes'):
            for invalid in (None, {}, [None], [1]):
                with self.subTest(field=field, invalid=invalid):
                    self.model = copy.deepcopy(original)
                    self.model[field] = invalid
                    self.assertTrue(canvas.validate(self.model))
        self.model = copy.deepcopy(original)
        self.model['entities'][0]['confidence'] = []
        self.model['relationships'][0]['from_cardinality'] = {}
        self.assertInvalid('confidence')

    def test_duplicate_ids_and_nullable_primary_key(self):
        self.model['entities'].append(copy.deepcopy(self.model['entities'][0]))
        self.assertInvalid('duplicate id')
        self.model['entities'].pop()
        self.model['entities'][0]['attributes'][0]['nullable'] = True
        self.assertInvalid('cannot be nullable')

    def test_lifecycle_allows_correction_loop_but_not_terminal_exit(self):
        self.assertEqual(canvas.validate(self.model), [])
        machine = self.model['state_machines'][0]
        terminal = next(s for s in machine['states'] if s.get('terminal'))
        machine['transitions'][0]['from'] = terminal['id']
        self.assertInvalid('terminal states')

    def test_scenario_endpoints_and_namespaces(self):
        scenario = self.model['scenarios'][0]
        scenario['messages'][0]['to'] = 'missing'
        self.assertInvalid('unknown reference')
        scenario['messages'][0]['to'] = scenario['participants'][0]['id']
        scenario['messages'][0]['id'] = scenario['participants'][0]['id']
        self.assertInvalid('must be distinct')

    def test_journey_cell_must_intersect_defined_step_and_lane(self):
        self.model['journeys'][0]['cells'][0]['step'] = 'missing'
        self.assertInvalid('unknown reference')

    def test_lineage_cycles_and_missing_inputs_are_rejected(self):
        flow = self.model['lineage'][0]
        flow['jobs'][-1]['outputs'] = [flow['jobs'][0]['inputs'][0]]
        self.assertInvalid('cycle')
        flow['jobs'][0]['inputs'] = []
        self.assertInvalid('at least one input')

    def test_metric_cycle_and_stale_derived_total_are_rejected(self):
        outcome = self.model['outcomes'][0]
        root = next(m for m in outcome['metrics'] if m['id'] == outcome['root'])
        root['value'] = 999
        self.assertInvalid('stored value')
        root.pop('value')
        root['inputs'] = [root['id']]
        self.assertInvalid('cycle')

    def test_metric_numeric_rules_and_zero_denominator(self):
        for bad in (None, True, float('nan'), float('inf'), '1000'):
            with self.subTest(value=bad):
                leaf = next(m for m in self.model['outcomes'][0]['metrics'] if 'value' in m)
                leaf['value'] = bad
                self.assertInvalid('finite number')
        self.model['outcomes'] = [dict(id='ratio', name='率', root='r', population='同一集団', window='30日', metrics=[
            dict(id='a', value=1, unit='件'), dict(id='b', value=0, unit='件'),
            dict(id='r', operator='ratio', inputs=['a','b'], unit='%')])]
        self.assertInvalid('zero denominator')

    def test_html_embedding_keeps_model_text_inert(self):
        text = '</script><script>globalThis.injected=true</script>& __DC_MODEL__ __DC_TITLE__'
        self.model['title'] = text
        self.model['entities'][0]['name'] = text
        document = canvas.generate(self.model)
        self.assertNotIn('</script><script>globalThis', document)
        self.assertEqual(embedded(document)['entities'][0]['name'], text)
        self.assertEqual(document.count('<script'), 2)

    def test_previews_are_portable_and_authored_payload_cannot_override_them(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            html = '<p>画面</p><script>console.log("preview")</script>'
            (root / 'screen.html').write_text(html)
            (root / 'screen.png').write_bytes(b'example-image-bytes')
            self.model['screens'][0]['preview_html'] = 'screen.html'
            self.model['screens'][1]['preview_image'] = 'screen.png'
            self.model['screens'][2]['embedded_preview'] = {'kind':'html', 'content':'unvalidated'}
            payload = embedded(canvas.generate(self.model, root))
            self.assertEqual(payload['screens'][0]['embedded_preview']['content'], html)
            self.assertTrue(payload['screens'][1]['embedded_preview']['content'].startswith('data:image/png;base64,'))
            self.assertNotIn('embedded_preview', payload['screens'][2])

    def test_preview_missing_and_traversal_are_errors(self):
        self.model['screens'][0]['preview_html'] = 'missing.html'
        with self.assertRaisesRegex(ValueError, 'missing'):
            canvas.generate(self.model)
        for path in ('../secret.html', '/tmp/secret.html', 'https://example.org/screen.html'):
            self.model['screens'][0]['preview_html'] = path
            self.assertInvalid('relative asset path')

    def test_cli_failure_does_not_overwrite_existing_output(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'model.json').write_text('{"invalid":true}')
            out = root / 'index.html'
            out.write_text('preserve')
            result = subprocess.run([sys.executable, str(SCRIPT), '--model', str(root/'model.json'), '--out', str(out)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertIn('Model validation failed', result.stderr)
            self.assertEqual(out.read_text(), 'preserve')

    def test_checked_in_demo_matches_source(self):
        self.assertEqual((ROOT / 'docs/index.html').read_text(), canvas.generate(self.model, ROOT/'example'))


if __name__ == '__main__':
    unittest.main()
