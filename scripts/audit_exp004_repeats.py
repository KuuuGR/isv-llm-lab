#!/usr/bin/env python3
"""EXP-004 phase repeat — collection audit (SODA Task 026, 2026-09-09).

Audit-before-analysis: reconcile the 120 planned repeated-generation runs
(Task 025 kit) with what the research lead actually collected, WITHOUT
changing any experimental evidence.

Principles (Task 026):
- raw model replies are immutable; this script only READS the
  operator-prompts records and never modifies them;
- missing runs are never fabricated;
- prompt parts are validated against the byte-identical authoritative
  renders produced by run_exp004_repeats.prepare (the Task-025 kit), not
  against the collected files themselves;
- operator-metadata-header edits (e.g. the recorded Grok model identity)
  are separated from model-facing content changes;
- deviations are classified and recorded, not silently repaired.

Outputs (deterministic, standard library only):
  experiments/exp004-modelscreen/repeats/outputs/audit.json   (machine-readable)
  experiments/exp004-modelscreen/repeats/outputs/audit.md     (human summary)

The script can optionally merge intake verdicts from outputs/roster.json
(when --roster is given after verify/evaluate) so the reconciliation
table carries final usable/partial/invalid numbers.
"""

import argparse
import importlib.util
import json
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXP = ROOT / "experiments" / "exp004-modelscreen"
REPEATS = EXP / "repeats"
OP_DIR = REPEATS / "operator-prompts"
OUTPUTS = REPEATS / "outputs"
MANIFEST = OP_DIR / "manifest.json"
PLAN = OUTPUTS / "plan.json"
AUDIT_JSON = OUTPUTS / "audit.json"
AUDIT_MD = OUTPUTS / "audit.md"

OUTPUT_MARKER = b"## Output\n"
BOILERPLATE = (b"Return the complete Interslavic translation of the "
               b"source text, and nothing\nelse.\n")

END_MARKER_RE = re.compile(r"^\s*(KONIEC|KONEC|KONĖC)\s*$")


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _sha256_bytes(data: bytes) -> str:
    import hashlib
    return hashlib.sha256(data).hexdigest()


def _split_reply(raw: bytes) -> tuple[bytes, bytes]:
    """Same slicing rule as run_exp004_repeats._split_reply: the closing
    '## Output\\n' marker separates prompt part from reply."""
    idx = raw.rfind(OUTPUT_MARKER)
    if idx < 0:
        return raw, b""
    pos = idx + len(OUTPUT_MARKER)
    while pos < len(raw) and raw[pos:pos + 1] in (b"\n", b"\r"):
        pos += 1
    return raw[:idx], raw[pos:]


def _row_from_run(run: dict) -> dict:
    return dict(
        provider=run["provider"],
        model=run["model"],
        model_version=run["model_version"],
        label=run["label"],
        interface=run["interface"],
        generation_parameters=run["generation_parameters"],
        custom_gpt=run.get("custom_gpt"),
        identity_note=run.get("identity_note"),
        primary=run.get("primary"),
        exploratory=run.get("exploratory"),
        run_number=run.get("run_number"),
    )


class Audit:
    def __init__(self, mod, plan: dict, manifest: dict, roster: dict | None,
                 op_dir: Path | None = None, outputs_dir: Path | None = None):
        self.mod = mod
        self.plan = plan
        self.manifest = manifest
        self.roster = roster
        self.op_dir = Path(op_dir) if op_dir else OP_DIR
        self.outputs_dir = Path(outputs_dir) if outputs_dir else OUTPUTS
        self.source_text = mod._ensure_source().read_text(encoding="utf-8")
        self.corpus_text = mod._ensure_corpus().read_text(encoding="utf-8")
        # authoritative per-file prompt bytes (what prepare would write)
        self.rows = {}
        for run in plan["runs"]:
            row = _row_from_run(run)
            self.rows[run["run_id"]] = row
            for fname in run["prompt_files"]:
                fname = Path(fname).name
                if fname.endswith("msg1.md"):
                    text = mod.render_primed_msg1(row, self.corpus_text)
                elif fname.endswith("msg2.md"):
                    text = mod.render_primed_msg2(row, self.source_text)
                else:
                    text = mod.render_direct_prompt(row, self.source_text)
                setattr(self, "_auth_" + fname, text.encode("utf-8"))

    def _auth(self, fname: str) -> bytes:
        return getattr(self, "_auth_" + Path(fname).name)

    # -- file-level checks -------------------------------------------------
    def file_prompt_status(self, run: dict, fname: str, raw: bytes) -> dict:
        """Compare a collected record against the authoritative render.
        Returns a dict describing prompt integrity."""
        auth = self._auth(fname)
        row = self.rows[run["run_id"]]
        fname = Path(fname).name
        if fname.endswith("msg1.md"):
            # msg1: full-byte comparison, but tolerate operator-metadata
            # header edits BEFORE the study instruction. The invariant is
            # that the model-facing study instruction + full corpus block
            # appear verbatim (and exactly once).
            study_off = auth.find(self.mod.PRIMED_MSG1_STUDY_TEXT.encode())
            tail = auth[study_off:]
            full_match = raw == auth
            tail_count = raw.count(tail)
            return {
                "kind": "msg1",
                "byte_identical": full_match,
                "model_facing_tail_intact": (study_off >= 0 and tail_count == 1),
                "model_facing_tail_bytes": len(tail) if study_off >= 0 else 0,
                "first_diff_offset": _first_diff(raw, auth),
                "header_region_only": (not full_match) and study_off >= 0
                and tail_count == 1,
            }
        # direct / primed msg2: the msg2-style record keeps the prompt
        # through the '## Output' marker; header edits before the
        # translation instruction are tolerated. The invariant region is
        # _translation_body(prefix) == _translation_body(auth prefix).
        prefix, _ = _split_reply(raw)
        auth_prefix = auth.split(OUTPUT_MARKER)[0]
        body_rec = self.mod._translation_body(
            prefix.decode("utf-8", errors="replace"))
        body_auth = self.mod._translation_body(
            auth_prefix.decode("utf-8", errors="replace"))
        prefix_exact = prefix == auth_prefix
        first = _first_diff(prefix, auth_prefix)
        return {
            "kind": "msg2-style",
            "prefix_byte_identical": prefix_exact,
            "translation_body_identical": bool(body_rec)
            and body_rec == body_auth,
            "first_diff_offset": first,
            "header_region_only": (not prefix_exact)
            and bool(body_rec) and body_rec == body_auth,
        }

    # -- per-run audit -----------------------------------------------------
    def audit_run(self, run: dict) -> dict:
        rid = run["run_id"]
        fnames = [Path(f).name for f in run["prompt_files"]]
        last_raw = (self.op_dir / fnames[-1]).read_bytes()
        auth_last = self._auth(fnames[-1])
        pristine = last_raw == auth_last
        rec = {
            "run_id": rid,
            "phase": run["phase"],
            "condition": run["condition"],
            "replicate": run["replicate"],
            "primary": bool(run["primary"]),
            "exploratory": bool(run["exploratory"]),
            "provider": run["provider"],
            "model": run["model"],
            "model_version": run["model_version"],
            "label": run["label"],
            "plan_status": run.get("status"),
            "collection_status": "missing" if pristine else "collected",
            "record_shape": "msg2-style",
            "prompt_files": fnames,
        }
        if not pristine:
            for fname in fnames:
                raw = (self.op_dir / fname).read_bytes()
                st = self.file_prompt_status(run, fname, raw)
                if fname == fnames[-1]:
                    rec["last_file_prompt"] = st
                else:
                    rec.setdefault("msg1_prompt", st)
                rec.setdefault("file_prompt_ok", True)
                rec["file_prompt_ok"] = rec["file_prompt_ok"] and bool(
                    st.get("byte_identical")
                    or st.get("model_facing_tail_intact")
                    or st.get("translation_body_identical"))
            # reply extraction + structural checks
            prefix, reply = _split_reply(last_raw)
            if reply.startswith(BOILERPLATE):
                rec["boilerplate_before_reply"] = True
                reply = reply[len(BOILERPLATE):]
            text = reply.decode("utf-8", errors="replace")
            nonempty = [ln for ln in text.splitlines() if ln.strip()]
            last_line = nonempty[-1].strip() if nonempty else ""
            end_ok = bool(nonempty) and bool(END_MARKER_RE.match(last_line))
            rec["reply_bytes"] = len(reply)
            rec["reply_head"] = text[:60]
            rec["end_marker_ok"] = end_ok
            rec["last_line"] = last_line
            rec["reply_nonempty"] = bool(reply.strip())
            rec["size_floor_ok"] = len(reply) >= int(
                0.60 * len(self.source_text.encode("utf-8")))
        return rec

    # -- deviations --------------------------------------------------------
    def classify_deviations(self, rows: list[dict]) -> list[dict]:
        """Attach the known/observed deviations. Returns a registry of
        deviation objects with affected run ids."""
        by_run = {}
        for rec in rows:
            by_run.setdefault(rec["run_id"], [])

        def add(dev_type: str, run_ids: list[str], desc: str,
                evidence: str, usability: str, canonical: str = "") -> None:
            found = [rid for rid in run_ids if rid in by_run]
            by_run_id = {rid: dev_type for rid in found}

        registry: dict[str, dict] = {}

        def reg(dev_type: str, run_ids: list[str], description: str,
                evidence: str, usability: str,
                severity: str = "minor") -> None:
            registry[dev_type] = {
                "id": dev_type,
                "run_ids": [rid for rid in run_ids if rid in by_run],
                "description": description,
                "evidence": evidence,
                "usability_assessment": usability,
                "severity": severity,
            }

        # 1. Grok identity header edit (observed in files)
        grok_runs = [r["run_id"] for r in rows if r["provider"] == "xai"]
        reg("grok-identity-header-edit",
            grok_runs,
            "Operator recorded the actual model identity in the operator "
            "metadata header of the Grok prompt files ('Model version / "
            "settings: unknown (unknown)' -> 'Grok 4.5, built by xAI "
            "(fast)'). The model-facing instruction/source/corpus regions "
            "are byte-identical to the Task-025 kit. Original files were "
            "'unknown'; the identity is operator-reported (not "
            "independently verifiable from provider metadata in these "
            "records).",
            "Header-line edit present in all nine Grok files (3 direct, "
            "3 msg1, 3 msg2); translation bodies byte-identical.",
            "usable — model-facing content unchanged; identity recorded "
            "as operator-reported.",
            severity="minor")

        # 2. Claude Sonnet 5 — max: thinking/reasoning OFF during repeats
        cmax_runs = [r["run_id"] for r in rows
                     if r["provider"] == "anthropic"
                     and r["model_version"] == "sonnet-5-max"]
        reg("claude-max-thinking-off",
            cmax_runs,
            "Execution deviation (operator-reported): during repeated "
            "collection the research lead disabled thinking/reasoning "
            "mode for the Claude Sonnet 5 — max configuration (enabled "
            "mode operationally impractical: very long analysis, repeated "
            "token-limit interruptions, continuation requirements, hours "
            "of waiting). Differs from the Task-024 Phase-1/Phase-2A "
            "collection condition, where the configuration ran with "
            "intensive reasoning. The configuration is NOT renamed; this "
            "deviation is recorded as separate execution metadata.",
            "Research-lead report (Task 026 brief); no thinking-mode "
            "field is machine-visible in the msg2-style records.",
            "usable with recorded deviation — do not silently merge as "
            "identical configuration; comparability with Task-024 "
            "affected by mode difference.",
            severity="moderate")

        # 3. Gemini primed split-message delivery (operator-reported)
        gem_primed = [r["run_id"] for r in rows
                      if r["provider"] == "google"
                      and r["condition"] == "primed"
                      and r["collection_status"] == "collected"]
        reg("gemini-primed-split-delivery",
            gem_primed,
            "Interface deviation (operator-reported): for Gemini primed "
            "runs the reference-texts message may have exceeded the "
            "single-message window, so the operator split message 1 into "
            "two messages with a 'continue last prompt:'-style "
            "continuation. The stored msg1 files still carry the "
            "byte-identical study instruction + full authoritative "
            "corpus, so the complete corpus was available before the "
            "translation task; the split itself is not machine-visible in "
            "these records. Matches the known Task-021/024 Gemini "
            "two-message delivery deviation.",
            "Research-lead report (Task 026 brief); msg1 records verified "
            "to contain the full authoritative corpus tail verbatim.",
            "usable with recorded interface deviation where corpus "
            "integrity is verified; not marked invalid for splitting "
            "alone.",
            severity="minor")

        # 4. Dola Pro primed r03 msg1: one extra blank line in header
        dp_rows = [r for r in rows if r["provider"] == "bytedance"
                   and r["model_version"] == "pro"]
        dola_pro_r03_msg1 = []
        for r in dp_rows:
            if r["condition"] == "primed" and r["replicate"] == "r03":
                dola_pro_r03_msg1.append(r["run_id"])
        reg("dola-pro-r03-msg1-blank-line",
            dola_pro_r03_msg1,
            "Operator-metadata header edit: one blank line inserted near "
            "the top of the msg1 record (byte offset ~741). The model-"
            "facing study instruction and the full corpus tail remain "
            "byte-identical.",
            "File diff vs authoritative render shows a single inserted "
            "blank line; corpus tail intact.",
            "usable — header whitespace only.",
            severity="trivial")

        # 5. Fresh-session evidence
        return list(registry.values())

    def run(self) -> dict:
        plan = self.plan
        manifest = self.manifest
        # manifest -> run mapping and consistency
        man_files = {Path(f["file"]).name: f for f in manifest["files"]}
        plan_files = [Path(f).name
                      for run in plan["runs"] for f in run["prompt_files"]]
        dup_files = sorted({f for f in plan_files if plan_files.count(f) > 1})
        man_extra = sorted(set(man_files) - set(plan_files))
        plan_missing_man = sorted(set(plan_files) - set(man_files))
        on_disk = sorted(f.name for f in self.op_dir.glob("*.md"))
        on_disk_no_readme = [f for f in on_disk if f != "README.md"]
        disk_extra = sorted(set(on_disk_no_readme) - set(man_files))
        disk_missing = sorted(set(man_files) - set(on_disk_no_readme))

        rows = [self.audit_run(run) for run in plan["runs"]]

        # hash gates: authoritative source/corpus vs plan
        src_sha = _sha256_bytes(self.source_text.encode("utf-8"))
        cor_sha = _sha256_bytes(self.corpus_text.encode("utf-8"))
        plan_src = plan.get("source") or {}
        plan_cor = plan.get("corpus") or {}
        hash_ok = {
            "source": (plan_src.get("sha256") == src_sha),
            "corpus": (plan_cor.get("sha256") == cor_sha),
        }
        # per-run plan hash consistency (all direct runs share source sha;
        # primed runs share corpus sha)
        run_src_ok = all(r["source_sha256"] == src_sha for r in plan["runs"])
        run_cor_ok = all(r["corpus_sha256"] == cor_sha
                         for r in plan["runs"] if r["corpus_sha256"])
        hash_ok["plan_run_source_shas"] = run_src_ok
        hash_ok["plan_run_corpus_shas"] = run_cor_ok

        deviations = self.classify_deviations(rows)

        # merge roster verdicts when available (must precede counts)
        if self.roster:
            by_id = {r["run_id"]: r
                     for r in self.roster.get("rows", self.roster.get("runs", []))}
            for r in rows:
                rr = by_id.get(r["run_id"])
                if rr:
                    r["roster_status"] = rr.get("status")
                    if isinstance(rr.get("intake"), dict):
                        r["intake_verdict"] = rr["intake"].get("verdict")

        # counts
        def pop(rows_, key, pred=None):
            return sum(1 for r in rows_ if (pred(r) if pred else True)
                       and r["collection_status"] == key)

        counts = {}
        for pop_name, pop_rows in (("primary", [r for r in rows
                                                if r["primary"]]),
                                   ("exploratory", [r for r in rows
                                                    if r["exploratory"]])):
            counts[pop_name] = {
                "planned": len(pop_rows),
                "collected": sum(1 for r in pop_rows
                                 if r["collection_status"] == "collected"),
                "missing": sum(1 for r in pop_rows
                               if r["collection_status"] == "missing"),
                "usable": sum(1 for r in pop_rows
                              if r.get("intake_verdict") == "complete"),
                "partial": sum(1 for r in pop_rows
                               if r.get("intake_verdict") == "partial"),
                "invalid": sum(1 for r in pop_rows
                               if r.get("intake_verdict") == "failed"),
                "verdicts_recorded": sum(1 for r in pop_rows
                                         if r.get("intake_verdict")),
            }

        summary = {
            "artifact": "exp004-repeats-collection-audit",
            "experiment_id": plan["experiment_id"],
            "phase": plan["phase"],
            "audit_date": date.today().isoformat(),
            "plan": {
                "planned_runs": len(plan["runs"]),
                "planned_primary": counts["primary"]["planned"],
                "planned_exploratory": counts["exploratory"]["planned"],
                "planned_condition_replicates": {
                    "conditions": plan["conditions"],
                    "replicates": plan["replicates"],
                },
            },
            "manifest": {
                "files": len(man_files),
                "duplicate_file_entries": dup_files,
                "files_in_plan_not_in_manifest": plan_missing_man,
                "manifest_files_not_in_plan": man_extra,
                "on_disk_md": len(on_disk_no_readme),
                "on_disk_not_in_manifest": disk_extra,
                "manifest_missing_on_disk": disk_missing,
            },
            "hash_gates": hash_ok,
            "collection": {
                "collected": sum(r["collection_status"] == "collected"
                                 for r in rows),
                "missing": sum(r["collection_status"] == "missing"
                               for r in rows),
                "primary": counts["primary"],
                "exploratory": counts["exploratory"],
            },
            "fresh_session_proof": "unavailable",
            "runs": rows,
            "deviations": deviations,
        }
        return summary


def _first_diff(a: bytes, b: bytes) -> int:
    i = 0
    while i < min(len(a), len(b)) and a[i] == b[i]:
        i += 1
    return i


def _render_md(summary: dict) -> str:
    plan = summary["plan"]
    man = summary["manifest"]
    coll = summary["collection"]
    lines = [
        "# EXP-004 phase repeat — collection audit (Task 026)",
        "",
        f"- audit date: {summary['audit_date']}",
        "- fresh-session proof: `unavailable` (msg2-style operator "
        "records carry no machine-visible session provenance; absence of "
        "proof is not proof of violation)",
        "",
        "## Plan (Task-025 kit)",
        "",
        f"- planned runs: **{plan['planned_runs']}** "
        f"({plan['planned_primary']} primary + "
        f"{plan['planned_exploratory']} exploratory)",
        f"- conditions: {', '.join(plan['planned_condition_replicates']['conditions'])}; "
        f"replicates: {', '.join(plan['planned_condition_replicates']['replicates'])}",
        "",
        "## Manifest consistency",
        "",
        f"- manifest files: {man['files']}",
        f"- on-disk prompt files: {man['on_disk_md']}",
        f"- duplicate entries: {man['duplicate_file_entries'] or 'none'}",
        f"- in plan but not manifest: {man['files_in_plan_not_in_manifest'] or 'none'}",
        f"- in manifest but not plan: {man['manifest_files_not_in_plan'] or 'none'}",
        f"- on disk but not manifest: {man['on_disk_not_in_manifest'] or 'none'}",
        f"- manifest file missing on disk: {man['manifest_missing_on_disk'] or 'none'}",
        "",
        "## Hash gates (authoritative)",
        "",
        "- source story hash match: "
        f"{'OK' if summary['hash_gates']['source'] else 'MISMATCH'}",
        "- corpus hash match: "
        f"{'OK' if summary['hash_gates']['corpus'] else 'MISMATCH'}",
        "- per-run plan source shas consistent: "
        f"{'OK' if summary['hash_gates']['plan_run_source_shas'] else 'MISMATCH'}",
        "- per-run plan corpus shas consistent: "
        f"{'OK' if summary['hash_gates']['plan_run_corpus_shas'] else 'MISMATCH'}",
        "",
        "## Reconciliation",
        "",
        "| category | count |",
        "|---|---:|",
        f"| planned primary | {plan['planned_primary']} |",
        f"| collected primary | {coll['primary']['collected']} |",
        f"| missing primary | {coll['primary']['missing']} |",
        f"| planned exploratory | {plan['planned_exploratory']} |",
        f"| collected exploratory | {coll['exploratory']['collected']} |",
        f"| missing exploratory | {coll['exploratory']['missing']} |",
        "",
    ]
    verdict_note = ""
    for pop_name in ("primary", "exploratory"):
        c = coll[pop_name]
        if c["verdicts_recorded"]:
            lines.append(
                f"Intake verdicts ({pop_name}, recorded for "
                f"{c['verdicts_recorded']} collected runs after verify):")
            lines.append("")
            lines.append(
                "| verdict | count |\n|---|---:|\n"
                f"| usable (complete) | {c['usable']} |\n"
                f"| partial | {c['partial']} |\n"
                f"| invalid (failed) | {c['invalid']} |\n")
        else:
            verdict_note = (f"- intake verdicts not yet recorded for "
                            f"{pop_name} collected runs — run "
                            "`verify`/`evaluate` + `roster`, then re-run "
                            "this audit with `--roster`.")
    if verdict_note:
        lines.append(verdict_note)
        lines.append("")
    for pop_name in ("primary", "exploratory"):
        sub = [r for r in summary["runs"]
               if ("primary" in r and r["primary"] and pop_name == "primary")
               or ("exploratory" in r and r["exploratory"]
                   and pop_name == "exploratory")]
        missing = [r for r in sub if r["collection_status"] == "missing"]
        collected = [r for r in sub if r["collection_status"] == "collected"]
        lines.append(f"### Missing {pop_name} runs "
                     f"({len(missing)}):")
        for r in missing:
            lines.append(f"- `{r['run_id']}` (pristine prompt file, no "
                         "reply appended)")
        lines.append("")
        n_bad = sum(1 for r in collected
                    if not r.get("file_prompt_ok", False)
                    or r.get("boilerplate_before_reply")
                    or not r.get("end_marker_ok"))
        lines.append(f"### {pop_name.title()} collected runs "
                     f"({len(collected)}) with structural flags "
                     f"({n_bad}):")
        for r in collected:
            flags = []
            lp = r.get("last_file_prompt") or {}
            if not lp.get("translation_body_identical", False) \
               and not lp.get("model_facing_tail_intact", False):
                flags.append("PROMPT-BODY-MISMATCH")
            if r.get("boilerplate_before_reply"):
                flags.append("BOILERPLATE-BEFORE-REPLY")
            if not r.get("end_marker_ok"):
                flags.append(f"END-MARKER: {r['last_line']!r}")
            if not r.get("size_floor_ok"):
                flags.append("UNDER-SIZE-FLOOR")
            if flags:
                lines.append(f"- `{r['run_id']}` — "
                             + "; ".join(flags))
        if n_bad == 0:
            lines.append("- none")
        lines.append("")
    lines += [
        "## Deviations",
        "",
    ]
    for d in summary["deviations"]:
        lines += [
            f"### {d['id']}  ({len(d['run_ids'])} runs, severity "
            f"{d['severity']})",
            "",
            d["description"],
            "",
            f"- affected runs: "
            + ", ".join(f"`{rid}`" for rid in d["run_ids"]),
            f"- evidence: {d['evidence']}",
            f"- usability: {d['usability_assessment']}",
            "",
        ]
    lines += [
        "## Raw output preservation",
        "",
        "No raw reply was rewritten, normalized or repaired. Collected "
        "replies are registered byte-for-byte into "
        "`outputs/<run_id>/output.txt` at collection time; everything "
        "else lives in metadata/reporting only.",
        "",
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--plan", type=Path, default=PLAN)
    ap.add_argument("--manifest", type=Path, default=MANIFEST)
    ap.add_argument("--roster", type=Path, default=None,
                    help="optional outputs/roster.json to merge verdicts")
    args = ap.parse_args(argv)

    mod = _load_module("run_exp004_repeats",
                       ROOT / "scripts" / "run_exp004_repeats.py")
    plan = json.loads(args.plan.read_text(encoding="utf-8"))
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    roster = None
    if args.roster and args.roster.is_file():
        roster = json.loads(args.roster.read_text(encoding="utf-8"))
    audit = Audit(mod, plan, manifest, roster)
    summary = audit.run()
    AUDIT_JSON.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8")
    AUDIT_MD.write_text(_render_md(summary), encoding="utf-8")
    print(f"audit written: {AUDIT_JSON}")
    print(f"audit written: {AUDIT_MD}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
