import os
import pandas as pd
from flask import Flask, render_template, redirect, request, session, send_file, url_for
import matplotlib
import matplotlib.pyplot as plt
from io import BytesIO
from frans import get_user  # Assuming this function works as expected.

matplotlib.use('Agg')  # Use a non-interactive backend for Flask

# Initialize Flask app
app = Flask(
    __name__,
    template_folder="/Users/ninayehorova/projectfinalfinal/FRANS-Airlines/templates",
    static_folder="/Users/ninayehorova/projectfinalfinal/FRANS-Airlines/static"
)
app.secret_key = "your_secret_key"

# Hardcoded session for testing
DEBUG_USER = {"email": "test@example.com", "name": "Test User"}
session = {'user': DEBUG_USER}  # REMOVE THIS FOR PRODUCTION.

# Helper function to load CSV data
def load_data():
    try:
        seats = pd.read_csv("/Users/ninayehorova/projectfinalfinal/FRANS-Airlines/data/seats.csv")
        print("Seats data loaded successfully.")
    except FileNotFoundError:
        print("Seats.csv not found!")
        return None
    return seats

# Helper function to fetch statistics
def fetch_statistics(users, seats):
    available_seats = seats[seats["Status"] == "Available"].shape[0]
    reserved_seats = seats[seats["Status"] == "Reserved"].shape[0]
    total_seats = len(seats)

    available_percentage = (available_seats / total_seats) * 100 if total_seats > 0 else 0
    reserved_percentage = (reserved_seats / total_seats) * 100 if total_seats > 0 else 0

    return {
        "available_seats": available_seats,
        "reserved_seats": reserved_seats,
        "total_seats": total_seats,
        "available_percentage": available_percentage,
        "reserved_percentage": reserved_percentage,
        "users": users.to_dict(orient="records"),
        "total_users": len(users),
    }

# Main route
@app.route("/", methods=["GET", "POST"])
def index():
    print(f"Session: {session}")
    user = session.get('user', DEBUG_USER)  # Use hardcoded user for testing.
    return render_template("statisticindex.html", user=user)

# Route to display statistics
@app.route("/display")
def display_statistics():
    print(f"Session: {session}")
    users = pd.DataFrame([session.get('user', DEBUG_USER)])  # Use hardcoded user.
    seats = load_data()
    if seats is None:
        return render_template("statisticindex.html", message="Seats data is missing!")
    
    stats = fetch_statistics(users, seats)
    return render_template("statisticindex.html", stats=stats)

# Route to export statistics
@app.route("/export")
def export():
    print(f"Session: {session}")
    users = pd.DataFrame([session.get('user', DEBUG_USER)])  # Use hardcoded user.
    seats = load_data()
    if seats is None:
        return render_template("statisticindex.html", message="Seats data is missing!")
    
    stats = fetch_statistics(users, seats)
    
    # Define the data folder path
    data_dir = "/Users/ninayehorova/projectfinalfinal/FRANS-Airlines/data/"
    os.makedirs(data_dir, exist_ok=True)  # Ensure the folder exists
    file_path = os.path.join(data_dir, "statistics.txt")
    
    # Write statistics to the file
    with open(file_path, "w") as file:
        file.write(f"Available Seats: {stats['available_seats']} ({stats['available_percentage']:.2f}%)\n")
        file.write(f"Reserved Seats: {stats['reserved_seats']} ({stats['reserved_percentage']:.2f}%)\n")
        file.write(f"Total Seats: {stats['total_seats']}\n\n")
        file.write("Users:\n")
        for user in stats["users"]:
            file.write(f"ID: {user.get('id', 'N/A')}, Name: {user['name']}, Email: {user['email']}\n")
        file.write(f"\nTotal Users: {stats['total_users']}")
    
    return send_file(file_path, as_attachment=True)

# Route to display a pie chart
@app.route("/chart")
def chart():
    print(f"Session: {session}")
    users = pd.DataFrame([session.get('user', DEBUG_USER)])  # Use hardcoded user.
    seats = load_data()
    if seats is None:
        return render_template("statisticindex.html", message="Seats data is missing!")
    
    stats = fetch_statistics(users, seats)
    
    # Create chart
    fig, ax = plt.subplots(figsize=(5, 5))
    labels = ["Available Seats", "Reserved Seats"]
    sizes = [stats["available_percentage"], stats["reserved_percentage"]]
    colors = ["green", "red"]
    explode = (0.1, 0)
    ax.pie(sizes, explode=explode, labels=labels, colors=colors, autopct="%1.1f%%", shadow=True, startangle=140)
    ax.set_title("Seat Availability")
    
    # Define the static directory path
    static_dir = "/Users/ninayehorova/projectfinalfinal/FRANS-Airlines/static/"
    os.makedirs(static_dir, exist_ok=True)  # Ensure the folder exists
    chart_path = os.path.join(static_dir, "chart.png")
    
    # Save chart
    fig.savefig(chart_path, format="png")
    plt.close(fig)
    
    chart_url = url_for('static', filename='chart.png')
    return render_template("statisticindex.html", chart=chart_url)

# Run the app
if __name__ == "__main__":
    app.run(debug=True)
