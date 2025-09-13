# Flask Email Verification System

A comprehensive Flask web application that implements user registration with email verification using OTP (One-Time Password) codes. This dynamic app manager to test because this is only quicly check the app manager works or not and before you code to test here.

### If you need the Email Authentication OTP System, visit here https://github.com/ASHIK27445/Flash-Outh  
---

## ✨ Highlighted Feature: Dynamic Email Configuration (It's for test only)
**Most Notable Feature:**  
This application includes a unique dynamic email configuration system that allows users to input their SMTP credentials directly through the web interface.  

Unlike traditional systems that require hardcoded email settings or environment variables, this implementation enables **real-time configuration of email settings** without restarting the application.



### 🔧 How It Works
1. Users visit the homepage and input their email service credentials  
2. The application dynamically updates Flask-Mail configuration in real-time  
3. All subsequent email operations use these user-provided settings  
4. No code changes or server restarts required  

### ✅ Benefits
- **User-Friendly:** No technical knowledge needed to configure email settings  
- **Flexible:** Supports any SMTP service (Gmail, Outlook, custom servers)  
- **Testable:** Immediate feedback on email configuration validity  
- **Dynamic:** Settings can be updated anytime without application downtime  

---

## 🚀 Full Features List
- **User Registration & Authentication:** Secure user sign-up and login system  
- **Email Verification:** OTP-based email verification system with expiration  
- **Database Management:** SQLite database with user and OTP management  
- **Session Management:** Secure user session handling with cleanup options  
- **Responsive Design:** Clean templates for all user interactions  
- **Error Handling:** Comprehensive error handling and logging  

---

## 🛠️ Technical Stack
- **Backend:** Flask (Python)  
- **Database:** SQLite with SQLAlchemy-like connection management  
- **Email:** Flask-Mail with SMTP fallback  
- **Security:** Password hashing with Werkzeug, session management  
- **Templates:** Jinja2 templating engine  

---

## 📋 Key Functionality
- **Dynamic Email Configuration:** Set up SMTP credentials through the web interface without restarting the application  
- **User Registration:** New users receive OTP codes via email using the configured SMTP settings  
- **OTP Verification:** Time-limited verification codes (5-minute expiration)  
- **Account Management:** Login, dashboard, and logout functionality  
- **Admin Functions:** Ability to clear all users and test email functionality  

---

## 🗂️ Project Structure
```
flask-email-verification/
├── app.py                 # Main application file
├── users.db              # SQLite database (created automatically)
├── templates/            # HTML templates
│   ├── index.html        # Homepage with email configuration
│   ├── register.html     # User registration form
│   ├── login.html        # User login form
│   ├── verify.html       # OTP verification form
│   ├── resend_otp.html   # OTP resend form
│   └── dashboard.html    # User dashboard after login
└── README.md             # Project documentation
```
## 🚦 Getting Started
### Prerequisites
- Python 3.7+
- pip (Python package manager)

### Installation
1. Clone the repository:
```bash
git clone <repository-url>
cd flask-email-verification
```
2. Install required packages:
```bash
pip install flask flask-mail
```
3. Run the application:
```bash
python app.py
```
4. Open your browser and navigate to http://localhost:5000

### Configuration
On the homepage, configure your SMTP settings:

- **Email username** (Gmail or other SMTP service)  
- **Email password** (App password for Gmail)  
- **Default sender email**  

### 🔍 Test Endpoints
- `/test-email` → Tests OTP email sending  
- `/test-verification-email` → Tests verification success email  

---

## 🔧 API Endpoints
| Endpoint                  | Method   | Description                           |
|---------------------------|----------|---------------------------------------|
| `/`                       | GET      | Homepage with email configuration     |
| `/update-email-config`    | POST     | Update SMTP settings                  |
| `/register`               | GET/POST | User registration                     |
| `/verify`                 | GET/POST | OTP verification                      |
| `/resend-otp`             | GET/POST | Resend OTP code                       |
| `/login`                  | GET/POST | User login                            |
| `/dashboard`              | GET      | User dashboard                        |
| `/logout`                 | GET      | User logout                           |
| `/clear-session`          | POST     | Clear session data                    |
| `/delete-all-users`       | POST     | Admin function to delete all users    |
| `/test-email`             | GET      | Test email functionality              |
| `/test-verification-email`| GET      | Test verification email               |

---

## 🧪 Testing
The application includes several test routes to verify functionality:

- Email configuration testing  
- OTP generation and validation  
- Database operations  
- Session management  

---

## 🔒 Security Features
- Password hashing with **Werkzeug**  
- Secure session management  
- OTP expiration (**5 minutes**)  
- SQL injection prevention with parameterized queries  
- Email validation before account activation  

---

## 📝 License
This project is open source and available under the **MIT License**.  

---

## 🤝 Contributing
Contributions, issues, and feature requests are welcome.  
Feel free to check the **issues page** if you want to contribute.  

---

## 📞 Support
If you have any questions or need help with setup, please open an issue in the **GitHub repository**.  

⚠️ **Note**: This application is designed for development and testing purposes.  
For production use, ensure you:
- Change the **secret key**  
- Use a **production-grade WSGI server**  
- Implement **additional security measures**  
- Use a more robust **database system**  
- Set up proper **SSL encryption**  