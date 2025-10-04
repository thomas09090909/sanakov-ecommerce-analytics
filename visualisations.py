import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
import numpy as np
import plotly.express as px
import os

# ------------------ Ensure charts folder exists ------------------
os.makedirs("charts", exist_ok=True)

# ------------------ PostgreSQL Connection ------------------
engine = create_engine('postgresql+psycopg2://postgres:7777@localhost:5432/olist')

# ------------------ 1. Top 5 Sellers by Number of Orders (Pie Chart) ------------------
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

fig, ax = plt.subplots(figsize=(10, 8))
colors = ['#FF9999', '#66B2FF', '#99FF99', '#FFCC99', '#FF66CC']
explode = [0.1 if i == 0 else 0 for i in range(len(df_sellers))]
wedges, texts, autotexts = ax.pie(
    df_sellers['orders_count'],
    labels=df_sellers['seller_city'],
    autopct='%1.1f%%',
    colors=colors,
    explode=explode,
    shadow=True,
    startangle=140,
    wedgeprops={'edgecolor': 'black'}
)
for autotext in autotexts:
    autotext.set_color('white')
    autotext.set_weight('bold')
    autotext.set_size(12)
ax.set_title('Top 5 Sellers by Number of Orders', fontsize=18, pad=20)
plt.tight_layout()
plt.savefig('charts/top_5_sellers_pie.png', dpi=300)
plt.show()

# ------------------ 2. Top 10 Product Categories by Units Sold (Bar Chart) ------------------
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
df_categories['category'] = df_categories['category'].str.replace('_', ' ').str.title()

fig, ax = plt.subplots(figsize=(12, 7))
bars = ax.bar(df_categories['category'], df_categories['units_sold'], color='#66B2FF', edgecolor='black')
for bar in bars:
    height = bar.get_height()
    ax.annotate(f'{height}', xy=(bar.get_x() + bar.get_width()/2, height),
                xytext=(0, 5), textcoords='offset points', ha='center', va='bottom', fontsize=10, fontweight='bold')
ax.set_title('Top 10 Product Categories by Units Sold', fontsize=18, pad=20)
ax.set_xlabel('Product Category', fontsize=14)
ax.set_ylabel('Units Sold', fontsize=14)
plt.xticks(rotation=45, ha='right')
ax.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig('charts/top_10_categories_bar.png', dpi=300)
plt.show()

# ------------------ 3. Top 10 Brazilian States by Total Seller Sales (Horizontal Bar) ------------------
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
state_names = {
    'AC': 'Acre', 'AL': 'Alagoas', 'AP': 'Amapá', 'AM': 'Amazonas',
    'BA': 'Bahia', 'CE': 'Ceará', 'DF': 'Distrito Federal', 'ES': 'Espírito Santo',
    'GO': 'Goiás', 'MA': 'Maranhão', 'MT': 'Mato Grosso', 'MS': 'Mato Grosso do Sul',
    'MG': 'Minas Gerais', 'PA': 'Pará', 'PB': 'Paraíba', 'PR': 'Paraná',
    'PE': 'Pernambuco', 'PI': 'Piauí', 'RJ': 'Rio de Janeiro', 'RN': 'Rio Grande do Norte',
    'RS': 'Rio Grande do Sul', 'RO': 'Rondônia', 'RR': 'Roraima', 'SC': 'Santa Catarina',
    'SP': 'São Paulo', 'SE': 'Sergipe', 'TO': 'Tocantins'
}
df_states['state'] = df_states['state'].map(state_names)

fig, ax = plt.subplots(figsize=(12, 7))
colors = plt.cm.viridis(range(len(df_states)))
bars = ax.barh(df_states['state'], df_states['total_sales'], color=colors, edgecolor='black')
for bar in bars:
    width = bar.get_width()
    ax.text(width + 0.01*width, bar.get_y() + bar.get_height()/2, f"{width:,.0f}", va='center', fontweight='bold', fontsize=10)
ax.set_title('Top 10 Brazilian States by Total Seller Sales', fontsize=16, pad=20)
ax.set_xlabel('Total Sales (BRL)', fontsize=12)
ax.set_ylabel('State', fontsize=12)
ax.grid(axis='x', alpha=0.3)
plt.tight_layout()
plt.savefig('charts/top_states_sales_horizontal.png', dpi=300)
plt.show()

# ------------------ 4. Sales by Department Over Time (Line Chart) ------------------
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
category_to_dept = {
    'beleza_saude': 'Beauty & Health', 'artesanato': 'Arts & Crafts', 'cama_mesa_banho': 'Home & Living',
    'informatica_acessorios': 'Electronics', 'esporte_lazer': 'Sports & Leisure', 'moveis_decoracao': 'Home & Living',
    'automotivo': 'Automotive', 'telefonia': 'Electronics', 'brinquedos': 'Toys & Kids', 'alimentos_bebidas': 'Food & Drinks'
}
df_sales['department'] = df_sales['product_category_name'].map(category_to_dept)
df_sales = df_sales.dropna(subset=['department'])
sales_by_dept = df_sales.groupby(['date', 'department'])['sales'].sum().unstack(fill_value=0)
sales_by_dept.index = pd.to_datetime(sales_by_dept.index)
sales_monthly = sales_by_dept.resample('M').sum()

fig, ax = plt.subplots(figsize=(14, 8))
colors = plt.cm.tab10(range(len(sales_monthly.columns)))
for i, dept in enumerate(sales_monthly.columns):
    ax.plot(sales_monthly.index, sales_monthly[dept], label=dept, linewidth=2, marker='o', markersize=4, color=colors[i])
    ax.plot(sales_monthly[dept].rolling(window=3).mean(), '--', alpha=0.7, linewidth=1, color=colors[i])
ax.set_title('Monthly Sales by Department (with Trends)', fontsize=16, pad=20)
ax.set_xlabel('Month', fontsize=12)
ax.set_ylabel('Sales (BRL)', fontsize=12)
ax.legend(title='Department', bbox_to_anchor=(1.05, 1), loc='upper left')
ax.grid(True, alpha=0.3)
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('charts/sales_by_department_line.png', dpi=300)
plt.show()

# ------------------ 5. Payment Value Distribution (Histogram using Plotly) ------------------
sql_payments = """
SELECT p.payment_value
FROM payments p
JOIN orders o ON p.order_id = o.order_id
JOIN order_items oi ON o.order_id = oi.order_id
WHERE p.payment_value IS NOT NULL
LIMIT 5000;
"""
df_payments = pd.read_sql_query(sql_payments, engine)

# ------------------ Compute histogram ------------------
counts, bins = np.histogram(df_payments.payment_value, bins=range(0, 2000, 50))
bins_center = 0.5 * (bins[:-1] + bins[1:])

# ------------------ Plot histogram using Matplotlib ------------------
plt.figure(figsize=(12, 7))
plt.bar(bins_center, counts, width=45, color='#66B2FF', edgecolor='black')
plt.xlabel('Payment Value (BRL)', fontsize=12)
plt.ylabel('Number of Orders', fontsize=12)
plt.title('Distribution of Order Payments (BRL)', fontsize=16)
plt.xticks(rotation=45)
plt.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig('charts/payment_histogram.png', dpi=300)
plt.show()

# ------------------ 6. Top 10 States: Orders vs Sales (Scatter Plot) ------------------
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
df_state_orders['state'] = df_state_orders['state'].map(state_names)
df_top_states = df_state_orders.nlargest(10, 'total_sales')

plt.figure(figsize=(12, 8))
plt.scatter(df_top_states['total_orders'], df_top_states['total_sales'],
            s=df_top_states['avg_order_value']*10, c=np.arange(len(df_top_states)),
            cmap='viridis', alpha=0.7, edgecolors='black')
for i, row in df_top_states.iterrows():
    plt.text(row['total_orders'], row['total_sales'], row['state'], fontsize=9, ha='center', va='bottom')
plt.title('Top 10 Brazilian States: Orders vs Sales', fontsize=16)
plt.xlabel('Total Orders', fontsize=12)
plt.ylabel('Total Sales (BRL)', fontsize=12)
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()
