import psycopg2

# Connect to the database
conn = psycopg2.connect(
    host="localhost",
    database="olist",
    user="postgres",
    password="7777"
)
cur = conn.cursor()

# Dictionary of queries
queries = {
    "1. Customers count per state": """
        SELECT customer_state, COUNT(*) AS total_customers
        FROM customers
        GROUP BY customer_state
        ORDER BY total_customers DESC;
    """,
    "2. Average order value per customer (>5 orders)": """
        SELECT c.customer_id,
               COUNT(o.order_id) AS total_orders,
               AVG(oi.price) AS avg_order_value
        FROM customers c
        JOIN orders o ON c.customer_id = o.customer_id
        JOIN order_items oi ON o.order_id = oi.order_id
        GROUP BY c.customer_id
        HAVING COUNT(o.order_id) > 5
        ORDER BY avg_order_value DESC;
    """,
    "3. Top product categories by number of orders": """
        SELECT p.product_category_name,
               COUNT(DISTINCT o.order_id) AS total_orders,
               AVG(oi.price) AS avg_price
        FROM products p
        JOIN order_items oi ON p.product_id = oi.product_id
        JOIN orders o ON oi.order_id = o.order_id
        GROUP BY p.product_category_name
        ORDER BY total_orders DESC
        LIMIT 10;
    """,
    "4. Avg, min, max freight per seller": """
        SELECT seller_id,
               AVG(freight_value) AS avg_freight,
               MIN(freight_value) AS min_freight,
               MAX(freight_value) AS max_freight
        FROM order_items
        GROUP BY seller_id
        ORDER BY avg_freight DESC
        LIMIT 10;
    """,
    "5. Items per customer (>5)": """
        SELECT c.customer_id,
               c.customer_city,
               COUNT(oi.order_id) AS total_items
        FROM customers c
        JOIN orders o ON c.customer_id = o.customer_id
        JOIN order_items oi ON o.order_id = oi.order_id
        GROUP BY c.customer_id, c.customer_city
        HAVING COUNT(oi.order_id) > 5
        ORDER BY total_items DESC
        LIMIT 10;
    """,
    "6. Orders delivered late": """
        SELECT order_id,
               order_status,
               order_purchase_timestamp,
               order_delivered_customer_date,
               order_estimated_delivery_date,
               (CAST(order_delivered_customer_date AS timestamp) - CAST(order_estimated_delivery_date AS timestamp)) AS delay_days
        FROM orders
        WHERE CAST(order_delivered_customer_date AS timestamp) > CAST(order_estimated_delivery_date AS timestamp)
        ORDER BY delay_days DESC
        LIMIT 10;
    """,
    "7. Product price stats per seller": """
        SELECT s.seller_id,
               COUNT(oi.product_id) AS total_products_sold,
               AVG(oi.price) AS avg_price,
               MIN(oi.price) AS min_price,
               MAX(oi.price) AS max_price
        FROM order_items oi
        JOIN sellers s ON oi.seller_id = s.seller_id
        GROUP BY s.seller_id
        ORDER BY avg_price DESC
        LIMIT 10;
    """,
    "8. Total payment by state": """
        SELECT c.customer_state,
               COUNT(p.payment_value) AS num_payments,
               SUM(p.payment_value::numeric) AS total_payment,
               AVG(p.payment_value::numeric) AS avg_payment
        FROM orders o
        JOIN customers c ON o.customer_id = c.customer_id
        JOIN payments p ON o.order_id = p.order_id
        GROUP BY c.customer_state
        ORDER BY total_payment DESC;
    """,
    "9. Top product categories by total sales": """
        SELECT p.product_category_name,
               SUM(oi.price::numeric) AS total_sales,
               COUNT(oi.order_id) AS total_orders
        FROM order_items oi
        JOIN products p ON oi.product_id = p.product_id
        GROUP BY p.product_category_name
        ORDER BY total_sales DESC
        LIMIT 10;
    """,
    "10. Average review score per product": """
        SELECT 
            oi.product_id,
            p.product_category_name,
            AVG(r.review_score) AS avg_review_score
        FROM reviews r
        JOIN orders o ON r.order_id = o.order_id
        JOIN order_items oi ON o.order_id = oi.order_id
        JOIN products p ON oi.product_id = p.product_id
        GROUP BY oi.product_id, p.product_category_name
        ORDER BY avg_review_score DESC
        LIMIT 10;
    """
}

# Execute and display results
for desc, query in queries.items():
    print(f"\n--- {desc} ---")
    cur.execute(query)
    rows = cur.fetchall()
    for row in rows:
        print(row)

# Close connection
cur.close()
conn.close()
