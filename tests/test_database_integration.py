
import os
from datetime import date

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

from engine.policy_engine import (
    get_rule,
    evaluate_percentage,
)


@pytest.fixture(scope="module")
def database_connection():

    database_url = os.environ.get("DATABASE_URL")

    if not database_url:
        pytest.skip(
            "Integration tests require DATABASE_URL "
            "for the restricted database account."
        )


    engine = create_engine(
        database_url,
        connect_args={"connect_timeout": 5},
    )

    try:
        with engine.connect() as connection:
            connection.exec_driver_sql(
                "SET TRANSACTION READ ONLY"
            )

            actual_database = connection.scalar(
                text("SELECT current_database()")
            )

            assert actual_database == "supply_chain_forensics"

            connected_user = connection.scalar(
                text("SELECT current_user")
            )

            assert connected_user == "sc_policy_reader"


            yield connection
    finally:
        engine.dispose()


def test_olist_delivery_policy_against_database(
    database_connection,
):
    result = database_connection.execute(
        text("""
            SELECT
                COUNT(*) AS eligible,
                COUNT(*) FILTER (
                    WHERE order_delivered_customer_date::date
                          <= order_estimated_delivery_date::date
                ) AS on_time
            FROM olist.orders
            WHERE order_status = 'delivered'
              AND order_delivered_customer_date IS NOT NULL
              AND order_estimated_delivery_date IS NOT NULL
        """)
    ).mappings().one()

    rule = get_rule(
        domain="olist",
        rule_id="OL-DEL-001",
        on_date=date.today().isoformat(),
    )

    assessment = evaluate_percentage(
        rule,
        int(result["on_time"]),
        int(result["eligible"]),
    )

    assert assessment["decision"] == "below_target"

    assert round(assessment["observed"], 2) == 93.23


def test_olist_seller_policy_against_database(
    database_connection,
):
    result = database_connection.execute(
        text("""
            SELECT
                eligible_seller_orders,
                on_time_seller_orders
            FROM olist.v_seller_order_policy_kpi
        """)
    ).mappings().one()

    rule = get_rule(
        domain="olist",
        rule_id="OL-SHP-001",
        on_date=date.today().isoformat(),
    )

    assessment = evaluate_percentage(
        rule,
        int(result["on_time_seller_orders"]),
        int(result["eligible_seller_orders"]),
    )

    assert assessment["decision"] == "below_target"

    assert round(assessment["observed"], 2) == 91.00


def test_bpi_population_reconciliation(
    database_connection,
):
    result = database_connection.execute(
        text("""
            SELECT
                COUNT(*) AS total,
                COUNT(*) FILTER (
                    WHERE evidence_status = 'valid'
                ) AS valid,
                COUNT(*) FILTER (
                    WHERE evidence_status <> 'valid'
                ) AS insufficient
            FROM bpi2019.v_standard_first_receipt_policy
        """)
    ).mappings().one()

    assert result["total"] == (
        result["valid"] + result["insufficient"]
    )

def test_bpi_sql_python_policy_consistency(database_connection):
    from engine.policy_engine import (
        get_rule,
        evaluate_first_goods_receipt,
    )

    from datetime import date

    rule = get_rule(
        domain="bpi",
        rule_id="BP-GR-001",
        on_date=date.today().isoformat(),
    )

    rows = database_connection.execute(
        text("""
            SELECT
                case_id,
                policy_category,
                po_created_at,
                first_gr_at,
                first_receipt_lead_days
            FROM bpi2019.v_standard_first_receipt_policy
            WHERE evidence_status = 'valid'
            ORDER BY ABS(first_receipt_lead_days - 12), case_id
            LIMIT 100
        """)
    ).mappings().all()

    assert len(rows) == 100

    for row in rows:
        python_result = evaluate_first_goods_receipt(
            rule=rule,
            category=row["policy_category"],
            po_created_at=row["po_created_at"].isoformat(),
            first_gr_at=row["first_gr_at"].isoformat(),
        )

        sql_decision = (
            "meets_target"
            if row["first_receipt_lead_days"] <= 12
            else "below_target"
        )

        assert python_result["decision"] == sql_decision, (
            f"SQL/Python disagreement for case {row['case_id']}"
        )
