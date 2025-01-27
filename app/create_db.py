import sqlite3
import os

# Paths for database and initial data
DATABASE_PATH = os.path.join("app", "database.sqlite3")
SEATS_CSV_PATH = os.path.join("data", "seats.csv")

def initialize_database():
    """Create tables and initialize the database."""
    # Ensure the app directory exists
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)

    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    # Create Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            is_admin BOOLEAN DEFAULT 0
        )
    """)

    # Create Seats table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS seats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            seat_number TEXT NOT NULL,
            class_type TEXT NOT NULL,
            price REAL NOT NULL,
            status TEXT DEFAULT 'available'
        )
    """)

    # Populate Seats table with initial data
    populate_seats(cursor)

    connection.commit()
    connection.close()
    print("Database initialized successfully!")

def populate_seats(cursor):
    """Populate seats table from seats.csv."""
    if not os.path.exists(SEATS_CSV_PATH):
        print(f"Missing {SEATS_CSV_PATH}, skipping seat population.")
        return

    with open(SEATS_CSV_PATH, "r") as file:
        header = next(file)  # Skip the header
        for line_number, line in enumerate(file, start=2):
            values = line.strip().split(",")
            if len(values) != 4:
                print(f"Skipping invalid row at line {line_number}: {line.strip()}")
                continue

            seat_number, class_type, price, status = values
            try:
                cursor.execute("""
                    INSERT INTO seats (seat_number, class_type, price, status)
                    VALUES (?, ?, ?, ?)
                """, (seat_number, class_type, float(price), status))
            except Exception as e:
                print(f"Error inserting row at line {line_number}: {e}")

if __name__ == "__main__":
    initialize_database()