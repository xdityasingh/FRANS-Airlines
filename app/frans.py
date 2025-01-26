from flask import Flask, render_template, session, redirect, request
import sqlite3
import hashlib
import uuid
import requests
import pandas as pd


db = sqlite3.connect('database.sqlite3', check_same_thread=False)
db.row_factory = sqlite3.Row
app = Flask(__name__)
app.secret_key = "project_air_frans"


def get_uuid():
    return uuid.uuid4().hex.upper()


def get_user(username=None, email=None):
    if username is None and email is None:
        return None
    if username is not None and email is not None:
        return None
    cur = db.cursor()
    if username is not None:
        cur.execute('SELECT * FROM users WHERE user_name=?', (username,))
    if email is not None:
        cur.execute('SELECT * FROM users WHERE email=?', (email,))
    row = cur.fetchone()
    return row


def is_user_already_exists(username, email):
    cur = db.cursor()
    cur.execute('SELECT * FROM users WHERE user_name=? OR email=?', (username, email))
    len(cur.fetchall()) > 0


def delete_user(email):
    query = 'DELETE FROM users WHERE email=?'
    cur = db.cursor()
    cur.execute(query, (email,))
    db.commit()
    if 'user' in session:
        session.clear()


def activate_user(email):
    query = 'UPDATE users SET confirmation_token=? WHERE email=?'
    cur = db.cursor()
    cur.execute(query, ('activate', email))
    db.commit()


def prepare_user_deletion(email):
    confirmation = 'del:' + get_uuid()
    query = 'UPDATE users SET confirmation_token=? WHERE email=?'
    cur = db.cursor()
    cur.execute(query, (confirmation, email))
    db.commit()
    return confirmation


def send_email(email, token, is_del):
    try:
        subject = 'Account deletion token' if is_del else 'New account token'
        body = f'Here is your token {token}'
        requests.post(
            "https://api.useplunk.com/v1/send",
            headers={"Content-Type": "application/json", "Authorization": "Bearer sk_9649c4d488d8d132afe8d4565db911d2f760fe91847f40c5"},
            json={
                "subject": subject,
                "body": body, 
                "to": email, 
            },
        )
        return True
    except Exception as e:
        print('Mail error', e)
        return False


def new_user(name, username, pw_hash, email):
    confirmation = 'new:' + get_uuid()
    query = 'INSERT INTO users(name, user_name, password, email, confirmation_token) VALUES(?,?,?,?,?)'
    cur = db.cursor()
    cur.execute(query, (name, username, pw_hash, email, confirmation))
    db.commit()


@app.route('/')
def homepage():
    if 'user' not in session or 'email' not in session['user']:
        return render_template('login.html')
    user = session['user']
    return redirect('/seats')
    #return render_template('home.html', name=user['name'],  username=user['user_name'],  email=user['email'])


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


@app.route('/delete')
def delete():
    if 'user' not in session or 'email' not in session['user']:
        return redirect('/')
    user = session['user']
    confirmation = prepare_user_deletion(user['email'])
    if not send_email(user['email'], confirmation[4:], is_del=True):
        return render_template('home.html', message='Something went wrong with email server! User could not deleted!')
    return render_template('email_confirmation.html', email=user['email'], message='Check your emails to delete your account.')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if len(username) == 0:
            return render_template('login.html', message='Username cannot be empty!')
        if len(password) == 0:
            return render_template('login.html', message='Password cannot be empty!')
        user = get_user(username, email=None)
        if user is None:
            print('nonenone')
            return render_template('login.html', message='Wrong username or password!')
        pw_hash = hashlib.md5(password.encode()).hexdigest()
        is_pw_correct = user['password'] == pw_hash
        if not is_pw_correct:
            print('is_pw_correct', pw_hash, user['password'])
            return render_template('login.html', message='Wrong username or password!')
        if user['confirmation_token'][:3] == 'new':
            return render_template('login.html', message='User/Email has not been activated!')
        user_keys = ['name', 'user_name', 'email', 'is_admin']
        session['user'] = {k: user[k] for k in user.keys()}
        return redirect('/')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    if request.method == 'POST':
        name = request.form.get('name')
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        if len(name) == 0:
            return render_template('register.html', message='Name cannot be empty!')
        if len(username) == 0:
            return render_template('register.html', message='Username cannot be empty!')
        if len(password) == 0:
            return render_template('register.html', message='Password cannot be empty!')
        if len(email) == 0:
            return render_template('register.html', message='Email cannot be empty!')
        if is_user_already_exists(username, email):
            return render_template('register.html', message='Username or email already exists in the database!')
        pw_hash = hashlib.md5(password.encode()).hexdigest()
        new_user(name, username, pw_hash, email)
        user = get_user(username, email=None)
        if user is None:
            return render_template('register.html', message='Something went wrong!')
        if not send_email(email, user['confirmation_token'][4:], is_del=False):
            delete_user(email)
            return render_template('register.html', message='Something went wrong with email server! User deleted!')
        return render_template('email_confirmation.html', email=email, message='Check your emails to activate your account.')


@app.route('/confirm', methods=['GET', 'POST'])
def confirm():
    if request.method == 'GET':
        return render_template('email_confirmation.html')
    if request.method == 'POST':
        email = request.form.get('email')
        token = request.form.get('token')
        if len(email) == 0:
            return render_template('email_confirmation.html', message='Email cannot be empty!')
        if len(token) == 0:
            return render_template('email_confirmation.html', message='Token cannot be empty!')
        user = get_user(username=None, email=email)
        if user is None:
            return render_template('email_confirmation.html', message='Wrong email address!')
        if len(user['confirmation_token']) != 36:
            return render_template('email_confirmation.html', message='Email already confirmed!')
        token_type = user['confirmation_token'][:3]
        is_token_correct = token == user['confirmation_token'][4:]
        if not is_token_correct:
            return render_template('email_confirmation.html', message='Wrong token for the email address!')
        if token_type == 'new':
            activate_user(email)
            return render_template('login.html', message='Your registration has been completed!')
        if token_type == 'del':
            delete_user(email)
            return render_template('email_confirmation.html', message='Your account deleted!')


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


@app.route('/seats')
def seat_chart():
    # Sol ve sağ taraflar için örnek koltuk düzeni
    left_side = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
    right_side = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
    return render_template('seat_chart.html', left_side=left_side, right_side=right_side)


# Load or create seat data
def load_seat_data():
    try:
        return pd.re51_csv("seats.csv")
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