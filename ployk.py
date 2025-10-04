import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine

# ------------------------------
# 1. Connect to PostgreSQL
# ------------------------------
engine = create_engine('postgresql+psycopg2://postgres:7777@localhost:5432/olist')

# ------------------------------
# 2. Query sales by product category and date
# ------------------------------
query = """
SELECT 
    o.order_purchase_timestamp::date AS date,
    p.product_category_name,
    SUM(oi.price * oi.order_item_id) AS sales
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p ON oi.product_id = p.product_id
GROUP BY date, p.product_category_name
ORDER BY date;
"""
df_sales = pd.read_sql(query, engine)

# ------------------------------
# 3. Map categories to broader departments
# ------------------------------
category_to_dept = {
    'beleza_saude': 'Beauty & Health',
    'informatica_acessorios': 'Electronics',
    'telefonia': 'Electronics',
    'cama_mesa_banho': 'Home & Living',
    'moveis_decoracao': 'Home & Living',
    # add more if needed
}

df_sales['department'] = df_sales['product_category_name'].map(category_to_dept).fillna('Other')

# ------------------------------
# 4. Aggregate monthly sales
# ------------------------------
df_sales['date'] = pd.to_datetime(df_sales['date'])
df_sales['month'] = df_sales['date'].dt.to_period('M')
monthly_sales = df_sales.groupby(['month', 'department'])['sales'].sum().reset_index()
monthly_sales['month'] = monthly_sales['month'].dt.to_timestamp()

# ------------------------------
# 5. Filter only 3 departments
# ------------------------------
monthly_sales = monthly_sales[monthly_sales['department'].isin(['Beauty & Health', 'Electronics', 'Home & Living'])]

# ------------------------------
# 6. Interactive Bar Chart with Time Slider
# ------------------------------
fig = px.bar(
    monthly_sales,
    x='department',
    y='sales',
    color='department',
    animation_frame=monthly_sales['month'].dt.strftime('%Y-%m'),
    range_y=[0, monthly_sales['sales'].max()*1.1],
    title='Monthly Sales by Department (Beauty, Electronics, Home & Living)',
    labels={'sales':'Sales (BRL)', 'department':'Department', 'month':'Month'}
)

fig.show()
