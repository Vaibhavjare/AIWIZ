from flask import Flask, request, jsonify, session
from Database.super_admin_db import get_customer_by_email, insert_tempuser, insert_customer, delete_temp_user, delete_otp, insert_otp, get__email_and_otp
from Database.customer_db import insert_device_data
from flask_session import Session

from email_validator import validate_email, EmailNotValidError
from flask_mail import Mail, Message
from passlib.hash import sha256_crypt
from flask_cors import CORS
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user
import random
import os
import logging
from datetime import timedelta

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Enable CORS for all routes and allow credentials
# CORS(app, supports_credentials=True, origins=['http://localhost:3000'])
# from flask_cors import CORS

CORS(app, supports_credentials=True, origins=['*'],
     allow_headers=['Content-Type', 'Authorization'],
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])


# Secret key for sessions
app.config['SECRET_KEY'] = 'your-secret-key'

# Mail configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME', 'default@example.com')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD', 'defaultpassword')

mail = Mail(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Logging configuration
logging.basicConfig(level=logging.INFO)

# Session configuration
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False

# Initialize session
Session(app)
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False

# User model for Flask-Login
class User(UserMixin):
    def __init__(self, id, email):
        self.id = id
        self.email = email

@login_manager.user_loader
def load_user(user_id):
    customer = get_customer_by_email(user_id)
    if customer:
        return User(id=user_id, email=customer[2])  # Assuming customer[2] is the email
    return None

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




# Forgot password function to send OTP
@app.route('/forgot-password', methods=['POST'])
def forgot_password():
    print("\n forgot-password...||")
    data = request.json
    email = data.get('email')

    # Check if the email exists in the customer database
    existing_customer = get_customer_by_email(email)
    if not existing_customer:
        return jsonify({"error": "Email not found"}), 404

    # Send OTP via email
    otp = send_otp(email)

    if otp is None:
        return jsonify({"error": "Failed to send OTP. Please try again later."}), 500

    return jsonify({"message": "OTP sent to your email. Please verify it."}), 200



# Login function
@app.route('/login', methods=['GET', 'POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        # Handle OPTIONS request
        return jsonify({
            "methods": ["GET", "POST", "OPTIONS"],
            "description": "Login endpoint for user authentication"
        }), 200

    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')

        logging.info("Login API called")

        # Validate input fields
        if not all([email, password]):
            return jsonify({"error": "Email and Password are required"}), 400

        # Fetch customer by email
        customer = get_customer_by_email(email)

        # Check if customer exists
        if customer is None:
            return jsonify({"error": "Invalid email or password"}), 400

        # Check password hash
        if sha256_crypt.verify(password, customer[4]):  # Assuming customer[4] holds the password hash
            session["user"] = email
            logging.info(f"Session set with user email: {session['user']}")

            # Create customer-specific tables
            database_name = email.split('@')[0]
            logging.info(f"Logged-in user database: {database_name}")

            from Database.customer_db import create_Cameras_info_table, create_device_info_table
            create_Cameras_info_table(database_name)
            create_device_info_table(database_name)

            return jsonify({"message": "Login successful"}), 200

        return jsonify({"error": "Invalid email or password"}), 400
    except Exception as e:
        logging.error(f"Error during login: {str(e)}")
        return jsonify({"error": "Failed to login"}), 500
    


# OTP verification function for forgot password@app.route('/f_verifyOtp', methods=['POST'])
@app.route('/f_verifyOtp', methods=['POST'])
def f_verifyOtp():
    print("\nEntering verify OTP...||")
    data = request.json
    email = data.get('email')
    otp = data.get('otp')

    if not all([email, otp]):
        return jsonify({"error": "Email and OTP are required"}), 400

    # Retrieve OTP from the database
    from Database.super_admin_db import retrieve_otp_by_email
    try:
        # Debug print to ensure function runs
        print(f"Fetching OTP for email: {email} and otp: {otp}")

        # Retrieve stored OTP
        stored_otp = retrieve_otp_by_email(email, otp)
        if not stored_otp:
            return jsonify({"error": "OTP not found or expired"}), 404

        stored_otp = list(stored_otp)
        print(f"Stored OTP: {stored_otp}")

        # Compare stored OTP and provided OTP
        if str(stored_otp[2]) == str(otp):  # Ensure string comparison
            print(f"OTP verified successfully for {email}")
            return jsonify({"message": "OTP verified"}), 200
        else:
            print(f"Invalid OTP entered: {otp}")
            return jsonify({"error": "Invalid OTP"}), 400
    except Exception as e:
        # Log the exact error
        print(f"Error during OTP verification: {e}")
        return jsonify({"error": "Failed to verify OTP"}), 500
    




@app.route('/reset-password', methods=['POST'])
def reset_password():
    print("\n enter reset-password...||")

    # Log the incoming data for debugging
    data = request.json
    print(f"Received data: {data}")  # Log the full JSON data

    email = data.get('email')
    new_password = data.get('new_password')
    confirm_password = data.get('confirm_password')

    # Log each field to see if they're correctly extracted
    print(f"Email: {email}, New Password: {new_password}, Confirm Password: {confirm_password}")

    # Check if any field is missing
    if not all([email, new_password, confirm_password]):
        return jsonify({"error": "All fields are required"}), 400

    # Password validation
    if len(new_password) < 8 or not any(char.isdigit() for char in new_password) or not any(char.isupper() for char in new_password):
        return jsonify({"error": "Password must be at least 8 characters long, contain a number, and an uppercase letter"}), 400

    if new_password != confirm_password:
        return jsonify({"error": "Passwords do not match"}), 400

    # Hash the new password and update it in the database
    password_hash = sha256_crypt.hash(new_password)
    from Database.super_admin_db import update_customer_password
    update_customer_password(email, password_hash)

    # Clean up OTP after successful reset
    delete_otp(email)

    return jsonify({"message": "Password reset successful. You can now log in with the new password."}), 200


#################################################################################################################################################################################################


# Add Camera Info
@app.route('/api/camera-info', methods=['POST', 'GET', 'OPTIONS'])
def add_camera_info():
    print("hi")
    if request.method == 'OPTIONS':
        # Handle CORS preflight
        return jsonify({
            "methods": ["POST", "GET", "OPTIONS"],
            "description": "Camera Info endpoint for adding new camera details"
        }), 200

    logging.info("From camera_info endpoint")
    logging.info(f"Current session data: {session}")

    try:
        # Get user from session
        if 'user' not in session:
            logging.warning("Unauthorized access: No user in session")
            return jsonify({"error": "Unauthorized access. Please log in."}), 401

        email = session['user']
        logging.info(f"Session user email: {email}")

        # Convert email into database name
        database_name = email.split('@')[0]
        logging.info(f"Logged-in user database: {database_name}")

        # Ensure Content-Type is application/json
        if request.content_type != 'application/json':
            return jsonify({"error": "Content-Type must be application/json"}), 415

        # Extract and validate JSON data from the request
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid request. No JSON payload provided."}), 400

        # Extract fields from the request
        customer_email = data.get('customer_email')
        ip_address = data.get('ip_address')
        mac_address = data.get('mac_address')
        username = data.get('username')
        password = data.get('password')
        onvif_rtsp_settings = data.get('onvif_rtsp_settings')
        port_number = data.get('port_number')
        alert_mode = data.get('alertmode')
        use_cases = data.get('use_cases')

        # Validate required fields
        if not all([customer_email, ip_address, mac_address, username, password, onvif_rtsp_settings, port_number, alert_mode, use_cases]):
            return jsonify({"error": "All fields are required"}), 400

        logging.info(f"Received data: {customer_email}, {ip_address}, {mac_address}, {username}, {onvif_rtsp_settings}, {port_number}, {alert_mode}, {use_cases}")

        # Insert camera info into the database
        from Database.customer_db import insert_camera_info
        insert_camera_info(
            database_name,
            ip_address,
            mac_address,
            username,
            password,
            onvif_rtsp_settings,
            port_number,
            alert_mode,
            use_cases
        )

        logging.info("Camera info inserted successfully.")
        return jsonify({"message": "Camera info inserted successfully"}), 201

    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    



# API route to insert serach camera info
@app.route('/api/camera-info/search', methods=['POST'])
def search_camera_info():

    print("  Camera-info  search......????")
    print("hi")
    if request.method == 'OPTIONS':
        # Handle CORS preflight
        return jsonify({
            "methods": ["POST", "GET", "OPTIONS"],
            "description": "Camera Info endpoint for adding new camera details"
        }), 200

    logging.info("From camera_info search  endpoint")
    logging.info(f"Current session data: {session}")

    try:
        data = request.json
        print(data)
        customer_email = session['user']
        if not customer_email:
            return jsonify({"error": "Customer email is required"}), 400
        customer_db_name = customer_email.split('@')[0]  
        # customer_db_name = 'abhi45'
        print("hi",customer_db_name)

        cam_id = data['camera_id']
        from Database.customer_db import get_camera_info_by_id
        res = get_camera_info_by_id(customer_db_name,cam_id)
        print(res)

        if not res:
            print("data are retrive : ")
            return jsonify(res)
        else:
            print(f"Error not retrive camera info: {e}")
            return jsonify({"error": "Failed to retrive camera-info"}), 500
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    


# API route to insert device data
@app.route('/api/camera-info/update', methods=['POST'])
def update_camera_info():

    print("  Camera-info update ......????")

    print("hi")
    if request.method == 'OPTIONS':
        # Handle CORS preflight
        return jsonify({
            "methods": ["POST", "GET", "OPTIONS"],
            "description": "Camera Info endpoint for adding new camera details"
        }), 200

    logging.info("From camera_info search  endpoint")
    logging.info(f"Current session data: {session}")

    try:
        data = request.json
        print(data)
        customer_email = session['user']
    
        if not customer_email:
            return jsonify({"error": "Customer email is required"}), 400
        customer_db_name = customer_email.split('@')[0]  
        # customer_db_name = 'abhi45'
        print("hi",customer_db_name)

        cam_id = data['camera_id']

        ip_address = data['ip_address']
        mac_address= data['mac_address']
        username =  data['username']
        password = data['password']
        onvif_rtsp_settings =data['onvif_rtsp_settings']
        port_number = data['port_number']
        alert_mode = data['alertmode']
        use_cases = data['use_cases']
        print(customer_db_name, cam_id,ip_address, mac_address, username, password, onvif_rtsp_settings, port_number, alert_mode, use_cases)
        if not [customer_db_name,cam_id,ip_address, mac_address, username, password, onvif_rtsp_settings, port_number, alert_mode, use_cases]:
            return jsonify({"error": "All field required is required"}), 400

        from Database.customer_db import update_camera_info
        try:
            update_camera_info(customer_db_name,cam_id, ip_address, mac_address, username, password, onvif_rtsp_settings, port_number, alert_mode, use_cases)
            return jsonify({"message": "Camera info updated   successfully"}), 201
        except Exception as e:
            print(f"Error inserting device data: {e}")
            return jsonify({"error": "Failed update camera-info"}), 500
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    


# API route to insert device data
@app.route('/api/camera-info/delete', methods=['POST'])
def delete_camera_info():

    print("  Camera-info delete  ......????")
    

    print("hi")
    if request.method == 'OPTIONS':
        # Handle CORS preflight
        return jsonify({
            "methods": ["POST", "GET", "OPTIONS"],
            "description": "Camera Info endpoint for adding new camera details"
        }), 200

    logging.info("From camera_info search  endpoint")
    logging.info(f"Current session data: {session}")

    try:
        data = request.json
        customer_email = session['user']
    
        if not customer_email:
            return jsonify({"error": "Customer email is required"}), 400
        customer_db_name = customer_email.split('@')[0]  
        print(customer_db_name)
        cam_id = data.get('cam_id')
        from Database.customer_db import delete_camera_info
        delete_camera_info(customer_db_name,cam_id)
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    



@app.route('/api/device', methods=['POST'])
def add_device():
    print("Device insertion request received.")
    
    customer_db_name ='tsbagul21'
    # show_devices(customer_db_name)
    data = request.json
    print(data)
    
    # Check if data is provided
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    try:
        # Extract fields from the incoming JSON data
        customer_email = data.get('customer_email')  # Adjusted to match the input JSON field
        name = data['deviceName']
        ip_or_domain_name = data['ipDomainName']
        device_type = data['deviceType']  # Ensure this variable name is consistent
        device_model = data['deviceModel']
        port = data['port']
        channel_no = data['channelNumber']
        online_status = data['onlineStatus']
        sn = data['sn']
        operation = 'Active'  # Assuming default operation status is 'Active'

        # Print extracted values for debugging
        print([customer_email, name, ip_or_domain_name, device_type, device_model, port, channel_no, online_status, sn, operation])
        
        # Check that all required fields are provided
        if not all([customer_email, name, ip_or_domain_name, device_type, device_model, port, channel_no, online_status, sn]):
            return jsonify({"error": "All fields are required"}), 400

        # Generate the customer database name from the email
        customer_db_name = customer_email.split('@')[0]
        print(f"Inserting device for {customer_db_name}")

        # Insert device data into the customer database
        insert_device_data(customer_db_name, name, ip_or_domain_name, device_type, device_model, port, channel_no, online_status, sn, operation)

        return jsonify({"message": "Device data inserted successfully"}), 201
    
    except KeyError as e:
        return jsonify({"error": f"Missing field: {str(e)}"}), 400
    except Exception as e:
        print(f"Error inserting device data: {e}")
        return jsonify({"error": "Failed to insert device data"}), 500




# Logout function
@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user', None)
    return jsonify({'message': 'Logged out successfully'}), 200

# Add CORS headers to all responses
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    return response

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)


