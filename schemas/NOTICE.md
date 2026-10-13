# Original NIST OSCAL schemas

The six `oscal_*_schema.json` files are exact unmodified JSON schemas from the [NIST OSCAL 1.2.3 release](https://github.com/usnistgov/OSCAL/releases/tag/v1.2.3). The National Institute of Standards and Technology is the source; `oscal.lock.json` pins each official asset's SHA-256. `scripts/vendor_oscal.py --check` verifies exact bytes without network access.

[NIST-NOTICE.md](NIST-NOTICE.md) preserves the complete original notice and public-domain/CC0 terms. Our MIT license applies to authored code, not these vendor files. No NIST endorsement, certification or authorization is implied. The illustrative selected-control catalog and predicates are ours; they are not the complete NIST control catalog/baselines.

Original schema patterns include Unicode property escapes. Python uses a tested Unicode-aware pattern extension, and native Ajv independently validates the same originals. Schema bytes are not rewritten or relaxed. JSON schemas validate structure/formats; the app adds explicit consistency checks for its supported chain, not every normative Metaschema constraint.
