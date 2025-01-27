from flask import Blueprint, render_template, request, redirect, url_for
import sqlite3
import os

app_routes = Blueprint("app_routes", __name__)
DATABASE_PATH = os.path.join("app", "database.sqlite3")

@app_routes.route("/")
def home():
    return render_template("home.html")

@app_routes.route("/seat_chart")
def seat_chart():
    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM seats")
    seats = cursor.fetchall()
    connection.close()
    return render_template("seat_chart.html", seats=seats)

@app_routes.route("/reserve/<int:seat_id>", methods=["POST"])
def reserve_seat(seat_id):
    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()
    cursor.execute("UPDATE seats SET status = 'reserved' WHERE id = ?", (seat_id,))
    connection.commit()
    connection.close()
    return redirect(url_for("app_routes.seat_chart"))