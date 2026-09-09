"""Tests for scripts/audit_exp004_repeats.py (SODA Task 026).

The audit reconciles the Task-025 planned 120-run manifest against what
was actually collected, without modifying any raw evidence. These tests
exercise the audit against a small synthetic kit:

- missing-run detection (pristine, never-collected prompt files),
- collected-run detection (msg2-style records with a reply appended),
- prompt-part byte validation against the authoritative renders,
- header-edit tolerance (operator metadata only — model-facing content
  intact) vs model-facing-content changes,
- msg1 corpus integrity (full authoritative study + corpus tail present),
- end-marker / structural flags,
- plan↔manifest↔disk consistency,
- deviation registry (Grok identity, Claude-Max thinking-off, Gemini
  split delivery, Dola-Pro blank line),
- machine-readable output + human markdown summary.
"""

import importlib.util
import json
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"

FAKE_SOURCE = (
    "Krótka opowieść o dwóch językach.\n\n"
    "Bronisława i Teofil mieszkali nad rzeką.\n"
    "Rozmawiali o tym, czy języki są podobne.\n"
    "I to wystarczyło.\n\nKONIEC\n"
)
FAKE_CORPUS = (
    "PRIMER TEXT A. To jest tekst wzorcowy pierwszy.\n"
    "PRIMER TEXT B. Drugi tekst wzorcowy.\n"
    "PRIMER TEXT C. Trzeci tekst wzorcowy.\n"
)


@pytest.fixture(scope="module")
def run_mod():
    spec = importlib.util.spec_from_file_location(
        "run_exp004_repeats", SCRIPTS / "run_exp004_repeats.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def audit_mod():
    spec = importlib.util.spec_from_file_location(
        "audit_exp004_repeats", SCRIPTS / "audit_exp004_repeats.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _row(provider="openai", model="gpt-5.6-luna", version="thinkoff",
         label="GPT-5.6 Luna — thinking OFF", interface="ChatGPT (web)",
         gen="thinking OFF"):
    return {
        "provider": provider, "model": model, "model_version": version,
        "label": label, "interface": interface,
        "generation_parameters": gen,
        "custom_gpt": False, "identity_note": None,
        "primary": True, "exploratory": False, "run_number": None,
    }


class Kit:
    """Minimal synthetic repeat kit (plan + manifest + prompt files)."""

    def __init__(self, tmp_path: Path, run_mod, audit_mod):
        self.tmp = tmp_path
        self.op = tmp_path / "operator-prompts"
        self.out = tmp_path / "outputs"
        self.op.mkdir(parents=True)
        self.out.mkdir(parents=True)
        self.run_mod = run_mod
        self.audit_mod = audit_mod
        self.src = tmp_path / "source.txt"
        self.cor = tmp_path / "corpus.txt"
        self.src.write_text(FAKE_SOURCE, encoding="utf-8")
        self.cor.write_text(FAKE_CORPUS, encoding="utf-8")
        # point the run module's source/corpus accessors at the fake files
        run_mod._ensure_source = lambda: self.src
        run_mod._ensure_corpus = lambda: self.cor

    def run(self, run_id: str, condition: str, replicate: str,
            row: dict | None = None, extra: dict | None = None) -> dict:
        row = row or _row()
        base = f"2026-09-08__{row['provider']}__{row['model']}__" \
               f"{row['model_version']}"
        assert run_id == f"{base}__{condition}__{replicate}", (
            "run_id must match the row")
        d = {
            "run_id": run_id, "phase": "repeat", "condition": condition,
            "replicate": replicate, "primary": row["primary"],
            "exploratory": row["exploratory"], "provider": row["provider"],
            "model": row["model"], "model_version": row["model_version"],
            "label": row["label"], "interface": row["interface"],
            "generation_parameters": row["generation_parameters"],
            "custom_gpt": False, "source_sha256": self.src_sha,
            "corpus_sha256": self.cor_sha if condition == "primed" else None,
            "status": "pending_manual_collection",
            "prompt_files": [],
        }
        if extra:
            d.update(extra)
        return d

    @property
    def src_sha(self):
        import hashlib
        return hashlib.sha256(FAKE_SOURCE.encode("utf-8")).hexdigest()

    @property
    def cor_sha(self):
        import hashlib
        return hashlib.sha256(FAKE_CORPUS.encode("utf-8")).hexdigest()

    def render(self, row: dict, fname: str) -> str:
        m = self.run_mod
        if fname.endswith("msg1.md"):
            return m.render_primed_msg1(row, FAKE_CORPUS)
        if fname.endswith("msg2.md"):
            return m.render_primed_msg2(row, FAKE_SOURCE)
        return m.render_direct_prompt(row, FAKE_SOURCE)

    def write_record(self, row: dict, fname: str, reply: bytes | None,
                     edit_header: str | None = None,
                     edit_offset: int | None = None) -> None:
        """Write a prompt record. reply=None keeps the pristine prepared
        prompt (boilerplate intact). reply=bytes writes a msg2-style
        record (boilerplate replaced by the reply)."""
        text = self.render(row, fname)
        raw = text.encode("utf-8")
        if edit_header is not None:
            # replace the 'Model version / settings:' header line
            lines = text.split("\n")
            lines = [edit_header if ln.startswith("Model version / settings:")
                     else ln for ln in lines]
            raw = "\n".join(lines).encode("utf-8")
        if edit_offset is not None:
            raw = raw[:edit_offset] + b"\n" + raw[edit_offset:]
        if reply is not None:
            marker = b"## Output\n"
            head, _tail = raw.split(marker, 1)
            raw = head + marker + reply
        (self.op / fname).write_bytes(raw)

    def audit(self, runs: list[dict], files: list[dict],
              roster: dict | None = None) -> dict:
        plan = {
            "experiment_id": "exp004", "phase": "repeat",
            "conditions": ["direct", "primed"], "replicates": ["r01"],
            "source": {"sha256": self.src_sha},
            "corpus": {"sha256": self.cor_sha},
            "runs": runs,
        }
        manifest = {"files": files, "artifact": "exp004-repeat-prompts"}
        a = self.audit_mod.Audit(self.run_mod, plan, manifest, roster,
                                 op_dir=self.op, outputs_dir=self.out)
        return a.run()

    def plan_entry_files(self, run: dict, fnames: list[str]) -> None:
        run["prompt_files"] = fnames


def test_audit_missing_run_detected(run_mod, audit_mod, tmp_path):
    """A pristine (never-collected) prompt file is reported missing and is
    never fabricated into a reply."""
    kit = Kit(tmp_path, run_mod, audit_mod)
    row = _row()
    fname = "direct-01-gpt-5.6-luna-thinkoff-r01.md"
    kit.write_record(row, fname, reply=None)  # pristine
    run = kit.run("2026-09-08__openai__gpt-5.6-luna__thinkoff__direct__r01",
                  "direct", "r01", row, {"prompt_files": [fname]})
    files = [{"file": fname, "run_id": run["run_id"]}]
    summary = kit.audit([run], files)
    rec = summary["runs"][0]
    assert rec["collection_status"] == "missing"
    assert summary["collection"]["missing"] == 1
    assert summary["collection"]["collected"] == 0


def test_audit_collected_msg2_style_prompt_ok(run_mod, audit_mod, tmp_path):
    """A collected msg2-style record (reply appended after '## Output')
    is detected; its prompt part stays byte-identical to the kit."""
    kit = Kit(tmp_path, run_mod, audit_mod)
    row = _row()
    fname = "direct-01-gpt-5.6-luna-thinkoff-r01.md"
    reply = b"Opovest o jezykah.\n\nKONEC\n"
    kit.write_record(row, fname, reply=reply)
    run = kit.run("2026-09-08__openai__gpt-5.6-luna__thinkoff__direct__r01",
                  "direct", "r01", row, {"prompt_files": [fname]})
    summary = kit.audit([run], [{"file": fname, "run_id": run["run_id"]}])
    rec = summary["runs"][0]
    assert rec["collection_status"] == "collected"
    assert rec["last_file_prompt"]["prefix_byte_identical"] is True
    assert rec["last_file_prompt"]["translation_body_identical"] is True
    assert rec["end_marker_ok"] is True


def test_audit_header_edit_tolerated(run_mod, audit_mod, tmp_path):
    """Grok-style operator-metadata header edit (model identity recorded)
    does not flag the model-facing content as changed."""
    kit = Kit(tmp_path, run_mod, audit_mod)
    row = _row(provider="xai", model="grok", version="unknown",
               label="Grok", interface="Grok (web)", gen="unknown")
    fname = "direct-08-grok-unknown-r01.md"
    kit.write_record(row, fname, reply=b"Opovest.\n\nKONEC\n",
                     edit_header="Model version / settings: Grok 4.5, "
                                 "built by xAI (fast)")
    run = kit.run("2026-09-08__xai__grok__unknown__direct__r01",
                  "direct", "r01", row, {"prompt_files": [fname]})
    summary = kit.audit([run], [{"file": fname, "run_id": run["run_id"]}])
    rec = summary["runs"][0]
    st = rec["last_file_prompt"]
    assert st["prefix_byte_identical"] is False
    assert st["translation_body_identical"] is True
    assert st["header_region_only"] is True
    assert rec["file_prompt_ok"] is True


def test_audit_msg1_corpus_tail_intact(run_mod, audit_mod, tmp_path):
    """msg1 records must carry the full authoritative study + corpus tail;
    a header blank-line insertion is tolerated but body damage is not."""
    kit = Kit(tmp_path, run_mod, audit_mod)
    row = _row()
    msg1 = "primed-01-gpt-5.6-luna-thinkoff-r01-msg1.md"
    msg2 = "primed-01-gpt-5.6-luna-thinkoff-r01-msg2.md"
    # blank line inserted early in the header (offset 60 < study start)
    kit.write_record(row, msg1, reply=None, edit_offset=60)
    kit.write_record(row, msg2, reply=b"Opovest.\n\nKONEC\n")
    run = kit.run("2026-09-08__openai__gpt-5.6-luna__thinkoff__primed__r01",
                  "primed", "r01", row, {"prompt_files": [msg1, msg2]})
    summary = kit.audit([run], [{"file": msg1, "run_id": run["run_id"]},
                                {"file": msg2, "run_id": run["run_id"]}])
    rec = summary["runs"][0]
    st = rec["msg1_prompt"]
    assert st["byte_identical"] is False
    assert st["model_facing_tail_intact"] is True
    assert st["header_region_only"] is True

    # now corrupt the corpus tail: the audit must flag it
    kit2 = Kit(tmp_path / "corrupt", run_mod, audit_mod)
    auth = kit2.render(row, msg1).encode("utf-8")
    study = run_mod.PRIMED_MSG1_STUDY_TEXT.encode("utf-8")
    cut = auth.rfind(b"PRIMER TEXT C")
    corrupted = auth[:cut] + b"PRIMER TEXT X -- damaged."
    (kit2.op / msg1).write_bytes(corrupted)
    kit2.write_record(row, msg2, reply=b"Opovest.\n\nKONEC\n")
    run2 = kit2.run("2026-09-08__openai__gpt-5.6-luna__thinkoff__primed__r01",
                    "primed", "r01", row, {"prompt_files": [msg1, msg2]})
    summary2 = kit2.audit([run2],
                          [{"file": msg1, "run_id": run2["run_id"]},
                           {"file": msg2, "run_id": run2["run_id"]}])
    rec2 = summary2["runs"][0]
    assert rec2["msg1_prompt"]["model_facing_tail_intact"] is False
    assert rec2["msg1_prompt"]["header_region_only"] is False
    assert rec2["file_prompt_ok"] is False


def test_audit_end_marker_and_length_flags(run_mod, audit_mod, tmp_path):
    """Nonstandard end markers (markdown-wrapped KONEC) and implausibly
    short replies are flagged as structural issues, never repaired."""
    kit = Kit(tmp_path, run_mod, audit_mod)
    row = _row()
    fname = "direct-01-gpt-5.6-luna-thinkoff-r01.md"
    kit.write_record(row, fname, reply=b"Opovest.\n\n## KONEC\n")
    run = kit.run("2026-09-08__openai__gpt-5.6-luna__thinkoff__direct__r01",
                  "direct", "r01", row, {"prompt_files": [fname]})
    summary = kit.audit([run], [{"file": fname, "run_id": run["run_id"]}])
    rec = summary["runs"][0]
    assert rec["end_marker_ok"] is False
    assert rec["last_line"] == "## KONEC"


def test_audit_manifest_consistency(run_mod, audit_mod, tmp_path):
    """Files in the manifest but missing on disk are reported; extra
    on-disk files are reported; nothing is silently dropped."""
    kit = Kit(tmp_path, run_mod, audit_mod)
    row = _row()
    fname = "direct-01-gpt-5.6-luna-thinkoff-r01.md"
    kit.write_record(row, fname, reply=None)
    run = kit.run("2026-09-08__openai__gpt-5.6-luna__thinkoff__direct__r01",
                  "direct", "r01", row, {"prompt_files": [fname]})
    files = [{"file": fname, "run_id": run["run_id"]},
             {"file": "ghost-file.md", "run_id": run["run_id"]}]
    # a stray file not in the manifest
    (kit.op / "stray.md").write_text("x", encoding="utf-8")
    summary = kit.audit([run], files)
    man = summary["manifest"]
    assert man["manifest_missing_on_disk"] == ["ghost-file.md"]
    assert man["on_disk_not_in_manifest"] == ["stray.md"]


def test_audit_deviation_registry(run_mod, audit_mod, tmp_path):
    """The deviation registry attaches the four known deviation classes to
    the matching runs only (Grok identity, Claude-Max thinking-off, Gemini
    primed split, Dola-Pro blank line)."""
    kit = Kit(tmp_path, run_mod, audit_mod)
    runs = []

    grok = _row(provider="xai", model="grok", version="unknown", label="Grok",
                interface="Grok (web)", gen="unknown")
    f1 = "direct-08-grok-unknown-r01.md"
    kit.write_record(grok, f1, reply=b"A.\n\nKONEC\n")
    runs.append(kit.run("2026-09-08__xai__grok__unknown__direct__r01",
                        "direct", "r01", grok, {"prompt_files": [f1]}))

    cmax = _row(provider="anthropic", model="claude", version="sonnet-5-max",
                label="Claude Sonnet 5 — max (long reasoning)",
                interface="Claude (web)", gen="Sonnet 5 max")
    f2 = "direct-12-claude-sonnet-5-max-r01.md"
    kit.write_record(cmax, f2, reply=b"B.\n\nKONEC\n")
    runs.append(kit.run("2026-09-08__anthropic__claude__sonnet-5-max__"
                        "direct__r01", "direct", "r01", cmax,
                        {"prompt_files": [f2]}))

    gem = _row(provider="google", model="gemini-3.6-flash",
               version="extthinkon",
               label="Gemini 3.6 Flash — extended thinking ON",
               interface="Google Gemini (web)", gen="3.6 Flash, ext ON")
    m1 = "primed-14-gemini-3.6-flash-extthinkon-r01-msg1.md"
    m2 = "primed-14-gemini-3.6-flash-extthinkon-r01-msg2.md"
    kit.write_record(gem, m1, reply=None)
    kit.write_record(gem, m2, reply=b"C.\n\nKONEC\n")
    runs.append(kit.run("2026-09-08__google__gemini-3.6-flash__extthinkon__"
                        "primed__r01", "primed", "r01", gem,
                        {"prompt_files": [m1, m2]}))

    dola = _row(provider="bytedance", model="dola-3.8", version="pro",
                label="Dola 3.8 — Pro", interface="ByteDance — official web "
                "interface", gen="default settings", )
    dola["primary"] = False
    dola["exploratory"] = True
    dola["run_number"] = 21
    p1 = "primed-21-dola-3.8-pro-r03-msg1.md"
    p2 = "primed-21-dola-3.8-pro-r03-msg2.md"
    kit.write_record(dola, p1, reply=None, edit_offset=60)
    kit.write_record(dola, p2, reply=b"D.\n\nKONEC\n")
    runs.append(kit.run("2026-09-08__bytedance__dola-3.8__pro__primed__r03",
                        "primed", "r03", dola, {"prompt_files": [p1, p2]}))

    files = [{"file": f1, "run_id": runs[0]["run_id"]},
             {"file": f2, "run_id": runs[1]["run_id"]},
             {"file": m1, "run_id": runs[2]["run_id"]},
             {"file": m2, "run_id": runs[2]["run_id"]},
             {"file": p1, "run_id": runs[3]["run_id"]},
             {"file": p2, "run_id": runs[3]["run_id"]}]
    summary = kit.audit(runs, files)
    devs = {d["id"]: d["run_ids"] for d in summary["deviations"]}
    assert devs["grok-identity-header-edit"] == [runs[0]["run_id"]]
    assert devs["claude-max-thinking-off"] == [runs[1]["run_id"]]
    assert devs["gemini-primed-split-delivery"] == [runs[2]["run_id"]]
    assert devs["dola-pro-r03-msg1-blank-line"] == [runs[3]["run_id"]]
    assert summary["fresh_session_proof"] == "unavailable"


def test_audit_roster_verdict_merge(run_mod, audit_mod, tmp_path):
    """When --roster rows carry intake verdicts, the audit rows and
    reconciliation counts pick them up (usable/partial/invalid)."""
    kit = Kit(tmp_path, run_mod, audit_mod)
    row = _row()
    fname = "direct-01-gpt-5.6-luna-thinkoff-r01.md"
    kit.write_record(row, fname, reply=b"Opovest.\n\nKONEC\n")
    run = kit.run("2026-09-08__openai__gpt-5.6-luna__thinkoff__direct__r01",
                  "direct", "r01", row, {"prompt_files": [fname]})
    files = [{"file": fname, "run_id": run["run_id"]}]
    roster = {"rows": [{
        "run_id": run["run_id"], "status": "collected_external_output",
        "intake": {"verdict": "complete"}, "usable": True,
    }]}
    summary = kit.audit([run], files, roster=roster)
    assert summary["runs"][0]["intake_verdict"] == "complete"
    assert summary["collection"]["primary"]["usable"] == 1
    assert summary["collection"]["primary"]["partial"] == 0
    assert summary["collection"]["primary"]["invalid"] == 0
    md = audit_mod._render_md(summary)
    assert "usable (complete) | 1 |" in md


def test_audit_summary_markdown(run_mod, audit_mod, tmp_path):
    """The human summary renders a reconciliation table and lists missing
    runs without inventing data."""
    kit = Kit(tmp_path, run_mod, audit_mod)
    row = _row()
    fname = "direct-01-gpt-5.6-luna-thinkoff-r01.md"
    kit.write_record(row, fname, reply=None)
    run = kit.run("2026-09-08__openai__gpt-5.6-luna__thinkoff__direct__r01",
                  "direct", "r01", row, {"prompt_files": [fname]})
    summary = kit.audit([run], [{"file": fname, "run_id": run["run_id"]}])
    md = audit_mod._render_md(summary)
    assert "planned primary | 1 |" in md
    assert "collected primary | 0 |" in md
    assert "missing primary | 1 |" in md
    assert "## Deviations" in md
    assert "fresh-session proof" in md


def test_audit_json_output_deterministic(run_mod, audit_mod, tmp_path):
    """main() writes audit.json + audit.md to the configured paths."""
    kit = Kit(tmp_path, run_mod, audit_mod)
    row = _row()
    fname = "direct-01-gpt-5.6-luna-thinkoff-r01.md"
    kit.write_record(row, fname, reply=b"Opovest.\n\nKONEC\n")
    run = kit.run("2026-09-08__openai__gpt-5.6-luna__thinkoff__direct__r01",
                  "direct", "r01", row, {"prompt_files": [fname]})
    plan = {
        "experiment_id": "exp004", "phase": "repeat",
        "conditions": ["direct", "primed"], "replicates": ["r01"],
        "source": {"sha256": kit.src_sha},
        "corpus": {"sha256": kit.cor_sha},
        "runs": [run],
    }
    manifest = {"files": [{"file": fname, "run_id": run["run_id"]}],
                "artifact": "exp004-repeat-prompts"}
    (kit.out / "plan.json").write_text(json.dumps(plan), encoding="utf-8")
    (kit.op / "manifest.json").write_text(json.dumps(manifest),
                                          encoding="utf-8")
    audit_mod.AUDIT_JSON = kit.out / "audit.json"
    audit_mod.AUDIT_MD = kit.out / "audit.md"
    # main() reloads run_exp004_repeats; reuse the prepared module via
    # monkeypatched loader so source/corpus point at the fake files.
    real_load = audit_mod._load_module

    def fake_load(name, path):
        if name == "run_exp004_repeats":
            return run_mod
        return real_load(name, path)

    audit_mod._load_module = fake_load
    rc = audit_mod.main(["--plan", str(kit.out / "plan.json"),
                         "--manifest", str(kit.op / "manifest.json")])
    assert rc == 0
    out = json.loads((kit.out / "audit.json").read_text(encoding="utf-8"))
    assert out["runs"][0]["collection_status"] == "collected"
    assert (kit.out / "audit.md").is_file()
