from flask import Flask, render_template, request, jsonify
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
DB_PATH = 'messages.db'
TXT_PATH = 'messages.txt'

# Ensure database exists
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT,
        phone TEXT,
        service TEXT,
        message TEXT,
        timestamp TEXT
    )''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/contact', methods=['POST'])
def contact():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    phone = data.get('phone')
    service = data.get('service')
    message = data.get('message')
    timestamp = datetime.now().isoformat()

    # Save to database
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT INTO messages (name, email, phone, service, message, timestamp) VALUES (?, ?, ?, ?, ?, ?)',
              (name, email, phone, service, message, timestamp))
    conn.commit()
    conn.close()

    # Save to text file
    with open(TXT_PATH, 'a', encoding='utf-8') as f:
        f.write(f"[{timestamp}] {name} <{email}> ({phone}) [{service}]: {message}\n")

    return jsonify({'success': True}), 200

if __name__ == '__main__':
    app.run(debug=True)
