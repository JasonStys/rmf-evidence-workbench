#!/usr/bin/env bash
# Cross-platform strict checks, actual schema engines and local evidence verification. Created by Jason Stys.
# No shell eval, downloaded artifacts, account changes or external evidence collection.
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# END CODE MAP
set -euo pipefail
python -m ruff check .
python -m ruff format --check .
python -m mypy
npm test
python -m pytest --cov --cov-report=term-missing --tb=short
python scripts/vendor_oscal.py --check
python scripts/examples.py --check
python scripts/code_map.py --check
npm run maps:check
python scripts/file_guide.py --check
python scripts/validate_repo.py
python scripts/benchmark.py
