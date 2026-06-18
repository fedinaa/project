-- 1. Топ-10 клиентов по сумме покупок
SELECT 
    c.full_name,
    c.email,
	c.city,
    SUM(f.quantity * f.unit_price) AS total_amount
FROM fact_orders f
LEFT JOIN dim_customers c ON f.customer_sk = c.customer_sk
WHERE f.customer_sk IS NOT NULL 
GROUP BY c.full_name, c.email, c.city  
ORDER BY total_amount DESC
LIMIT 10;

-- 2. Выручка по месяцам
SELECT 
    d.year,
    d.month,
    SUM(f.quantity * f.unit_price) AS revenue
FROM fact_orders f
LEFT JOIN dim_date d ON f.date_sk = d.date_sk
WHERE year IS NOT NULL and month IS NOT NULL
GROUP BY d.year, d.month
ORDER BY d.year, d.month;

-- 3. Самые популярные товары (по количеству заказов)
SELECT 
    p.product_name,
    p.category,
    p.price,
    COUNT(DISTINCT f.order_id) AS order_count
FROM fact_orders f
JOIN dim_products p ON f.product_sk = p.product_sk
GROUP BY p.product_name, p.category, p.price
ORDER BY order_count DESC
LIMIT 10;

-- 4. Последняя активность (дата) топ-5 пользователей, которые совершили больше всего покупок
WITH top_customers AS (
    SELECT 
        customer_sk,
        COUNT(order_id) AS orders_count
    FROM fact_orders
    WHERE customer_sk IS NOT NULL
    GROUP BY customer_sk
    ORDER BY orders_count DESC
    LIMIT 5
),
ranked_events AS (
    SELECT 
        customer_sk,
        event_timestamp,
        event_id,
        event_type,
        ROW_NUMBER() OVER (PARTITION BY customer_sk ORDER BY event_timestamp DESC) AS rn
    FROM fact_events
)
SELECT 
    tc.customer_sk,
    d.full_name,
    d.email,
    tc.orders_count,
    re.event_timestamp AS last_active_date,
    re.event_id,
    re.event_type
FROM top_customers tc
LEFT JOIN dim_customers d ON tc.customer_sk = d.customer_sk
LEFT JOIN ranked_events re ON tc.customer_sk = re.customer_sk AND re.rn = 1
ORDER BY tc.orders_count DESC;

-- 5. Пользователи без заказа
SELECT 
	customer_id,
	full_name,
	email, 
	phone,
	city, 
	created_at
FROM dim_customers c
LEFT JOIN fact_orders f ON c.customer_sk = f.customer_sk
WHERE f.order_sk IS NULL;