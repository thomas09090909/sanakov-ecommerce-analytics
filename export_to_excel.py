import pandas as pd
from sqlalchemy import create_engine
import os

# ------------------ Ensure exports folder exists ------------------
os.makedirs("exports", exist_ok=True)

# ------------------ PostgreSQL Connection ------------------
engine = create_engine('postgresql+psycopg2://postgres:7777@localhost:5432/olist')

# ------------------ 1. Top 5 Sellers ------------------
sql_top_sellers = """
SELECT s.seller_id, s.seller_city, COUNT(oi.order_id) AS orders_count
FROM sellers s
JOIN order_items oi ON s.seller_id = oi.seller_id
JOIN orders o ON oi.order_id = o.order_id
GROUP BY s.seller_id, s.seller_city
ORDER BY orders_count DESC
LIMIT 5;
"""
df_sellers = pd.read_sql_query(sql_top_sellers, engine)

# ------------------ 2. Top 10 Product Categories ------------------
sql_top_categories = """
SELECT ct.product_category_name_english AS category, SUM(oi.order_item_id) AS units_sold
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
JOIN category_translation ct ON p.product_category_name = ct.product_category_name
GROUP BY ct.product_category_name_english
ORDER BY units_sold DESC
LIMIT 10;
"""
df_categories = pd.read_sql_query(sql_top_categories, engine)

# ------------------ 3. Top 10 Brazilian States ------------------
sql_top_states = """
SELECT g.geolocation_state AS state, SUM(p.payment_value) AS total_sales
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
JOIN payments p ON o.order_id = p.order_id
JOIN sellers s ON oi.seller_id = s.seller_id
JOIN geolocation g ON s.seller_zip_code_prefix = g.geolocation_zip_code_prefix
GROUP BY g.geolocation_state
ORDER BY total_sales DESC
LIMIT 10;
"""
df_states = pd.read_sql(sql_top_states, engine)

# ------------------ 4. Sales by Department Over Time ------------------
sql_sales_dept = """
SELECT o.order_purchase_timestamp::date AS date,
       p.product_category_name,
       SUM(oi.price * oi.order_item_id) AS sales
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p ON oi.product_id = p.product_id
GROUP BY date, p.product_category_name
ORDER BY date;
"""
df_sales = pd.read_sql(sql_sales_dept, engine)

# ------------------ 5. Payment Value Distribution ------------------
sql_payments = """
SELECT p.payment_value
FROM payments p
JOIN orders o ON p.order_id = o.order_id
JOIN order_items oi ON o.order_id = oi.order_id
WHERE p.payment_value IS NOT NULL
LIMIT 5000;
"""
df_payments = pd.read_sql_query(sql_payments, engine)

# ------------------ 6. Top 10 States: Orders vs Sales ------------------
sql_state_orders = """
SELECT g.geolocation_state AS state,
       COUNT(DISTINCT o.order_id) AS total_orders,
       SUM(p.payment_value) AS total_sales,
       AVG(p.payment_value) AS avg_order_value
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
JOIN payments p ON o.order_id = p.order_id
JOIN sellers s ON oi.seller_id = s.seller_id
JOIN geolocation g ON s.seller_zip_code_prefix = g.geolocation_zip_code_prefix
GROUP BY g.geolocation_state;
"""
df_state_orders = pd.read_sql(sql_state_orders, engine)

# ------------------ Export All to Excel ------------------
excel_path = "exports/charts_data.xlsx"
with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
    df_sellers.to_excel(writer, sheet_name='Top 5 Sellers', index=False)
    df_categories.to_excel(writer, sheet_name='Top 10 Categories', index=False)
    df_states.to_excel(writer, sheet_name='Top 10 States Sales', index=False)
    df_sales.to_excel(writer, sheet_name='Sales by Department', index=False)
    df_payments.to_excel(writer, sheet_name='Payment Distribution', index=False)
    df_state_orders.to_excel(writer, sheet_name='Top States Orders vs Sales', index=False)

print(f"Excel file created: {excel_path}")
