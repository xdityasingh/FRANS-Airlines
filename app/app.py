from flask import Flask, render_template, request, jsonify
import pandas as pd

app = Flask(__name__)

# Load or create seat data
def load_seat_data():
    try:
        return pd.read_csv("seats.csv")
    except FileNotFoundError:
        return create_seat_data()

# Save seat data to CSV
def save_seat_data(dataframe):
    dataframe.to_csv("seats.csv", index=False)

# Create default seat data
def create_seat_data(rows=5):
    seat_data = []
    positions = ['window', 'middle', 'aisle', 'aisle', 'middle', 'window']
    statuses = ['available', 'occupied', 'ghost']
    for row_label in "ABCDEF"[:rows]:
        for col in range(1, 7):
            seat_id = f"{row_label}{col}"
            position = positions[col - 1]
            status = "available"
            if row_label == "A":
                category = "business"
                price = 200 if position == 'window' else 150 if position == 'aisle' else 120
            else:
                category = "economy"
                price = 100 if position == 'window' else 80 if position == 'aisle' else 70
            seat_data.append({'Seat ID': seat_id, 'Status': status, 'Category': category, 'Position': position, 'Price': price})
    df = pd.DataFrame(seat_data)
    save_seat_data(df)
    return df

@app.route('/')
def seat_chart():
    # Sol ve sağ taraflar için örnek koltuk düzeni
    left_side = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
    right_side = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
    
    return render_template('seat_chart.html', left_side=left_side, right_side=right_side)

if __name__ == '__main__':
    app.run(debug=True)

@app.route("/")
def index():
    seats_df = load_seat_data()
    return render_template("index.html", seats=seats_df.to_dict(orient="records"))

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

if __name__ == "__main__":
    app.run(debug=True)
