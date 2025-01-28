import pandas as pd
from flask import Flask, render_template, redirect, request, session, send_file, url_for
import matplotlib
import matplotlib.pyplot as plt
from io import BytesIO
from frans import get_user

matplotlib.use('Agg')

app = Flask(__name__, template_folder="/Users/ninayehorova/projectfinalfinal/FRANS-Airlines/templates")
app.secret_key = "your_secret_key"

def load_data():
    try:
        seats = pd.read_csv("/Users/ninayehorova/projectfinalfinal/FRANS-Airlines/data/seats.csv")
    except FileNotFoundError:
        return None
    return seats

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

@app.route("/", methods=["GET", "POST"])
def index():
    if 'user' in session and 'email' in session['user']:
        user = get_user(email=session['user']['email'])
        if user:
            return render_template("statisticindex.html", user=user)
    return render_template("statisticindex.html")

@app.route("/display")
def display_statistics():
    if 'user' not in session or 'email' not in session['user']:
        return redirect('/')  # Redirect to login page if not logged in

    users = pd.DataFrame([user for user in [get_user(email=session['user']['email'])] if user])
    seats = load_data()
    if seats is None:
        return render_template("statisticindex.html", message="Seats data is missing!")
    
    stats = fetch_statistics(users, seats)
    return render_template("statisticindex.html", stats=stats)

@app.route("/export")
def export():
    if 'user' not in session or 'email' not in session['user']:
        return redirect('/')  # Redirect to login page if not logged in

    users = pd.DataFrame([user for user in [get_user(email=session['user']['email'])] if user])
    seats = load_data()
    if seats is None:
        return render_template("statisticindex.html", message="Seats data is missing!")
    
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

@app.route("/chart")
def chart():
    if 'user' not in session or 'email' not in session['user']:
        return redirect('/')  # Redirect to login page if not logged in

    users = pd.DataFrame([user for user in [get_user(email=session['user']['email'])] if user])
    seats = load_data()
    if seats is None:
        return render_template("statisticindex.html", message="Seats data is missing!")
    
    stats = fetch_statistics(users, seats)
    fig, ax = plt.subplots(figsize=(5, 5))
    labels = ["Available Seats", "Reserved Seats"]
    sizes = [stats["available_percentage"], stats["reserved_percentage"]]
    colors = ["green", "red"]
    explode = (0.1, 0)
    ax.pie(sizes, explode=explode, labels=labels, colors=colors, autopct="%1.1f%%", shadow=True, startangle=140)
    ax.set_title("Seat Availability")
    chart_path = "static/chart.png"
    fig.savefig(chart_path, format="png")
    plt.close(fig)
    chart_url = url_for('static', filename='chart.png')
    return render_template("statisticindex.html", chart=chart_url)

if __name__ == "__main__":
    app.run(debug=True)
