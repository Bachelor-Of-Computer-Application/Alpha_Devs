-- QuickBite Database Schema
-- All Tables Structure
-- This file documents the Django ORM models as SQL for reference

-- Users App Tables
-- =================

-- Custom User Table
CREATE TABLE users_user (
    id SERIAL PRIMARY KEY,
    password VARCHAR(128) NOT NULL,
    last_login TIMESTAMP,
    is_superuser BOOLEAN DEFAULT FALSE NOT NULL,
    username VARCHAR(150) UNIQUE,
    first_name VARCHAR(150) NOT NULL,
    last_name VARCHAR(150) NOT NULL,
    is_staff BOOLEAN DEFAULT FALSE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    date_joined TIMESTAMP NOT NULL,
    email VARCHAR(254) UNIQUE NOT NULL,
    role VARCHAR(20) NOT NULL,
    phone_number VARCHAR(20),
    profile_image VARCHAR(100),
    is_email_verified BOOLEAN DEFAULT FALSE NOT NULL,
    is_phone_verified BOOLEAN DEFAULT FALSE NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);

-- Customer Profile Table
CREATE TABLE users_customerprofile (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL REFERENCES users_user(id) ON DELETE CASCADE,
    default_address TEXT,
    city VARCHAR(100),
    postal_code VARCHAR(20),
    loyalty_points INTEGER DEFAULT 0 NOT NULL,
    total_orders INTEGER DEFAULT 0 NOT NULL,
    dietary_preferences TEXT,
    notification_preferences JSONB
);

-- Restaurant Profile Table
CREATE TABLE users_restaurantprofile (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL REFERENCES users_user(id) ON DELETE CASCADE,
    business_name VARCHAR(200) NOT NULL,
    pan_number VARCHAR(20),
    business_license VARCHAR(100),
    logo_image VARCHAR(100),
    banner_image VARCHAR(100),
    opening_time TIME,
    closing_time TIME,
    delivery_radius_km DECIMAL(5,2),
    is_verified BOOLEAN DEFAULT FALSE NOT NULL,
    is_approved BOOLEAN DEFAULT FALSE NOT NULL,
    total_revenue DECIMAL(12,2) DEFAULT 0.00 NOT NULL
);

-- Rider Profile Table
CREATE TABLE users_riderprofile (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL REFERENCES users_user(id) ON DELETE CASCADE,
    citizenship_number VARCHAR(50),
    vehicle_type VARCHAR(50),
    vehicle_number VARCHAR(20),
    vehicle_image VARCHAR(100),
    license_image VARCHAR(100),
    is_available BOOLEAN DEFAULT TRUE NOT NULL,
    current_latitude DECIMAL(9,6),
    current_longitude DECIMAL(9,6),
    total_earnings DECIMAL(12,2) DEFAULT 0.00 NOT NULL,
    rating DECIMAL(3,2) DEFAULT 0.00 NOT NULL,
    total_deliveries INTEGER DEFAULT 0 NOT NULL,
    is_verified BOOLEAN DEFAULT FALSE NOT NULL
);

-- Restaurant App Tables
-- =====================

-- Cuisine Table
CREATE TABLE restaurant_cuisine (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    image VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);

-- Restaurant Table
CREATE TABLE restaurant_restaurant (
    id SERIAL PRIMARY KEY,
    owner_id INTEGER NOT NULL REFERENCES users_user(id) ON DELETE CASCADE,
    name VARCHAR(200) NOT NULL,
    slug VARCHAR(200) UNIQUE NOT NULL,
    description TEXT,
    image VARCHAR(100),
    cover_image VARCHAR(100),
    address TEXT NOT NULL,
    city VARCHAR(100) NOT NULL,
    latitude DECIMAL(9,6),
    longitude DECIMAL(9,6),
    phone VARCHAR(20),
    email VARCHAR(254),
    cuisine_id INTEGER REFERENCES restaurant_cuisine(id) ON DELETE SET NULL,
    is_featured BOOLEAN DEFAULT FALSE NOT NULL,
    is_verified BOOLEAN DEFAULT FALSE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    average_rating DECIMAL(3,2) DEFAULT 0.00 NOT NULL,
    total_reviews INTEGER DEFAULT 0 NOT NULL,
    preparation_time_min INTEGER DEFAULT 15 NOT NULL,
    delivery_fee DECIMAL(8,2) DEFAULT 50.00 NOT NULL,
    minimum_order DECIMAL(8,2) DEFAULT 100.00 NOT NULL,
    opening_time TIME,
    closing_time TIME,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);

-- Food Item Table
CREATE TABLE restaurant_fooditem (
    id SERIAL PRIMARY KEY,
    restaurant_id INTEGER NOT NULL REFERENCES restaurant_restaurant(id) ON DELETE CASCADE,
    name VARCHAR(200) NOT NULL,
    slug VARCHAR(200) NOT NULL,
    description TEXT,
    image VARCHAR(100),
    price DECIMAL(8,2) NOT NULL,
    discount_price DECIMAL(8,2),
    category VARCHAR(100),
    is_veg BOOLEAN DEFAULT FALSE NOT NULL,
    is_spicy BOOLEAN DEFAULT FALSE NOT NULL,
    is_available BOOLEAN DEFAULT TRUE NOT NULL,
    preparation_time INTEGER DEFAULT 15,
    calories INTEGER,
    average_rating DECIMAL(3,2) DEFAULT 0.00 NOT NULL,
    total_orders INTEGER DEFAULT 0 NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);

-- Favorite Table
CREATE TABLE restaurant_favorite (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users_user(id) ON DELETE CASCADE,
    restaurant_id INTEGER NOT NULL REFERENCES restaurant_restaurant(id) ON DELETE CASCADE,
    created_at TIMESTAMP NOT NULL,
    UNIQUE(user_id, restaurant_id)
);

-- Review Table
CREATE TABLE restaurant_review (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users_user(id) ON DELETE CASCADE,
    restaurant_id INTEGER NOT NULL REFERENCES restaurant_restaurant(id) ON DELETE CASCADE,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    UNIQUE(user_id, restaurant_id)
);

-- Orders App Tables
-- =================

-- Order Table
CREATE TABLE orders_order (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users_user(id) ON DELETE CASCADE,
    restaurant_id INTEGER NOT NULL REFERENCES restaurant_restaurant(id) ON DELETE CASCADE,
    order_number VARCHAR(50) UNIQUE NOT NULL,
    status VARCHAR(20) NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL,
    delivery_fee DECIMAL(8,2) NOT NULL,
    discount_amount DECIMAL(8,2) DEFAULT 0.00 NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    payment_method VARCHAR(50) NOT NULL,
    payment_status VARCHAR(20) NOT NULL,
    delivery_address TEXT NOT NULL,
    delivery_city VARCHAR(100) NOT NULL,
    delivery_latitude DECIMAL(9,6),
    delivery_longitude DECIMAL(9,6),
    special_instructions TEXT,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);

-- Order Item Table
CREATE TABLE orders_orderitem (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES orders_order(id) ON DELETE CASCADE,
    food_item_id INTEGER NOT NULL REFERENCES restaurant_fooditem(id) ON DELETE CASCADE,
    quantity INTEGER NOT NULL,
    price DECIMAL(8,2) NOT NULL,
    subtotal DECIMAL(8,2) NOT NULL,
    special_instructions TEXT
);

-- Order Tracking Table
CREATE TABLE orders_ordertracking (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES orders_order(id) ON DELETE CASCADE,
    status VARCHAR(20) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    notes TEXT,
    location_latitude DECIMAL(9,6),
    location_longitude DECIMAL(9,6)
);

-- Support Ticket Table
CREATE TABLE orders_supportticket (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users_user(id) ON DELETE CASCADE,
    order_id INTEGER REFERENCES orders_order(id) ON DELETE SET NULL,
    subject VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    status VARCHAR(20) NOT NULL,
    priority VARCHAR(20) NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);

-- Payments App Tables
-- ===================

-- Payment Method Table
CREATE TABLE payments_paymentmethod (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users_user(id) ON DELETE CASCADE,
    method_type VARCHAR(50) NOT NULL,
    provider VARCHAR(50),
    account_number VARCHAR(100),
    is_default BOOLEAN DEFAULT FALSE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP NOT NULL
);

-- Payment Table
CREATE TABLE payments_payment (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES orders_order(id) ON DELETE CASCADE,
    payment_method VARCHAR(50) NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    transaction_id VARCHAR(100),
    status VARCHAR(20) NOT NULL,
    payment_date TIMESTAMP NOT NULL,
    response_data JSONB
);

-- Invoice Table
CREATE TABLE payments_invoice (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES orders_order(id) ON DELETE CASCADE,
    invoice_number VARCHAR(50) UNIQUE NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    tax_amount DECIMAL(8,2) DEFAULT 0.00 NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    status VARCHAR(20) NOT NULL,
    due_date TIMESTAMP,
    paid_date TIMESTAMP,
    created_at TIMESTAMP NOT NULL
);

-- Coupon Table
CREATE TABLE payments_coupon (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    discount_type VARCHAR(20) NOT NULL,
    discount_value DECIMAL(8,2) NOT NULL,
    minimum_order DECIMAL(8,2) DEFAULT 0.00 NOT NULL,
    max_discount DECIMAL(8,2),
    usage_limit INTEGER,
    used_count INTEGER DEFAULT 0 NOT NULL,
    valid_from TIMESTAMP NOT NULL,
    valid_until TIMESTAMP NOT NULL,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP NOT NULL
);

-- Partners App Tables
-- ====================

-- Partner Subscription Table
CREATE TABLE partners_partnersubscription (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    duration_days INTEGER NOT NULL,
    features JSONB,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);

-- Restaurant Partner Table
CREATE TABLE partners_restaurantpartner (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users_user(id) ON DELETE CASCADE,
    subscription_id INTEGER REFERENCES partners_partnersubscription(id) ON DELETE SET NULL,
    start_date TIMESTAMP NOT NULL,
    end_date TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    auto_renew BOOLEAN DEFAULT FALSE NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);

-- Restaurant Earnings Table
CREATE TABLE partners_restauranlearnings (
    id SERIAL PRIMARY KEY,
    restaurant_id INTEGER NOT NULL REFERENCES restaurant_restaurant(id) ON DELETE CASCADE,
    order_id INTEGER NOT NULL REFERENCES orders_order(id) ON DELETE CASCADE,
    order_amount DECIMAL(10,2) NOT NULL,
    commission_amount DECIMAL(8,2) NOT NULL,
    net_amount DECIMAL(10,2) NOT NULL,
    earning_date TIMESTAMP NOT NULL,
    created_at TIMESTAMP NOT NULL
);

-- Riders App Tables
-- =================

-- Rider Table
CREATE TABLE riders_rider (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users_user(id) ON DELETE CASCADE,
    vehicle_type VARCHAR(50) NOT NULL,
    vehicle_number VARCHAR(20) NOT NULL,
    license_number VARCHAR(50),
    is_available BOOLEAN DEFAULT TRUE NOT NULL,
    current_latitude DECIMAL(9,6),
    current_longitude DECIMAL(9,6),
    rating DECIMAL(3,2) DEFAULT 0.00 NOT NULL,
    total_deliveries INTEGER DEFAULT 0 NOT NULL,
    total_earnings DECIMAL(12,2) DEFAULT 0.00 NOT NULL,
    is_verified BOOLEAN DEFAULT FALSE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);

-- Delivery Table
CREATE TABLE riders_delivery (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES orders_order(id) ON DELETE CASCADE,
    rider_id INTEGER NOT NULL REFERENCES riders_rider(id) ON DELETE CASCADE,
    status VARCHAR(20) NOT NULL,
    pickup_latitude DECIMAL(9,6),
    pickup_longitude DECIMAL(9,6),
    delivery_latitude DECIMAL(9,6),
    delivery_longitude DECIMAL(9,6),
    pickup_time TIMESTAMP,
    delivery_time TIMESTAMP,
    distance_km DECIMAL(8,2),
    delivery_fee DECIMAL(8,2) NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);

-- Rider Earnings Table
CREATE TABLE riders_riderearnings (
    id SERIAL PRIMARY KEY,
    rider_id INTEGER NOT NULL REFERENCES riders_rider(id) ON DELETE CASCADE,
    delivery_id INTEGER NOT NULL REFERENCES riders_delivery(id) ON DELETE CASCADE,
    order_id INTEGER NOT NULL REFERENCES orders_order(id) ON DELETE CASCADE,
    amount DECIMAL(8,2) NOT NULL,
    tip_amount DECIMAL(8,2) DEFAULT 0.00 NOT NULL,
    total_amount DECIMAL(8,2) NOT NULL,
    earning_date TIMESTAMP NOT NULL,
    created_at TIMESTAMP NOT NULL
);

-- Core App Tables
-- ===============

-- Test Table (for development)
CREATE TABLE core_test (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

-- Create Indexes for Performance
-- ===============================

CREATE INDEX idx_users_user_email ON users_user(email);
CREATE INDEX idx_users_user_role ON users_user(role);
CREATE INDEX idx_restaurant_restaurant_slug ON restaurant_restaurant(slug);
CREATE INDEX idx_restaurant_restaurant_city ON restaurant_restaurant(city);
CREATE INDEX idx_restaurant_fooditem_restaurant ON restaurant_fooditem(restaurant_id);
CREATE INDEX idx_orders_order_user ON orders_order(user_id);
CREATE INDEX idx_orders_order_restaurant ON orders_order(restaurant_id);
CREATE INDEX idx_orders_order_status ON orders_order(status);
CREATE INDEX idx_payments_payment_order ON payments_payment(order_id);
CREATE INDEX idx_riders_delivery_rider ON riders_delivery(rider_id);
CREATE INDEX idx_riders_delivery_status ON riders_delivery(status);
