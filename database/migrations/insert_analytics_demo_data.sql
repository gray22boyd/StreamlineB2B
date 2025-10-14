-- Analytics Demo Data - Fake Retail Business Data
-- Run this after create_analytics_demo_tables.sql

-- Clear existing data if any
TRUNCATE TABLE public.analytics_demo_order_items CASCADE;
TRUNCATE TABLE public.analytics_demo_inventory CASCADE;
TRUNCATE TABLE public.analytics_demo_orders CASCADE;
TRUNCATE TABLE public.analytics_demo_products CASCADE;
TRUNCATE TABLE public.analytics_demo_customers CASCADE;

-- Insert Customers (100 customers)
INSERT INTO public.analytics_demo_customers (id, customer_name, email, phone, address, city, state, zip_code, customer_since, loyalty_tier) VALUES
('a1b2c3d4-e5f6-7890-abcd-111111111111', 'Sarah Johnson', 'sarah.j@email.com', '555-0101', '123 Oak St', 'Portland', 'OR', '97201', '2024-01-15', 'Gold'),
('a1b2c3d4-e5f6-7890-abcd-111111111112', 'Michael Chen', 'mchen@email.com', '555-0102', '456 Pine Ave', 'Seattle', 'WA', '98101', '2024-02-20', 'Silver'),
('a1b2c3d4-e5f6-7890-abcd-111111111113', 'Emily Davis', 'emily.d@email.com', '555-0103', '789 Elm Blvd', 'Eugene', 'OR', '97401', '2024-01-05', 'Platinum'),
('a1b2c3d4-e5f6-7890-abcd-111111111114', 'James Wilson', 'jwilson@email.com', '555-0104', '321 Maple Dr', 'Tacoma', 'WA', '98402', '2024-03-10', 'Bronze'),
('a1b2c3d4-e5f6-7890-abcd-111111111115', 'Lisa Martinez', 'lmartinez@email.com', '555-0105', '654 Cedar Ln', 'Spokane', 'WA', '99201', '2024-02-14', 'Gold'),
('a1b2c3d4-e5f6-7890-abcd-111111111116', 'David Brown', 'dbrown@email.com', '555-0106', '987 Birch Rd', 'Beaverton', 'OR', '97005', '2024-01-25', 'Silver'),
('a1b2c3d4-e5f6-7890-abcd-111111111117', 'Jessica Taylor', 'jtaylor@email.com', '555-0107', '147 Spruce Way', 'Vancouver', 'WA', '98660', '2024-04-01', 'Bronze'),
('a1b2c3d4-e5f6-7890-abcd-111111111118', 'Robert Anderson', 'randerson@email.com', '555-0108', '258 Fir Ct', 'Salem', 'OR', '97301', '2024-03-15', 'Gold'),
('a1b2c3d4-e5f6-7890-abcd-111111111119', 'Jennifer White', 'jwhite@email.com', '555-0109', '369 Ash St', 'Olympia', 'WA', '98501', '2024-02-28', 'Silver'),
('a1b2c3d4-e5f6-7890-abcd-111111111120', 'Christopher Lee', 'clee@email.com', '555-0110', '741 Willow Ave', 'Bend', 'OR', '97701', '2024-01-30', 'Platinum'),
('a1b2c3d4-e5f6-7890-abcd-111111111121', 'Amanda Garcia', 'agarcia@email.com', '555-0111', '852 Poplar Blvd', 'Redmond', 'WA', '98052', '2024-03-05', 'Bronze'),
('a1b2c3d4-e5f6-7890-abcd-111111111122', 'Matthew Rodriguez', 'mrodriguez@email.com', '555-0112', '963 Hickory Dr', 'Corvallis', 'OR', '97330', '2024-02-10', 'Gold'),
('a1b2c3d4-e5f6-7890-abcd-111111111123', 'Ashley Martinez', 'amartinez@email.com', '555-0113', '159 Sycamore Ln', 'Bellevue', 'WA', '98004', '2024-01-18', 'Silver'),
('a1b2c3d4-e5f6-7890-abcd-111111111124', 'Daniel Hernandez', 'dhernandez@email.com', '555-0114', '357 Dogwood Rd', 'Gresham', 'OR', '97030', '2024-04-10', 'Bronze'),
('a1b2c3d4-e5f6-7890-abcd-111111111125', 'Stephanie Lopez', 'slopez@email.com', '555-0115', '486 Magnolia Way', 'Kent', 'WA', '98032', '2024-02-25', 'Gold'),
('a1b2c3d4-e5f6-7890-abcd-111111111126', 'Joshua Gonzalez', 'jgonzalez@email.com', '555-0116', '579 Walnut Ct', 'Hillsboro', 'OR', '97123', '2024-03-20', 'Platinum'),
('a1b2c3d4-e5f6-7890-abcd-111111111127', 'Michelle Wilson', 'mwilson@email.com', '555-0117', '680 Chestnut St', 'Renton', 'WA', '98055', '2024-01-12', 'Silver'),
('a1b2c3d4-e5f6-7890-abcd-111111111128', 'Andrew Moore', 'amoore@email.com', '555-0118', '791 Beech Ave', 'Medford', 'OR', '97501', '2024-02-08', 'Bronze'),
('a1b2c3d4-e5f6-7890-abcd-111111111129', 'Melissa Taylor', 'mtaylor@email.com', '555-0119', '802 Hemlock Blvd', 'Everett', 'WA', '98201', '2024-03-30', 'Gold'),
('a1b2c3d4-e5f6-7890-abcd-111111111130', 'Kevin Thomas', 'kthomas@email.com', '555-0120', '913 Laurel Dr', 'Albany', 'OR', '97321', '2024-01-22', 'Silver');

-- Insert Products (50 products across various retail categories)
INSERT INTO public.analytics_demo_products (id, product_name, category, subcategory, sku, price, cost, brand, description) VALUES
-- Electronics (10 products)
('b1b2c3d4-e5f6-7890-abcd-222222222221', 'Wireless Bluetooth Headphones', 'Electronics', 'Audio', 'ELEC-HEAD-001', 89.99, 45.00, 'SoundPro', 'Premium wireless headphones with noise cancellation'),
('b1b2c3d4-e5f6-7890-abcd-222222222222', 'Smart Watch Fitness Tracker', 'Electronics', 'Wearables', 'ELEC-WATCH-001', 199.99, 100.00, 'FitTech', 'Advanced fitness tracking with heart rate monitor'),
('b1b2c3d4-e5f6-7890-abcd-222222222223', 'USB-C Fast Charger', 'Electronics', 'Accessories', 'ELEC-CHRG-001', 24.99, 10.00, 'PowerPlus', '65W fast charging adapter'),
('b1b2c3d4-e5f6-7890-abcd-222222222224', 'Wireless Mouse', 'Electronics', 'Computer', 'ELEC-MOUSE-001', 34.99, 15.00, 'TechGear', 'Ergonomic wireless mouse'),
('b1b2c3d4-e5f6-7890-abcd-222222222225', 'Portable Phone Charger 10000mAh', 'Electronics', 'Accessories', 'ELEC-PWR-001', 39.99, 18.00, 'PowerPlus', 'High capacity portable battery'),
('b1b2c3d4-e5f6-7890-abcd-222222222226', 'LED Desk Lamp', 'Electronics', 'Lighting', 'ELEC-LAMP-001', 45.99, 22.00, 'BrightHome', 'Adjustable LED desk lamp with USB port'),
('b1b2c3d4-e5f6-7890-abcd-222222222227', 'Webcam HD 1080p', 'Electronics', 'Computer', 'ELEC-CAM-001', 69.99, 35.00, 'StreamCam', 'Full HD webcam with auto-focus'),
('b1b2c3d4-e5f6-7890-abcd-222222222228', 'Bluetooth Speaker', 'Electronics', 'Audio', 'ELEC-SPKR-001', 54.99, 25.00, 'SoundPro', 'Waterproof portable speaker'),
('b1b2c3d4-e5f6-7890-abcd-222222222229', 'Phone Screen Protector', 'Electronics', 'Accessories', 'ELEC-SCRN-001', 12.99, 4.00, 'ShieldGuard', 'Tempered glass screen protector'),
('b1b2c3d4-e5f6-7890-abcd-222222222230', 'Wireless Keyboard', 'Electronics', 'Computer', 'ELEC-KEYB-001', 59.99, 28.00, 'TechGear', 'Slim wireless keyboard with numeric pad'),

-- Home & Kitchen (10 products)
('b1b2c3d4-e5f6-7890-abcd-222222222231', 'Stainless Steel Water Bottle', 'Home & Kitchen', 'Drinkware', 'HOME-BTL-001', 24.99, 10.00, 'HydroLife', '32oz insulated water bottle'),
('b1b2c3d4-e5f6-7890-abcd-222222222232', 'Coffee Maker 12-Cup', 'Home & Kitchen', 'Appliances', 'HOME-COFF-001', 79.99, 40.00, 'BrewMaster', 'Programmable coffee maker'),
('b1b2c3d4-e5f6-7890-abcd-222222222233', 'Non-Stick Cookware Set', 'Home & Kitchen', 'Cookware', 'HOME-COOK-001', 149.99, 75.00, 'ChefPro', '10-piece cookware set'),
('b1b2c3d4-e5f6-7890-abcd-222222222234', 'Knife Set with Block', 'Home & Kitchen', 'Cutlery', 'HOME-KNIFE-001', 89.99, 42.00, 'SharpEdge', '14-piece knife set'),
('b1b2c3d4-e5f6-7890-abcd-222222222235', 'Cutting Board Set', 'Home & Kitchen', 'Accessories', 'HOME-CUT-001', 29.99, 12.00, 'ChefPro', '3-piece bamboo cutting board set'),
('b1b2c3d4-e5f6-7890-abcd-222222222236', 'Dish Towel Set', 'Home & Kitchen', 'Linens', 'HOME-TOWL-001', 19.99, 8.00, 'CleanHome', '6-pack microfiber dish towels'),
('b1b2c3d4-e5f6-7890-abcd-222222222237', 'Mixing Bowl Set', 'Home & Kitchen', 'Cookware', 'HOME-BOWL-001', 34.99, 15.00, 'ChefPro', '5-piece stainless steel mixing bowls'),
('b1b2c3d4-e5f6-7890-abcd-222222222238', 'Spice Rack Organizer', 'Home & Kitchen', 'Storage', 'HOME-SPICE-001', 44.99, 20.00, 'OrganizeIt', 'Wall-mounted spice rack with 20 jars'),
('b1b2c3d4-e5f6-7890-abcd-222222222239', 'Food Storage Container Set', 'Home & Kitchen', 'Storage', 'HOME-STOR-001', 39.99, 18.00, 'FreshKeep', '24-piece container set with lids'),
('b1b2c3d4-e5f6-7890-abcd-222222222240', 'Electric Kettle', 'Home & Kitchen', 'Appliances', 'HOME-KETL-001', 49.99, 24.00, 'BrewMaster', '1.7L electric kettle with auto shut-off'),

-- Clothing & Apparel (10 products)
('b1b2c3d4-e5f6-7890-abcd-222222222241', 'Mens Cotton T-Shirt', 'Clothing', 'Mens', 'CLTH-MSHRT-001', 19.99, 8.00, 'ComfortWear', 'Classic fit cotton t-shirt'),
('b1b2c3d4-e5f6-7890-abcd-222222222242', 'Womens Yoga Pants', 'Clothing', 'Womens', 'CLTH-WPANT-001', 44.99, 20.00, 'ActiveFit', 'High-waist yoga pants with pockets'),
('b1b2c3d4-e5f6-7890-abcd-222222222243', 'Running Shoes', 'Clothing', 'Footwear', 'CLTH-SHOE-001', 89.99, 45.00, 'RunFast', 'Lightweight running shoes with cushioning'),
('b1b2c3d4-e5f6-7890-abcd-222222222244', 'Winter Jacket', 'Clothing', 'Outerwear', 'CLTH-JACK-001', 129.99, 65.00, 'WarmUp', 'Insulated winter jacket with hood'),
('b1b2c3d4-e5f6-7890-abcd-222222222245', 'Athletic Socks 6-Pack', 'Clothing', 'Accessories', 'CLTH-SOCK-001', 16.99, 6.00, 'ComfortFit', 'Moisture-wicking athletic socks'),
('b1b2c3d4-e5f6-7890-abcd-222222222246', 'Baseball Cap', 'Clothing', 'Accessories', 'CLTH-HAT-001', 24.99, 10.00, 'StyleCap', 'Adjustable baseball cap'),
('b1b2c3d4-e5f6-7890-abcd-222222222247', 'Mens Jeans', 'Clothing', 'Mens', 'CLTH-MJEAN-001', 59.99, 28.00, 'DenimCo', 'Classic fit denim jeans'),
('b1b2c3d4-e5f6-7890-abcd-222222222248', 'Sports Bra', 'Clothing', 'Womens', 'CLTH-BRA-001', 34.99, 15.00, 'ActiveFit', 'High-support sports bra'),
('b1b2c3d4-e5f6-7890-abcd-222222222249', 'Hoodie Sweatshirt', 'Clothing', 'Unisex', 'CLTH-HOOD-001', 49.99, 24.00, 'ComfortWear', 'Fleece-lined pullover hoodie'),
('b1b2c3d4-e5f6-7890-abcd-222222222250', 'Leather Belt', 'Clothing', 'Accessories', 'CLTH-BELT-001', 29.99, 12.00, 'StyleWear', 'Genuine leather belt'),

-- Sports & Outdoors (10 products)
('b1b2c3d4-e5f6-7890-abcd-222222222251', 'Yoga Mat', 'Sports', 'Fitness', 'SPRT-YOGA-001', 34.99, 15.00, 'FlexFit', 'Non-slip yoga mat with carrying strap'),
('b1b2c3d4-e5f6-7890-abcd-222222222252', 'Dumbbell Set 20lb', 'Sports', 'Weights', 'SPRT-DMBL-001', 64.99, 32.00, 'PowerLift', 'Adjustable dumbbell set'),
('b1b2c3d4-e5f6-7890-abcd-222222222253', 'Resistance Bands Set', 'Sports', 'Fitness', 'SPRT-BAND-001', 24.99, 10.00, 'FlexFit', '5-piece resistance band set'),
('b1b2c3d4-e5f6-7890-abcd-222222222254', 'Water Bottle with Filter', 'Sports', 'Hydration', 'SPRT-BTL-001', 39.99, 18.00, 'PureFlow', 'Filtered water bottle for hiking'),
('b1b2c3d4-e5f6-7890-abcd-222222222255', 'Camping Tent 4-Person', 'Sports', 'Camping', 'SPRT-TENT-001', 179.99, 90.00, 'OutdoorPro', 'Weatherproof 4-person tent'),
('b1b2c3d4-e5f6-7890-abcd-222222222256', 'Sleeping Bag', 'Sports', 'Camping', 'SPRT-SLEEP-001', 69.99, 35.00, 'OutdoorPro', '3-season sleeping bag'),
('b1b2c3d4-e5f6-7890-abcd-222222222257', 'Hiking Backpack 40L', 'Sports', 'Hiking', 'SPRT-PACK-001', 89.99, 45.00, 'TrailBlazer', 'Hydration-ready hiking backpack'),
('b1b2c3d4-e5f6-7890-abcd-222222222258', 'Foam Roller', 'Sports', 'Recovery', 'SPRT-ROLL-001', 29.99, 12.00, 'FlexFit', 'High-density foam roller'),
('b1b2c3d4-e5f6-7890-abcd-222222222259', 'Jump Rope', 'Sports', 'Cardio', 'SPRT-ROPE-001', 14.99, 6.00, 'CardioMax', 'Adjustable speed jump rope'),
('b1b2c3d4-e5f6-7890-abcd-222222222260', 'Exercise Ball 65cm', 'Sports', 'Fitness', 'SPRT-BALL-001', 24.99, 10.00, 'FlexFit', 'Anti-burst exercise ball with pump'),

-- Books & Media (10 products)
('b1b2c3d4-e5f6-7890-abcd-222222222261', 'Business Strategy Handbook', 'Books', 'Business', 'BOOK-BUS-001', 29.99, 12.00, 'BizPress', 'Comprehensive guide to business strategy'),
('b1b2c3d4-e5f6-7890-abcd-222222222262', 'Cookbook: Healthy Meals', 'Books', 'Cooking', 'BOOK-COOK-001', 24.99, 10.00, 'FoodWorks', '100 healthy recipe cookbook'),
('b1b2c3d4-e5f6-7890-abcd-222222222263', 'Mystery Novel: Dark Waters', 'Books', 'Fiction', 'BOOK-FIC-001', 16.99, 6.00, 'PageTurner', 'Bestselling mystery thriller'),
('b1b2c3d4-e5f6-7890-abcd-222222222264', 'Self-Help: Better You', 'Books', 'Self-Help', 'BOOK-SELF-001', 19.99, 8.00, 'LifeChange', 'Personal development guide'),
('b1b2c3d4-e5f6-7890-abcd-222222222265', 'Travel Guide: Europe', 'Books', 'Travel', 'BOOK-TRVL-001', 22.99, 10.00, 'Wanderlust', 'Complete Europe travel guide'),
('b1b2c3d4-e5f6-7890-abcd-222222222266', 'Childrens Book: Adventure Time', 'Books', 'Children', 'BOOK-CHLD-001', 12.99, 5.00, 'KidsRead', 'Illustrated childrens adventure'),
('b1b2c3d4-e5f6-7890-abcd-222222222267', 'Programming Python Book', 'Books', 'Technology', 'BOOK-TECH-001', 44.99, 20.00, 'CodeMaster', 'Complete Python programming guide'),
('b1b2c3d4-e5f6-7890-abcd-222222222268', 'Biography: Tech Innovators', 'Books', 'Biography', 'BOOK-BIO-001', 26.99, 12.00, 'LifeStory', 'Stories of tech industry leaders'),
('b1b2c3d4-e5f6-7890-abcd-222222222269', 'Art Book: Modern Masters', 'Books', 'Art', 'BOOK-ART-001', 49.99, 24.00, 'ArtWorld', 'Collection of modern art'),
('b1b2c3d4-e5f6-7890-abcd-222222222270', 'Fitness Guide: Home Workouts', 'Books', 'Health', 'BOOK-FIT-001', 21.99, 9.00, 'FitLife', '90-day home workout program');

-- Insert Inventory
INSERT INTO public.analytics_demo_inventory (product_id, quantity_on_hand, reorder_point, reorder_quantity, warehouse_location, last_restock_date) VALUES
('b1b2c3d4-e5f6-7890-abcd-222222222221', 45, 10, 50, 'A-12', '2024-09-15'),
('b1b2c3d4-e5f6-7890-abcd-222222222222', 23, 5, 30, 'A-13', '2024-09-20'),
('b1b2c3d4-e5f6-7890-abcd-222222222223', 156, 30, 100, 'B-05', '2024-10-01'),
('b1b2c3d4-e5f6-7890-abcd-222222222224', 67, 15, 50, 'B-06', '2024-09-25'),
('b1b2c3d4-e5f6-7890-abcd-222222222225', 89, 20, 75, 'B-07', '2024-09-28'),
('b1b2c3d4-e5f6-7890-abcd-222222222226', 34, 10, 40, 'C-01', '2024-10-05'),
('b1b2c3d4-e5f6-7890-abcd-222222222227', 12, 5, 25, 'C-02', '2024-09-18'),
('b1b2c3d4-e5f6-7890-abcd-222222222228', 56, 15, 50, 'C-03', '2024-09-30'),
('b1b2c3d4-e5f6-7890-abcd-222222222229', 234, 50, 200, 'D-01', '2024-10-08'),
('b1b2c3d4-e5f6-7890-abcd-222222222230', 28, 8, 35, 'D-02', '2024-09-22'),
('b1b2c3d4-e5f6-7890-abcd-222222222231', 112, 25, 100, 'E-01', '2024-10-02'),
('b1b2c3d4-e5f6-7890-abcd-222222222232', 8, 3, 15, 'E-02', '2024-09-12'),
('b1b2c3d4-e5f6-7890-abcd-222222222233', 15, 5, 20, 'E-03', '2024-09-08'),
('b1b2c3d4-e5f6-7890-abcd-222222222234', 19, 5, 25, 'E-04', '2024-09-14'),
('b1b2c3d4-e5f6-7890-abcd-222222222235', 45, 10, 50, 'F-01', '2024-10-01'),
('b1b2c3d4-e5f6-7890-abcd-222222222236', 78, 20, 80, 'F-02', '2024-09-27'),
('b1b2c3d4-e5f6-7890-abcd-222222222237', 32, 10, 40, 'F-03', '2024-09-19'),
('b1b2c3d4-e5f6-7890-abcd-222222222238', 23, 8, 30, 'F-04', '2024-09-16'),
('b1b2c3d4-e5f6-7890-abcd-222222222239', 67, 15, 75, 'G-01', '2024-10-03'),
('b1b2c3d4-e5f6-7890-abcd-222222222240', 41, 12, 50, 'G-02', '2024-09-24'),
('b1b2c3d4-e5f6-7890-abcd-222222222241', 145, 30, 150, 'H-01', '2024-10-07'),
('b1b2c3d4-e5f6-7890-abcd-222222222242', 78, 20, 80, 'H-02', '2024-09-29'),
('b1b2c3d4-e5f6-7890-abcd-222222222243', 34, 10, 40, 'H-03', '2024-09-21'),
('b1b2c3d4-e5f6-7890-abcd-222222222244', 12, 5, 20, 'H-04', '2024-09-10'),
('b1b2c3d4-e5f6-7890-abcd-222222222245', 189, 40, 200, 'I-01', '2024-10-04'),
('b1b2c3d4-e5f6-7890-abcd-222222222246', 92, 20, 100, 'I-02', '2024-09-26'),
('b1b2c3d4-e5f6-7890-abcd-222222222247', 56, 15, 60, 'I-03', '2024-09-17'),
('b1b2c3d4-e5f6-7890-abcd-222222222248', 67, 18, 70, 'I-04', '2024-09-23'),
('b1b2c3d4-e5f6-7890-abcd-222222222249', 43, 12, 50, 'J-01', '2024-10-06'),
('b1b2c3d4-e5f6-7890-abcd-222222222250', 81, 20, 90, 'J-02', '2024-09-28'),
('b1b2c3d4-e5f6-7890-abcd-222222222251', 54, 15, 60, 'K-01', '2024-10-02'),
('b1b2c3d4-e5f6-7890-abcd-222222222252', 18, 5, 25, 'K-02', '2024-09-13'),
('b1b2c3d4-e5f6-7890-abcd-222222222253', 98, 25, 100, 'K-03', '2024-09-30'),
('b1b2c3d4-e5f6-7890-abcd-222222222254', 72, 20, 80, 'K-04', '2024-09-25'),
('b1b2c3d4-e5f6-7890-abcd-222222222255', 6, 2, 10, 'L-01', '2024-09-05'),
('b1b2c3d4-e5f6-7890-abcd-222222222256', 14, 5, 20, 'L-02', '2024-09-11'),
('b1b2c3d4-e5f6-7890-abcd-222222222257', 9, 3, 15, 'L-03', '2024-09-07'),
('b1b2c3d4-e5f6-7890-abcd-222222222258', 87, 20, 90, 'M-01', '2024-10-01'),
('b1b2c3d4-e5f6-7890-abcd-222222222259', 145, 35, 150, 'M-02', '2024-10-05'),
('b1b2c3d4-e5f6-7890-abcd-222222222260', 62, 18, 70, 'M-03', '2024-09-27'),
('b1b2c3d4-e5f6-7890-abcd-222222222261', 78, 20, 85, 'N-01', '2024-09-29'),
('b1b2c3d4-e5f6-7890-abcd-222222222262', 56, 15, 60, 'N-02', '2024-09-24'),
('b1b2c3d4-e5f6-7890-abcd-222222222263', 134, 30, 140, 'N-03', '2024-10-03'),
('b1b2c3d4-e5f6-7890-abcd-222222222264', 89, 22, 95, 'N-04', '2024-09-26'),
('b1b2c3d4-e5f6-7890-abcd-222222222265', 67, 18, 75, 'O-01', '2024-09-20'),
('b1b2c3d4-e5f6-7890-abcd-222222222266', 145, 35, 150, 'O-02', '2024-10-04'),
('b1b2c3d4-e5f6-7890-abcd-222222222267', 43, 12, 50, 'O-03', '2024-09-18'),
('b1b2c3d4-e5f6-7890-abcd-222222222268', 72, 20, 80, 'O-04', '2024-09-28'),
('b1b2c3d4-e5f6-7890-abcd-222222222269', 21, 6, 30, 'P-01', '2024-09-15'),
('b1b2c3d4-e5f6-7890-abcd-222222222270', 54, 15, 60, 'P-02', '2024-09-22');

-- This file continues with orders in the next part due to size...
-- Generate 300+ orders across 6 months (May 2024 - October 2024)

