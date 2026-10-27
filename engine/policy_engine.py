"""Pure-Python, read-only sample evaluator; no LLM or database connection required."""
from datetime import datetime, date
from pathlib import Path
import json

RULES_PATH = Path(__file__).resolve().parents[1] / "rules" / "policy_rules.json"


def load_rules(path=RULES_PATH):
    with open(path, encoding="utf-8") as file:
        return json.load(file)["rules"]


def get_rule(domain, rule_id, on_date, rules=None):
    rules = load_rules() if rules is None else rules
    date_value = date.fromisoformat(on_date)
    matches = [r for r in rules if r["domain"] == domain and r["id"] == rule_id
               and date.fromisoformat(r["effective_from"]) <= date_value
               and (r.get("effective_to") is None or date_value <= date.fromisoformat(r["effective_to"]))]
    if len(matches) != 1:
        raise ValueError("Expected exactly one applicable version of this domain-specific rule")
    return matches[0]


def evaluate_percentage(rule, numerator, denominator):
    if rule["unit"] != "percent":
        raise ValueError("Rule is not a percentage KPI")
    if not isinstance(numerator, int) or isinstance(numerator, bool) or not isinstance(denominator, int) or isinstance(denominator, bool):
        return {"decision": "insufficient_data", "reason": "Counts must be integers"}
    if denominator < rule.get("min_sample", 1) or numerator < 0 or numerator > denominator:
        return {"decision": "insufficient_data", "reason": "Missing or invalid KPI population"}
    observed = 100 * numerator / denominator
    passed = observed >= rule["target"] if rule["operator"] == ">=" else observed <= rule["target"]
    return {"decision": "meets_target" if passed else "below_target", "observed": round(observed, 4), "target": rule["target"], "gap_percentage_points": round(observed - rule["target"], 4), "rule_id": rule["id"], "policy_version": rule["policy_version"], "policy_status": rule["approval_status"]}


def evaluate_first_goods_receipt(rule, category, po_created_at, first_gr_at):
    if rule["domain"] != "bpi" or rule["unit"] != "calendar_days":
        raise ValueError("Incorrect domain or rule unit")
    if category is None:
        return {"decision": "insufficient_data", "reason": "Missing category"}
    if category != rule["scope"]:
        return {"decision": "not_applicable", "reason": "Category outside policy scope"}
    if not po_created_at or not first_gr_at:
        return {"decision": "insufficient_data", "reason": "Missing event timestamp"}
    try:
        start, end = datetime.fromisoformat(po_created_at), datetime.fromisoformat(first_gr_at)
        # Both timestamps must use compatible timezone conventions.
        elapsed = (end - start).total_seconds() / 86400
    except (ValueError, TypeError):
        return {"decision": "insufficient_data", "reason": "Invalid or incomparable timestamps"}
    if elapsed < 0:
        return {"decision": "insufficient_data", "reason": "Goods receipt predates purchase order"}
    decision = "meets_target" if elapsed <= rule["target"] else "below_target"
    return {"decision": decision, "elapsed_calendar_days": round(elapsed, 4), "target": rule["target"], "rule_id": rule["id"], "policy_version": rule["policy_version"], "policy_status": rule["approval_status"]}
