from flask import Flask, render_template, request, jsonify
import pandas as pd
import os

app = Flask(__name__)

# File path for seat data aiwufhqurfqiufr
SEAT_DATA_FILE = "seats.csv"

# Load seat data from a CSV file
def load_seat_data(file_path):
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    else:
        return pd.DataFrame(columns=["Seat ID", "Status", "Category", "Position", "Price"])

# Save seat data to a CSV file
def save_seat_data(df, file_path):
    df.to_csv(file_path, index=False)

# Load initial seat data
seat_data = load_seat_data(SEAT_DATA_FILE)

@app.route('/')
def index():
    # Generate data for seat layout
    rows = seat_data["Seat ID"].str[0].unique()  # Get unique row labels (A, B, C, etc.)
    seats = {row: seat_data[seat_data["Seat ID"].str.startswith(row)].to_dict(orient="records") for row in rows}
    return render_template("index.html", seats=seats)

@app.route('/update_seat', methods=['POST'])
def update_seat():
    # Update seat information (admin feature)
    data = request.get_json()
    seat_id = data.get("seat_id")
    status = data.get("status")
    price = data.get("price")
    category = data.get("category")

    global seat_data
    # Update the seat data DataFrame
    seat_data.loc[seat_data["Seat ID"] == seat_id, ["Status", "Price", "Category"]] = [status, price, category]
    save_seat_data(seat_data, SEAT_DATA_FILE)

    return jsonify({"success": True, "message": "Seat updated successfully!"})

@app.route('/get_seat/<seat_id>', methods=['GET'])
def get_seat(seat_id):
    # Retrieve seat information by ID
    seat = seat_data.loc[seat_data["Seat ID"] == seat_id].to_dict(orient="records")
    if seat:
        return jsonify(seat[0])
    else:
        return jsonify({"success": False, "message": "Seat not found!"})

@app.route('/upload', methods=['POST'])
def upload():
    # Upload a new seating chart CSV
    if 'file' not in request.files:
        return jsonify({"success": False, "message": "No file uploaded!"})

    file = request.files['file']
    if file.filename == '':
        return jsonify({"success": False, "message": "No file selected!"})

    global seat_data
    seat_data = pd.read_csv(file)
    save_seat_data(seat_data, SEAT_DATA_FILE)

    return jsonify({"success": True, "message": "Seating chart uploaded successfully!"})

if __name__ == '__main__':
    app.run(debug=True)
