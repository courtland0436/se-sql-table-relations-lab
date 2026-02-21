# STEP 0

# SQL Library and Pandas Library
import sqlite3
import pandas as pd

# Connect to the database
conn = sqlite3.connect('data.sqlite')

# STEP 1: Boston employees
df_boston = pd.read_sql("""
SELECT firstName, lastName
FROM employees e
JOIN offices o ON e.officeCode = o.officeCode
WHERE o.city = 'Boston'
""", conn)

# STEP 2: Offices with zero employees
df_zero_emp = pd.read_sql("""
SELECT o.officeCode, o.city
FROM offices o
LEFT JOIN employees e ON o.officeCode = e.officeCode
WHERE e.employeeNumber IS NULL
""", conn)

# STEP 3: Employees with office info (all employees included)
df_employee = pd.read_sql("""
SELECT e.firstName, e.lastName, o.city, o.state
FROM employees e
LEFT JOIN offices o ON e.officeCode = o.officeCode
ORDER BY e.firstName, e.lastName
""", conn)

# STEP 4: Customers who have not placed orders
df_contacts = pd.read_sql("""
SELECT c.contactFirstName, c.contactLastName, c.phone, c.salesRepEmployeeNumber
FROM customers c
LEFT JOIN orders o ON c.customerNumber = o.customerNumber
WHERE o.orderNumber IS NULL
ORDER BY c.contactLastName
""", conn)

# STEP 5: Customer payments sorted by amount
df_payment = pd.read_sql("""
SELECT c.contactFirstName, c.contactLastName, p.amount, p.paymentDate
FROM customers c
JOIN payments p ON c.customerNumber = p.customerNumber
ORDER BY CAST(p.amount AS FLOAT) DESC
""", conn)

# STEP 6: Employees with customers averaging credit limit > 90k
df_credit = pd.read_sql("""
SELECT e.employeeNumber, e.firstName, e.lastName, COUNT(c.customerNumber) AS num_customers
FROM employees e
JOIN customers c ON e.employeeNumber = c.salesRepEmployeeNumber
GROUP BY e.employeeNumber
HAVING AVG(c.creditLimit) > 90000
ORDER BY num_customers DESC
""", conn)

# STEP 7: Products sold with total units
df_product_sold = pd.read_sql("""
SELECT p.productName, COUNT(od.orderNumber) AS numorders, SUM(od.quantityOrdered) AS totalunits
FROM products p
JOIN orderdetails od ON p.productCode = od.productCode
GROUP BY p.productName
ORDER BY totalunits DESC
""", conn)

# STEP 8: Number of customers per product
df_total_customers = pd.read_sql("""
SELECT p.productName, p.productCode, COUNT(DISTINCT o.customerNumber) AS numpurchasers
FROM products p
JOIN orderdetails od ON p.productCode = od.productCode
JOIN orders o ON od.orderNumber = o.orderNumber
GROUP BY p.productName, p.productCode
ORDER BY numpurchasers DESC
""", conn)

# STEP 9: Number of customers per office
df_customers = pd.read_sql("""
SELECT o.officeCode, o.city, COUNT(c.customerNumber) AS n_customers
FROM offices o
LEFT JOIN employees e ON o.officeCode = e.officeCode
LEFT JOIN customers c ON e.employeeNumber = c.salesRepEmployeeNumber
GROUP BY o.officeCode, o.city
""", conn)

# STEP 10: Employees who sold products ordered by fewer than 20 customers
df_under_20 = pd.read_sql("""
WITH low_sales_products AS (
    SELECT od.productCode
    FROM orderdetails od
    JOIN orders o ON od.orderNumber = o.orderNumber
    GROUP BY od.productCode
    HAVING COUNT(DISTINCT o.customerNumber) < 20
)
SELECT DISTINCT e.employeeNumber, e.firstName, e.lastName, o.city, o.officeCode
FROM customers c
JOIN employees e ON c.salesRepEmployeeNumber = e.employeeNumber
JOIN offices o ON e.officeCode = o.officeCode
WHERE c.customerNumber IN (
    SELECT DISTINCT o.customerNumber
    FROM orders o
    JOIN orderdetails od ON o.orderNumber = od.orderNumber
    WHERE od.productCode IN (SELECT productCode FROM low_sales_products)
)
ORDER BY e.firstName
""", conn)

# Close the connection
conn.close()