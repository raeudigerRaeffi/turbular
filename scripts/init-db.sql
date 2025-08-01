-- Create tables
CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    stock_quantity INTEGER NOT NULL DEFAULT 0,
    category VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(customer_id),
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_amount DECIMAL(10,2) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending'
);

CREATE TABLE order_items (
    order_item_id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(order_id),
    product_id INTEGER REFERENCES products(product_id),
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    subtotal DECIMAL(10,2) GENERATED ALWAYS AS (quantity * unit_price) STORED
);

-- Insert sample data
INSERT INTO customers (first_name, last_name, email) VALUES
    ('John', 'Doe', 'john.doe@example.com'),
    ('Jane', 'Smith', 'jane.smith@example.com'),
    ('Bob', 'Johnson', 'bob.johnson@example.com'),
    ('Alice', 'Williams', 'alice.williams@example.com'),
    ('Charlie', 'Brown', 'charlie.brown@example.com');

INSERT INTO products (name, description, price, stock_quantity, category) VALUES
    ('Laptop', 'High-performance laptop', 999.99, 50, 'Electronics'),
    ('Smartphone', '5G enabled smartphone', 699.99, 100, 'Electronics'),
    ('Coffee Maker', 'Automatic coffee maker', 79.99, 30, 'Appliances'),
    ('Running Shoes', 'Comfortable running shoes', 89.99, 200, 'Sports'),
    ('Backpack', 'Waterproof hiking backpack', 49.99, 150, 'Outdoor');

INSERT INTO orders (customer_id, total_amount, status) VALUES
    (1, 1699.98, 'completed'),
    (2, 79.99, 'completed'),
    (3, 139.98, 'processing'),
    (4, 999.99, 'pending'),
    (5, 49.99, 'completed');

INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES
    (1, 1, 1, 999.99),
    (1, 2, 1, 699.99),
    (2, 3, 1, 79.99),
    (3, 4, 2, 89.99),
    (4, 1, 1, 999.99),
    (5, 5, 1, 49.99);

-- Create a view for order summaries
CREATE VIEW order_summaries AS
SELECT 
    o.order_id,
    c.first_name || ' ' || c.last_name as customer_name,
    o.order_date,
    o.status,
    COUNT(oi.order_item_id) as total_items,
    o.total_amount
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY o.order_id, c.first_name, c.last_name, o.order_date, o.status, o.total_amount;

-- Create indexes for better performance
CREATE INDEX idx_customers_email ON customers(email);
CREATE INDEX idx_products_category ON products(category);
CREATE INDEX idx_orders_customer ON orders(customer_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_order_items_order ON order_items(order_id);
CREATE INDEX idx_order_items_product ON order_items(product_id); 