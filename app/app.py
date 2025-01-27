from flask import Flask
from seatreservationsystem import app_routes
from statistics3 import stats_routes
from auth import auth_routes

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app/database.sqlite3'
app.config['SECRET_KEY'] = 'your_secret_key'

# Register blueprints
app.register_blueprint(app_routes)
app.register_blueprint(stats_routes)
app.register_blueprint(auth_routes, url_prefix="/auth")

if __name__ == "__main__":
    app.run(debug=True)