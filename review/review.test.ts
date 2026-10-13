/** Typed review parser, privacy boundaries and snapshot-diff regression tests. Created by Jason Stys. */
// BEGIN CODE MAP (generated; npm run maps)
// parameter: name — line 25
// definition: report — line 25
// parameter: state — line 25
// variable: result — line 26
// variable: original — line 31
// variable: changed — line 33
// variable: path — line 34
// variable: before — line 46
// variable: after — line 47
// variable: other — line 51
// variable: {assessment_id: _identity, ...payload} — line 52
// variable: original — line 58
// variable: path — line 59
// END CODE MAP
import assert from 'node:assert/strict';
import { mkdtempSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { test } from 'node:test';
import { canonical, compare, contentId, load, parseReport } from './review.js';

/** Create an independently fictional normalized report with a matching content-derived UUID. */
function report(state = 'SATISFIED', name = 'Fictional unit system') {
  const result = {schema:1,synthetic:true,authorization:'NOT_GRANTED',system_id:'11111111-1111-5111-8111-111111111111',manifest_sha256:'0'.repeat(64),system_name:name,revision:1,as_of:'2026-10-13T12:00:00Z',checks:[{control_id:'ac-2',title:'Account review',state,reason:'Fictional selected check',evidence_id:null,observed_at:null,expected_sha256:null,actual_sha256:null}],risks:[],summary:{SATISFIED:state === 'SATISFIED' ? 1 : 0,NOT_SATISFIED:state === 'NOT_SATISFIED' ? 1 : 0,UNKNOWN:state === 'UNKNOWN' ? 1 : 0,INTEGRITY_ERROR:0}};
  return {...result,assessment_id:contentId(result)};
}

test('closed records, precise state/counts and data-only local reading', () => {
  const original = report();
  assert.equal(parseReport(original).checks[0]?.state, 'SATISFIED');
  for (const changed of [{...original,schema:true},{...original,synthetic:false},{...original,authorization:'AUTHORIZED'},{...original,unexpected:'private'},{...original,revision:1.5},{...original,as_of:'2026-02-30T12:00:00Z'},{...original,system_name:'secret\u001b[31m'},{...original,checks:[...original.checks,...original.checks]},{...original,summary:{...original.summary,UNKNOWN:1}},{...original,system_id:'0'.repeat(32)},{...original,assessment_id:'11111111-1111-5111-8111-111111111111'}]) assert.throws(() => parseReport(changed));
  const path = join(mkdtempSync(join(tmpdir(), 'rmf-review-')), 'report.json');
  writeFileSync(path, canonical(original) + '\n');
  assert.equal(load(path).system_name, original.system_name);
  writeFileSync(path, canonical(original).replace('"schema":1', '"schema":1,"schema":1') + '\n');
  assert.throws(() => load(path));
  writeFileSync(path, 'x'.repeat(2 * 1024 * 1024 + 1));
  assert.throws(() => load(path));
  writeFileSync(path, Buffer.from([255]));
  assert.throws(() => load(path));
});

test('comparison preserves unknown/integrity distinctions and refuses another system', () => {
  const before = parseReport(report('UNKNOWN'));
  const after = parseReport(report());
  assert.deepEqual(compare(before, after).changes, [{control_id:'ac-2',before:'UNKNOWN',after:'SATISFIED'}]);
  assert.equal(compare(before, after).authorization, 'NOT_GRANTED');
  assert.equal(compare(after, after).changes.length, 0);
  const other = {...report(),system_id:'22222222-2222-5222-8222-222222222222'};
  const {assessment_id: _identity, ...payload} = other;
  other.assessment_id = contentId(payload);
  assert.throws(() => compare(before, parseReport(other)));
});

test('Unicode canonical byte compatibility and terminal-label boundaries', () => {
  const original = report('SATISFIED', 'Fictional café — Ω');
  const path = join(mkdtempSync(join(tmpdir(), 'rmf-unicode-')), 'report.json');
  writeFileSync(path, canonical(original) + '\n');
  assert.equal(load(path).system_name, 'Fictional café — Ω');
  assert(canonical(original).includes('caf\\u00e9'));
  assert.throws(() => parseReport({...original,system_name:'Fictional\u202e spoof'}));
});
