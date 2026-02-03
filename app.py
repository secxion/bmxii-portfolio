@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    session.pop('admin_secret', None)
    return redirect(url_for('admin_messages', secret=os.environ.get('ADMIN_SECRET', 'lofi2.0')))


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
from flask import request, abort, render_template_string, session, redirect, url_for

# Secret URL and password prompt for admin messages

# Simple login log (in-memory, resets on server restart)
admin_logins = []


# Admin login with POST and session
@app.route('/admin/messages', methods=['GET', 'POST'])
def admin_messages():
    from datetime import datetime
    import requests
    admin_secret = os.environ.get('ADMIN_SECRET', 'lofi2.0')
    admin_password = os.environ.get('ADMIN_PASSWORD', 'adminpass201')
    secret = request.args.get('secret')

    # Check session for admin login
    if session.get('admin_logged_in') == True and session.get('admin_secret') == admin_secret:
        pass  # Already logged in
    else:
        # Not logged in, check secret
        if secret != admin_secret:
            abort(404)
        if request.method == 'POST':
            password = request.form.get('password')
            if password == admin_password:
                session['admin_logged_in'] = True
                session['admin_secret'] = admin_secret
                # Redirect to remove password from POST body
                return redirect(url_for('admin_messages', secret=secret))
            else:
                return render_template_string('''
                    <form method="post">
                        <input type="hidden" name="secret" value="{{ secret }}" />
                        <input type="password" name="password" placeholder="Admin Password" />
                        <button type="submit">Login</button>
                    </form>
                    <p style="color:red">Incorrect password</p>
                ''', secret=secret)
        # Show password prompt
        return render_template_string('''
            <form method="post">
                <input type="hidden" name="secret" value="{{ secret }}" />
                <input type="password" name="password" placeholder="Admin Password" />
                <button type="submit">Login</button>
            </form>
        ''', secret=secret)

    # Log timestamp and IP (geo lookup placeholder)
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    timestamp = datetime.utcnow().isoformat()
    try:
        geo = requests.get(f'https://ipinfo.io/{ip}/json', timeout=2).json()
        location = geo.get('city', '') + ', ' + geo.get('region', '') + ', ' + geo.get('country', '')
    except Exception:
        location = 'Unknown'
    admin_logins.append({'timestamp': timestamp, 'ip': ip, 'location': location})
    messages = Message.query.order_by(Message.timestamp.desc()).all()
    return render_template('admin_messages.html', messages=messages, admin_logins=admin_logins, show_logout=True)


# Logout route (should be after all other routes)
@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    session.pop('admin_secret', None)
    return redirect(url_for('admin_messages', secret=os.environ.get('ADMIN_SECRET', 'lofi2.0')))

# For local development only

# Set a secret key for session management
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev-secret-key')

if __name__ == '__main__':
    app.run(debug=True)

# For production (Render), use gunicorn:
#   gunicorn app:app
