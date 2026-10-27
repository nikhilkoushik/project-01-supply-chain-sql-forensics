
from datetime import datetime, timedelta

import pytest

from engine.policy_engine import evaluate_first_goods_receipt


@pytest.fixture
def procurement_rule():
    return {
        "id": "BP-GR-001",
        "domain": "bpi",
        "unit": "calendar_days",
        "scope": "STD_MATERIAL",
        "target": 12.0,
        "policy_version": "0.1",
        "approval_status": "simulated",
    }


def evaluate(rule, days, category="STD_MATERIAL"):
    start = datetime(2019, 1, 1, 9, 0)
    end = start + timedelta(days=days)

    return evaluate_first_goods_receipt(
        rule=rule,
        category=category,
        po_created_at=start.isoformat(),
        first_gr_at=end.isoformat(),
    )


def test_exactly_12_days_meets_target(procurement_rule):
    result = evaluate(procurement_rule, 12)
    assert result["decision"] == "meets_target"


def test_less_than_12_days_meets_target(procurement_rule):
    result = evaluate(procurement_rule, 11)
    assert result["decision"] == "meets_target"


def test_more_than_12_days_below_target(procurement_rule):
    result = evaluate(procurement_rule, 13)
    assert result["decision"] == "below_target"


def test_negative_duration_is_invalid(procurement_rule):
    result = evaluate(procurement_rule, -1)
    assert result["decision"] == "insufficient_data"


def test_missing_receipt_is_insufficient(procurement_rule):
    result = evaluate_first_goods_receipt(
        rule=procurement_rule,
        category="STD_MATERIAL",
        po_created_at="2019-01-01T09:00:00",
        first_gr_at=None,
    )
    assert result["decision"] == "insufficient_data"


def test_nonstandard_category_not_applicable(procurement_rule):
    result = evaluate(
        procurement_rule,
        5,
        category="SERVICE",
    )
    assert result["decision"] == "not_applicable"


def test_invalid_timestamp_is_insufficient(procurement_rule):
    result = evaluate_first_goods_receipt(
        rule=procurement_rule,
        category="STD_MATERIAL",
        po_created_at="invalid-date",
        first_gr_at="2019-01-10T09:00:00",
    )
    assert result["decision"] == "insufficient_data"


def test_policy_metadata_is_preserved(procurement_rule):
    result = evaluate(procurement_rule, 5)

    assert result["rule_id"] == "BP-GR-001"
    assert result["policy_version"] == "0.1"
    assert result["policy_status"] == "simulated"
