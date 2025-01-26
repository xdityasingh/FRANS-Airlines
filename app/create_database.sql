-- Create the users table 
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL
);

-- Create the seats table
CREATE TABLE IF NOT EXISTS seats (
    seat_id INTEGER PRIMARY KEY AUTOINCREMENT,
    status TEXT NOT NULL,   -- e.g., 'available', 'reserved', 'ghost'
    category TEXT,          -- e.g., 'first', 'business', 'economy'
    price REAL              -- price of the seat
);

-- Insert example data for users 
INSERT INTO users (name, email) VALUES ('Admin User', 'admin@example.com');
INSERT INTO users (name, email) VALUES ('User One', 'user1@example.com');
-- create_database.sql
INSERT INTO users (id, name, email) VALUES (6, 'User2', 'user2@example.com');
INSERT INTO users (id, name, email) VALUES (7, 'User3', 'user3@example.com');
INSERT INTO users (id, name, email) VALUES (8, 'user4', 'user4@example.com');

-- Insert example data for seats
INSERT INTO seats (status, category, price) VALUES ('available', 'economy', 100.00);
INSERT INTO seats (status, category, price) VALUES ('reserved', 'business', 300.00);
INSERT INTO seats (status, category, price) VALUES ('available', 'first', 500.00);
INSERT INTO seats (status, category, price) VALUES ('reserved', 'economy', 120.00);
INSERT INTO seats (status, category, price) VALUES ('available', 'business', 400.00);
