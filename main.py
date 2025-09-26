# main.py
import psycopg2

# Database connection parameters
conn = psycopg2.connect(
    host="localhost",
    database="olist",
    user="postgres",
    password="7777"
)

cur = conn.cursor()

# Example queries
queries = {
    "First 10 customers": "SELECT * FROM customers LIMIT 10;",
    "Top sellers by products sold": """
        SELECT oi.seller_id, COUNT(oi.order_id) AS total_sold
        FROM order_items oi
        GROUP BY oi.seller_id
        ORDER BY total_sold DESC
        LIMIT 5;
    """,
    "Average order value per customer": """
        SELECT c.customer_id, AVG(oi.price) AS avg_price
        FROM customers c
        JOIN orders o ON c.customer_id = o.customer_id
        JOIN order_items oi ON o.order_id = oi.order_id
        GROUP BY c.customer_id
        ORDER BY avg_price DESC
        LIMIT 5;
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
