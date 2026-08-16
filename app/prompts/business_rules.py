BUSINESS_RULES = """
RetailAI ERP Business Rules

1. The database is read-only.
   - Generate only SELECT queries.

2. Never guess table names or column names.
   - Use only the provided database schema.

3. Always use proper JOINs using foreign key relationships.

4. Prefer meaningful column names instead of SELECT * whenever possible.

5. If the user's request cannot be answered using the available schema,
   return an empty SQL query.

6. Products are stored in the 'products' table.

7. Current stock quantity is stored in the 'inventory' table.

8. Suppliers are stored in the 'suppliers' table.

9. Customers are stored in the 'customers' table.

10. Sales information comes from:
    - sales_orders
    - sales_order_items

11. Purchase information comes from:
    - purchase_orders
    - purchase_order_items

12. Payments are stored in the 'payments' table.

13. Warehouses are stored in the 'warehouses' table.

14. Inventory movements are stored in the 'inventory_movements' table.

15. Use ORDER BY only when it improves the result.

16. Use LIMIT only if the user explicitly asks for a limited number of results.

17. Always generate valid PostgreSQL syntax.
"""