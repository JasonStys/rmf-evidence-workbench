"""Offline assessment, OSCAL validation and evidence-ledger CLI. Created by Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: main — line 31
# variable: parser — line 33
# variable: subcommands — line 36
# variable: assessment — line 37
# variable: model_validation — line 43
# variable: new_ledger — line 45
# variable: verification — line 47
# variable: history_command — line 50
# variable: arguments — line 53
# variable: bundle — line 56
# variable: result — line 56
# variable: receipt — line 58
# END CODE MAP

from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path

from rmf.assessment import assess
from rmf.contracts import STATES
from rmf.ledger import append, create, history, verify
from rmf.oscal import validate_directory
from rmf.report import publish


def main() -> int:
    """Parse explicit local commands, never execute uploaded code, and suppress untrusted/private exception contents."""
    parser = argparse.ArgumentParser(
        description="RMF Evidence Workbench — Jason Stys — educational only"
    )
    subcommands = parser.add_subparsers(dest="command", required=True)
    assessment = subcommands.add_parser("assess")
    assessment.add_argument("workspace", type=Path)
    assessment.add_argument("--as-of", required=True)
    assessment.add_argument("--output", type=Path, required=True)
    assessment.add_argument("--ledger", type=Path)
    assessment.add_argument("--expected-tip")
    model_validation = subcommands.add_parser("validate-oscal")
    model_validation.add_argument("directory", type=Path)
    new_ledger = subcommands.add_parser("init-ledger")
    new_ledger.add_argument("path", type=Path)
    verification = subcommands.add_parser("verify-ledger")
    verification.add_argument("path", type=Path)
    verification.add_argument("--expected-tip")
    history_command = subcommands.add_parser("history")
    history_command.add_argument("path", type=Path)
    history_command.add_argument("--state", choices=sorted(STATES))
    arguments = parser.parse_args()
    try:
        if arguments.command == "assess":
            bundle, result = assess(arguments.workspace, arguments.as_of)
            publish(bundle, result, arguments.output)
            receipt = (
                append(arguments.ledger, result, arguments.expected_tip)
                if arguments.ledger
                else None
            )
            print(
                json.dumps(
                    {
                        "summary": result["summary"],
                        "authorization": result["authorization"],
                        "ledger_receipt": receipt,
                    },
                    sort_keys=True,
                )
            )
        elif arguments.command == "validate-oscal":
            validate_directory(arguments.directory)
            print("Six OSCAL schemas and supported local references validated")
        elif arguments.command == "init-ledger":
            create(arguments.path)
            print("New local ledger created; save future chain tips independently")
        elif arguments.command == "verify-ledger":
            print(
                json.dumps(
                    verify(arguments.path, arguments.expected_tip), sort_keys=True
                )
            )
        else:
            print(json.dumps(history(arguments.path, arguments.state), sort_keys=True))
    except (OSError, ValueError, UnicodeError, RecursionError, sqlite3.Error):
        print(
            "Operation rejected; no existing output was overwritten. Check local contracts in docs/runbook.md."
        )
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
