from flask import Flask, render_template, request, redirect, jsonify
import csv

app = Flask(__name__)

DATA_FILE = "seating_chart.csv"

# Helper Functions
def load_seats():
    with open(DATA_FILE, "r") as file:
        return list(csv.DictReader(file))

def save_seats(rows):
    with open(DATA_FILE, "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

def find_seat(seat_id, rows):
    for row in rows:
        if row["Seat ID"] == seat_id:
            return row
    return None

# Routes
@app.route("/")
def home():
    seats = load_seats()
    return render_template("seat_chart.html", seats=seats)

@app.route("/reserve", methods=["POST"])
def reserve_seat():
    seat_id = request.json.get("seat_id")
    rows = load_seats()
    seat = find_seat(seat_id, rows)
    
    if not seat:
        return jsonify({"success": False, "error": "Seat not found."})
    
    if seat["Status"] == "occupied":
        return jsonify({"success": False, "error": "Seat is already reserved."})
    
    seat["Status"] = "occupied"
    save_seats(rows)
    return jsonify({"success": True, "message": f"Seat {seat_id} reserved successfully."})

@app.route("/cancel", methods=["POST"])
def cancel_reservation():
    seat_id = request.json.get("seat_id")
    rows = load_seats()
    seat = find_seat(seat_id, rows)
    
    if not seat:
        return jsonify({"success": False, "error": "Seat not found."})
    
    if seat["Status"] != "occupied":
        return jsonify({"success": False, "error": "Seat is not reserved."})
    
    seat["Status"] = "available"
    save_seats(rows)
    return jsonify({"success": True, "message": f"Reservation for seat {seat_id} canceled successfully."})

@app.route("/admin/override", methods=["POST"])
def admin_override():
    # Admin-specific route to force reservation/cancellation
    seat_id = request.json.get("seat_id")
    action = request.json.get("action")  # "reserve" or "cancel"
    rows = load_seats()
    seat = find_seat(seat_id, rows)
    
    if not seat:
        return jsonify({"success": False, "error": "Seat not found."})
    
    if action == "reserve":
        seat["Status"] = "occupied"
    elif action == "cancel":
        seat["Status"] = "available"
    else:
        return jsonify({"success": False, "error": "Invalid action."})
    
    save_seats(rows)
    return jsonify({"success": True, "message": f"Admin override successful for seat {seat_id}."})

if __name__ == "__main__":
    app.run(debug=True)