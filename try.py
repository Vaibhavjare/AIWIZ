




from flask import Flask, request, jsonify
from Database.super_admin_db import get_customers
from Database.customer_db import create_Cameras_info_table,create_device_info_table,create_event_table,create_log_table,get_customer_db_connection,insert_camera_info,get_all_cameras_info,insert_device_data,insert_event_data,insert_log_data,get_all_devices,get_all_events,get_all_logs



from email_validator import validate_email, EmailNotValidError
import pyotp
from flask_mail import Mail, Message
from passlib.hash import sha256_crypt
import os


from flask_cors import CORS
app = Flask(__name__)
CORS(app)


app = Flask(__name__)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = "aiwiztechsoln@gmail.com"
app.config['MAIL_PASSWORD'] = 'lqfp kvxh nhnm abnx'

# mysql = MySQL(app)
mail = Mail(app)


def create_tables():
    from Database.super_admin_db import create_customer_table,create_tempuser_and_otp_tables
    create_customer_table()
    create_tempuser_and_otp_tables()
    
 
with app.app_context():
    create_tables()

import random
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

    from Database.super_admin_db import insert_otp
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
    from Database.super_admin_db import get_customer_by_email
    existing_customer = get_customer_by_email(email)
    if existing_customer:
        return jsonify({"error": "Email is already registered"}), 400

    # Send OTP and insert temp user
    otp_1 = send_otp(email)
    password_hash = sha256_crypt.hash(password)
    from Database.super_admin_db import insert_tempuser
    insert_tempuser(full_name, email, email, password_hash, contact_number, address, database_name, sn, otp_1)
    
    return jsonify({"message": "OTP sent to email. Please verify to complete registration."}), 201





# Resend OTP function with a one-minute restriction
@app.route('/resend-otp', methods=['POST'])
def resend_otp():
    print("\n resend-otp.......!")
    data = request.json
    email = data.get('email')
    new_otp = send_otp(email)
    print(email,new_otp)

    if not all([email, new_otp]):
        return jsonify({"error": "Email is required"}), 400
      
    # Check the last OTP request time
    from Database.super_admin_db import update_otp_in_both_tables
    update_otp_in_both_tables(email, new_otp)
    
    
    return jsonify({"message": "otp are resended"}), 200




# OTP verification function
@app.route('/verify-otp', methods=['POST'])
def verify_otp():
    print("\n verify-otp.......!")
    data = request.json
    email = data.get('email')
    otp = data.get('otp')
    

    if not all([email, otp]):
        return jsonify({"error": "Email and OTP are required"}), 400

    from Database.super_admin_db import get__email_and_otp
    temp_user = get__email_and_otp(email, otp)
    print("121221",type(temp_user))
    

    if temp_user:
        temp_user = list(temp_user)
        print(temp_user)
        from Database.super_admin_db import insert_customer
        insert_customer( temp_user[1], temp_user[2], 
                        temp_user[3], temp_user[4], temp_user[5], temp_user[6],
                        temp_user[7], temp_user[8])

        from Database.super_admin_db import delete_otp,delete_temp_user
        delete_temp_user(email)
        delete_otp(email)
        database_name = temp_user[7]
        print(database_name)
        from Database.customer_db import create_Cameras_info_table,create_device_info_table,create_event_table,create_log_table
        create_Cameras_info_table(database_name)
        create_device_info_table(database_name)
        create_event_table(database_name)
        create_log_table(database_name)
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

    from Database.super_admin_db import get_customer_by_email
    customer = get_customer_by_email(email)
   
    customer =list(customer)
    
    
    if customer and sha256_crypt.verify(password, customer[4]):
        database_name = email.split('@')[0]  
        print(database_name)
        from Database.customer_db import create_Cameras_info_table,create_customer,create_device_info_table,create_event_table,create_log_table,create_table
        create_Cameras_info_table(database_name)
        create_device_info_table(database_name)
        create_event_table(database_name)
        create_log_table(database_name)
        print("login successful....!")
        return jsonify({"message": "Login successful"}), 200
        

    return jsonify({"error": "Invalid email or password"}), 400





# Forgot password function to send OTP
@app.route('/forgot-password', methods=['POST'])
def forgot_password():
    print("\n forget...||")
    data = request.json
    email = data.get('email')

    # Check if the email exists in the customer database
    from Database.super_admin_db import get_customer_by_email
    existing_customer = get_customer_by_email(email)
    if not existing_customer:
        return jsonify({"error": "Email not found"}), 404

    # Send OTP via email
    otp = send_otp(email)

    return jsonify({"message": "OTP sent to your email. Please verify it."}), 200

# OTP verification function
@app.route('/f_verifyOtp', methods=['POST'])
def f_verifyOtp():
    print("\n enter verify...||")
    data = request.json
    email = data.get('email')
    otp = data.get('otp')
    if not all([email, otp]):
        return jsonify({"error": "Email and OTP are required"}), 400

    # Retrieve OTP from the database
    from Database.super_admin_db import retrieve_otp_by_email
    stored_otp = retrieve_otp_by_email(email)
    stored_otp = list(stored_otp)
    print(stored_otp)
    if  stored_otp[1] == otp:  # Assuming OTP is stored in the second field
        return jsonify({"message": "OTP verified"}), 200
    else:
        return jsonify({"error": "Invalid OTP"}), 400

# Reset password function after verifying OTP
@app.route('/reset-password', methods=['POST'])
def reset_password():
    print("\n enter reset...||")
    data = request.json
    email = data.get('email')
    new_password = data.get('new_password')
    confirm_password = data.get('confirm_password')

    if not all([email, new_password, confirm_password]):
        return jsonify({"error": "All fields are required"}), 400

    # Check password validity
    if len(new_password) < 8 or not any(char.isdigit() for char in new_password) or not any(char.isupper() for char in new_password):
        return jsonify({"error": "Password must be at least 8 characters long, contain a number, and an uppercase letter"}), 400

    if new_password != confirm_password:
        return jsonify({"error": "Passwords do not match"}), 400

    # Update password in the database
    password_hash = sha256_crypt.hash(new_password)
    from Database.super_admin_db import update_customer_password
    update_customer_password(email, password_hash)

    # Clean up OTP after successful reset
    from Database.super_admin_db import delete_otp
    delete_otp(email)

    return jsonify({"message": "Password reset successful. You can now log in with the new password."}), 200













# API route to insert device data
@app.route('/api/device', methods=['POST'])
def add_device():
    print("  device ......????")
    
    data = request.json
    
    # Log the incoming data to verify the request payload
    print("Received data:", data)
    
    if not data:
        return jsonify({"error": "No data provided"}), 400

    # Extract the customer email from the incoming request
    customer_email = data.get('customer_email')
    if not customer_email:
        return jsonify({"error": "Customer email is required"}), 400

    # Get the customer database name (using part of the email)
    customer_db_name = customer_email.split('@')[0]  
    print(customer_db_name)
    
    # Extract device details
    name = data.get('deviceName')
    ip_or_domain_name = data.get('ipDomainName')
    device_type = data.get('deviceType')
    device_model = data.get('deviceModel')
    port = data.get('port')
    channel_no = data.get('channelNumber')
    online_status = data.get('onlineStatus')
    sn = data.get('sn')
    operation = 'Active'

    # Log the extracted fields to verify them
    print("Device data:", name, ip_or_domain_name, device_type, device_model, port, channel_no, online_status, sn)
    
    # Validate that all required fields are provided
    if not all([name, ip_or_domain_name, device_type, device_model, port, channel_no, online_status, sn]):
        return jsonify({"error": "All fields are required"}), 400

    # Insert device data into the customer's database
    from Database.customer_db import insert_device_data
    try:
        insert_device_data(customer_db_name, name, ip_or_domain_name, device_type, device_model, port, channel_no, online_status, sn, operation)
        return jsonify({"message": "Device data inserted successfully"}), 201
    except Exception as e:
        print(f"Error inserting device data: {e}")
        return jsonify({"error": "Failed to insert device data"}), 500

























# Add CORS headers to all responses
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')  # Replace '*' with specific origin if needed
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    return response




if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0',port=8080)
