from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_mail import Mail, Message
import sqlite3
import os
import random
import string
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from contextlib import contextmanager
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__)
app.secret_key = 'your-secret-key-here-change-in-production'

# Default email configuration (will be updated by user)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = ''  # Will be set by user
app.config['MAIL_PASSWORD'] = ''  # Will be set by user
app.config['MAIL_DEFAULT_SENDER'] = ''  # Will be set by user

# Initialize Flask-Mail
mail = Mail(app)

# Database connection manager
@contextmanager
def get_db_connection():
    conn = sqlite3.connect('users.db', timeout=30)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

# Initialize database
def init_db():
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     username TEXT UNIQUE NOT NULL,
                     email TEXT UNIQUE NOT NULL,
                     password TEXT NOT NULL,
                     is_verified INTEGER DEFAULT 0)''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS otps
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     email TEXT NOT NULL,
                     otp_code TEXT NOT NULL,
                     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                     expires_at TIMESTAMP NOT NULL)''')
        
        conn.commit()

init_db()

def generate_otp(length=6):
    """Generate a random OTP code"""
    return ''.join(random.choices(string.digits, k=length))

def is_otp_valid(email, otp_code):
    """Check if OTP is valid and not expired"""
    try:
        with get_db_connection() as conn:
            c = conn.cursor()
            c.execute("SELECT expires_at FROM otps WHERE email = ? AND otp_code = ?", 
                      (email, otp_code))
            result = c.fetchone()
            
            if result:
                # Handle datetime with microseconds
                expires_at_str = result['expires_at']
                try:
                    # Try parsing with microseconds
                    expires_at = datetime.strptime(expires_at_str, '%Y-%m-%d %H:%M:%S.%f')
                except ValueError:
                    try:
                        # Try parsing without microseconds
                        expires_at = datetime.strptime(expires_at_str, '%Y-%m-%d %H:%M:%S')
                    except ValueError:
                        # If both fail, return False
                        print(f"Failed to parse datetime: {expires_at_str}")
                        return False
                
                return datetime.now() < expires_at
            return False
    except sqlite3.OperationalError as e:
        print(f"Database error in is_otp_valid: {e}")
        return False

def cleanup_expired_otps():
    """Remove expired OTPs from database"""
    try:
        with get_db_connection() as conn:
            c = conn.cursor()
            c.execute("DELETE FROM otps WHERE expires_at < datetime('now')")
            conn.commit()
    except sqlite3.OperationalError as e:
        print(f"Database error in cleanup_expired_otps: {e}")

def send_email_directly(to_email, subject, body):
    """Send email directly using smtplib (for testing if Flask-Mail doesn't work)"""
    try:
        sender_email = app.config['MAIL_USERNAME']
        sender_password = app.config['MAIL_PASSWORD']
        
        # Check if email is configured
        if not sender_email or not sender_password:
            print("Email not configured. Cannot send email.")
            return False
            
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = app.config['MAIL_DEFAULT_SENDER']
        msg['To'] = to_email
        
        with smtplib.SMTP(app.config['MAIL_SERVER'], app.config['MAIL_PORT']) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
        
        print(f"Email sent successfully to {to_email}")
        return True
    except Exception as e:
        print(f"Error sending email directly: {e}")
        return False

def send_otp_email(to_email, otp_code):
    """Send OTP email using Flask-Mail with fallback to direct sending"""
    # Check if email is configured
    if not app.config.get('MAIL_USERNAME') or not app.config.get('MAIL_PASSWORD'):
        print("Email not configured. Cannot send OTP.")
        return False
        
    try:
        # Try Flask-Mail first
        msg = Message('Your Verification Code',
                      sender=app.config['MAIL_DEFAULT_SENDER'],
                      recipients=[to_email])
        msg.body = f"""
        Hello,
        
        Your verification code is: {otp_code}
        
        This code will expire in 5 minutes.
        
        If you didn't request this code, please ignore this email.
        
        Best regards,
        The Website Team
        """
        mail.send(msg)
        print(f"Email sent via Flask-Mail to {to_email}")
        return True
    except Exception as e:
        print(f"Flask-Mail error: {e}. Trying direct email...")
        
        # Fallback to direct email sending
        subject = "Your Verification Code"
        body = f"""
        Hello,
        
        Your verification code is: {otp_code}
        
        This code will expire in 5 minutes.
        
        If you didn't request this code, please ignore this email.
        
        Best regards,
        The Website Team
        """
        
        return send_email_directly(to_email, subject, body)

def send_verification_success_email(to_email, username):
    """Send email notification when user successfully verifies their account"""
    # Check if email is configured
    if not app.config.get('MAIL_USERNAME') or not app.config.get('MAIL_PASSWORD'):
        print("Email not configured. Cannot send verification success email.")
        return False
        
    try:
        # Try Flask-Mail first
        msg = Message('Account Verified Successfully',
                      sender=app.config['MAIL_DEFAULT_SENDER'],
                      recipients=[to_email])
        msg.body = f"""
        Hello {username},
        
        Congratulations! Your account has been successfully verified.
        
        You can now log in to your account and access all features.
        
        Thank you for joining our community!
        
        Best regards,
        The Website Team
        """
        mail.send(msg)
        print(f"Verification success email sent via Flask-Mail to {to_email}")
        return True
    except Exception as e:
        print(f"Flask-Mail error: {e}. Trying direct email...")
        
        # Fallback to direct email sending
        subject = "Account Verified Successfully"
        body = f"""
        Hello {username},
        
        Congratulations! Your account has been successfully verified.
        
        You can now log in to your account and access all features.
        
        Thank you for joining our community!
        
        Best regards,
        The Website Team
        """
        
        return send_email_directly(to_email, subject, body)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/update-email-config', methods=['POST'])
def update_email_config():
    try:
        # Get form data
        mail_username = request.form['mail_username']
        mail_password = request.form['mail_password']
        mail_default_sender = request.form['mail_default_sender']
        
        # Update app configuration
        app.config['MAIL_USERNAME'] = mail_username
        app.config['MAIL_PASSWORD'] = mail_password
        app.config['MAIL_DEFAULT_SENDER'] = mail_default_sender
        
        # Reinitialize mail with new settings
        mail.init_app(app)
        
        # Return success response
        return jsonify({
            'success': True,
            'config': {
                'MAIL_USERNAME': mail_username,
                'MAIL_DEFAULT_SENDER': mail_default_sender
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/register', methods=['GET', 'POST'])
def register():
    # Check if email is configured
    if not app.config.get('MAIL_USERNAME') or not app.config.get('MAIL_PASSWORD'):
        flash('Please configure email settings first on the homepage.', 'warning')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password)
        
        try:
            with get_db_connection() as conn:
                c = conn.cursor()
                c.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                         (username, email, hashed_password))
                conn.commit()
            
            # Generate and send OTP
            otp_code = generate_otp()
            expires_at = datetime.now() + timedelta(minutes=5)
            
            try:
                with get_db_connection() as conn:
                    c = conn.cursor()
                    c.execute("INSERT INTO otps (email, otp_code, expires_at) VALUES (?, ?, ?)",
                             (email, otp_code, expires_at.strftime('%Y-%m-%d %H:%M:%S')))
                    conn.commit()
                
                # Send OTP email
                email_sent = send_otp_email(email, otp_code)
                
                if email_sent:
                    session['verify_email'] = email
                    session['username'] = username  # Store username for later use
                    flash('Registration successful! Please check your email for the verification code.', 'success')
                    return redirect(url_for('verify_otp', email=email))  # Pass email as parameter
                else:
                    flash('Failed to send verification email. Please try again later.', 'danger')
                    return redirect(url_for('register'))
                
            except sqlite3.OperationalError as e:
                flash('Database error. Please try again.', 'danger')
                print(f"Database error in OTP creation: {e}")
                
        except sqlite3.IntegrityError:
            flash('Username or email already exists.', 'danger')
        except sqlite3.OperationalError as e:
            flash('Database error. Please try again.', 'danger')
            print(f"Database error in user registration: {e}")
    
    return render_template('register.html')


@app.route('/verify', methods=['GET', 'POST'])
def verify_otp():
    # Try to get email from session first, then from request args
    email = session.get('verify_email')
    
    if not email:
        # Try to get from request args
        email = request.args.get('email')
    
    if not email:
        flash('Please register first.', 'warning')
        return redirect(url_for('register'))
    
    # Store in session for future requests
    session['verify_email'] = email
    username = session.get('username', 'User')
    
    if request.method == 'POST':
        otp_code = request.form['otp']
        
        if is_otp_valid(email, otp_code):
            try:
                # Mark user as verified
                with get_db_connection() as conn:
                    c = conn.cursor()
                    c.execute("UPDATE users SET is_verified = 1 WHERE email = ?", (email,))
                    conn.commit()
                
                # Clean up OTP
                with get_db_connection() as conn:
                    c = conn.cursor()
                    c.execute("DELETE FROM otps WHERE email = ?", (email,))
                    conn.commit()
                
                # Send verification success email
                send_verification_success_email(email, username)
                
                session.pop('verify_email', None)
                session.pop('username', None)
                flash('Email verified successfully! You can now login.', 'success')
                return redirect(url_for('login'))
                
            except sqlite3.OperationalError as e:
                flash('Database error. Please try again.', 'danger')
                print(f"Database error in verification: {e}")
        else:
            flash('Invalid or expired OTP code.', 'danger')
    
    # Pass email to template
    return render_template('verify.html', email=email)

@app.route('/resend-otp', methods=['GET', 'POST'])
def resend_otp():
    # Try to get email from session first, then from request args
    email = session.get('verify_email')
    
    if not email:
        # Try to get from request args
        email = request.args.get('email')
    
    if not email:
        flash('Please register first.', 'warning')
        return redirect(url_for('register'))
    
    # Store in session for future requests
    session['verify_email'] = email
    
    if request.method == 'POST':
        # Generate new OTP
        otp_code = generate_otp()
        expires_at = datetime.now() + timedelta(minutes=5)
        
        try:
            # Remove any existing OTPs for this email
            with get_db_connection() as conn:
                c = conn.cursor()
                c.execute("DELETE FROM otps WHERE email = ?", (email,))
                c.execute("INSERT INTO otps (email, otp_code, expires_at) VALUES (?, ?, ?)",
                         (email, otp_code, expires_at.strftime('%Y-%m-%d %H:%M:%S')))
                conn.commit()
            
            # Send new OTP email
            email_sent = send_otp_email(email, otp_code)
            
            if email_sent:
                flash('New OTP has been sent to your email.', 'success')
                return redirect(url_for('verify_otp', email=email))
            else:
                flash('Failed to send OTP. Please try again.', 'danger')
                return redirect(url_for('verify_otp', email=email))
            
        except sqlite3.OperationalError as e:
            flash('Database error. Please try again.', 'danger')
            print(f"Database error in resend OTP: {e}")
            return redirect(url_for('verify_otp', email=email))
    
    return render_template('resend_otp.html', email=email)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        try:
            with get_db_connection() as conn:
                c = conn.cursor()
                c.execute("SELECT * FROM users WHERE username = ?", (username,))
                user = c.fetchone()
            
            if user and check_password_hash(user['password'], password):
                if user['is_verified']:  # Check if user is verified
                    session['user_id'] = user['id']
                    session['username'] = user['username']
                    flash('Login successful!', 'success')
                    return redirect(url_for('dashboard'))
                else:
                    session['verify_email'] = user['email']
                    flash('Please verify your email first.', 'warning')
                    return redirect(url_for('verify_otp', email=user['email']))  # Pass email as parameter
            else:
                flash('Invalid username or password.', 'danger')
                
        except sqlite3.OperationalError as e:
            flash('Database error. Please try again.', 'danger')
            print(f"Database error in login: {e}")
    
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    return render_template('dashboard.html', username=session['username'])

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/clear-session', methods=['POST'])
def clear_session():
    # Get request data
    data = request.get_json() or {}
    preserve_verification = data.get('preserve_verification', False)
    
    # Save verification data if needed
    verify_email = session.get('verify_email')
    username = session.get('username')
    
    # Clear all session data
    session.clear()
    
    # Restore verification data if requested
    if preserve_verification and verify_email:
        session['verify_email'] = verify_email
        if username:
            session['username'] = username
    
    return jsonify({'success': True})

@app.route('/delete-all-users', methods=['POST'])
def delete_all_users():
    """Delete all users from the database"""
    try:
        with get_db_connection() as conn:
            c = conn.cursor()
            
            # Delete all users
            c.execute("DELETE FROM users")
            
            # Delete all OTPs
            c.execute("DELETE FROM otps")
            
            conn.commit()
        
        # Clear any active sessions
        session.clear()
        
        return jsonify({
            'success': True,
            'message': 'All users have been deleted successfully.'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error deleting users: {str(e)}'
        }), 500

# Test email route to check if email is working
@app.route('/test-email')
def test_email():
    """Test route to check if email is working"""
    # Check if email is configured
    if not app.config.get('MAIL_USERNAME') or not app.config.get('MAIL_PASSWORD'):
        return "Email not configured. Please set up email first."
    
    test_email = "test@example.com"  # Change to a real email for testing
    otp_code = generate_otp()
    
    email_sent = send_otp_email(test_email, otp_code)
    
    if email_sent:
        return f"Test email sent successfully to {test_email} with OTP: {otp_code}"
    else:
        return "Failed to send test email. Check your email configuration."

# Test verification success email
@app.route('/test-verification-email')
def test_verification_email():
    """Test route to check if verification success email is working"""
    # Check if email is configured
    if not app.config.get('MAIL_USERNAME') or not app.config.get('MAIL_PASSWORD'):
        return "Email not configured. Please set up email first."
    
    test_email = "test@example.com"  # Change to a real email for testing
    username = "TestUser"
    
    email_sent = send_verification_success_email(test_email, username)
    
    if email_sent:
        return f"Verification success email sent successfully to {test_email}"
    else:
        return "Failed to send verification success email. Check your email configuration."

# Clean up expired OTPs on each request but handle exceptions
@app.before_request
def before_request():
    try:
        cleanup_expired_otps()
    except Exception as e:
        print(f"Error in before_request cleanup: {e}")
        # Don't crash the app if cleanup fails

if __name__ == '__main__':
    app.run(debug=True)