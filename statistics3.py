import pandas as pd
from flask import Flask, render_template, send_file, url_for
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from io import BytesIO

app = Flask(__name__)

# Load data from CSV files or initialize if not available
def load_data():
    try:
        users = pd.read_csv("users.csv")
        seats = pd.read_csv("seats.csv")
    except FileNotFoundError:
        # Initialize with sample data if files don't exist
        users = pd.DataFrame(
            {
                "id": [1, 2, 3],
                "name": ["Admin User", "User One", "User Two"],
                "email": ["admin@example.com", "user1@example.com", "user2@example.com"],
            }
        )
        seats = pd.DataFrame(
            {
                "seat_id": [1, 2, 3, 4, 5],
                "status": ["available", "reserved", "available", "reserved", "available"],
                "category": ["economy", "business", "first", "economy", "business"],
                "price": [100.0, 300.0, 500.0, 120.0, 400.0],
            }
        )
    return users, seats


# Fetch statistics
def fetch_statistics(users, seats):
    available_seats = seats[seats["status"] == "available"].shape[0]
    reserved_seats = seats[seats["status"] == "reserved"].shape[0]
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


# Route: Homepage
@app.route("/", methods=["GET", "POST"])
def index():
    # No statistics are shown on the homepage
    return render_template("index2.html")


# Route: Display statistics
@app.route("/display")
def display_statistics():
    users, seats = load_data()
    stats = fetch_statistics(users, seats)
    return render_template("index2.html", stats=stats)


# Route: Export statistics to text file
@app.route("/export")
def export():
    users, seats = load_data()
    stats = fetch_statistics(users, seats)

    file_path = "statistics.txt"
    with open(file_path, "w") as file:
        file.write(f"Available Seats: {stats['available_seats']} ({stats['available_percentage']:.2f}%)\n")
        file.write(f"Reserved Seats: {stats['reserved_seats']} ({stats['reserved_percentage']:.2f}%)\n")
        file.write(f"Total Seats: {stats['total_seats']}\n\n")
        file.write("Users:\n")
        for user in stats["users"]:
            file.write(f"ID: {user['id']}, Name: {user['name']}, Email: {user['email']}\n")
        file.write(f"\nTotal Users: {stats['total_users']}")

    return send_file(file_path, as_attachment=True)


# Route: Show chart


@app.route("/chart")
def chart():
    users, seats = load_data()
    stats = fetch_statistics(users, seats)

    fig, ax = plt.subplots(figsize=(5, 5))
    labels = ["Available Seats", "Reserved Seats"]
    sizes = [stats["available_percentage"], stats["reserved_percentage"]]
    colors = ["green", "red"]
    explode = (0.1, 0)

    ax.pie(sizes, explode=explode, labels=labels, colors=colors, autopct="%1.1f%%", shadow=True, startangle=140)
    ax.set_title("Seat Availability")

    # Speichern des Diagramms in der Datei
    chart_path = "static/chart.png"
    fig.savefig(chart_path, format="png")
    plt.close(fig)  # Schließen der Figur, um Speicher freizugeben

    chart_url = url_for('static', filename='chart.png')
    return render_template("index2.html", chart=chart_url)



if __name__ == "__main__":
    app.run(debug=True)