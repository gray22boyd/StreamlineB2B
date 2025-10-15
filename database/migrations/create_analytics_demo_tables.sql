-- Analytics Demo Database Schema for Retail Business
-- This creates fake data tables for demonstrating the analytics agent

-- Customers table
CREATE TABLE IF NOT EXISTS public.analytics_demo_customers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    address TEXT,
    city VARCHAR(50),
    state VARCHAR(50),
    zip_code VARCHAR(10),
    customer_since DATE NOT NULL,
    loyalty_tier VARCHAR(20) DEFAULT 'Bronze',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Products table
CREATE TABLE IF NOT EXISTS public.analytics_demo_products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_name VARCHAR(200) NOT NULL,
    category VARCHAR(50) NOT NULL,
    subcategory VARCHAR(50),
    sku VARCHAR(50) UNIQUE NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    cost DECIMAL(10, 2) NOT NULL,
    brand VARCHAR(50),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Orders table
CREATE TABLE IF NOT EXISTS public.analytics_demo_orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_number VARCHAR(50) UNIQUE NOT NULL,
    customer_id UUID NOT NULL REFERENCES public.analytics_demo_customers(id),
    order_date TIMESTAMP NOT NULL,
    status VARCHAR(20) NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL,
    discount_amount DECIMAL(10, 2) DEFAULT 0,
    tax_amount DECIMAL(10, 2) DEFAULT 0,
    shipping_amount DECIMAL(10, 2) DEFAULT 0,
    payment_method VARCHAR(30),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Order items table
CREATE TABLE IF NOT EXISTS public.analytics_demo_order_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id UUID NOT NULL REFERENCES public.analytics_demo_orders(id),
    product_id UUID NOT NULL REFERENCES public.analytics_demo_products(id),
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    discount DECIMAL(10, 2) DEFAULT 0,
    subtotal DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Inventory table
CREATE TABLE IF NOT EXISTS public.analytics_demo_inventory (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID NOT NULL REFERENCES public.analytics_demo_products(id),
    quantity_on_hand INTEGER NOT NULL,
    reorder_point INTEGER NOT NULL,
    reorder_quantity INTEGER NOT NULL,
    warehouse_location VARCHAR(50),
    last_restock_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(product_id)
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_orders_customer_id ON public.analytics_demo_orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_orders_order_date ON public.analytics_demo_orders(order_date);
CREATE INDEX IF NOT EXISTS idx_order_items_order_id ON public.analytics_demo_order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_order_items_product_id ON public.analytics_demo_order_items(product_id);
CREATE INDEX IF NOT EXISTS idx_products_category ON public.analytics_demo_products(category);
CREATE INDEX IF NOT EXISTS idx_inventory_product_id ON public.analytics_demo_inventory(product_id);

-- Add comments for documentation
COMMENT ON TABLE public.analytics_demo_customers IS 'Demo customer data for analytics agent';
COMMENT ON TABLE public.analytics_demo_products IS 'Demo product catalog for analytics agent';
COMMENT ON TABLE public.analytics_demo_orders IS 'Demo order transactions for analytics agent';
COMMENT ON TABLE public.analytics_demo_order_items IS 'Demo order line items for analytics agent';
COMMENT ON TABLE public.analytics_demo_inventory IS 'Demo inventory levels for analytics agent';


