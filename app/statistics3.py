from flask import Blueprint, render_template
import sqlite3
import os

stats_routes = Blueprint("stats_routes", __name__)
DATABASE_PATH = os.path.join("app", "database.sqlite3")

@stats_routes.route("/admin_dashboard")
def admin_dashboard():
    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    # Get statistics
    cursor.execute("SELECT COUNT(*) FROM seats WHERE status = 'available'")
    available_seats = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM seats WHERE status = 'reserved'")
    reserved_seats = cursor.fetchone()[0]

    stats = {
        "available_seats": available_seats,
        "reserved_seats": reserved_seats,
    }

    connection.close()
    return render_template("admin_dashboard.html", stats=stats)