CREATE TABLE dim_customers (
    customer_sk SERIAL PRIMARY KEY,
    customer_id INTEGER UNIQUE NOT NULL,
    full_name VARCHAR(100),
    email VARCHAR(100),
    phone VARCHAR(12),
    city VARCHAR(100),
    created_at DATE
);

CREATE TABLE dim_products (
    product_sk SERIAL PRIMARY KEY,
    product_id INTEGER UNIQUE NOT NULL,
    product_name VARCHAR(100),
    category VARCHAR(100),
    price NUMERIC(12,2),
    currency VARCHAR(5),
    is_active BOOLEAN
);

CREATE TABLE dim_date (
    date_sk SERIAL PRIMARY KEY,
    full_date DATE UNIQUE NOT NULL,
    year INTEGER,
    month INTEGER,
    quarter INTEGER,
    day_of_week INTEGER,
    is_weekend BOOLEAN
);


CREATE TABLE fact_orders (
    order_sk SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL,
    customer_sk INTEGER REFERENCES dim_customers(customer_sk),
    product_sk INTEGER REFERENCES dim_products(product_sk),
    date_sk INTEGER REFERENCES dim_date(date_sk),
    quantity INTEGER,
    unit_price NUMERIC(12,2),
    currency VARCHAR(5),
    status VARCHAR(20)
);

CREATE TABLE fact_payments (
    payment_sk SERIAL PRIMARY KEY,
    payment_id INTEGER NOT NULL,
    order_id INTEGER,
    date_sk INTEGER REFERENCES dim_date(date_sk),
    amount NUMERIC(12,2),
    currency VARCHAR(5),
    payment_method VARCHAR(20)
);

CREATE TABLE fact_events (
    event_sk SERIAL PRIMARY KEY,
    event_id VARCHAR(50),
    customer_sk INTEGER REFERENCES dim_customers(customer_sk),
    product_sk INTEGER REFERENCES dim_products(product_sk),
    date_sk INTEGER REFERENCES dim_date(date_sk),
    event_type VARCHAR(30),
    event_timestamp TIMESTAMP
);
CREATE TABLE dq_error_log (
    error_id SERIAL PRIMARY KEY,
    source_table VARCHAR(100),
    record_id VARCHAR(100),
    error_type VARCHAR(100),
    error_detail TEXT,
    logged_at TIMESTAMP
);