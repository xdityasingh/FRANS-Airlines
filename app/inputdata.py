from flask import Flask, render_template, session, redirect, request, jsonify, g
import matplotlib.pyplot as plt
import sqlite3
import hashlib
import uuid
import requests
import pandas as pd
import logging
import random
from io import BytesIO
import base64

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

# Database connection
def connect_db():
    """Database connection to the SQLite database."""
    conn = sqlite3.connect('C:/Users/asus.LAPTOP-SMDU8F43/Desktop/pythonproje-local/sqlite/database.sqlite3')
    conn.row_factory = sqlite3.Row
    return conn


# Utility function to initialize the database schema if needed
def initialize_db():
    """Create tables if they don't exist."""
    with connect_db() as conn:
        # Create the 'seats' table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS seats (
                id INTEGER PRIMARY KEY,
                seat_id TEXT UNIQUE,
                status TEXT DEFAULT 'Available',
                category TEXT,
                position TEXT,
                price REAL
            )
        """)
        
        # Create the 'reservations' table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS reservations (
                id INTEGER PRIMARY KEY,
                seat_id TEXT,
                user_id INTEGER,
                reservation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (seat_id) REFERENCES seats (seat_id)
            )
        """)
        
        # Create the 'users' table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT UNIQUE,
                password TEXT
            )
        """)
        
        conn.commit()  # Commit the changes


# Ensure tables exist
initialize_db()

if __name__ == '__main__':
    initialize_db()  # Initialize the database schema if not already initialized
    app.run(debug=True)


@app.route('/')
def index():
    """Main page that displays the seating chart."""
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT SUBSTR(seat_id, 1, INSTR(seat_id, ' ') - 1) AS row_number FROM seats")
        rows = sorted([row["row_number"] for row in cursor.fetchall()])

        seats = {}
        for row in rows:
            cursor.execute("SELECT * FROM seats WHERE seat_id LIKE ?", (f"{row}%",))
            seats[row] = [dict(seat) for seat in cursor.fetchall()]

    return render_template("index.html", seats=seats)


@app.route('/upload', methods=['POST'])
def upload():
    """Endpoint to upload seating chart from a .txt file."""
    if 'file' not in request.files:
        return jsonify({"success": False, "message": "No file uploaded!"})

    file = request.files['file']
    if not file.filename.endswith('.txt'):
        return jsonify({"success": False, "message": "Invalid file type! Only .txt files are allowed."})

    try:
        seats = []
        for line in file.stream:
            line = line.decode('utf-8').strip()
            seat_id, category, position, price = line.split(',')

            # Check for the gap between C and D and handle it as a corridor
            if 'C' in seat_id and 'D' in seat_id:
                seats.append((seat_id, "Corridor", category, position, float(price)))
            else:
                seats.append((seat_id, "Available", category, position, float(price)))

        with connect_db() as conn:
            conn.executemany("""
                INSERT OR REPLACE INTO seats (seat_id, status, category, position, price)
                VALUES (?, ?, ?, ?, ?)
            """, seats)
            conn.commit()

        return jsonify({"success": True, "message": "Seating chart uploaded successfully!"})
    except Exception as e:
        return jsonify({"success": False, "message": f"Error processing file: {e}"})


@app.route('/reserve_random_seats', methods=['POST'])
def reserve_random_seats():
    """Reserve 5 random available seats."""
    with connect_db() as conn:
        cursor = conn.cursor()
        
        # Fetch available seats
        cursor.execute("SELECT seat_id FROM seats WHERE status = 'Available'")
        available_seats = [row["seat_id"] for row in cursor.fetchall()]
        
        # Check if enough available seats exist
        if len(available_seats) < 5:
            return jsonify({"success": False, "message": "Not enough available seats to reserve!"})

        # Select 5 random seats to reserve
        reserved_seats = random.sample(available_seats, 5)
        
        # Update the status to 'Reserved' for those seats
        cursor.executemany("""
            UPDATE seats SET status = 'Reserved' WHERE seat_id = ?
        """, [(seat,) for seat in reserved_seats])
        
        conn.commit()

    return jsonify({"success": True, "message": "5 random seats reserved successfully!"})


@app.route('/stats')
def seat_stats():
    """Fetch seat statistics."""
    with connect_db() as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM seats WHERE status = 'Available'")
        available_seats = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM seats WHERE status = 'Reserved'")
        reserved_seats = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM seats")
        total_seats = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(DISTINCT user_id) FROM reservations")
        total_users = cursor.fetchone()[0]

    available_percentage = (available_seats / total_seats) * 100 if total_seats else 0
    reserved_percentage = (reserved_seats / total_seats) * 100 if total_seats else 0

    stats = {
        'available_seats': available_seats,
        'reserved_seats': reserved_seats,
        'available_percentage': available_percentage,
        'reserved_percentage': reserved_percentage,
        'total_seats': total_seats,
        'total_users': total_users
    }

    return render_template("index.html", stats=stats)


@app.route('/chart')
def seat_chart():
    """Generate a chart of seat availability."""
    with connect_db() as conn:
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM seats WHERE status = 'Available'")
        available_seats = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM seats WHERE status = 'Reserved'")
        reserved_seats = cursor.fetchone()[0]

    # Generate a bar chart for the seat availability
    fig, ax = plt.subplots()
    ax.bar(['Available', 'Reserved'], [available_seats, reserved_seats], color=['green', 'red'])
    ax.set_title('Seat Availability')
    ax.set_xlabel('Status')
    ax.set_ylabel('Number of Seats')

    # Save the chart to a BytesIO buffer
    img = BytesIO()
    fig.savefig(img, format='png')
    img.seek(0)

    # Encode the image to base64
    img_base64 = base64.b64encode(img.getvalue()).decode('utf-8')
    img_url = f"data:image/png;base64,{img_base64}"

    return render_template("index.html", chart=img_url)
