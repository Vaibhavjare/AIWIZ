
from flask import Flask, request, jsonify
from Database.super_admin_db import (
    get_customer_by_email,
    insert_tempuser,
    insert_customer,
    delete_temp_user,
    delete_otp,
    insert_otp,
    get__email_and_otp,
    update_otp_in_both_tables,
    retrieve_otp_by_email,
    update_customer_password,
)
from Database.customer_db import (
    insert_device_data,
    get_all_devices,
    insert_camera_info,
    get_camera_info_by_id,
    update_camera_info,
    delete_camera_info,
)
from email_validator import validate_email, EmailNotValidError
from flask_mail import Mail, Message
from passlib.hash import sha256_crypt
from flask_cors import CORS
import random
import os
import logging
from functools import wraps

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.urandom(24)

# Enable CORS
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# Mail configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = "aiwiztechsoln@gmail.com"
app.config['MAIL_PASSWORD'] = 'lqfp kvxh nhnm abnx'

mail = Mail(app)
logging.basicConfig(level=logging.INFO)

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

# Authentication middleware
def authenticate_user(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        username = request.headers.get('X-Username')
        password = request.headers.get('X-Password')
        print(username,password,"11111111")
        if not username or not password:
            return jsonify({"error": "Authentication credentials are missing"}), 401

        # Authenticate user
        customer = get_customer_by_email(username)
        if not customer or not sha256_crypt.verify(password, customer[4]):
            return jsonify({"error": "Invalid username or password"}), 401

        return func(*args, **kwargs)
    return wrapper

# Registration endpoint
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

    print(full_name, email, password, confirm_password, agree_terms, sn, address)

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
    # print(existing_customer,"2222")
    if existing_customer:
        return jsonify({"error": "Email is already registered"}), 401
    
    sn_list = [f"rbpi{str(i)}" for i in range(1, 101)]
    print("!!!!!!!!!!!!!")

    # Check if a given serial number (sn) is in the list
    if sn in sn_list:
        print(f"{sn} is present in the list.")
    else:
        return jsonify({"error": "WRONG SN"}), 405
    
    

    from Database.super_admin_db import get_customer_by_sn
    sn_info = get_customer_by_sn(sn)
    print(sn_info,"!!!!!!!!!!!!!")
    if sn_info:
        return jsonify({"error": "Sn is already registered"}), 405

    # Send OTP and insert temp user
    else:
        otp_1 = send_otp(email)
        password_hash = sha256_crypt.hash(password)
        insert_tempuser(full_name, email, email, password_hash, contact_number, address, database_name, sn, otp_1)
        
        return jsonify({"success": True,"message": "OTP sent to email. Please verify to complete registration."}), 201


# Login endpoint
@app.route('/login', methods=['POST'])
def login():
    try:
        print("\n login API........!!!!!")
        data = request.json
        email = data.get('email')
        password = data.get('password')

        # Validate input fields
        if not all([email, password]):
            return jsonify({"error": "Email and Password are required"}), 400
        
        # Fetch customer by email
        customer = get_customer_by_email(email)
        print(customer)

        # Check if customer exists before attempting to process
        if customer is None:
            return jsonify({"error": "Invalid email or password"}), 400
    
        customer = list(customer)  # Converting dictionary values to list if necessary

        # Check password hash
        if sha256_crypt.verify(password, customer[4]):  # Assuming customer[4] holds the password hash
            database_name = email.split('@')[0]
            
            print(database_name)

            # Import and create necessary tables
            from Database.customer_db import (create_Cameras_info_table, create_device_info_table, 
                                               create_event_table, get_all_cameras_generated_https)
            create_Cameras_info_table(database_name)
            create_device_info_table(database_name)
            create_event_table(database_name)
            
            # Create the MongoDB database
            from Database.mongo_db import create_database
            create_database(database_name)
            
            # Get all cameras and generated_https URLs
            camera_data = get_all_cameras_generated_https(database_name)

            print("login successful....!")
            return jsonify({"success": True, "message": "Login successful", "camera_data": camera_data}), 200

        return jsonify({"success": True, "error": "Invalid email or password"}), 400

    except Exception as e:
        print(f"error during login: {e}")
        return jsonify({"error": "Failed to login"}), 500


# Resend OTP endpoint
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



# Verify OTP endpoint
@app.route('/verify-otp', methods=['POST'])
def verify_otp():
    print("\n verify-otp.......!")
    data = request.json
    email = data.get('email')
    otp = data.get('otp')


    # if not all([email, otp]):
    #     return jsonify({"error": "Email and OTP are required"}), 400
    if not all([email, otp]):
        return jsonify({"success": False, "error": "Email and OTP are required"}), 400



    temp_user = get__email_and_otp(email, otp)
    # print("121221",type(temp_user))
    

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
        from Database.mongo_db import create_database
        create_database(database_name)
        
    
        return jsonify({"success":True,"message": "Registration complete. You can now login."}), 200
    else:
        return jsonify({"success":True,"error": "Invalid OTP"}), 400




# Forgot password function to send OTP
@app.route('/forgot-password', methods=['POST'])
def forgot_password():
    print("\n forgot-password...||")
    data = request.json
    email = data.get('email')
    print(email)
    # Check if the email exists in the customer database
    existing_customer = get_customer_by_email(email)
    if not existing_customer:
        return jsonify({"error": "Email not found"}), 404

    # Send OTP via email
    otp = send_otp(email)

    if otp is None:
        return jsonify({"error": "Failed to send OTP. Please try again later."}), 500

    return jsonify({"message": "OTP sent to your email. Please verify it."}), 200

# Resend OTP endpoint
@app.route('/f_resend-otp', methods=['POST'])
def f_resend_otp():
    print("\n resend-otp.......!")
    data = request.json
    email = data.get('email')
    

    if not email:
        return jsonify({"error": "Email is required"}), 400
    new_otp = send_otp(email)
    print(email,new_otp)
    
    
    return jsonify({"message": "otp are resended"}), 200

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
            from Database.super_admin_db  import delete_otp
            
            return jsonify({"message": "OTP verified"}), 200
        else:
            print(f"Invalid OTP entered: {otp}")
            return jsonify({"error": "Invalid OTP"}), 400
    except Exception as e:
        # Log the exact error
        print(f"Error during OTP verification: {e}")
        return jsonify({"error": "Failed to verify OTP"}), 500




# Registration endpoint
@app.route('/reset-password', methods=['POST'])
def reset_password():
    print("\n enter reset-password...||")

    # Log the incoming data for debugging
    data = request.json
    print(f"Received data: {data}")  # Log the full JSON data

    email = data.get('email')
    new_password = data.get('newPassword')
    confirm_password = data.get('confirmPassword')

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





# Add device endpoint
@app.route('/api/device', methods=['POST'])
@authenticate_user
def add_device():
    data = request.json
    customer_email = request.headers.get('X-Username')
    customer_db_name = customer_email.split('@')[0]

    name = data['deviceName']
    ip_or_domain_name = data['ipDomainName']
    device_type = data['deviceType']
    device_model = data['deviceModel']
    port = data['port']
    channel_no = data['channelNumber']
    online_status = data['onlineStatus']
    sn = data['sn']
    operation = 'Active'

    insert_device_data(customer_db_name, name, ip_or_domain_name, device_type, device_model, port, channel_no, online_status, sn, operation)
    return jsonify({"message": "Device data inserted successfully"}), 201



@app.route('/api/camera-info/retrieve', methods=['GET'])
@authenticate_user
def retrieve_all_camera_info():
    try:
        customer_email = request.headers.get('X-Username')
        if not customer_email:
            return jsonify({"error": "Missing 'X-Username' header"}), 400

        customer_db_name = customer_email.split('@')[0]
        from Database.customer_db import get_all_cameras_info       
        camera_info_list = get_all_cameras_info(customer_db_name)
        
        if not camera_info_list:
            return jsonify({"message": "No camera information found"}), 404

        # Returning the raw list for simplicity
        return jsonify(camera_info_list), 200

    except Exception as e:
        print(f"Error retrieving camera info: {str(e)}")
        return jsonify({"error": "Failed to retrieve camera info", "details": str(e)}), 500

def generate_https(customer_db_name, camera_id):
    print("hi")
    from Database.super_admin_db import get_sn_from_database_name

    # Retrieve the serial number (sn) using the customer's database name
    sn = get_sn_from_database_name(customer_db_name)  # Pass customer_db_name as the target db name

    if sn is None:
        return {"error": "SN not found for the given customer database name"}
    
    # Build the HTTPS URL
    public_ip = "54.156.163.234"
    port = "8082"
    https_url = f"http://{public_ip}:{port}/video_feed/{sn}/{camera_id}"

    print(https_url)
    return  https_url




@app.route('/api/camera-info', methods=['POST'])
@authenticate_user
def add_camera_info():
    print("Camera-info endpoint triggered...")

    # Get data from the request body
    data = request.json
    print("Received data:", data)

    customer_email = request.headers.get('X-Username')
    customer_db_name = customer_email.split('@')[0]
    print("Customer DB Name:", customer_db_name)

    # Extract the data fields
    ip_address = data.get('ip_address')
    mac_address = data.get('mac_address')
    username = data.get('username')
    password = data.get('password')
    onvif_rtsp_settings = data.get('onvif_rtsp_settings')
    port_number = data.get('port_number')
    alert_mode = data['alertmode']
    print(alert_mode)
    use_cases = data.get('use_cases')
    
    # Get the current camera count and generate camera_id
    from Database.customer_db import count_camera_ids
    camera_count = count_camera_ids(customer_db_name)
    print(camera_count)
    camera_count=camera_count['camera_count']
    camera_id =  + 1
    print(camera_id)  # Assuming the camera_id starts from 1 and increments with each new entry
    
    # Generate the HTTPS URL for the camera
    generated_https = generate_https(customer_db_name,camera_id)

    # Log the extracted fields
    print(customer_db_name, ip_address, mac_address, username, password, onvif_rtsp_settings, port_number, alert_mode, use_cases, generated_https)

    # Validate required fields
    if not all([customer_db_name, ip_address, mac_address, username, password, onvif_rtsp_settings, port_number, alert_mode, use_cases, generated_https]):
        return jsonify({"error": "All fields are required"}), 400

    try:
        # Call the insert_camera_info function to insert the data into the database
        insert_camera_info(customer_db_name, ip_address, mac_address, username, password, onvif_rtsp_settings, port_number, alert_mode, use_cases, generated_https)
        return jsonify({"message": "Camera info inserted successfully"}), 201
    except Exception as e:
        print(f"Error inserting camera info: {e}")
        return jsonify({"error": "Failed to insert camera info"}), 500




# Search camera info endpoint


@app.route('/api/camera-info/search', methods=['POST'])
@authenticate_user
def search_camera_info():
   
    try:
        # Logging initial API call
        print("Camera-info search initiated...")

        # Parse request data and headers
        data = request.get_json()
        if not data or 'camera_id' not in data:
            return jsonify({"error": "Missing required 'camera_id' in request body"}), 400

        customer_email = request.headers.get('X-Username')
        if not customer_email:
            return jsonify({"error": "Missing 'X-Username' header"}), 400

        customer_db_name = customer_email.split('@')[0]
        cam_id = data['camera_id']
        print(f"Customer DB: {customer_db_name}, Camera ID: {cam_id}")

        # Fetch camera info from the database
        res = get_camera_info_by_id(customer_db_name, cam_id)

        if res:
            print(f"Data retrieved: {res}")
            response_data = {
                "camera_id": res[0],
                "ipAddress": res[1],
                "macAddress": res[2],
                "username": res[3],
                "password": res[4],
                "onvifRtspSettings": res[5],
                "portNumber": res[6],
                "alertMode": res[7],
                "useCases": res[8],
            }
            print(response_data)
            
            return jsonify(response_data), 200
        else:
            print("No data found for the given camera ID.")
            return jsonify({"error": "Camera information not found"}), 404

    except Exception as e:
        print(f"An error occurred while retrieving camera info: {str(e)}")
        return jsonify({"error": "Failed to retrieve camera info", "details": str(e)}), 500

    



@app.route('/api/camera-info/update', methods=['POST'])
@authenticate_user
def update_camera_info():
    print("Camera-info update endpoint triggered...")
    # Get data from the request body
    data = request.json
    customer_email = request.headers.get('X-Username')
    customer_db_name = customer_email.split('@')[0]

    print("Customer DB Name:", customer_db_name)

    # Check if request body is empty
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    # Extract camera info from the data
    cam_id = data.get('camera_id')
    ip_address = data.get('ip_address')
    mac_address = data.get('mac_address')
    username = data.get('username')
    password = data.get('password')
    onvif_rtsp_settings = data.get('onvif_rtsp_settings')
    port_number = data.get('port_number')
    alert_mode = data.get('alert_mode')
    use_cases = data.get('use_cases')

    # Generate HTTPS URL using the camera ID and customer DB name
    generated_https = generate_https(customer_db_name, cam_id)

    # Log extracted fields
    print(customer_db_name, cam_id, ip_address, mac_address, username, password, onvif_rtsp_settings, port_number, alert_mode, use_cases, generated_https)

    # Validate required fields
    if not all([cam_id, ip_address, mac_address, username, password, onvif_rtsp_settings, port_number, alert_mode, use_cases, generated_https]):
        return jsonify({"error": "All fields are required"}), 400

    # Import the function to update camera info in the database
    from Database.customer_db import update_camera_info
    try:
        # Update camera info in the database
        update_camera_info(customer_db_name, cam_id, ip_address, mac_address, username, password, onvif_rtsp_settings, port_number, alert_mode, use_cases, generated_https)
        return jsonify({"message": "Camera info updated successfully"}), 200
    except Exception as e:
        print(f"Error updating camera info: {e}")
        return jsonify({"error": "Failed to update camera info"}), 500

    

# Delete camera info endpoint
@app.route('/api/camera-info/delete', methods=['POST'])
@authenticate_user
def delete_camera_info():
    print("  Camera-info delete  ......????")
    data = request.json
    customer_email = request.headers.get('X-Username')
    customer_db_name = customer_email.split('@')[0]
    print(customer_db_name)
    cam_id = data.get('camera_id')
    print(cam_id)
    from Database.customer_db import delete_camera_info
    delete_camera_info(customer_db_name,cam_id)
    return jsonify({"message": "Camera info deleted successfully"}), 200



#### EVENT APIS######



@app.route('/api/event-info/retrieve', methods=['GET'])
@authenticate_user
def retrieve_all_event_info():
    try:
        # Retrieve the customer email from the headers
        customer_email = request.headers.get('X-Username')
        if not customer_email:
            return jsonify({"error": "Missing 'X-Username' header"}), 400

        # Extract customer database name from email
        customer_db_name = customer_email.split('@')[0]
        print(f"Customer DB: {customer_db_name}")

        # Import the database function to fetch all event info
        from Database.customer_db import get_all_events      
        event_info_list = get_all_events(customer_db_name)
        
        # Check if event data exists
        if not event_info_list:
            return jsonify({"message": "No event information found"}), 404

        # Return the event information list
        return jsonify(event_info_list), 200

    except Exception as e:
        print(f"Error retrieving event info: {str(e)}")
        return jsonify({"error": "Failed to retrieve event info", "details": str(e)}), 500








@app.route('/api/event-info', methods=['POST'])
@authenticate_user
def add_event_info():
    print("  Event-info ......????")
    data = request.json
    print(data)

    # Extract customer email and derive database name
    customer_email = request.headers.get('X-Username')
    if not customer_email:
        return jsonify({"error": "Customer email is required"}), 400
    customer_db_name = customer_email.split('@')[0]
    print("Database Name:", customer_db_name)

    # Extract and validate required fields
    occur_time = data.get('occur_time')
    occur_date = data.get('occur_date')
    event_type = data.get('event_type')
    device_name = data.get('device_name')
    camera_location_description = data.get('camera_location_description')
    handling_time = data.get('handling_time')
    handling_status = data.get('handling_status')
    operation = data.get('operation')

    # Check if any required field is missing
    if not all([occur_time, occur_date, event_type, device_name, camera_location_description, 
                handling_time, handling_status, operation]):
        return jsonify({"error": "All fields are required"}), 400

    # Call the database function to insert event data
    from Database.customer_db import insert_event_data
    try:
        insert_event_data(
            customer_db_name, occur_time, occur_date, event_type, device_name,
            camera_location_description, handling_time, handling_status, operation
        )
        return jsonify({"message": "Event info inserted successfully"}), 201
    except Exception as e:
        print(f"Error inserting EVENT data: {e}")
        return jsonify({"error": "Failed to insert Event info"}), 500


@app.route('/api/event-info/search', methods=['POST'])
@authenticate_user
def search_event_info():
    try:
        # Logging initial API call
        print("Event-info search initiated...")

        # Parse request data and headers
        data = request.get_json()
        if not data or 'serial_no' not in data:
            return jsonify({"error": "Missing required 'serial_no' in request body"}), 400

        customer_email = request.headers.get('X-Username')
        if not customer_email:
            return jsonify({"error": "Missing 'X-Username' header"}), 400

        customer_db_name = customer_email.split('@')[0]
        serial_no = data['serial_no']
        print(f"Customer DB: {customer_db_name}, Serial No: {serial_no}")

        # Fetch event info from the database
        from Database.customer_db import get_event_by_serial_no
        res = get_event_by_serial_no(customer_db_name, serial_no)

        if res:
            print(f"Data retrieved: {res}")
            response_data = {
                "serial_no": res[0],
                "occur_time": res[1],
                "occur_date": res[2],
                "event_type": res[3],
                "device_name": res[4],
                "camera_location_description": res[5],
                "handling_time": res[6],
                "handling_status": res[7],
                "operation": res[8],
            }
            print(response_data)

            return jsonify(response_data), 200
        else:
            print("No data found for the given serial number.")
            return jsonify({"error": "Event information not found"}), 404

    except Exception as e:
        print(f"An error occurred while retrieving event info: {str(e)}")
        return jsonify({"error": "Failed to retrieve event info", "details": str(e)}), 500


@app.route('/api/event-info/update', methods=['POST'])
@authenticate_user
def update_event_info():
    print("Event-info update initiated...")

    # Parse request data and headers
    data = request.json
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    customer_email = request.headers.get('X-Username')
    if not customer_email:
        return jsonify({"error": "Missing 'X-Username' header"}), 400

    customer_db_name = customer_email.split('@')[0]
    print("Customer DB:", customer_db_name)

    # Extract fields from request data
    serial_no = data.get('serial_no')
    occur_time = data.get('occur_time')
    occur_date = data.get('occur_date')
    event_type = data.get('event_type')
    device_name = data.get('device_name')
    handling_person = data.get('handling_person')
    handling_time = data.get('handling_time')
    handling_remark = data.get('handling_remark')
    handling_status = data.get('handling_status')
    operation = data.get('operation')

    print(f"Data received for update: {serial_no}, {occur_time}, {occur_date}, {event_type}, {device_name}, {handling_person}, {handling_time}, {handling_remark}, {handling_status}, {operation}")

    # Validate required fields
    if not serial_no:
        return jsonify({"error": "'serial_no' is required"}), 400

    if not any([occur_time, occur_date, event_type, device_name, handling_person, handling_time, handling_remark, handling_status, operation]):
        return jsonify({"error": "At least one field to update is required"}), 400

    # Update event info in the database
    from Database.customer_db import update_event_by_serial_no
    try:
        update_event_by_serial_no(customer_db_name, serial_no, occur_time, occur_date, event_type, device_name, handling_person, handling_time, handling_remark, handling_status, operation)
        return jsonify({"message": "Event info updated successfully"}), 200
    except Exception as e:
        print(f"Error updating event info: {e}")
        return jsonify({"error": "Failed to update event info", "details": str(e)}), 500






@app.route('/insert_video', methods=['POST'])
@authenticate_user
def insert_video_route():
    """
    Endpoint to insert video data into the MongoDB database.
    Expects JSON input with 'db_name' and 'video_data'.
    """
    print("[INFO] Executing '/insert_video' route")
    data = request.json
    customer_email = request.headers.get('X-Username')
    if not customer_email:
        return jsonify({"error": "Missing 'X-Username' header"}), 400

    customer_db_name = customer_email.split('@')[0]
    print("Customer DB:", customer_db_name)

    video_data = data.get('video_data')

    if not customer_db_name or not video_data:
        print("[ERROR] Missing 'db_name' or 'video_data' in request")
        return jsonify({"status": "failure", "message": "Missing required fields: 'db_name' or 'video_data'"}), 400

    try:
        from Database.mongo_db import insert_video_data
        inserted_id = insert_video_data(customer_db_name, video_data)
        print(f"[SUCCESS] Video data inserted with ID: {inserted_id}")
        return jsonify({
            "status": "success",
            "message": f"Video data inserted successfully with ID: {inserted_id}"
        }), 200
    except Exception as e:
        print(f"[ERROR] Exception occurred: {e}")
        return jsonify({"status": "failure", "message": f"Error occurred: {str(e)}"}), 500

@app.route('/search_videos', methods=['GET'])
@authenticate_user
def search_videos_route():
    
    print("Executing '/search_videos' route")
    customer_email = request.headers.get('X-Username')
    if not customer_email:
        return jsonify({"error": "Missing 'X-Username' header"}), 400

    customer_db_name = customer_email.split('@')[0]
    print("Customer DB:", customer_db_name)

    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')

    if not customer_db_name or not start_time or not end_time:
        print(" Missing 'db_name', 'start_time', or 'end_time' in request")
        return jsonify({"status": "failure", "message": "Missing required fields: 'db_name', 'start_time', or 'end_time'"}), 400

    try:
        from Database.mongo_db import search_videos_by_time
        results = search_videos_by_time(customer_db_name, start_time, end_time)
        if results:
            print(f"[SUCCESS] Found {len(results)} video(s) matching the criteria")
            return jsonify({
                "status": "success",
                "message": f"Found {len(results)} video(s) within the specified time range.",
                "data": results
            }), 200
        else:
            print("[INFO] No videos found within the specified time range")
            return jsonify({
                "status": "success",
                "message": "No videos found within the specified time range."
            }), 200
    except Exception as e:
        print(f"[ERROR] Exception occurred: {e}")
        return jsonify({"status": "failure", "message": f"Error occurred: {str(e)}"}), 500






# Add CORS headers to all responses
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-Username,X-Password')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    return response

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)


