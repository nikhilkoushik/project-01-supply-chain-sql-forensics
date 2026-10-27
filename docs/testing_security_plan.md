# Testing, Environment and Security Plan — Projects 1–5

**Version:** 0.1; portfolio checklist, not evidence that controls have been deployed.

## Test levels and project stages
- **Project 1 (SQL forensics):** deterministic KPI and rule tests, boundary dates, missing timestamps, seller-order deduplication, procurement classification, SQL read-only checks and dataset exclusion verification.
- **Project 2 (forecasting):** train/test leakage checks, time-series splits, reproducible seeds, drift and forecast-error monitoring; secure model artifact loading.
- **Project 3 (inventory simulation):** conservation/constraints invariants, sensitivity tests, simulated disruptions, solver tolerance and safe fallback.
- **Project 4 (streaming logistics):** schema validation, duplicate/idempotent processing, late events, replay, backpressure and message-broker permissions.
- **Project 5 (multi-agent):** policy retrieval/version correctness, prompt-injection tests, tool allowlists, cross-tenant isolation, authorization, human approvals, model regression and auditability.

## Repeat for every project
1. **Unit tests:** fixed inputs and expected outputs, boundary values and failure cases.
2. **Integration/environment tests:** installation in fresh virtual environment; pinned/locked dependencies; database connectivity with test database; reproducible commands and platform notes.
3. **Security tests:** dependency and secret scans, least-privilege account validation, defensive input validation, SQL parameterization, authorization checks and reviewed logs.
4. **Acceptance:** README with intended scope, limits and what was tested; only claim passing results observed in the actual environment.

## Adversarial testing (only within authorized local/staging systems)
- Try fake or tampered policy versions; overlapping effective dates; malicious instructions inserted in seller comments; missing data; unauthorized domain crossover; overbroad query parameters; malformed timestamps; duplicate and reordered events; secrets in environment/logs.
- Expected behavior: reject or quarantine unauthorized/ambiguous input, return `insufficient_data` where appropriate, do not reveal secrets, do not run arbitrary shell or database writes, and preserve a minimal audit trail.
- Test your **own** test harness or an explicitly authorized staging deployment. A portfolio script does not establish the security of a production host. Retesting is required after changes.

## Suggested commands (once files are placed in project root)
```bash
python3 -m unittest discover -s tests -v
python3 -m compileall -q engine tests
python3 -m pip check
```
`pip check` examines the **active Python environment** and requires dependencies to be installed there. These commands do not substitute for SQL integration or penetration testing.

## Before GitHub publishing
Check `.gitignore` against the *actual* dataset directory names; verify tracked files using `git status` and `git ls-files`; scan for secrets; remove local datasets, private documents, `.env` and `.venv`. If a secret was ever committed, rotate it—adding `.gitignore` does not remove it from Git history.
