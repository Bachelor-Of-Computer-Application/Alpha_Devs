-- QuickBite Initial Subscription Plans
-- This file creates the initial subscription plans for restaurants and riders

-- Restaurant Monthly Plan (NPR 10,000/month)
INSERT INTO partners_subscriptionplan (name, plan_type, price, duration_days, features, max_menu_items, max_orders_per_day, priority_listing, analytics_access, promotional_boosts, is_active, is_featured, created_at, updated_at)
VALUES (
    'Restaurant Monthly Plan',
    'RESTAURANT_MONTHLY',
    10000.00,
    30,
    '{"unlimited_menu_uploads": true, "analytics_dashboard": true, "priority_listing": false, "order_management": true, "customer_insights": true}',
    100,
    100,
    false,
    true,
    0,
    true,
    false,
    NOW(),
    NOW()
);

-- Restaurant Yearly Plan (NPR 100,000/year - 2 months free)
INSERT INTO partners_subscriptionplan (name, plan_type, price, duration_days, features, max_menu_items, max_orders_per_day, priority_listing, analytics_access, promotional_boosts, is_active, is_featured, created_at, updated_at)
VALUES (
    'Restaurant Yearly Plan',
    'RESTAURANT_YEARLY',
    100000.00,
    365,
    '{"unlimited_menu_uploads": true, "analytics_dashboard": true, "priority_listing": true, "order_management": true, "customer_insights": true, "promotional_boosts": 5, "featured_placement": true}',
    500,
    500,
    true,
    true,
    5,
    true,
    true,
    NOW(),
    NOW()
);

-- Rider Monthly Plan (NPR 1,000/month)
INSERT INTO partners_subscriptionplan (name, plan_type, price, duration_days, features, max_menu_items, max_orders_per_day, priority_listing, analytics_access, promotional_boosts, is_active, is_featured, created_at, updated_at)
VALUES (
    'Rider Monthly Plan',
    'RIDER_MONTHLY',
    1000.00,
    30,
    '{"delivery_access": true, "rider_dashboard": true, "earnings_analytics": true, "priority_delivery_allocation": true}',
    0,
    50,
    false,
    true,
    0,
    true,
    false,
    NOW(),
    NOW()
);
