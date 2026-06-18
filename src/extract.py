import json
import pandas as pd
import xml.etree.ElementTree as ET
from config import DATA_DIR, log


def extract_customers():
    log.info("Extracting customers...")
    df = pd.read_csv(DATA_DIR / "customers.csv")
    log.info(f"Extracted {len(df)} customers")
    return df


def extract_orders():
    log.info("Extracting orders...")
    with open(DATA_DIR / "orders.json", encoding="utf-8") as f:
        df = pd.DataFrame(json.load(f))
    log.info(f"Extracted {len(df)} orders")
    return df


def extract_products():
    log.info("Extracting products...")
    df = pd.read_excel(DATA_DIR / "products.xlsx")
    log.info(f"Extracted {len(df)} products")
    return df


def extract_payments():
    log.info("Extracting payments...")
    df = pd.read_csv(DATA_DIR / "payments.csv", sep="^")
    log.info(f"Extracted {len(df)} payments")
    return df


def extract_events():
    log.info("Extracting events...")
    tree = ET.parse(DATA_DIR / "events.xml")
    root = tree.getroot()
    data = []

    for record in root:
        row = {}
        row.update(record.attrib)
        for child in record:
            row[child.tag] = child.text
        data.append(row)

    df = pd.DataFrame(data)
    log.info(f"Extracted {len(df)} events")
    return df


def extract_all():
    return {
        "customers": extract_customers(),
        "orders": extract_orders(),
        "products": extract_products(),
        "payments": extract_payments(),
        "events": extract_events(),
    }
