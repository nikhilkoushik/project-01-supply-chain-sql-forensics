# Olist-Inspired E-commerce Operating Policy

**Policy ID:** OL-POL-001 | **Version:** 0.1 | **Status:** SIMULATED / NOT APPROVED | **Effective for tests:** 2026-01-01 | **Owner (simulated):** E-commerce Operations

## Scope and integrity
This fictional policy is a portfolio exercise, **not a policy of Olist or its sellers**. Apply it only to an illustrative e-commerce organization, not to the real historical Olist business. Do not infer contract breaches, fault, or legal compliance from dataset patterns.

## Proposed performance rules
| Rule ID | Proposed rule | Scope | Evaluation | Important limitation |
|---|---|---|---|---|
| OL-DEL-001 | At least 97% of qualifying delivered orders arrive on/before promised date | Portfolio-wide monthly delivered orders with non-null actual and estimated dates | `on_time / qualified * 100 >= 97` | A *performance target*, not a contractual seller breach. |
| OL-SHP-001 | At least 95% of eligible seller-order handoffs occur on/before item-specific shipping deadline | Seller-order pairs with recorded handoff and deadline | `on_time_handoffs / qualified * 100 >= 95` | Distinct seller-order unit; item duplicates must not inflate count. |
| OL-DAT-001 | Require actual delivery and estimated delivery dates for delivery assessment | Delivered orders | Missing data => `insufficient_data` | Never classify missing timestamp as on-time or late. |
| OL-INV-001 | Investigate any monthly shortfall, prioritizing high-volume and repeated exceptions | Monthly performance review | Open review ticket, verify underlying events and cohort | Do not assert carrier or seller fault without evidence. |

## KPI specification
- Qualifying on-time delivery population: delivered orders having both actual and estimated delivery timestamps. Define comparison consistently using timestamps (`actual <= estimated`) and document time-zone and date-only normalization choices.
- Monthly cohort is order's actual delivery month for this illustrative standard, not purchase month. Record and consistently apply the cohort definition.
- Olist shipping deadline is a dataset field. The policy **does not assume** that sellers have a universal two-business-day contract.
- Seller handoff metrics must use a clearly documented seller-order grain and deduplication strategy. Item-level historical rates must not be compared directly to seller-order targets.

## Exceptions, ownership and escalation
- Exceptions may include revised promises, approved holds, disruptions, cancellations and missing data. None may be silently inferred from historical records.
- Operations analyst validates the calculation; seller operations reviews seller-specific concerns; operations lead signs off on corrective actions.
- Assess aggregated performance as `meets_target`, `below_target`, or `insufficient_data`; log the rule ID, version, dates, SQL query reference, row counts and exception evidence.
- A below-target result creates a recommendation for investigation; it does **not** authorize punitive actions, payment freezes, or automatic seller suspension.

## Historical illustration (not a production evaluation)
Earlier portfolio analysis reported 89,936 on-time of 96,470 qualifying delivered orders (~93.23%). Against the **simulated** 97% target, this is ~3.77 percentage points below target. Verify SQL definitions, cohort selection and source extracts before presenting as independently reproduced.

## Policy lifecycle
Proposed targets require SME review, feasibility analysis, approval and controlled version updates before real deployment. Prior versions remain available for historical evaluations.
