import csv
from flask import Flask, request, jsonify

app = Flask(__name__)
DATA_FILE = "seating_chart.csv"

# Helper Functions
def load_seats():
    """Load seats from the CSV file."""
    with open(DATA_FILE, "r") as file:
        return list(csv.DictReader(file))

def save_seats(rows):
    """Save seat data back to the CSV file."""
    with open(DATA_FILE, "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

def find_seat(seat_id, rows):
    """Find a seat by its ID."""
    for row in rows:
        if row["Seat ID"] == seat_id:
            return row
    return None

# Core Functions
def reserve_seat(seat_id):
    """Reserve a seat."""
    rows = load_seats()
    seat = find_seat(seat_id, rows)
    if not seat:
        return {"success": False, "error": "Seat not found."}
    if seat["Status"] == "occupied":
        return {"success": False, "error": "Seat is already reserved."}
    seat["Status"] = "occupied"
    save_seats(rows)
    return {"success": True, "message": f"Seat {seat_id} reserved successfully."}

def cancel_seat(seat_id):
    """Cancel a seat reservation."""
    rows = load_seats()
    seat = find_seat(seat_id, rows)
    if not seat:
        return {"success": False, "error": "Seat not found."}
    if seat["Status"] != "occupied":
        return {"success": False, "error": "Seat is not reserved."}
    seat["Status"] = "available"
    save_seats(rows)
    return {"success": True, "message": f"Reservation for seat {seat_id} canceled successfully."}

# Flask Routes
@app.route("/reserve", methods=["POST"])
def reserve():
    seat_id = request.json.get("seat_id")
    result = reserve_seat(seat_id)
    return jsonify(result)

@app.route("/cancel", methods=["POST"])
def cancel():
    seat_id = request.json.get("seat_id")
    result = cancel_seat(seat_id)
    return jsonify(result)

@app.route("/view", methods=["GET"])
def view():
    """View all seat data."""
    seats = load_seats()
    return jsonify({"success": True, "seats": seats})

if __name__ == "__main__":
    app.run(debug=True)