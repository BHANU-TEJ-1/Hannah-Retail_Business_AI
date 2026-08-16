DATABASE_SCHEMA = """
Table: customers
- id (integer)
- name (character varying)
- contact_email (character varying)
- contact_phone (character varying)
- address (text)
- credit_limit (numeric)
- current_credit (numeric)
- created_at (timestamp without time zone)
- updated_at (timestamp without time zone)

Table: inventory
- id (integer)
- product_id (integer)
- warehouse_id (integer)
- quantity (integer)
- reserved_quantity (integer)
- last_updated (timestamp without time zone)

Table: inventory_movements
- id (integer)
- product_id (integer)
- warehouse_id (integer)
- movement_type (character varying)
- quantity (integer)
- reason (character varying)
- reference_id (integer)
- created_at (timestamp without time zone)

Table: payments
- id (integer)
- customer_id (integer)
- sales_order_id (integer)
- amount (numeric)
- payment_method (character varying)
- payment_date (timestamp without time zone)
- status (character varying)

Table: products
- id (integer)
- sku (character varying)
- name (character varying)
- brand (character varying)
- category (character varying)
- unit (character varying)
- unit_price (numeric)
- reorder_level (integer)
- reorder_qty (integer)
- default_supplier_id (integer)
- is_active (boolean)
- created_at (timestamp without time zone)
- updated_at (timestamp without time zone)

Table: purchase_order_items
- id (integer)
- purchase_order_id (integer)
- product_id (integer)
- quantity (integer)
- unit_price (numeric)
- subtotal (numeric)

Table: purchase_orders
- id (integer)
- supplier_id (integer)
- status (character varying)
- order_date (timestamp without time zone)
- expected_delivery (date)
- total_amount (numeric)
- created_at (timestamp without time zone)

Table: sales_order_items
- id (integer)
- sales_order_id (integer)
- product_id (integer)
- quantity (integer)
- selling_price (numeric)
- subtotal (numeric)

Table: sales_orders
- id (integer)
- customer_id (integer)
- order_date (timestamp without time zone)
- payment_status (character varying)
- delivery_status (character varying)
- total_amount (numeric)
- created_at (timestamp without time zone)

Table: suppliers
- id (integer)
- name (character varying)
- contact_email (character varying)
- contact_phone (character varying)
- address (text)
- gst_number (character varying)
- rating (numeric)
- payment_terms (character varying)
- is_active (boolean)
- created_at (timestamp without time zone)
- updated_at (timestamp without time zone)

Table: warehouses
- id (integer)
- name (character varying)
- location (character varying)
- created_at (timestamp without time zone)
- updated_at (timestamp without time zone)

"""