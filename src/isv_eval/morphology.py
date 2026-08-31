"""Client for the Node morphology backend (``src/morphology_backend/backend.mjs``).

The backend is an isolated subprocess speaking line-delimited JSON over stdio
(see its docstring). This module keeps the morphology engine behind a narrow
interface: Python never reimplements inflection.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_BACKEND = PROJECT_ROOT / "src" / "morphology_backend" / "backend.mjs"

MORPHOLOGY_PACKAGE = "@interslavic/morphology"
TRANSLIT_PACKAGE = "@interslavic/translit"


def morphology_version() -> str:
    """Read the pinned morphology package version from the backend lockfile."""
    lockfile = DEFAULT_BACKEND.parent / "package-lock.json"
    try:
        data = json.loads(lockfile.read_text(encoding="utf-8"))
        for key, pkg in data.get("packages", {}).items():
            if key.endswith(f"node_modules/{MORPHOLOGY_PACKAGE}"):
                return pkg.get("version", "unknown")
    except (OSError, ValueError, KeyError):
        pass
    return "unknown"


class MorphologyBackend:
    def __init__(self, backend_path: str | Path | None = None):
        self.backend_path = str(backend_path or DEFAULT_BACKEND)

    def run(self, request: dict) -> dict:
        proc = subprocess.run(
            ["node", self.backend_path],
            input=json.dumps(request) + "\n",
            capture_output=True,
            text=True,
            timeout=600,
        )
        if proc.returncode != 0:
            raise RuntimeError(
                f"morphology backend failed: {proc.stderr.strip()[:500]}"
            )
        for line in proc.stdout.splitlines():
            try:
                resp = json.loads(line)
            except ValueError:
                continue
            if resp.get("id") == request["id"]:
                return resp
        raise RuntimeError(
            "morphology backend returned no response for request; "
            f"stderr: {proc.stderr.strip()[:300]}; "
            f"stdout bytes: {len(proc.stdout)}"
        )

    def inflect(self, items: list[dict]) -> dict[str, list[list]]:
        """Batch inflection. Each item: {id, form, xpos, addition}.
        Returns {item_id: [[form, lemma, upos, xpos, feats], ...]}."""
        resp = self.run({"op": "inflect", "id": "inflect", "items": items})
        if not resp.get("ok"):
            raise RuntimeError(resp.get("error", "inflect failed"))
        return {r["id"]: r["tokens"] for r in resp["results"]}

    def translit(self, text: str, target: str = "isv-Latn") -> str:
        resp = self.run({"op": "translit", "id": "translit", "text": text,
                         "target": target})
        if not resp.get("ok"):
            raise RuntimeError(resp.get("error", "translit failed"))
        return resp["text"]
