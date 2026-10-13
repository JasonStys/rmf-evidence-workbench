"""Maintain exhaustive tracked-file README summaries without reading ignored drill outputs. Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# variable: ROOT — line 32
# variable: BEGIN — line 33
# variable: END — line 33
# variable: SPECIAL — line 34
# definition: description — line 58
# parameter: path — line 58
# variable: content — line 74
# variable: line — line 82
# definition: main — line 90
# variable: parser — line 92
# variable: args — line 94
# variable: files — line 95
# variable: rows — line 103
# variable: path — line 104
# variable: label — line 105
# variable: destination — line 107
# variable: original — line 108
# variable: first — line 109
# variable: last — line 109
# variable: expected — line 110
# END CODE MAP

from __future__ import annotations

import argparse
import ast
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BEGIN, END = "<!-- BEGIN FILE GUIDE -->", "<!-- END FILE GUIDE -->"
SPECIAL = {
    ".gitattributes": "Portable LF text handling.",
    ".gitignore": "Keeps private local evidence, databases, tools and generated build/cache output out of Git.",
    "LICENSE": "MIT terms for authored code, not the unmodified NIST schemas.",
    "pyproject.toml": "Strict Python lint/type/tests and branch-inclusive coverage configuration.",
    "package.json": "Pinned native schema/review dependencies and Node scripts.",
    "package-lock.json": "Complete npm dependency graph with registry integrity hashes.",
    "tsconfig.json": "Strict Node TypeScript compiler settings.",
    "requirements.in": "Exact reviewed runtime dependencies with real JSON format and Unicode support.",
    "requirements.lock": "Complete hash-pinned portable runtime graph.",
    "requirements-dev.in": "Exact direct validation dependencies plus the runtime graph.",
    "requirements-dev.lock": "Complete hash-pinned portable validation graph.",
    "tools.lock.json": "Official scanner release URLs and archive SHA-256 digests.",
    "oscal.lock.json": "Official NIST OSCAL version and six untouched release-schema checksums.",
    "schemas/NIST-NOTICE.md": "Intact original NIST public-domain/CC0 notice for the unmodified schemas.",
    "docs/reports/demo.json": "Actual cross-language synthetic assessment, schema and ledger validation results.",
    "docs/reports/benchmark.json": "Actual warmed assessment/schema timing and allocation measurements.",
    "docs/reports/baseline.json": "Canonical measured baseline with unknown/failing states and exact evidence fingerprints.",
    "docs/reports/remediated.json": "Canonical measured remediation with fresh predicates and bounded risk closure.",
    "docs/reports/baseline.html": "Escaped network-inert rendered synthetic assessment.",
    "docs/reports/ci.json": "Verified executable-source SHA and actual completed CI check snapshot.",
}


def description(path: str) -> str:
    """Require a meaningful description for every tracked file; unknown formats fail maintenance checks."""
    if path in SPECIAL:
        return SPECIAL[path]
    if path.startswith("schemas/oscal_"):
        return (
            "Unmodified NIST OSCAL 1.2.3 "
            + Path(path).stem.replace("oscal_", "").replace("_schema", "")
            + " JSON schema; pinned and checked in both Unicode-capable engines."
        )
    if path.startswith("examples/"):
        return (
            "Fictional "
            + Path(path).stem
            + " evidence/manifest; no real identities, credentials, account data or host collection."
        )
    content = (ROOT / path).read_text(encoding="utf-8")
    if path.endswith(".py"):
        return (ast.get_docstring(ast.parse(content)) or "").splitlines()[0]
    if path.endswith(".md"):
        return content.splitlines()[0].lstrip("# ") + "."
    if path.endswith((".sh", ".yml", ".sql")):
        return next(
            line.lstrip("#- ")
            for line in content.splitlines()
            if line.startswith(("# ", "-- "))
        )
    if path.endswith((".ts", ".mjs")):
        return content.splitlines()[0].strip("/ *")
    raise ValueError(f"missing tracked-file purpose: {path}")


def main() -> int:
    """Generate/check the README inventory using intended Git-tracked files only; stage before generating."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    files = (
        subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT)
        .decode()
        .rstrip("\0")
        .split("\0")
    )
    if files == [""]:
        raise ValueError("stage intended files first")
    rows = ["| File | Purpose |", "| --- | --- |"]
    for path in sorted(files):
        label = path.replace("_", "\\_")
        rows.append(f"| [{label}]({path}) | {description(path).replace('|', '/')} |")
    destination = ROOT / "README.md"
    original = destination.read_text(encoding="utf-8")
    first, last = original.index(BEGIN) + len(BEGIN), original.index(END)
    expected = original[:first] + "\n\n" + "\n".join(rows) + "\n\n" + original[last:]
    if args.check and expected != original:
        raise ValueError("README inventory stale")
    if not args.check:
        destination.write_text(expected, encoding="utf-8", newline="\n")
    print(f"README inventory current: {len(files)} tracked files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
