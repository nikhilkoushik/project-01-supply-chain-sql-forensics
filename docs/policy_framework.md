# Lesson 45A — Policy-Aware Supply Chain Intelligence Starter

This self-contained **add-on** belongs inside `PROJECT-01-SQL-FORENSICS/`. It does not overwrite existing datasets, SQL scripts, reports or requirements. Everything here is a **simulated company design**, not an actual Olist/BPI organizational policy or a security certification.

## Contents
- `policies/olist_operating_policy.md` — e-commerce targets, definitions, evidence and exceptions.
- `policies/bpi_procurement_policy.md` — procurement category-specific rules and caution about event logs.
- `policies/ai_decision_governance.md` — retrieval, authorization, evidence and human approval rules.
- `rules/policy_rules.json` — example machine-readable rules.
- `engine/policy_engine.py` — deterministic sample evaluator.
- `tests/test_policy_engine.py` — unit tests and fail-closed scenarios.
- `docs/testing_security_plan.md` — shared security/testing roadmap for Projects 1–5.

## Install into your existing VS Code project
Extract this package. Copy the folders `policies`, `rules`, `engine` and `tests` into the project root; copy `docs/testing_security_plan.md` into a new `docs` directory. Keep your original `README.md` unchanged, and optionally link to these files from it. Do not replace an existing folder without merging contents first.

From the VS Code terminal at `PROJECT-01-SQL-FORENSICS` run:

```bash
python3 -m unittest discover -s tests -v
```

Expected for **this isolated starter**: 11 unit tests. Tests are independent of PostgreSQL and external data. To confirm only the isolated starter without merging, run from this extracted folder.

## Integration to do later (not included)
Connect these rules to verified SQL KPI views; qualify BPI categories from real available fields; map relevant policy effective dates to operational event periods; add proper tests for SQL, database permissions, secrets, API authorization, prompt injection and deployment; review policy targets with domain experts. The 2026 effective dates here are for demonstration and **must not be represented as active rules governing the historical datasets**.

## Decision categories
`meets_target`, `below_target`, `insufficient_data`, `not_applicable`; other review workflow labels described in the policy documents are not yet implemented.
