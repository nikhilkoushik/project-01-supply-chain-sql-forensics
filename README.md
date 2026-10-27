# Supply Chain SQL Forensics Engine

**PostgreSQL | Python | Process Mining | Supply Chain Analytics | Policy Governance**

## Overview

An end-to-end supply chain analytics and governance project investigating e-commerce delivery reliability and enterprise procurement operations.

The project combines PostgreSQL analytics, process-event analysis, query optimization, Python-based policy evaluation, automated testing, and restricted database access to turn historical supply-chain records into explainable business findings.

The objective is to demonstrate how data analysts and supply-chain teams can identify operational inefficiencies, prioritize investigations, and evaluate hypothetical service-level policies using reproducible analytical workflows.

## Business Problems

**E-commerce logistics — Olist**
- How reliable are customer delivery estimates?
- Which geographic regions experience the highest late-delivery rates?
- How can seller shipping handoff performance be measured?
- How do product characteristics relate to freight costs and delivery outcomes?

**Enterprise procurement — BPI Challenge 2019**
- How long do procurement processes take?
- Where do goods-receipt and invoice-processing delays occur?
- Which cases contain changes, cancellations, or repeated process activities?
- Which records should analysts prioritize for further investigation?

The datasets are analyzed independently and do not represent a single real company.

## Technologies

- **Database:** PostgreSQL, SQL, pgAdmin
- **Programming:** Python, Pandas
- **Database connectivity:** SQLAlchemy, psycopg
- **Testing:** pytest, Python unittest
- **Analysis:** KPI design, process mining, data-quality validation, SQL window functions, execution-plan analysis
- **Governance:** Versioned simulated policies, rule-based evaluations, evidence classification, restricted database access

## Datasets

### Olist Brazilian E-Commerce

Historical transactional data covering orders, sellers, customers, products, and deliveries.

**Key finding:** Approximately 93.23% of 96,470 qualifying delivered orders arrived by the estimated delivery date.

### BPI Challenge 2019

Enterprise purchase-to-pay event data containing:

- **251,734 procurement cases**
- **1,595,923 recorded events**

Historical process analysis identified a mean purchase-order-to-first-goods-receipt interval of approximately 15.48 days for the broader valid population and an average invoice-receipt-to-clearing interval of approximately 48.20 days.

## Key Analytical Findings

| Area | Finding |
|---|---|
| Olist delivery reliability | 93.23% on time across 96,470 eligible orders |
| Olist seller-order handoff proxy | 90.997% on time across 99,000 eligible seller-order pairs |
| Procurement investigations | 16,522 cases classified as high-priority by an exploratory rule-based scorecard |
| Standard procurement first receipt | 206,275 cases with valid first-receipt lead times |
| Simulated procurement 12-day standard | 112,824 within target; 93,451 above target |
| Procurement evidence gaps | 13,911 Standard cases without a recorded first goods receipt |

The seller handoff measure uses an order-level carrier timestamp as a proxy and should not be interpreted as verified individual seller compliance.

Missing goods-receipt records are treated as insufficient evidence rather than automatically counted as delays.

## Policy Evaluation Engine

A deterministic Python rules engine evaluates three illustrative operational policies:

| Policy | Simulated standard |
|---|---|
| OL-DEL-001 | At least 97% on-time customer delivery |
| OL-SHP-001 | At least 95% on-time seller-order handoff |
| BP-GR-001 | First goods receipt within 12 calendar days for mapped Standard material cases |

The engine supports:

- Policy identifiers, versions, and effective dates
- Domain-specific scope checking
- Decisions such as `meets_target`, `below_target`, `not_applicable`, and `insufficient_data`
- Historical what-if comparisons
- Explicit separation of source evidence and business-rule decisions

**Governance limitation:** These policies are simulated portfolio assumptions, not approved operational policies from Olist or the BPI dataset contributors. Their 2026 effective dates are not presented as historical obligations.

## SQL Query Optimization

A targeted PostgreSQL partial index improved one locally measured procurement query from **692.982 ms to 4.235 ms**, approximately a 164× observed execution-time difference.

This is a single local query-plan comparison, not a guaranteed production improvement or a repeated performance benchmark.

## Automated Testing and Security

The project includes 23 automated tests that passed in recent runs:

- 11 policy-engine unit tests
- 8 procurement boundary and invalid-input tests
- 4 PostgreSQL integration tests

Testing covers policy applicability, required evidence, threshold boundaries, database population reconciliation, and SQL/Python decision agreement for selected near-threshold cases.

A dedicated PostgreSQL account, `sc_policy_reader`, is used to run the policy assessment with restricted permissions. The application validates its database name and current database user.

The project does not store database passwords in its source code.

## Project Structure

| Folder | Purpose |
|---|---|
| `sql/` | Data-quality analysis, supply-chain KPIs, process investigations, optimization, and policy views |
| `python/` | Dataset exploration, procurement import, and policy database integration |
| `engine/` | Deterministic Python policy evaluator |
| `rules/` | Versioned simulated policy definitions |
| `policies/` | Business-policy assumptions and governance documentation |
| `tests/` | Unit, boundary, and database integration tests |
| `reports/` | Executive findings |
| `docs/` | Testing, security, and architecture documentation |

## Local Setup

Install Python dependencies from `requirements.txt` in a virtual environment.

The SQL analysis requires a locally configured PostgreSQL database named `supply_chain_forensics`, with imported Olist and BPI Challenge 2019 data.

The SQL view definitions are stored in `sql/`, with policy views in `sql/08_policy_kpi_views.sql`.

The policy database integration requires a `DATABASE_URL` environment variable pointing to an appropriately configured restricted PostgreSQL account.

Credentials must be supplied securely and must not be committed to Git.

**Run database-independent tests:**

```bash
python -m pytest tests/test_policy_engine.py tests/test_bpi_policy_boundaries.py -v
```

Database integration tests additionally require a running PostgreSQL instance with the imported data, expected schemas and views, and `DATABASE_URL` configured for `sc_policy_reader`.

## Data and Reproducibility Notes

Raw source datasets are excluded from GitHub because of their size. Users must obtain the datasets from the original providers and load them into PostgreSQL before running database-backed assessments.

The Olist and BPI Challenge 2019 datasets remain analytically separate. No cross-dataset relationships are asserted.

The risk prioritization scorecard is an exploratory investigation heuristic, not a validated predictive model.

## Future Development

This project forms the historical analytics and governance foundation for a larger supply-chain AI portfolio that will include demand forecasting, inventory simulation, event-stream processing, and an agentic command center.

Future agents will be expected to use approved deterministic tools, retrieve versioned policies, cite source evidence, and request human approval for consequential operational actions.
