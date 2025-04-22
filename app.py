import hashlib
import json
import sqlite3

from flask import Flask, render_template, request, redirect, url_for

# Create Flask App
app = Flask(__name__)

# Filename for users DB
DB_FILE = 'users.db'

# Default page URLs
REGISTER_URL = '/register'
LOGIN_URL = '/login'
WELCOME_URL = '/welcome'

# Error messages to display
PASSWORD_UNMATCH_MESSAGE = 'Passwords did not match!'
PASSWORD_TOO_SHORT_MESSAGE = 'Password must be at least 8 characters'
EMAIL_ALREADY_EXISTS_MESSAGE = 'Email already exists! Try a different one'
INVALID_CREDENTIALS_MESSAGE = 'Invalid credentials! Try again'


def create_db(db_path):
    """
    Creates SQL database for users, if it does not exist already.
    @param db_path: The path for the DB file.
    """
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
        )
        ''')
    conn.commit()
    conn.close()

@app.route(REGISTER_URL, methods=['GET', 'POST'])
def register():
    """
    Handles user registration.

    GET: Displays the registration form.
    POST: Checks password validity, verifies that email does not already exist, and creates a new user if so. Redirects to the login page.
    """
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        repeat_password = request.form['repeat_password']

        # Check password validity
        if len(password) < 8:
            return render_template('register.html', error_message=PASSWORD_TOO_SHORT_MESSAGE)
        if password != repeat_password:
            return render_template('register.html', error_message=PASSWORD_UNMATCH_MESSAGE)
        hashed_password = hashlib.md5(password.encode()).hexdigest()
        
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        try:
            c.execute('INSERT INTO users (name, email, password) VALUES (?, ?, ?)', (name, email, hashed_password))
            conn.commit()
            conn.close()
            return redirect(url_for('login', success_message=True))
        except sqlite3.IntegrityError:
            conn.close()
            return render_template('register.html', error_message=EMAIL_ALREADY_EXISTS_MESSAGE)
    return render_template('register.html')

@app.route(LOGIN_URL, methods=['GET', 'POST'])
def login():
    """
    Handles user login.

    GET: Displays the login page.
    POST: Checks that the email and password match an existing user in the database, and logs in if so.
    """
    if request.method == 'POST':
        email = request.form['email']
        password_input = request.form['password']

        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('SELECT name, password FROM users WHERE email = ?', (email,))
        result = c.fetchone()
        conn.close()

        if result and hashlib.md5(password_input.encode()).hexdigest() == result[1]:
            return redirect(url_for('welcome', name=result[0]))
        else:
            return render_template('login.html', error_message=INVALID_CREDENTIALS_MESSAGE)
    return render_template('login.html', success_message=request.args.get('success_message'))

@app.route(WELCOME_URL, methods=['GET'])
def welcome():
    """
    Displays welcome page.
    """
    return render_template('welcome.html', name=request.args.get('name'))

@app.route('/')
def index():
    """
    Redirects the root URL the login page.
    """
    return redirect(LOGIN_URL)


if __name__ == '__main__':
    # Initialize the database file
    create_db(DB_FILE)
    # Start app
    app.run(debug=True) 
