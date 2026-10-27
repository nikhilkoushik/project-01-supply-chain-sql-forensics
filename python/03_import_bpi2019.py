
from pathlib import Path
from datetime import datetime
from decimal import Decimal
import gzip
import json
import xml.etree.ElementTree as ET

from sqlalchemy import create_engine, text


# ==========================================
# STEP 1: LOCATE THE ORIGINAL XES FILE
# ==========================================

project_path = Path(__file__).resolve().parent.parent

xes_file = (
    project_path
    / "data : bpi2019"
    / "BPI_Challenge_2019.xes"
)

if not xes_file.exists():
    raise FileNotFoundError(xes_file)

print("XES file found:", xes_file.name, flush=True)


# ==========================================
# STEP 2: CONNECT TO POSTGRESQL
# ==========================================

engine = create_engine(
    "postgresql+psycopg://nikhilkoushik@localhost:5432/supply_chain_forensics"
)

print("Database connection configured.", flush=True)


# ==========================================
# STEP 3: PREPARE SQL INSERT STATEMENTS
# ==========================================

insert_case = text("""
INSERT INTO bpi2019.procurement_cases (
    case_id,
    purchasing_document,
    item_number,
    vendor_id,
    company,
    document_type,
    item_type,
    item_category,
    spend_area,
    sub_spend_area,
    raw_attributes
)
VALUES (
    :case_id,
    :purchasing_document,
    :item_number,
    :vendor_id,
    :company,
    :document_type,
    :item_type,
    :item_category,
    :spend_area,
    :sub_spend_area,
    CAST(:raw_attributes AS JSONB)
)
""")

insert_event = text("""
INSERT INTO bpi2019.procurement_events (
    case_id,
    event_position,
    activity,
    event_timestamp,
    resource,
    event_user,
    cumulative_net_worth_eur,
    raw_attributes
)
VALUES (
    :case_id,
    :event_position,
    :activity,
    :event_timestamp,
    :resource,
    :event_user,
    :cumulative_net_worth_eur,
    CAST(:raw_attributes AS JSONB)
)
""")


# ==========================================
# STEP 4: HELPER FUNCTIONS
# ==========================================

def local_name(tag):
    return tag.split("}")[-1]


def get_attributes(element):
    attributes = {}

    for child in element:
        if "key" in child.attrib:
            attributes[child.attrib["key"]] = (
                child.attrib.get("value")
            )

    return attributes


def parse_timestamp(value):
    if not value:
        return None

    return datetime.fromisoformat(
        value.replace("Z", "+00:00")
    )


# ==========================================
# STEP 5: PREPARE BATCH STORAGE
# ==========================================

case_batch = []
event_batch = []

total_cases = 0
total_events = 0

BATCH_SIZE = 200


def save_batch():

    if not case_batch:
        return

    with engine.begin() as connection:

        connection.execute(
            insert_case,
            case_batch
        )

        if event_batch:
            connection.execute(
                insert_event,
                event_batch
            )

    case_batch.clear()
    event_batch.clear()


# ==========================================
# STEP 6: CHECK DATABASE IS EMPTY
# ==========================================

with engine.connect() as connection:

    existing_cases = connection.execute(
        text("""
            SELECT COUNT(*)
            FROM bpi2019.procurement_cases
        """)
    ).scalar_one()

    existing_events = connection.execute(
        text("""
            SELECT COUNT(*)
            FROM bpi2019.procurement_events
        """)
    ).scalar_one()

if existing_cases > 0 or existing_events > 0:
    raise RuntimeError(
        "The procurement tables already contain data. "
        "Stop and inspect them before importing again."
    )

print("Database tables are empty. Starting import...", flush=True)


# ==========================================
# STEP 7: READ THE XES EVENT LOG
# ==========================================

open_file = (
    gzip.open
    if xes_file.name.lower().endswith(".gz")
    else open
)

with open_file(xes_file, "rb") as source:

    context = ET.iterparse(
        source,
        events=("start", "end")
    )

    _, root = next(context)

    for action, element in context:

        # Only process complete traces
        if action != "end":
            continue

        if local_name(element.tag) != "trace":
            continue

        # Read procurement case attributes
        case_data = get_attributes(element)

        case_id = case_data["concept:name"]

        case_batch.append({
            "case_id": case_id,
            "purchasing_document": case_data.get(
                "Purchasing Document"
            ),
            "item_number": case_data.get("Item"),
            "vendor_id": case_data.get("Vendor"),
            "company": case_data.get("Company"),
            "document_type": case_data.get(
                "Document Type"
            ),
            "item_type": case_data.get("Item Type"),
            "item_category": case_data.get(
                "Item Category"
            ),
            "spend_area": case_data.get(
                "Spend area text"
            ),
            "sub_spend_area": case_data.get(
                "Sub spend area text"
            ),
            "raw_attributes": json.dumps(case_data)
        })

        total_cases += 1

        # Read all events belonging to this case
        event_position = 0

        for child in element:

            if local_name(child.tag) != "event":
                continue

            event_position += 1

            event_data = get_attributes(child)

            amount = event_data.get(
                "Cumulative net worth (EUR)"
            )

            event_batch.append({
                "case_id": case_id,
                "event_position": event_position,
                "activity": event_data.get(
                    "concept:name"
                ),
                "event_timestamp": parse_timestamp(
                    event_data.get("time:timestamp")
                ),
                "resource": event_data.get(
                    "org:resource"
                ),
                "event_user": event_data.get(
                    "User"
                ),
                "cumulative_net_worth_eur": (
                    Decimal(amount)
                    if amount not in (None, "")
                    else None
                ),
                "raw_attributes": json.dumps(event_data)
            })

            total_events += 1

        # Save every 200 cases
        if len(case_batch) >= BATCH_SIZE:

            save_batch()

            if total_cases % 1000 == 0:
                print(
                    f"Imported {total_cases:,} cases "
                    f"and {total_events:,} events",
                    flush=True
                )

        # Clear XML only after the full trace
        # has been processed
        root.clear()


# ==========================================
# STEP 8: SAVE REMAINING RECORDS
# ==========================================

save_batch()

print("\nIMPORT COMPLETED", flush=True)
print("Total cases:", total_cases)
print("Total events:", total_events)
