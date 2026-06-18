import pandas as pd
import numpy as np
from config import log, log_dq_error
import re


def is_valid_email(email):
    if pd.isna(email):
        return False
    email_str = str(email).strip()
    pattern = r"^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email_str))


def normalize_phone(phone):
    if pd.isna(phone):
        return None
    digits = re.sub(r"\D", "", str(phone))
    if len(digits) == 11 and digits[0] in ("7", "8"):
        return "+7" + digits[1:]
    if len(digits) == 10:
        return "+7" + digits
    return None


def transform_customers(df, errors):
    log.info("Transforming customers...")
    df = df.copy()
    df["full_name"] = df["full_name"].astype("string").str.strip()
    df["email"] = df["email"].astype("string").str.strip()
    df["city"] = df["city"].astype("string").str.strip()

    duplicates = df[df.duplicated("email", keep="first")]
    for _, row in duplicates.iterrows():
        log_dq_error(
            errors, "customers", row["customer_id"], "DUPLICATE_EMAIL", row["email"]
        )
    df = df.drop_duplicates("email", keep="first")

    df["phone"] = df["phone"].apply(normalize_phone)

    invalid_email = df["email"].apply(is_valid_email) == False
    for _, row in df[invalid_email].iterrows():
        log_dq_error(
            errors, "customers", row["customer_id"], "INVALID_EMAIL", row["email"]
        )
    df.loc[invalid_email, "email"] = np.nan

    df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")
    for _, row in df[df["created_at"].isna()].iterrows():
        log_dq_error(
            errors,
            "customers",
            row["customer_id"],
            "INVALID_CREATED_AT",
            "invalid created_at",
        )

    log.info(f"Transformed {len(df)} customers")
    return df


def transform_orders(df, errors):
    log.info("Transforming orders...")
    df = df.copy()

    df["customer_id"] = pd.to_numeric(df["customer_id"], errors="coerce")
    df["product_id"] = pd.to_numeric(df["product_id"], errors="coerce")

    duplicates = df[df.duplicated("order_id", keep="first")]
    for _, row in duplicates.iterrows():
        log_dq_error(
            errors, "orders", row["order_id"], "DUPLICATE_ORDER", "duplicate order_id"
        )
    df = df.drop_duplicates("order_id", keep="first")

    for _, row in df[df["customer_id"].isna()].iterrows():
        log_dq_error(
            errors,
            "orders",
            row["order_id"],
            "MISSING_CUSTOMER_ID",
            "customer_id is null",
        )

    df["order_timestamp"] = pd.to_datetime(df["order_timestamp"], errors="coerce")
    for _, row in df[df["order_timestamp"].isna()].iterrows():
        log_dq_error(
            errors,
            "orders",
            row["order_id"],
            "INVALID_ORDER_TIMESTAMP",
            "invalid order_timestamp",
        )

    log.info(f"Transformed {len(df)} orders")
    return df


def transform_products(df, errors):
    log.info("Transforming products...")
    df = df.copy()

    df["product_name"] = df["product_name"].astype(str).str.strip()

    duplicates = df[df.duplicated("product_id", keep="first")]
    for _, row in duplicates.iterrows():
        log_dq_error(
            errors,
            "products",
            row["product_id"],
            "DUPLICATE_PRODUCT",
            "duplicate product_id",
        )
    df = df.drop_duplicates("product_id", keep="first")

    median_price = df["price"].median()
    for _, row in df[df["price"].isna()].iterrows():
        log_dq_error(
            errors, "products", row["product_id"], "MISSING_PRICE", "price is missing"
        )
    df["price"] = df["price"].fillna(median_price)

    log.info(f"Transformed {len(df)} products")
    return df


def transform_payments(df, errors):
    log.info("Transforming payments...")
    df = df.copy()

    duplicates = df[df.duplicated("payment_id", keep="first")]
    for _, row in duplicates.iterrows():
        log_dq_error(
            errors,
            "payments",
            row["payment_id"],
            "DUPLICATE_PAYMENT",
            "duplicate payment_id",
        )
    df = df.drop_duplicates("payment_id", keep="first")

    for _, row in df[df["payment_method"].isna()].iterrows():
        log_dq_error(
            errors,
            "payments",
            row["payment_id"],
            "MISSING_PAYMENT_METHOD",
            "payment_method is null",
        )
    df["payment_method"] = df["payment_method"].fillna("unknown")

    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    for _, row in df[df["amount"].isna()].iterrows():
        log_dq_error(
            errors,
            "payments",
            row["payment_id"],
            "INVALID_AMOUNT",
            "amount is not numeric",
        )
    median_amount = df["amount"].median()
    df["amount"] = df["amount"].fillna(median_amount)

    df["payment_timestamp"] = pd.to_datetime(df["payment_timestamp"], errors="coerce")
    for _, row in df[df["payment_timestamp"].isna()].iterrows():
        log_dq_error(
            errors,
            "payments",
            row["payment_id"],
            "INVALID_PAYMENT_TIMESTAMP",
            "invalid timestamp",
        )

    log.info(f"Transformed {len(df)} payments")
    return df


def transform_events(df, errors):
    log.info("Transforming events...")
    df = df.copy()

    df["customer_id"] = pd.to_numeric(df["customer_id"], errors="coerce")
    for _, row in df[df["customer_id"].isna()].iterrows():
        log_dq_error(
            errors,
            "events",
            row["event_id"],
            "MISSING_CUSTOMER_ID",
            "customer_id is null",
        )
    df["product_id"] = pd.to_numeric(df["product_id"], errors="coerce")
    for _, row in df[df["product_id"].isna()].iterrows():
        log_dq_error(
            errors,
            "events",
            row["event_id"],
            "MISSING_PRODUCT_ID",
            "product_id is null",
        )

    numeric_event_id = pd.to_numeric(df["event_id"], errors="coerce")
    for _, row in df[numeric_event_id.isna()].iterrows():
        log_dq_error(
            errors,
            "events",
            row["event_id"],
            "INVALID_EVENT_ID",
            "event_id is not numeric",
        )

    df["event_timestamp"] = pd.to_datetime(df["event_timestamp"], errors="coerce")
    for _, row in df[df["event_timestamp"].isna()].iterrows():
        log_dq_error(
            errors,
            "events",
            row["event_id"],
            "INVALID_EVENT_TIMESTAMP",
            "invalid timestamp",
        )

    log.info(f"Transformed {len(df)} events")
    return df


def transform_all(data, errors):
    return {
        "customers": transform_customers(data["customers"], errors),
        "orders": transform_orders(data["orders"], errors),
        "products": transform_products(data["products"], errors),
        "payments": transform_payments(data["payments"], errors),
        "events": transform_events(data["events"], errors),
    }


def check_referential_integrity(data, errors):
    log.info("Checking referential integrity...")

    valid_customers = set(data["customers"]["customer_id"].dropna())
    valid_products = set(data["products"]["product_id"].dropna())

    for _, row in data["orders"].iterrows():
        if pd.notna(row["customer_id"]) and row["customer_id"] not in valid_customers:
            log_dq_error(
                errors,
                "orders",
                row["order_id"],
                "INVALID_CUSTOMER_REFERENCE",
                f"customer_id={row['customer_id']}",
            )
        if pd.notna(row["product_id"]) and row["product_id"] not in valid_products:
            log_dq_error(
                errors,
                "orders",
                row["order_id"],
                "INVALID_PRODUCT_REFERENCE",
                f"product_id={row['product_id']}",
            )

    for _, row in data["events"].iterrows():
        if pd.notna(row["customer_id"]) and row["customer_id"] not in valid_customers:
            log_dq_error(
                errors,
                "events",
                row["event_id"],
                "INVALID_CUSTOMER_REFERENCE",
                f"customer_id={row['customer_id']}",
            )
        if pd.notna(row["product_id"]) and row["product_id"] not in valid_products:
            log_dq_error(
                errors,
                "events",
                row["event_id"],
                "INVALID_PRODUCT_REFERENCE",
                f"product_id={row['product_id']}",
            )
