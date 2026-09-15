// Syntax and pure layout checks; this does not claim a browser rendering pass.
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import vm from 'node:vm';

const html = readFileSync(new URL('../docs/index.html', import.meta.url), 'utf8');
const scripts = [...html.matchAll(/<script([^>]*)>([\s\S]*?)<\/script>/g)];
assert.equal(scripts.length, 2);
const code = scripts.find(([, attrs]) => !attrs.includes('application/json'))[2];
new vm.Script(code, { filename: 'generated-canvas.js' });
const layout = code.slice(code.indexOf('function layersFor('), code.indexOf('function placeGraph('));
const { layersFor } = vm.runInNewContext(`${layout}; ({ layersFor })`);
const layers = (ids, edges) => JSON.parse(JSON.stringify(layersFor(ids.map(id => ({id})), edges.map(([from,to]) => ({from,to})))));
const result = layers(['start','review','correction','approved','rejected'], [
  ['start','review'], ['review','correction'], ['correction','review'],
  ['review','approved'], ['review','rejected']
]);
assert.deepEqual(result, [['start'], ['review','correction'], ['approved','rejected']]);
assert.deepEqual(layers([], []), []);
assert.deepEqual(layers(['one'], [['one','one']]), [['one']]);
assert.deepEqual(layers(['a','b','c'], [['a','c'], ['b','c'], ['unknown','a']]), [['a','b'], ['c']]);
assert.deepEqual(layers(['a','b'], []), [['a','b']]);
console.log('Generated JavaScript syntax and 5 graph layout cases passed.');
