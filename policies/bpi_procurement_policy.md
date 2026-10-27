# BPI-2019-Inspired Procurement Operating Policy

**Policy ID:** BP-POL-001 | **Version:** 0.1 | **Status:** SIMULATED / NOT APPROVED | **Effective for tests:** 2026-01-01 | **Owner (simulated):** Procurement Operations

## Scope and separation
This policy belongs to a **fictional procurement organization** inspired by BPI Challenge 2019 data. It is separate from the Olist-inspired e-commerce operation. Do not call the standards rules of the actual BPI data contributor.

## Proposed, conditional rules
| Rule ID | Proposal | Required evidence | Outcome if missing |
|---|---|---|---|
| BP-GR-001 | Standard material category `STD_MATERIAL`, first goods receipt within **12 calendar days** of purchase-order-item creation | Category identifier; correct PO creation timestamp; first subsequent goods receipt timestamp; approved exceptions | `insufficient_data`, not breach |
| BP-CHG-001 | Quantity/price changes require review and authorization under fictional approval process | Change event, linked approval record, applicable workflow | `requires_review` if approval record unavailable |
| BP-CAN-001 | Receipt and invoice cancellations require a traceable reason and review | Cancellation event and reason/approval | `requires_review`, not automatically suspicious |
| BP-DAT-001 | Missing or out-of-order timestamps cannot establish lead-time compliance | Valid time-ordered pair | `insufficient_data` |

## Definitions and evaluation
- `PO-to-first-GR`: elapsed **calendar** days from PO item creation to first valid subsequent goods receipt for the *same procurement case*. This indicates first receipt, possibly partial fulfillment—not full delivery.
- Apply `BP-GR-001` **only** when the record is unambiguously classified `STD_MATERIAL` and the applicable policy version is in force. For service, custom or unknown categories, report `not_applicable` or `insufficient_data` rather than applying the 12-day target.
- A case's first invoice receipt to next clearing event is an exploratory process metric; it **does not by itself** prove invoice-specific payment term compliance.
- Flags for case duration greater than 90 days, modifications, and cancellations from prior analyses remain **descriptive investigation indicators**, not approved policy violations.
- Supplier delivery obligations would ordinarily depend on supplier contracts, purchasing conditions, working calendars, holidays and amendments. These are not established by the event log alone.

## Escalation
Procurement analyst checks the event trail and applicability. Category manager reviews valid deviations. Compliance/finance reviews changes or cancellations where a corresponding governance obligation is documented. Automatic financial or supplier sanctions are prohibited.

## Historical illustration (not a compliant-cohort comparison)
Earlier analysis reported a 15.48-day overall mean PO-to-first-GR across 234,229 qualifying cases. **Do not** compare that aggregate directly with the 12-day `STD_MATERIAL` policy: the subset and policy eligibility are not established.

## Approval, exception handling and versions
Any target is provisional. Require named owner, approval, effective interval, exception record and audit trail before production. Store historic versions unchanged for reproducible backtesting.
