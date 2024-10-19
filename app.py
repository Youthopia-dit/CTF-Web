import sqlite3
from flask import Flask, render_template, request

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row 
    return conn

# Function to create the users table if it doesn't exist
def create_users_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    )
    ''')
    # Optionally, create a flags table for CTF
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS flags (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        flag TEXT NOT NULL
    )
    ''')
    # Insert a flag (only if not exists)
    cursor.execute('SELECT COUNT(*) FROM flags')
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO flags (flag) VALUES ('CTF{SQL_Injection_Exploited}')")
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # Vulnerable SQL query using string formatting
            sql = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
            cursor.execute(sql)
            user = cursor.fetchone()
            if user:
                # For demonstration, retrieve the flag if login is successful
                cursor.execute("SELECT flag FROM flags WHERE id = 1")
                flag = cursor.fetchone()
                return f"Login successful! Your flag is: {flag['flag']}"
            else:
                return "Login failed. Invalid credentials."
        except sqlite3.Error as e:
            return f"Database error: {e}"
        finally:
            conn.close()

    return render_template('index.html')

if __name__ == '__main__':
    # Create the tables when the app starts
    create_users_table()
    app.run(debug=True)
