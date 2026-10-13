/** Typed offline snapshot comparison; data is parsed, never executed or sent remotely. Created by Jason Stys. */
// BEGIN CODE MAP (generated; npm run maps)
// variable: states — line 71
// definition: Check — line 73
// definition: Risk — line 74
// definition: Report — line 75
// parameter: fields — line 78
// definition: object — line 78
// parameter: value — line 78
// definition: uuid — line 84
// parameter: value — line 84
// definition: timestamp — line 89
// parameter: value — line 89
// definition: label — line 94
// parameter: value — line 94
// definition: count — line 99
// parameter: maximum — line 99
// parameter: minimum — line 99
// parameter: value — line 99
// parameter: input — line 104
// definition: parseReport — line 104
// variable: raw — line 105
// variable: selected — line 110
// variable: totals — line 111
// variable: item — line 112
// variable: check — line 113
// variable: key — line 114
// variable: summary — line 121
// variable: state — line 122
// variable: riskIds — line 123
// variable: item — line 124
// variable: risk — line 125
// variable: {assessment_id, ...payload} — line 131
// definition: canonical — line 137
// parameter: value — line 137
// parameter: item — line 139
// definition: sorted — line 139
// parameter: [key, entry] — line 141
// parameter: [left] — line 141
// parameter: [right] — line 141
// parameter: character — line 144
// definition: contentId — line 148
// parameter: value — line 148
// definition: load — line 153
// parameter: path — line 153
// variable: descriptor — line 154
// variable: info — line 156
// variable: content — line 158
// variable: raw — line 159
// parameter: after — line 166
// parameter: before — line 166
// definition: compare — line 166
// parameter: check — line 169
// variable: prior — line 169
// parameter: check — line 170
// variable: current — line 170
// variable: oldRisks — line 171
// parameter: risk — line 171
// variable: newRisks — line 172
// parameter: risk — line 172
// variable: changes — line 173
// parameter: id — line 173
// parameter: id — line 174
// variable: risk_changes — line 174
// END CODE MAP
import { closeSync, fstatSync, openSync, readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { v5 as uuidV5 } from 'uuid';

const states = ['SATISFIED', 'NOT_SATISFIED', 'UNKNOWN', 'INTEGRITY_ERROR'] as const;
export type State = typeof states[number];
export interface Check { control_id: string; title: string; state: State; reason: string; evidence_id: string | null; observed_at: string | null; expected_sha256: string | null; actual_sha256: string | null; }
export interface Risk { id: string; control_id: string; severity: string; status: string; owner: string; due_at: string; overdue: boolean; pending_milestones: number; }
export interface Report { schema: number; synthetic: true; authorization: 'NOT_GRANTED'; system_id: string; system_name: string; revision: number; as_of: string; assessment_id: string; manifest_sha256: string; checks: Check[]; risks: Risk[]; summary: Record<State, number>; }

/** Require a closed object and reject unknown fields, arrays and inherited/non-object scalar input. */
function object(value: unknown, fields: string[]): Record<string, unknown> {
  if (value === null || typeof value !== 'object' || Array.isArray(value) || Object.keys(value).sort().join('|') !== [...fields].sort().join('|')) throw new Error('closed report record required');
  return value as Record<string, unknown>;
}

/** Check fixed-format identities without interpreting IDs as authentication or authority. */
function uuid(value: unknown): asserts value is string {
  if (typeof value !== 'string' || !/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/.test(value) || /^0{8}-0{4}-0{4}-0{4}-0{12}$/.test(value)) throw new Error('canonical UUID required');
}

/** Require portable UTC calendar dates, rejecting JavaScript's silent normalization of invalid calendar dates. */
function timestamp(value: unknown): asserts value is string {
  if (typeof value !== 'string' || value.startsWith('0000') || !/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$/.test(value) || !Number.isFinite(Date.parse(value)) || new Date(value).toISOString().replace('.000Z', 'Z') !== value) throw new Error('UTC timestamp required');
}

/** Require bounded printable labels and reject terminal/bidi controls in the offline CLI output. */
function label(value: unknown): asserts value is string {
  if (typeof value !== 'string' || !value.trim() || value.length > 2000 || /[\p{Cc}\p{Cf}\p{Cs}\p{Zl}\p{Zp}]/u.test(value)) throw new Error('bounded printable label required');
}

/** Require integral finite counts; booleans and numeric strings are not accepted. */
function count(value: unknown, minimum = 0, maximum = 1000): asserts value is number {
  if (typeof value !== 'number' || !Number.isSafeInteger(value) || value < minimum || value > maximum) throw new Error('bounded integer required');
}

/** Parse normalized machine reports and independently verify references, summary counts and honest authorization state. */
export function parseReport(input: unknown): Report {
  const raw = object(input, ['schema','synthetic','authorization','system_id','system_name','revision','as_of','checks','risks','summary','assessment_id','manifest_sha256']);
  if (typeof raw.manifest_sha256 !== 'string' || !/^[0-9a-f]{64}$/.test(raw.manifest_sha256)) throw new Error('manifest fingerprint required');
  if (raw.schema !== 1 || raw.synthetic !== true || raw.authorization !== 'NOT_GRANTED') throw new Error('educational report required');
  uuid(raw.system_id); uuid(raw.assessment_id); label(raw.system_name); count(raw.revision, 1, 100000); timestamp(raw.as_of);
  if (!Array.isArray(raw.checks) || raw.checks.length < 1 || raw.checks.length > 1000 || !Array.isArray(raw.risks) || raw.risks.length > 1000) throw new Error('bounded report arrays required');
  const selected = new Set<string>();
  const totals: Record<State, number> = {SATISFIED:0,NOT_SATISFIED:0,UNKNOWN:0,INTEGRITY_ERROR:0};
  for (const item of raw.checks) {
    const check = object(item, ['control_id','title','state','reason','evidence_id','observed_at','expected_sha256','actual_sha256']);
    for (const key of ['expected_sha256','actual_sha256']) { if (check[key] !== null && (typeof check[key] !== 'string' || !/^[0-9a-f]{64}$/.test(check[key]))) throw new Error('evidence digest required'); }
    label(check.control_id); label(check.title); label(check.reason);
    if (selected.has(check.control_id) || typeof check.state !== 'string' || !states.includes(check.state as State)) throw new Error('duplicate control or unsupported state');
    selected.add(check.control_id); totals[check.state as State]++;
    if (check.evidence_id !== null) uuid(check.evidence_id);
    if (check.observed_at !== null) timestamp(check.observed_at);
  }
  const summary = object(raw.summary, [...states]);
  for (const state of states) { count(summary[state]); if (summary[state] !== totals[state]) throw new Error('summary mismatch'); }
  const riskIds = new Set<string>();
  for (const item of raw.risks) {
    const risk = object(item, ['id','control_id','severity','status','owner','due_at','overdue','pending_milestones']);
    uuid(risk.id); label(risk.control_id); label(risk.owner); timestamp(risk.due_at); count(risk.pending_milestones);
    label(risk.severity); label(risk.status);
    if (riskIds.has(risk.id) || !selected.has(risk.control_id) || !['low','moderate','high'].includes(String(risk.severity)) || !['open','in-progress','resolved'].includes(String(risk.status)) || typeof risk.overdue !== 'boolean') throw new Error('invalid risk or dangling control');
    riskIds.add(risk.id);
  }
  const {assessment_id, ...payload} = raw;
  if (assessment_id !== contentId(payload)) throw new Error('report content identity mismatch');
  return raw as unknown as Report;
}

/** Produce Python-compatible sorted ASCII finite JSON; canonical reports reject duplicate/shadow JSON keys. */
export function canonical(value: unknown): string {
  /** Sort every object recursively; arrays preserve their recorded chronological/control order. */
  function sorted(item: unknown): unknown {
    if (Array.isArray(item)) return item.map(sorted);
    if (item !== null && typeof item === 'object') return Object.fromEntries(Object.entries(item).sort(([left], [right]) => left < right ? -1 : left > right ? 1 : 0).map(([key, entry]) => [key, sorted(entry)]));
    return item;
  }
  return JSON.stringify(sorted(value)).replace(/[\u007f-\uffff]/g, (character) => '\\u' + character.charCodeAt(0).toString(16).padStart(4, '0'));
}

/** Match Python UUIDv5 content identity; this detects content changes, not an authenticated signature. */
export function contentId(value: unknown): string {
  return uuidV5(canonical(value), '6a11b4cd-6f31-5b49-8c05-05735e979260');
}

/** Read a capped ordinary file and require its normalized canonical encoding before any report comparison. */
export function load(path: string): Report {
  const descriptor = openSync(path, 'r');
  try {
    const info = fstatSync(descriptor);
    if (!info.isFile() || info.size > 2 * 1024 * 1024) throw new Error('bounded ordinary report file required');
    const content = new TextDecoder('utf-8', {fatal:true}).decode(readFileSync(descriptor));
    const raw: unknown = JSON.parse(content);
    if (canonical(raw) + '\n' !== content) throw new Error('normalized canonical report required');
    return parseReport(raw);
  } finally { closeSync(descriptor); }
}

/** Compare snapshots for the same fictional system in O(N); changing a control scope is explicitly reported. */
export function compare(before: Report, after: Report): {author: string; authorization: string; changes: {control_id: string; before: string; after: string}[]; risk_changes: {id: string; before: string; after: string}[]} {
  parseReport(before); parseReport(after);
  if (before.system_id !== after.system_id) throw new Error('cannot compare different system boundaries');
  const prior = new Map(before.checks.map((check) => [check.control_id, check.state]));
  const current = new Map(after.checks.map((check) => [check.control_id, check.state]));
  const oldRisks = new Map(before.risks.map((risk) => [risk.id, `${risk.status};overdue=${risk.overdue}`]));
  const newRisks = new Map(after.risks.map((risk) => [risk.id, `${risk.status};overdue=${risk.overdue}`]));
  const changes = [...new Set([...prior.keys(), ...current.keys()])].sort().filter((id) => prior.get(id) !== current.get(id)).map((id) => ({control_id:id,before:prior.get(id) ?? 'NOT_SELECTED',after:current.get(id) ?? 'NOT_SELECTED'}));
  const risk_changes = [...new Set([...oldRisks.keys(), ...newRisks.keys()])].sort().filter((id) => oldRisks.get(id) !== newRisks.get(id)).map((id) => ({id,before:oldRisks.get(id) ?? 'NOT_RECORDED',after:newRisks.get(id) ?? 'NOT_RECORDED'}));
  return {author:'Jason Stys',authorization:'NOT_GRANTED',changes,risk_changes};
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  try {
    if (process.argv.length !== 4) throw new Error('two local report paths required');
    console.log(JSON.stringify(compare(load(process.argv[2] ?? ''), load(process.argv[3] ?? '')), null, 2));
  } catch { console.error('Review rejected: use two normalized local reports from the same system; see docs/runbook.md.'); process.exitCode = 2; }
}
