# from flask import Flask, request, jsonify
# from Database.super_admin_db import get_customers, get_customer_by_email, insert_tempuser, insert_customer, delete_temp_user, delete_otp, insert_otp, get__email_and_otp
# from Database.customer_db import create_table

# from email_validator import validate_email, EmailNotValidError
# from flask_mail import Mail, Message
# from passlib.hash import sha256_crypt
# from flask_cors import CORS
# import random
# import os

# app = Flask(__name__)

# # Enable CORS for all routes and allow credentials
# CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# # Mail configuration
# app.config['MAIL_SERVER'] = 'smtp.gmail.com'
# app.config['MAIL_PORT'] = 587
# app.config['MAIL_USE_TLS'] = True
# app.config['MAIL_USE_SSL'] = False
# app.config['MAIL_USERNAME'] = "aiwiztechsoln@gmail.com"
# app.config['MAIL_PASSWORD'] = 'lqfp kvxh nhnm abnx'

# mail = Mail(app)

# # Function to create necessary tables
# def create_tables():
#     from Database.super_admin_db import create_customer_table, create_tempuser_and_otp_tables
#     create_customer_table()
#     create_tempuser_and_otp_tables()

# # Initialize tables on app startup
# with app.app_context():
#     create_tables()

# # Generate a random 6-digit OTP
# def generate_otp(length=6):
#     return ''.join([str(random.randint(0, 9)) for _ in range(length)])

# # Send OTP to the given email
# def send_otp(email):
#     print("\n send_otp........!!!")
#     otp = generate_otp()
#     print(otp)
#     try:
#         msg = Message('Your OTP Code', sender=app.config['MAIL_USERNAME'], recipients=[email])
#         msg.body = f'Your OTP code is {otp}'
#         mail.send(msg)
#         print('OTP sent successfully!')
#     except Exception as e:
#         print(f"Error: {e}")

#     insert_otp(email, otp)
#     return otp

# # Registration function
# @app.route('/register', methods=['POST'])
# def register():
#     print("\n Register API........!!!!")
#     data = request.json
#     full_name = data.get('full_name')
#     email = data.get('email')
#     password = data.get('password')
#     confirm_password = data.get('confirm_password')
#     contact_number = data.get('contact_number')
#     address = data.get('address')
#     database_name = email.split('@')[0]  # Example: Using part of email for db name
#     sn = data.get('sn')
#     agree_terms = data.get('agree_terms')

#     if not all([full_name, email, password, confirm_password, agree_terms, sn, address]):
#         return jsonify({"error": "All mandatory fields must be filled"}), 400

#     # Validate email format
#     try:
#         valid = validate_email(email)
#         email = valid.email
#     except EmailNotValidError as e:
#         return jsonify({"error": str(e)}), 400

#     # Password validation
#     if len(password) < 8 or not any(char.isdigit() for char in password) or not any(char.isupper() for char in password):
#         return jsonify({"error": "Password must be at least 8 characters long, contain a number, and an uppercase letter"}), 400

#     if password != confirm_password:
#         return jsonify({"error": "Passwords do not match"}), 400

#     # Check if email is already registered
#     existing_customer = get_customer_by_email(email)
#     if existing_customer:
#         return jsonify({"error": "Email is already registered"}), 400

#     # Send OTP and insert temp user
#     otp_1 = send_otp(email)
#     password_hash = sha256_crypt.hash(password)
#     insert_tempuser(full_name, email, email, password_hash, contact_number, address, database_name, sn, otp_1)
    
#     return jsonify({"message": "OTP sent to email. Please verify to complete registration."}), 201

# # OTP verification function
# @app.route('/verify-otp', methods=['POST'])
# def verify_otp():
#     print("\n verify-otp.......!")
#     data = request.json
#     email = data.get('email')
#     otp = data.get('otp')
    

#     if not all([email, otp]):
#         return jsonify({"error": "Email and OTP are required"}), 400

#     temp_user = get__email_and_otp(email, otp)
#     print("121221",type(temp_user))
    

#     if temp_user:
#         temp_user = list(temp_user)
#         print(temp_user)
#         from Database.super_admin_db import insert_customer
#         insert_customer( temp_user[1], temp_user[2], 
#                         temp_user[3], temp_user[4], temp_user[5], temp_user[6],
#                         temp_user[7], temp_user[8])

#         from Database.super_admin_db import delete_otp,delete_temp_user
#         delete_temp_user(email)
#         delete_otp(email)
#         return jsonify({"message": "Registration complete. You can now login."}), 200
#     else:
#         return jsonify({"error": "Invalid OTP"}), 400

# # Login function
# @app.route('/login', methods=['POST'])
# def login():
#     data = request.json
#     email = data.get('email')
#     password = data.get('password')
#     print("\n login API........!!!!!")

#     if not all([email, password]):
#         return jsonify({"error": "Email and Password are required"}), 400

#     customer = get_customer_by_email(email)
   
#     customer =list(customer)
    
    
#     if customer and sha256_crypt.verify(password, customer[4]):
#         return jsonify({"message": "Login successful"}), 200
#         print("login successful....!")

#     return jsonify({"error": "Invalid email or password"}), 400

# # Add CORS headers to all responses
# @app.after_request
# def after_request(response):
#     response.headers.add('Access-Control-Allow-Origin', '*')  # Replace '*' with specific origin if needed
#     response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
#     response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
#     return response

# if __name__ == '__main__':
#     app.run(debug=True, host='0.0.0.0', port=8080)








# from flask import Flask, request, jsonify
# from Database.super_admin_db import get_customers, get_customer_by_email, insert_tempuser, insert_customer, delete_temp_user, delete_otp, insert_otp, get__email_and_otp, get_last_otp_time, update_last_otp_time
# from Database.customer_db import create_table
# from email_validator import validate_email, EmailNotValidError
# from flask_mail import Mail, Message
# from passlib.hash import sha256_crypt
# from flask_cors import CORS
# import random
# import os
# import time
# from datetime import datetime, timedelta

# app = Flask(__name__)

# # Enable CORS for all routes and allow credentials
# CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# # Mail configuration
# app.config['MAIL_SERVER'] = 'smtp.gmail.com'
# app.config['MAIL_PORT'] = 587
# app.config['MAIL_USE_TLS'] = True
# app.config['MAIL_USE_SSL'] = False
# app.config['MAIL_USERNAME'] = "aiwiztechsoln@gmail.com"
# app.config['MAIL_PASSWORD'] = 'lqfp kvxh nhnm abnx'

# mail = Mail(app)

# # Function to create necessary tables
# def create_tables():
#     from Database.super_admin_db import create_customer_table, create_tempuser_and_otp_tables
#     create_customer_table()
#     create_tempuser_and_otp_tables()

# # Initialize tables on app startup
# with app.app_context():
#     create_tables()

# # Generate a random 6-digit OTP
# def generate_otp(length=6):
#     return ''.join([str(random.randint(0, 9)) for _ in range(length)])

# # Send OTP to the given email
# def send_otp(email):
#     print("\n send_otp........!!!")
#     otp = generate_otp()
#     print(otp)
#     try:
#         msg = Message('Your OTP Code', sender=app.config['MAIL_USERNAME'], recipients=[email])
#         msg.body = f'Your OTP code is {otp}'
#         mail.send(msg)
#         print('OTP sent successfully!')
#     except Exception as e:
#         print(f"Error: {e}")

#     insert_otp(email, otp)
#     return otp

# # Registration function
# @app.route('/register', methods=['POST'])
# def register():
#     print("\n Register API........!!!!")
#     data = request.json
#     full_name = data.get('full_name')
#     email = data.get('email')
#     password = data.get('password')
#     confirm_password = data.get('confirm_password')
#     contact_number = data.get('contact_number')
#     address = data.get('address')
#     database_name = email.split('@')[0]  # Example: Using part of email for db name
#     sn = data.get('sn')
#     agree_terms = data.get('agree_terms')

#     if not all([full_name, email, password, confirm_password, agree_terms, sn, address]):
#         return jsonify({"error": "All mandatory fields must be filled"}), 400

#     # Validate email format
#     try:
#         valid = validate_email(email)
#         email = valid.email
#     except EmailNotValidError as e:
#         return jsonify({"error": str(e)}), 400

#     # Password validation
#     if len(password) < 8 or not any(char.isdigit() for char in password) or not any(char.isupper() for char in password):
#         return jsonify({"error": "Password must be at least 8 characters long, contain a number, and an uppercase letter"}), 400

#     if password != confirm_password:
#         return jsonify({"error": "Passwords do not match"}), 400

#     # Check if email is already registered
#     existing_customer = get_customer_by_email(email)
#     if existing_customer:
#         return jsonify({"error": "Email is already registered"}), 400

#     # Send OTP and insert temp user
#     otp_1 = send_otp(email)
#     password_hash = sha256_crypt.hash(password)
#     insert_tempuser(full_name, email, email, password_hash, contact_number, address, database_name, sn, otp_1)
    
#     return jsonify({"message": "OTP sent to email. Please verify to complete registration."}), 201

# # OTP verification function
# @app.route('/verify-otp', methods=['POST'])
# def verify_otp():
#     print("\n verify-otp.......!")
#     data = request.json
#     email = data.get('email')
#     otp = data.get('otp')

#     if not all([email, otp]):
#         return jsonify({"error": "Email and OTP are required"}), 400

#     temp_user = get__email_and_otp(email, otp)
#     print("121221",type(temp_user))
    
#     if temp_user:
#         temp_user = list(temp_user)
#         print(temp_user)
#         from Database.super_admin_db import insert_customer
#         insert_customer( temp_user[1], temp_user[2], 
#                         temp_user[3], temp_user[4], temp_user[5], temp_user[6],
#                         temp_user[7], temp_user[8])

#         from Database.super_admin_db import delete_otp, delete_temp_user
#         delete_temp_user(email)
#         delete_otp(email)
#         return jsonify({"message": "Registration complete. You can now login."}), 200
#     else:
#         return jsonify({"error": "Invalid OTP"}), 400

# # Resend OTP function with a one-minute restriction
# @app.route('/resend-otp', methods=['POST'])
# def resend_otp():
#     print("\n resend-otp.......!")
#     data = request.json
#     email = data.get('email')
#     new_otp = data.get('otp')
#     print(email,new_otp)

#     if not all([email, new_otp]):
#         return jsonify({"error": "Email is required"}), 400

#     # Check the last OTP request time
#     from Database.super_admin_db import update_otp_in_both_tables
#     update_otp_in_both_tables(email, new_otp)

#     # if last_otp_time:
#     #     # Check if 1 minute has passed since the last OTP request
#     #     current_time = datetime.now()
#     #     time_difference = current_time - last_otp_time
#     #     if time_difference < timedelta(minutes=1):
#     #         return jsonify({"error": "Please wait for one minute before requesting a new OTP."}), 400

    
#     return jsonify({"message": "OTP resent to email."}), 200

# # Login function
# @app.route('/login', methods=['POST'])
# def login():
#     data = request.json
#     email = data.get('email')
#     password = data.get('password')
#     print("\n login API........!!!!!")

#     if not all([email, password]):
#         return jsonify({"error": "Email and Password are required"}), 400

#     customer = get_customer_by_email(email)
   
#     customer = list(customer)
    
#     if customer and sha256_crypt.verify(password, customer[4]):
#         return jsonify({"message": "Login successful"}), 200
#         print("login successful....!")

#     return jsonify({"error": "Invalid email or password"}), 400

# # Add CORS headers to all responses
# @app.after_request
# def after_request(response):
#     response.headers.add('Access-Control-Allow-Origin', '*')  # Replace '*' with specific origin if needed
#     response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
#     response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
#     return response

# if __name__ == '__main__':
#     app.run(debug=True, host='0.0.0.0', port=8080)











# workiing
from flask import Flask, request, jsonify
from Database.super_admin_db import get_customers, get_customer_by_email, insert_tempuser, insert_customer, delete_temp_user, delete_otp, insert_otp, get__email_and_otp, update_password
from Database.customer_db import create_table
from email_validator import validate_email, EmailNotValidError
from flask_mail import Mail, Message
from passlib.hash import sha256_crypt
from flask_cors import CORS
import random
import os

app = Flask(__name__)

# Enable CORS for all routes and allow credentials
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# Mail configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = "aiwiztechsoln@gmail.com"
app.config['MAIL_PASSWORD'] = 'lqfp kvxh nhnm abnx'

mail = Mail(app)

# Function to create necessary tables
def create_tables():
    from Database.super_admin_db import create_customer_table, create_tempuser_and_otp_tables
    create_customer_table()
    create_tempuser_and_otp_tables()

# Initialize tables on app startup
with app.app_context():
    create_tables()

# Generate a random 6-digit OTP
def generate_otp(length=6):
    return ''.join([str(random.randint(0, 9)) for _ in range(length)])

# Send OTP to the given email
def send_otp(email):
    print("\n send_otp........!!!")
    otp = generate_otp()
    print(otp)
    try:
        msg = Message('Your OTP Code', sender=app.config['MAIL_USERNAME'], recipients=[email])
        msg.body = f'Your OTP code is {otp}'
        mail.send(msg)
        print('OTP sent successfully!')
    except Exception as e:
        print(f"Error: {e}")

    insert_otp(email, otp)
    return otp

# Registration function
@app.route('/register', methods=['POST'])
def register():
    print("\n Register API........!!!!")
    data = request.json
    full_name = data.get('full_name')
    email = data.get('email')
    password = data.get('password')
    confirm_password = data.get('confirm_password')
    contact_number = data.get('contact_number')
    address = data.get('address')
    database_name = email.split('@')[0]  # Example: Using part of email for db name
    sn = data.get('sn')
    agree_terms = data.get('agree_terms')

    if not all([full_name, email, password, confirm_password, agree_terms, sn, address]):
        return jsonify({"error": "All mandatory fields must be filled"}), 400

    # Validate email format
    try:
        valid = validate_email(email)
        email = valid.email
    except EmailNotValidError as e:
        return jsonify({"error": str(e)}), 400

    # Password validation
    if len(password) < 8 or not any(char.isdigit() for char in password) or not any(char.isupper() for char in password):
        return jsonify({"error": "Password must be at least 8 characters long, contain a number, and an uppercase letter"}), 400

    if password != confirm_password:
        return jsonify({"error": "Passwords do not match"}), 400

    # Check if email is already registered
    existing_customer = get_customer_by_email(email)
    if existing_customer:
        return jsonify({"error": "Email is already registered"}), 400

    # Send OTP and insert temp user
    otp_1 = send_otp(email)
    password_hash = sha256_crypt.hash(password)
    insert_tempuser(full_name, email, email, password_hash, contact_number, address, database_name, sn, otp_1)
    
    return jsonify({"message": "OTP sent to email. Please verify to complete registration."}), 201

# OTP verification function
@app.route('/verify-otp', methods=['POST'])
def verify_otp():
    print("\n verify-otp.......!")
    data = request.json
    email = data.get('email')
    otp = data.get('otp')

    if not all([email, otp]):
        return jsonify({"error": "Email and OTP are required"}), 400

    temp_user = get__email_and_otp(email, otp)
    if temp_user:
        temp_user = list(temp_user)
        print(temp_user)
        from Database.super_admin_db import insert_customer
        insert_customer(temp_user[1], temp_user[2], 
                        temp_user[3], temp_user[4], temp_user[5], temp_user[6],
                        temp_user[7], temp_user[8])

        from Database.super_admin_db import delete_otp, delete_temp_user
        delete_temp_user(email)
        delete_otp(email)
        return jsonify({"message": "Registration complete. You can now login."}), 200
    else:
        return jsonify({"error": "Invalid OTP"}), 400

# Login function
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    print("\n login API........!!!!!")

    if not all([email, password]):
        return jsonify({"error": "Email and Password are required"}), 400

    customer = get_customer_by_email(email)
    customer = list(customer)

    if customer and sha256_crypt.verify(password, customer[4]):
        return jsonify({"message": "Login successful"}), 200
    return jsonify({"error": "Invalid email or password"}), 400



# Forgot password function to send OTP
@app.route('/forgot-password', methods=['POST'])
def forgot_password():
    print("\n Forgot Password API........!!!!")
    data = request.json
    email = data.get('email')

    if not email:
        return jsonify({"error": "Email is required"}), 400

    # Check if email exists in the customer database
    existing_customer = get_customer_by_email(email)
    if not existing_customer:
        return jsonify({"error": "Email not found"}), 404

    # Send OTP
    otp = send_otp(email)
    return jsonify({"message": "OTP sent to email. Please verify to reset password."}), 200

# Reset password function after verifying OTP
@app.route('/reset-password', methods=['POST'])
def reset_password():
    print("\n Reset Password API........!!!!")
    data = request.json
    email = data.get('email')
    otp = data.get('otp')
    new_password = data.get('new_password')
    confirm_password = data.get('confirm_password')

    if not all([email, otp, new_password, confirm_password]):
        return jsonify({"error": "All fields are required"}), 400

    # Check if OTP is valid
    temp_user = get__email_and_otp(email, otp)
    if not temp_user:
        return jsonify({"error": "Invalid OTP"}), 400

    # Check password validity
    if len(new_password) < 8 or not any(char.isdigit() for char in new_password) or not any(char.isupper() for char in new_password):
        return jsonify({"error": "Password must be at least 8 characters long, contain a number, and an uppercase letter"}), 400

    if new_password != confirm_password:
        return jsonify({"error": "Passwords do not match"}), 400

    # Update password in the database
    password_hash = sha256_crypt.hash(new_password)
    update_password(email, password_hash)

    # Clean up OTP
    delete_otp(email)

    return jsonify({"message": "Password reset successful. You can now login with the new password."}), 200

# Add CORS headers to all responses
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')  # Replace '*' with specific origin if needed
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    return response

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
