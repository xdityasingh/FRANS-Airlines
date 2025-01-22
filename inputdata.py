from flask import Flask, render_template, request, jsonify
import pandas as pd
import os

app = Flask(__name__)

# File paths
TEXT_FILE = "chartIn.txt"
SEAT_DATA_FILE = "seats.csv"

# Load seat data from a text file or existing CSV


def load_seat_data():
    if os.path.exists(SEAT_DATA_FILE):
        # Load from CSV if it exists
        return pd.read_csv(SEAT_DATA_FILE)
    elif os.path.exists(TEXT_FILE):
        # Load from text file and process
        with open(TEXT_FILE, 'r') as file:
            headers = file.readline().strip().split('\t')
            rows = []
            for line in file:
                row_label, *seats = line.strip().split('\t')
                for seat in seats:
                    # Assign categories and prices based on realistic airplane seating
                    row_number = int(row_label)  # Convert row label to an integer
                    if row_number <= 2:  # Rows 1-2 are First Class
                        category = "First"
                        price = 1000
                    elif 3 <= row_number <= 6:  # Rows 3-6 are Business Class
                        category = "Business"
                        price = 600
                    else:  # Rows 7+ are Economy Class
                        category = "Economy"
                        price = 200

                    rows.append({
                        "Seat ID": f"{row_label}{seat}",
                        "Status": "Available",
                        "Category": category,
                        "Position": classify_seat(seat),
                        "Price": price
                    })

        # Convert to DataFrame and save as CSV
        df = pd.DataFrame(rows)
        save_seat_data(df)
        return df
    else:
        # Return an empty DataFrame if neither file exists
        return pd.DataFrame(columns=["Seat ID", "Status", "Category", "Position", "Price"])

# Save seat data to a CSV file
def save_seat_data(df):
    df.to_csv(SEAT_DATA_FILE, index=False)

# Classify seats as Window, Middle, or Aisle
def classify_seat(seat):
    if seat in ["A", "F"]:
        return "Window"
    elif seat in ["B", "E"]:
        return "Middle"
    elif seat in ["C", "D"]:
        return "Aisle"
    return "Unknown"

# Load initial seat data
seat_data = load_seat_data()


@app.route('/')
def index():
    # Extract row numbers and sort them numerically
    seat_data['Row'] = seat_data['Seat ID'].str.extract('(\d+)').astype(int)  # Extract numeric row values as integers
    rows = seat_data['Row'].unique()  # Get unique row numbers
    rows.sort()  # Sort rows numerically

    # Create a dictionary of seats for each row
    seats = {row: seat_data[seat_data['Row'] == row].sort_values(by='Seat ID').to_dict(orient="records") for row in rows}
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
    save_seat_data(seat_data)

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
    save_seat_data(seat_data)

    return jsonify({"success": True, "message": "Seating chart uploaded successfully!"})

if __name__ == '__main__':
    app.run(debug=True)

