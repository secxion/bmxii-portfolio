
# ...existing code...

# Place this after app and db are defined

# Temporary admin migration trigger route (remove after use!)
@app.route('/admin/run-migrations')
def run_migrations():
    from flask import request, abort
    secret = request.args.get('secret')
    admin_secret = os.environ.get('ADMIN_SECRET', 'lofi2.0')
    password = request.args.get('password')
    admin_password = os.environ.get('ADMIN_PASSWORD', 'adminpass201')
    if secret != admin_secret or password != admin_password:
        abort(404)
    try:
        from flask_migrate import upgrade
        upgrade()
        return '<h2>Migration successful! You can now remove this route.</h2>'
    except Exception as e:
        return f'<h2>Migration failed:</h2><pre>{e}</pre>', 500

# Ensure .env is loaded for environment variables
from dotenv import load_dotenv
load_dotenv()



import os
from datetime import datetime
from flask import Flask, render_template, request, jsonify

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


# Configure app for SQLAlchemy with environment-based database URL
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///messages.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)



# Message model for storing contact form submissions
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(40))
    service = db.Column(db.String(120))
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

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

    # Save to database using SQLAlchemy
    msg = Message(
        name=name,
        email=email,
        phone=phone,
        service=service,
        message=message
    )
    db.session.add(msg)
    db.session.commit()
    return jsonify({'success': True}), 200


# Admin route to view all messages
from flask import request, abort, render_template_string

# Secret URL and password prompt for admin messages

# Simple login log (in-memory, resets on server restart)
admin_logins = []

@app.route('/admin/messages')
def admin_messages():
    from datetime import datetime
    import requests
    secret = request.args.get('secret')
    admin_secret = os.environ.get('ADMIN_SECRET', 'lofi2.0')
    print('DEBUG: Loaded admin_secret from env:', admin_secret)
    if secret != admin_secret:
        abort(404)
    # Password prompt
    password = request.args.get('password')
    admin_password = os.environ.get('ADMIN_PASSWORD', 'adminpass201')
    if password != admin_password:
        # Show password prompt form
        return render_template_string('''
            <form method="get">
                <input type="hidden" name="secret" value="{{ secret }}" />
                <input type="password" name="password" placeholder="Admin Password" />
                <button type="submit">Login</button>
            </form>
            {% if password is not none %}<p style="color:red">Incorrect password</p>{% endif %}
        ''', secret=secret, password=password)
    # Log timestamp and IP (geo lookup placeholder)
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    timestamp = datetime.utcnow().isoformat()
    # Simple geo lookup (using ipinfo.io, can be replaced with any service)
    try:
        geo = requests.get(f'https://ipinfo.io/{ip}/json', timeout=2).json()
        location = geo.get('city', '') + ', ' + geo.get('region', '') + ', ' + geo.get('country', '')
    except Exception:
        location = 'Unknown'
    admin_logins.append({'timestamp': timestamp, 'ip': ip, 'location': location})
    messages = Message.query.order_by(Message.timestamp.desc()).all()
    return render_template('admin_messages.html', messages=messages, admin_logins=admin_logins)


# For local development only
if __name__ == '__main__':
    app.run(debug=True)

# For production (Render), use gunicorn:
#   gunicorn app:app
