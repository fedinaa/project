import pandas as pd
from config import log, get_engine
from sqlalchemy import text


def generate_date_dim(all_dfs):
    all_dates = []
    for df, col in all_dfs:
        if col in df.columns:
            series = pd.to_datetime(df[col], errors="coerce").dropna()
            if not series.empty:
                all_dates.extend([series.min(), series.max()])

    start = min(all_dates).floor("D")
    end = max(all_dates).ceil("D")

    dates = pd.date_range(start=start, end=end, freq="D")
    return pd.DataFrame({
        "full_date": dates.date,
        "year": dates.year,
        "month": dates.month,
        "quarter": dates.quarter,
        "day_of_week": dates.dayofweek,
        "is_weekend": dates.dayofweek >= 5,
    })


def load_to_dwh(data, errors):
    log.info("Loading data into DWH …")
    engine = get_engine()

    customers = data["customers"]
    orders = data["orders"]
    products = data["products"]
    payments = data["payments"]
    events = data["events"]

    with engine.connect() as conn:
        conn.execute(text(
            "TRUNCATE TABLE dim_customers, dim_products, dim_date, "
            "fact_orders, fact_payments, fact_events, dq_error_log "
            "RESTART IDENTITY CASCADE;"
        ))
        conn.commit()
    log.info("Tables truncated")

    customers[[
        "customer_id", "full_name", "email", "phone", "city", "created_at"
    ]].to_sql("dim_customers", engine, if_exists="append", index=False)
    log.info("dim_customers loaded")

    products[[
        "product_id", "product_name", "category", "price", "currency", "is_active"
    ]].to_sql("dim_products", engine, if_exists="append", index=False)
    log.info("dim_products loaded")

    date_dim = generate_date_dim([
        (orders, "order_timestamp"),
        (payments, "payment_timestamp"),
        (events, "event_timestamp"),
    ])
    date_dim.to_sql("dim_date", engine, if_exists="append", index=False)
    log.info("dim_date loaded")

    cust_sk = pd.read_sql("SELECT customer_id, customer_sk FROM dim_customers", engine)
    prod_sk = pd.read_sql("SELECT product_id, product_sk FROM dim_products", engine)
    date_sk = pd.read_sql("SELECT full_date, date_sk FROM dim_date", engine)
    date_sk["full_date"] = pd.to_datetime(date_sk["full_date"])

    orders = orders.merge(cust_sk, on="customer_id", how="left")
    orders = orders.merge(prod_sk, on="product_id", how="left")
    orders["date"] = pd.to_datetime(orders["order_timestamp"]).dt.normalize()
    orders = orders.merge(date_sk.rename(columns={"full_date": "date"}), on="date", how="left")

    orders[[
        "order_id", "customer_sk", "product_sk", "date_sk", "quantity", "unit_price", "currency", "status"
    ]].to_sql("fact_orders", engine, if_exists="append", index=False)
    log.info("fact_orders loaded")

    payments["date"] = pd.to_datetime(payments["payment_timestamp"]).dt.normalize()
    payments = payments.merge(date_sk.rename(columns={"full_date": "date"}), on="date", how="left")

    payments[[
        "payment_id", "order_id", "date_sk", "amount", "currency", "payment_method"
    ]].to_sql("fact_payments", engine, if_exists="append", index=False)
    log.info("fact_payments loaded")

    events = events.merge(cust_sk, on="customer_id", how="left")
    events = events.merge(prod_sk, on="product_id", how="left")
    events["date"] = pd.to_datetime(events["event_timestamp"]).dt.normalize()
    events = events.merge(date_sk.rename(columns={"full_date": "date"}), on="date", how="left")

    events[[
        "event_id", "customer_sk", "product_sk", "date_sk", "event_type", "event_timestamp"
    ]].to_sql("fact_events", engine, if_exists="append", index=False)
    log.info("fact_events loaded")

    if errors:
        pd.DataFrame(errors).to_sql("dq_error_log", engine, if_exists="append", index=False)
        log.info(f"dq_error_log ({len(errors)} records)")

    log.info("DWH load complete")