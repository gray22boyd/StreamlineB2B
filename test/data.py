# Fake data for all tables (tuple format for executemany)

staff_data = [
    (1, "John Doe", "john.doe@example.com", "1234567890", "123 Main St, Anytown, USA", "Anytown", "CA", "Manager", 75000.00, "2021-01-01", "Management", None),
    (2, "Jane Smith", "jane.smith@example.com", "0987654321", "456 Oak Ave, Somewhere, USA", "Somewhere", "NY", "Staff", 50000.00, "2021-02-15", "Sales", 1),
    (3, "Mike Johnson", "mike.johnson@example.com", "5551234567", "789 Pine Rd, Elsewhere, USA", "Elsewhere", "TX", "Staff", 45000.00, "2021-03-20", "Operations", 1),
    (4, "Sarah Wilson", "sarah.wilson@example.com", "5559876543", "321 Elm St, Nowhere, USA", "Nowhere", "FL", "Staff", 48000.00, "2021-04-10", "Customer Service", 1),
    (5, "David Brown", "david.brown@example.com", "5554567890", "654 Maple Dr, Anywhere, USA", "Anywhere", "WA", "Staff", 52000.00, "2021-05-05", "Sales", 1)
]

customers_data = [
    (1, "Alice Cooper", "alice.cooper@email.com", "1112223333", "100 Customer Lane, Client City, USA", "Client City", "CA"),
    (2, "Bob Wilson", "bob.wilson@email.com", "2223334444", "200 Client Street, Customer Town, USA", "Customer Town", "NY"),
    (3, "Carol Davis", "carol.davis@email.com", "3334445555", "300 Patron Ave, Guest City, USA", "Guest City", "TX"),
    (4, "Dan Miller", "dan.miller@email.com", "4445556666", "400 User Road, Visitor Town, USA", "Visitor Town", "FL"),
    (5, "Eva Garcia", "eva.garcia@email.com", "5556667777", "500 Member Drive, Subscriber City, USA", "Subscriber City", "WA"),
    (6, "Frank Lee", "frank.lee@email.com", "6667778888", "600 Customer Circle, Client Village, USA", "Client Village", "OR"),
    (7, "Grace Taylor", "grace.taylor@email.com", "7778889999", "700 Patron Place, Guest Town, USA", "Guest Town", "AZ"),
    (8, "Henry Anderson", "henry.anderson@email.com", "8889990000", "800 User Way, Visitor City, USA", "Visitor City", "NV")
]

inventory_data = [
    (1, "Godlf Club Set", "Professional golf club set with 14 clubs", 899.99, 25, "Equipment", 5),
    (2, "Golf Balls (Dozen)", "Premium golf balls, 12 count", 24.99, 100, "Consumables", 20),
    (3, "Golf Cart", "Electric golf cart for course use", 2500.00, 15, "Equipment", 3),
    (4, "Golf Tees", "Wooden golf tees, 100 count", 5.99, 200, "Consumables", 50),
    (5, "Golf Gloves", "Leather golf gloves, various sizes", 19.99, 75, "Apparel", 15),
    (6, "Golf Bag", "Stand golf bag with multiple pockets", 149.99, 30, "Equipment", 8),
    (7, "Golf Towels", "Microfiber golf towels, 3 pack", 12.99, 60, "Accessories", 12),
    (8, "Golf Umbrella", "Large golf umbrella with stand", 34.99, 40, "Accessories", 10)
]

maintenance_data = [
    (1, 1, "2024-01-15", "Greens maintenance and mowing", 2500.00, 3),
    (2, 1, "2024-01-20", "Bunker sand replacement", 1800.00, 3),
    (3, 2, "2024-02-01", "Irrigation system repair", 3200.00, 3),
    (4, 1, "2024-02-10", "Tree trimming and removal", 1500.00, 3),
    (5, 2, "2024-02-15", "Cart path repairs", 2100.00, 3),
    (6, 1, "2024-03-01", "Fertilizer application", 900.00, 3),
    (7, 2, "2024-03-10", "Pest control treatment", 1200.00, 3),
    (8, 1, "2024-03-20", "Equipment maintenance", 800.00, 3)
]

events_data = [
    (1, "Spring Golf Tournament", "2024-04-15"),
    (2, "Corporate Golf Outing", "2024-05-20"),
    (3, "Junior Golf Camp", "2024-06-10"),
    (4, "Ladies Golf League", "2024-07-05"),
    (5, "Charity Golf Classic", "2024-08-12"),
    (6, "Fall Championship", "2024-09-25"),
    (7, "Holiday Golf Scramble", "2024-12-15"),
    (8, "New Year's Golf Tournament", "2025-01-02")
]

bookings_data = [
    (1, 1, "BK001", "2024-01-15", 125.00),
    (2, 2, "BK002", "2024-01-16", 150.00),
    (3, 3, "BK003", "2024-01-17", 200.00),
    (4, 4, "BK004", "2024-01-18", 175.00),
    (5, 5, "BK005", "2024-01-19", 225.00),
    (6, 6, "BK006", "2024-01-20", 300.00),
    (7, 7, "BK007", "2024-01-21", 250.00),
    (8, 8, "BK008", "2024-01-22", 180.00),
    (9, 1, "BK009", "2024-01-23", 140.00),
    (10, 2, "BK010", "2024-01-24", 160.00),
    (11, 3, "BK011", "2024-01-25", 190.00),
    (12, 4, "BK012", "2024-01-26", 210.00)
]
