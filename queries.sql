-- 1. Select first 10 rows from customers
SELECT * 
FROM customers
LIMIT 10;

-- 2. Filter orders with total price > 100 and sort by purchase date
SELECT o.order_id, o.customer_id, SUM(oi.price) AS total_price, o.order_purchase_timestamp
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY o.order_id, o.customer_id, o.order_purchase_timestamp
HAVING SUM(oi.price) > 100
ORDER BY o.order_purchase_timestamp DESC
LIMIT 10;

-- 3. Aggregation: total orders, average, min, max price per customer
SELECT o.customer_id,
       COUNT(oi.order_id) AS total_orders,
       AVG(oi.price) AS avg_price,
       MIN(oi.price) AS min_price,
       MAX(oi.price) AS max_price
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY o.customer_id
ORDER BY total_orders DESC
LIMIT 10;

-- 4. Join: get customer city and total spent per customer
SELECT c.customer_id, c.customer_city, SUM(oi.price) AS total_spent
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY c.customer_id, c.customer_city
ORDER BY total_spent DESC
LIMIT 10;


-- 1. Count how many customers are from each state
SELECT customer_state, COUNT(*) AS total_customers
FROM customers
GROUP BY customer_state
ORDER BY total_customers DESC;

-- 2. Find average order value per customer (only those with more than 5 orders)
SELECT c.customer_id,
       COUNT(o.order_id) AS total_orders,
       AVG(oi.price) AS avg_order_value
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY c.customer_id
HAVING COUNT(o.order_id) > 5
ORDER BY avg_order_value DESC;

-- 3. Find top product categories by number of orders
SELECT p.product_category_name,
       COUNT(DISTINCT o.order_id) AS total_orders,
       AVG(oi.price) AS avg_price
FROM products p
JOIN order_items oi ON p.product_id = oi.product_id
JOIN orders o ON oi.order_id = o.order_id
GROUP BY p.product_category_name
ORDER BY total_orders DESC
LIMIT 10;

-- 4. Aggregation: average, min, max freight per seller
SELECT seller_id,
       AVG(freight_value) AS avg_freight,
       MIN(freight_value) AS min_freight,
       MAX(freight_value) AS max_freight
FROM order_items
GROUP BY seller_id
ORDER BY avg_freight DESC
LIMIT 10;

-- 5. Join customers and orders, count items per customer (filter > 5)
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

-- 6. Find orders delivered late and calculate delay in days
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

-- 7. Average, minimum, and maximum product price per seller
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

-- 8. Total payment value by state
SELECT c.customer_state,
       COUNT(p.payment_value) AS num_payments,
       SUM(p.payment_value::numeric) AS total_payment,
       AVG(p.payment_value::numeric) AS avg_payment
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN payments p ON o.order_id = p.order_id
GROUP BY c.customer_state
ORDER BY total_payment DESC;

-- 9. Top 10 product categories by total sales value
SELECT p.product_category_name,
       SUM(oi.price::numeric) AS total_sales,
       COUNT(oi.order_id) AS total_orders
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
GROUP BY p.product_category_name
ORDER BY total_sales DESC
LIMIT 10;

-- 10. Average review score per product
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

