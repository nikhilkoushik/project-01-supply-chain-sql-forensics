
"""
Lesson 45B: PostgreSQL -> Olist Policy Evaluation

Read-only retrospective policy assessment.
No data is modified and no AI model is involved.
"""

import os
import sys
from pathlib import Path
from datetime import date

from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

# Make the project root importable.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))


from engine.policy_engine import (
    get_rule,
    evaluate_percentage,
    evaluate_first_goods_receipt,
)



def main():
    # Use DATABASE_URL if configured; otherwise try
    # the local PostgreSQL connection used in this project.

    database_url = os.environ.get("DATABASE_URL")

    if not database_url:
        raise RuntimeError(
            "DATABASE_URL is not configured. "
            "Set the read-only database connection first."
        )


    engine = create_engine(database_url, connect_args={"connect_timeout": 5})

    query = text("""
        SELECT
            COUNT(*) AS eligible_orders,
            COUNT(*) FILTER (
                WHERE order_delivered_customer_date::date
                      <= order_estimated_delivery_date::date
            ) AS on_time_orders,
            MIN(order_purchase_timestamp)::date AS first_purchase_date,
            MAX(order_purchase_timestamp)::date AS last_purchase_date
        FROM olist.orders
        WHERE order_status = 'delivered'
          AND order_delivered_customer_date IS NOT NULL
          AND order_estimated_delivery_date IS NOT NULL
    """)

    seller_query = text("""
        SELECT
            eligible_seller_orders,
            on_time_seller_orders,
            late_seller_orders
        FROM olist.v_seller_order_policy_kpi
    """)


    bpi_query = text("""
        SELECT
            case_id,
            policy_category,
            po_created_at,
            first_gr_at
        FROM bpi2019.v_standard_first_receipt_policy
        WHERE evidence_status = 'valid'
        ORDER BY case_id
        LIMIT 3
    """)

    bpi_summary_query = text("""
        SELECT
            COUNT(*) AS total_cases,

            COUNT(*) FILTER (
                WHERE evidence_status = 'valid'
            ) AS valid_cases,

            COUNT(*) FILTER (
                WHERE evidence_status = 'valid'
                  AND first_receipt_lead_days <= 12
            ) AS within_target,

            COUNT(*) FILTER (
                WHERE evidence_status = 'valid'
                  AND first_receipt_lead_days > 12
            ) AS above_target,

            COUNT(*) FILTER (
                WHERE evidence_status <> 'valid'
            ) AS insufficient_evidence

        FROM bpi2019.v_standard_first_receipt_policy
    """)




    try:
        with engine.connect() as connection:
            connection.exec_driver_sql("SET TRANSACTION READ ONLY")

            if connection.scalar(text("SELECT current_database()")) != "supply_chain_forensics":
                raise ValueError("Connected to the wrong database")

            connected_user = connection.scalar(
                text("SELECT current_user")
            )

            if connected_user != "sc_policy_reader":
                raise RuntimeError(
                    "Security check failed: "
                    f"Connected as {connected_user}, "
                    "expected sc_policy_reader"
                )

            print("Database security identity:", connected_user)


            result = connection.execute(query).mappings().one()

            seller_result = connection.execute(seller_query).mappings().one()

            bpi_results = connection.execute(bpi_query).mappings().all()

            bpi_summary = connection.execute(bpi_summary_query).mappings().one()


    finally:
        engine.dispose()

    eligible = int(result["eligible_orders"])
    on_time = int(result["on_time_orders"])

    # This selects the currently defined SIMULATED rule.
    # It does not establish historical policy applicability.
    rule = get_rule(
        domain="olist",
        rule_id="OL-DEL-001",
        on_date=date.today().isoformat(),
    )

    assessment = evaluate_percentage(
        rule=rule,
        numerator=on_time,
        denominator=eligible,
    )

    print("\n=== OLIST POLICY ASSESSMENT ===")
    print("Database: supply_chain_forensics")
    print("Eligible orders:", eligible)
    print("On-time orders:", on_time)
    print("First purchase date:", result["first_purchase_date"])
    print("Last purchase date:", result["last_purchase_date"])

    print("\n=== SIMULATED POLICY ===")
    print("Policy ID:", rule["id"])
    print("Policy version:", rule["policy_version"])
    print("Approval status:", rule["approval_status"])
    print("Target:", rule["target"], "%")

    print("\n=== EVALUATION RESULT ===")
    print("Decision:", assessment["decision"])
    print("Observed performance:", assessment.get("observed"), "%")
    print("Gap in percentage points:", assessment.get("gap_percentage_points"))

    print("\nIMPORTANT:")
    print("Retrospective what-if comparison only.")
    print("This is not a finding of historical policy noncompliance.")


    # Evaluate simulated seller handoff policy
    seller_rule = get_rule(
        domain="olist",
        rule_id="OL-SHP-001",
        on_date=date.today().isoformat(),
    )

    seller_assessment = evaluate_percentage(
        rule=seller_rule,
        numerator=int(seller_result["on_time_seller_orders"]),
        denominator=int(seller_result["eligible_seller_orders"]),
    )

    print("\n=== SELLER HANDOFF POLICY ASSESSMENT ===")
    print("Eligible seller-order pairs:",
          seller_result["eligible_seller_orders"])
    print("On-time seller-order pairs:",
          seller_result["on_time_seller_orders"])
    print("Late seller-order pairs:",
          seller_result["late_seller_orders"])

    print("\n=== SIMULATED SELLER POLICY ===")
    print("Policy ID:", seller_rule["id"])
    print("Policy version:", seller_rule["policy_version"])
    print("Approval status:", seller_rule["approval_status"])
    print("Target:", seller_rule["target"], "%")

    print("\n=== SELLER EVALUATION RESULT ===")
    print("Decision:", seller_assessment["decision"])
    print("Observed performance:",
          seller_assessment.get("observed"), "%")
    print("Gap in percentage points:",
          seller_assessment.get("gap_percentage_points"))

    print("\nIMPORTANT:")
    print("Retrospective what-if comparison using an")
    print("order-level carrier handoff timestamp as a proxy.")
    print("This does not establish individual seller noncompliance.")

    bpi_rule = get_rule(
        domain="bpi",
        rule_id="BP-GR-001",
        on_date=date.today().isoformat(),
    )

    print("\n=== BPI PROCUREMENT POLICY ASSESSMENT ===")
    print("Policy:", bpi_rule["id"])
    print("Simulated target:", bpi_rule["target"], "calendar days")

    for row in bpi_results:
        evaluation = evaluate_first_goods_receipt(
            rule=bpi_rule,
            category=row["policy_category"],
            po_created_at=row["po_created_at"].isoformat(),
            first_gr_at=row["first_gr_at"].isoformat(),
        )

        print("\nCase:", row["case_id"])
        print("Decision:", evaluation["decision"])
        print("First receipt lead time:",
              evaluation.get("elapsed_calendar_days"), "days")

    print("\nIMPORTANT:")
    print("STD_MATERIAL is a simulated category mapping.")
    print("Historical what-if evaluation only.")
    print("These findings are not actual policy violations.")

    print("\n=== FULL BPI PROCUREMENT ASSESSMENT ===")

    total = int(bpi_summary["total_cases"])
    valid = int(bpi_summary["valid_cases"])
    within = int(bpi_summary["within_target"])
    above = int(bpi_summary["above_target"])
    insufficient = int(bpi_summary["insufficient_evidence"])

    assert total == valid + insufficient, (
        "BPI population reconciliation failed"
    )
    assert valid == within + above, (
        "BPI policy classification reconciliation failed"
    )

    print("Total Standard cases:", total)
    print("Valid cases:", valid)
    print("Within simulated target:", within)
    print("Above simulated target:", above)
    print("Insufficient evidence:", insufficient)

    if valid > 0:
        print(
            "Within-target percentage:",
            round(100 * within / valid, 2),
            "%"
        )
        print(
            "Above-target percentage:",
            round(100 * above / valid, 2),
            "%"
        )

    print("\nAssessment type: Historical what-if simulation")
    print("Policy approval status:", bpi_rule["approval_status"])

if __name__ == "__main__":
    main()
