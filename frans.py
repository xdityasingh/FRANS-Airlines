from flask import Flask, render_template, session, redirect, request
import sqlite3
import hashlib
import uuid
import requests


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
    return render_template('home.html', name=user['name'],  username=user['user_name'],  email=user['email'])


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