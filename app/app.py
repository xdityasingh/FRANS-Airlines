from flask import Flask, render_template, request, jsonify
import pandas as pd
import random 

app = Flask(__name__)

# Load seat data
def load_seat_data():
    return pd.read_csv("seats.csv")  # Veritabanınızı bağlayabilirsiniz.

# Save seat data
def save_seat_data(seats_df):
    seats_df.to_csv("seats.csv", index=False)
import random

def random_reserved_seats():
    reserved_seats = []
    while len(reserved_seats) < 5:
        row = random.randint(1, 36)  # 1 ile 36 arasında rastgele satır
        seat = random.choice(['A', 'B', 'C', 'D', 'E', 'F'])  # A-F arasında rastgele koltuk
        seat_id = f"seat_{row}_{seat}"
        
        if seat_id not in reserved_seats:
            reserved_seats.append(seat_id)
    
    return reserved_seats

# Home route
@app.route("/")
def index():
    seats_df = load_seat_data()  # Koltuk verilerini yükleyin
    seats = seats_df.to_dict(orient="records")  # Veriyi sözlük haline getirin

    # stats nesnesini oluşturun
    stats = {
        "total_seats": len(seats),
        "available_seats": len([seat for seat in seats if seat["Status"] == "available"]),
        "reserved_seats": len([seat for seat in seats if seat["Status"] == "reserved"]),
    }

    # stats'ı şablona gönderin
    return render_template("index.html", seats=seats, stats=stats)

# Seat chart route
@app.route('/seat-chart')
def seat_chart():
    reserved_seats = random_reserved_seats()  # Rastgele rezerve edilmiş koltukları al
    return render_template('index.html', reserved_seats=reserved_seats)

# Reserve a seat
@app.route("/reserve", methods=["POST"])
def reserve_seat():
    seat_id = request.json.get("seat_id")
    seats_df = load_seat_data()
    if not seat_id:
        return jsonify({"error": "Seat ID not provided"}), 400

    if seat_id in seats_df["Seat ID"].values:
        current_status = seats_df.loc[seats_df["Seat ID"] == seat_id, "Status"].values[0]
        if current_status == "available":
            seats_df.loc[seats_df["Seat ID"] == seat_id, "Status"] = "occupied"
            save_seat_data(seats_df)
            return jsonify({"success": True, "message": f"Seat {seat_id} reserved."})
        else:
            return jsonify({"error": f"Seat {seat_id} is already {current_status}."}), 400
    return jsonify({"error": "Invalid Seat ID."}), 400

# Get a specific seat
@app.route("/get_seat/<seat_id>", methods=["GET"])
def get_seat(seat_id):
    seats_df = load_seat_data()
    seat = seats_df[seats_df["Seat ID"] == seat_id].to_dict(orient="records")
    if seat:
        return jsonify(seat[0])
    return jsonify({"error": "Seat not found"}), 404

# Update seat details
@app.route("/update_seat", methods=["POST"])
def update_seat():
    data = request.json
    seat_id = data.get("seat_id")
    status = data.get("status")
    category = data.get("category")
    price = data.get("price")
    
    seats_df = load_seat_data()
    if seat_id in seats_df["Seat ID"].values:
        seats_df.loc[seats_df["Seat ID"] == seat_id, ["Status", "Category", "Price"]] = [status, category, price]
        save_seat_data(seats_df)
        return jsonify({"success": True, "message": f"Seat {seat_id} updated."})
    return jsonify({"error": "Seat not found."}), 404

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
