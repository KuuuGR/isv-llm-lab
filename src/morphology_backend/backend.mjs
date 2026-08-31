#!/usr/bin/env node
// isv-morphology-backend: line-delimited JSON service over stdio.
//
// Protocol: one JSON request per line on stdin, one JSON response per line
// on stdout. Supported operations:
//
//   inflect  { "op": "inflect", "id": "...", "items": [
//               { "id": "...", "form": "brat", "xpos": "m.anim.", "addition": "" },
//               ...
//             ]}
//            -> { "ok": true, "id": "...", "results": [ { "id": "...", "tokens": [
//                 [form, lemma, upos, xpos, feats|null], ... ] } ] }
//
//   translit { "op": "translit", "id": "...", "text": "...", "target": "isv-Latn" }
//            -> { "ok": true, "id": "...", "text": "..." }
//
// The morphology engine is used strictly as-is (published package API).
// The only local preprocessing is dictionary-format cleanup: stripping
// parenthetical annotations from lemmas (e.g. `podhoditi (k)`) and numeric
// metadata annotations from additions (e.g. `(+2)`), and splitting
// comma-separated variant lemmas (e.g. `den, denj`).

import { inflect } from '@interslavic/morphology';
import { transliterate } from '@interslavic/translit';
import readline from 'node:readline';

const ANNOTATION_RE = /\s*\([^)]*\)/g;
const METADATA_RE = /\(\+\d+\)/g;

function cleanLemma(form) {
  return form.replace(ANNOTATION_RE, '').trim();
}

// Dictionary `addition` mixes morphology hints (e.g. `(opiše)`,
// `(odide; odšėl)`) with numeric metadata annotations (`(+2)`, `(+6)`).
// Metadata annotations must not be passed to the engine as principal parts.
function cleanAddition(addition) {
  if (!addition) return '';
  const cleaned = addition.replace(METADATA_RE, '').trim();
  return /[^\W\d_]/.test(cleaned) ? cleaned : '';
}

function inflectOne(form, xpos, addition) {
  const lemma = cleanLemma(form);
  if (!lemma) return [];
  const hint = cleanAddition(addition);
  const tokens = [];
  for (const piece of lemma.split(',').map((s) => s.trim()).filter(Boolean)) {
    const knowns = [{ form: piece, xpos: xpos || undefined }];
    if (hint) knowns.push({ form: hint });
    let toks;
    try {
      toks = inflect(knowns);
    } catch {
      toks = [];
    }
    for (const t of toks) {
      tokens.push([t.form, t.lemma ?? piece, t.upos ?? null, t.xpos ?? null, t.feats ?? null]);
    }
  }
  return tokens;
}

function handle(req) {
  if (req.op === 'inflect') {
    const items = req.items ?? [];
    const results = items.map((it) => ({
      id: it.id,
      tokens: inflectOne(it.form, it.xpos, it.addition),
    }));
    return { ok: true, id: req.id, results };
  }
  if (req.op === 'translit') {
    return {
      ok: true,
      id: req.id,
      text: transliterate(req.text, req.target ?? 'isv-Latn'),
    };
  }
  return { ok: false, id: req.id, error: `unknown op: ${req.op}` };
}

const rl = readline.createInterface({ input: process.stdin });
rl.on('line', (line) => {
  let req;
  try {
    req = JSON.parse(line);
  } catch {
    return;
  }
  let resp;
  try {
    resp = handle(req);
  } catch (e) {
    resp = { ok: false, id: req.id, error: String(e?.message ?? e) };
  }
  process.stdout.write(`${JSON.stringify(resp)}\n`);
});
// No process.exit on 'close': exiting immediately truncates unflushed stdout.
// After stdin EOF and stdout drain the process exits naturally.
