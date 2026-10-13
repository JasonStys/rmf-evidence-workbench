/** Independent native ECMAScript Unicode-schema validation using pinned Ajv. Created by Jason Stys. */
// BEGIN CODE MAP (generated; npm run maps)
// variable: root — line 23
// definition: bytes — line 26
// parameter: path — line 26
// variable: descriptor — line 27
// variable: info — line 29
// parameter: directory — line 36
// definition: validateDirectory — line 36
// variable: lock — line 37
// variable: [model, expected] — line 38
// variable: content — line 39
// variable: ajv — line 41
// variable: validate — line 43
// END CODE MAP
import Ajv from 'ajv';
import addFormats from 'ajv-formats';
import { createHash } from 'node:crypto';
import { closeSync, fstatSync, openSync, readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = resolve(import.meta.dirname, '..');

/** Read only a bounded ordinary local file; no schema/content URL loader is installed. */
function bytes(path) {
  const descriptor = openSync(path, 'r');
  try {
    const info = fstatSync(descriptor);
    if (!info.isFile() || info.size > 2 * 1024 * 1024) throw new Error('schema/document cap');
    return readFileSync(descriptor);
  } finally { closeSync(descriptor); }
}

/** Hash-verify each official schema before compiling it with the runtime's native Unicode regex support. */
export function validateDirectory(directory) {
  const lock = JSON.parse(bytes(resolve(root, 'oscal.lock.json')).toString('utf8'));
  for (const [model, expected] of Object.entries(lock.schemas)) {
    const content = bytes(resolve(root, 'schemas', `oscal_${model}_schema.json`));
    if (createHash('sha256').update(content).digest('hex') !== expected) throw new Error('schema checksum mismatch');
    const ajv = new Ajv({strict:true,allErrors:true,unicodeRegExp:true,validateFormats:true});
    addFormats(ajv);
    const validate = ajv.compile(JSON.parse(content.toString('utf8')));
    if (!validate(JSON.parse(bytes(resolve(directory, `${model}.json`)).toString('utf8')))) throw new Error(`schema validation failed: ${model}`);
  }
  return {models:6,oscal_version:lock.version,engine:'Ajv 8.20.0',remote_schema_retrieval:false};
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  try {
    if (process.argv.length !== 3) throw new Error('one local model directory required');
    console.log(JSON.stringify(validateDirectory(resolve(process.argv[2] ?? ''))));
  } catch { console.error('Independent OSCAL validation failed; no raw input or schema error instances are logged.'); process.exitCode = 2; }
}
