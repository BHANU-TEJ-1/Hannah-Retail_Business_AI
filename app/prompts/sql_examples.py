SQL_EXAMPLES = """
Example 1

User:
Show all products.

SQL:
SELECT
    id,
    sku,
    name,
    category,
    unit_price
FROM products;


------------------------------------------------------------

Example 2

User:
Show low stock products.

SQL:
SELECT
    p.name,
    i.quantity,
    p.reorder_level
FROM inventory i
JOIN products p
ON i.product_id = p.id
WHERE i.quantity < p.reorder_level;

"""
