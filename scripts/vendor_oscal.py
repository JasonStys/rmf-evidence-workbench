"""Fetch only six official hash-pinned NIST OSCAL schemas for offline validation. Created by Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# variable: ROOT — line 29
# definition: vendor — line 32
# parameter: check — line 32
# variable: lock — line 34
# variable: output — line 35
# variable: expected — line 37
# variable: name — line 37
# variable: path — line 38
# variable: content — line 40
# variable: url — line 44
# variable: response — line 45
# variable: content — line 46
# variable: stream — line 53
# definition: main — line 58
# variable: parser — line 60
# variable: arguments — line 62
# END CODE MAP

from __future__ import annotations

import argparse
import hashlib
import json
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def vendor(check: bool = False) -> None:
    """Verify existing schema digests or fetch bounded pinned release bytes; never evaluate remote schemas."""
    lock = json.loads((ROOT / "oscal.lock.json").read_text(encoding="utf-8"))
    output = ROOT / "schemas"
    output.mkdir(exist_ok=True)
    for name, expected in lock["schemas"].items():
        path = output / f"oscal_{name}_schema.json"
        if path.is_file():
            content = path.read_bytes()
        elif check:
            raise ValueError("required vendored OSCAL schema missing")
        else:
            url = f"https://github.com/usnistgov/OSCAL/releases/download/v{lock['version']}/oscal_{name}_schema.json"
            with urllib.request.urlopen(url, timeout=30) as response:
                content = response.read(2 * 1024 * 1024 + 1)
        if (
            len(content) > 2 * 1024 * 1024
            or hashlib.sha256(content).hexdigest() != expected
        ):
            raise ValueError("OSCAL schema checksum mismatch; input was not trusted")
        if not check and not path.exists():
            with path.open("xb") as stream:
                stream.write(content)
    print(f"Six official OSCAL {lock['version']} schema digests verified")


def main() -> int:
    """Vendor only explicitly reviewed release schemas or perform a no-network verification."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    arguments = parser.parse_args()
    vendor(arguments.check)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
