

import mysql.connector
import os
from flask import jsonify
from datetime import datetime
from mysql.connector import Error


# Function to connect to a specific customer database
def get_customer_db_connection(customer_db_name):
    conn = mysql.connector.connect(
        host='localhost',         # Localhost since MySQL is running on your machine
        user='root',              # MySQL root user (or another user if applicable)
        password='Indra#123',     # Password for the root user
        database=customer_db_name # Dynamic database name based on the customer
    )
    return conn





# Function to create the Cameras_info table in the customer database
def create_Cameras_info_table(customer_db_name):
    conn = get_customer_db_connection(customer_db_name)
    cursor = conn.cursor()

    # SQL statement to create the Cameras_info table
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS Cameras_info (
        camera_id INT AUTO_INCREMENT PRIMARY KEY,
        ip_address VARCHAR(45)  NOT NULL,
        mac_address VARCHAR(17)  NOT NULL,
        username VARCHAR(50) NOT NULL,
        password VARCHAR(255) NOT NULL,
        onvif_rtsp_settings VARCHAR(255),
        port_number INT NOT NULL,
        alert_mode VARCHAR(255) NOT NULL,
        use_cases VARCHAR(255),
        genrated_https VARCHAR(1000),
        rtsp_URL VARCHAR(1000),
        external_port INT 
    );
    """

    try:
        # Execute the SQL command to create the Cameras_info table
        cursor.execute(create_table_sql)
        conn.commit()
        print(f"Cameras_info table created successfully in {customer_db_name}!")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        cursor.close()
        conn.close()



# Database/customer_db.py
def create_table():
    # Logic to create a table in the database
    print("Table created")


def create_customer(customer_data):
    # Function logic for creating a customer
    pass



def insert_camera_info(customer_db_name, ip_address, mac_address, username, password, onvif_rtsp_settings, port_number, alert_mode, use_cases, generated_https):
    print("Starting to insert camera info...")  # Log to check if function is triggered
    conn = get_customer_db_connection(customer_db_name)
    cursor = conn.cursor()

    try:
        # Convert the list of use cases into a comma-separated string
        # Log the use cases if needed

        cursor.execute("""
            INSERT INTO Cameras_info (ip_address, mac_address, username, password, onvif_rtsp_settings, port_number, alert_mode, use_cases, genrated_https)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (ip_address, mac_address, username, password, onvif_rtsp_settings, port_number, alert_mode, use_cases, generated_https))

        print("Camera info inserted successfully")  # Log the success
        conn.commit()
    except mysql.connector.Error as err:
        print(f"Error: {err}")  # Log the error for debugging
        return jsonify({"error": str(err)}), 500
    finally:
        cursor.close()
        conn.close()

    return {"message": "Camera added successfully"}



# Function to retrieve all cameras_info data from the customer database
def get_all_cameras_info(customer_db_name):
    print("hi")
    conn = get_customer_db_connection(customer_db_name)
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM Cameras_info")
        cameras = cursor.fetchall()
        print(cameras)
        return cameras
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return []
    finally:
        cursor.close()
        conn.close()


def update_camera_info(customer_db_name, camera_id, ip_address, mac_address, username, password, onvif_rtsp_settings, port_number, alert_mode, use_cases, generated_https):
    print("Updating camera info...")
    conn = get_customer_db_connection(customer_db_name)
    cursor = conn.cursor()

    # Ensure 'use_cases' is a string if it's a list (convert list to comma-separated string)
    if isinstance(use_cases, list):
        use_cases = ', '.join(use_cases)

    update_query = """
        UPDATE Cameras_info
        SET ip_address = %s,
            mac_address = %s,
            username = %s,
            password = %s,
            onvif_rtsp_settings = %s,
            port_number = %s,
            alert_mode = %s,
            use_cases = %s,
            genrated_https = %s
        WHERE camera_id = %s
    """

    try:
        cursor.execute(update_query, (ip_address, mac_address, username, password, onvif_rtsp_settings, port_number, alert_mode, use_cases, generated_https, camera_id))
        conn.commit()
        return {"message": f"Camera with ID {camera_id} updated successfully"}
    except mysql.connector.Error as err:
        return {"error": str(err)}
    finally:
        cursor.close()
        conn.close()



def update_camera_info_rtsp(customer_db_name, camera_id, external_port, rtsp_url):

    print("Starting to update camera info in the database...")  # Log function start

    # Connect to the customer's database
    conn = get_customer_db_connection(customer_db_name)
    cursor = conn.cursor()

    try:
        # Update query for external_port and rtsp_URL
        cursor.execute("""
            UPDATE Cameras_info
            SET external_port = %s, rtsp_URL = %s
            WHERE camera_id = %s
        """, (external_port, rtsp_url, camera_id))
        
        conn.commit()
        print("Camera info updated successfully")  # Debug log
        return {"message": "Camera info updated successfully"}

    except mysql.connector.Error as err:
        print(f"Error updating camera info: {err}")  # Log error
        return {"error": str(err)}

    finally:
        cursor.close()
        conn.close()




# Function to get camera info by camera_id
def get_camera_info_by_id(customer_db_name, camera_id):
    # Connect to the customer database
    # print("get camera _info by id")
    conn = get_customer_db_connection(customer_db_name)
    cursor = conn.cursor()

    try:
        # SQL query to fetch camera details based on camera_id
        query = "SELECT * FROM Cameras_info WHERE camera_id = %s"
        cursor.execute(query, (camera_id,))

        # Fetch the result
        camera_info = cursor.fetchone()
        # print("hi",camera_info)
        if camera_info:
            return camera_info
        else:
            return {"message": f"No camera found with ID {camera_id}"}

    except mysql.connector.Error as err:
        return {"error": str(err)}

    finally:
        cursor.close()
        conn.close()

def count_camera_ids(customer_db_name):
    print("Counting camera ids...")
    conn = get_customer_db_connection(customer_db_name)
    cursor = conn.cursor()

    count_query = "SELECT COUNT(camera_id) FROM Cameras_info"

    try:
        cursor.execute(count_query)
        result = cursor.fetchone()
        camera_count = result[0]  # The count will be the first element in the result tuple
        return {"camera_count": camera_count}
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return {"error": str(err)}
    finally:
        cursor.close()
        conn.close()

def get_all_cameras_generated_https(customer_db_name):
    # Establish connection to the customer database
    conn = get_customer_db_connection(customer_db_name)
    cursor = conn.cursor()

    # Query to fetch camera_id and generated_https from the Cameras_info table
    query = """
        SELECT camera_id, generated_https
        FROM Cameras_info
    """

    try:
        cursor.execute(query)
        # Fetch all camera info
        camera_info = cursor.fetchall()

        # Convert camera_id into the format cam1, cam2, cam3, etc.
        result = [{"camera_id": f"cam{cam[0]}", "generated_https": cam[1]} for cam in camera_info]
        print(result)

        return result

    except mysql.connector.Error as err:
        print(f"Error fetching camera info: {err}")
        return {"error": str(err)}

    finally:
        cursor.close()
        conn.close()


# Function to delete camera information by camera_id
def delete_camera_info(customer_db_name, camera_id):
    print("delete")
    conn = get_customer_db_connection(customer_db_name)
    if conn is None:
        print("Failed to connect to the database.")
        return

    cursor = conn.cursor()
    print("sdfghjkfghj",camera_id)

    try:
        # Step 1: Delete the specified camera record
        print("hi")
        cursor.execute("DELETE FROM Cameras_info WHERE camera_id = %s", (camera_id,))
        conn.commit()
        print(f"Camera info with ID {camera_id} deleted successfully.")

        # Step 2: Renumber camera_id sequentially
        cursor.execute("SET @new_id = 0;")
        cursor.execute("UPDATE Cameras_info SET camera_id = (@new_id := @new_id + 1);")
        
        # Step 3: Reset the AUTO_INCREMENT value
        cursor.execute("ALTER TABLE Cameras_info AUTO_INCREMENT = 1;")
        conn.commit()
        print("Camera IDs renumbered successfully.")
        
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        cursor.close()
        conn.close()



# Function to create the Device_info table in the customer database
def create_device_info_table(customer_db_name):
    conn = get_customer_db_connection(customer_db_name)
    cursor = conn.cursor()

    # SQL statement to create the Device_info table
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS Device_info (
        No INT AUTO_INCREMENT PRIMARY KEY,
        Name VARCHAR(255),
        IP_or_Domain_Name VARCHAR(255),
        Device_type VARCHAR(255),
        Device_model VARCHAR(255),
        Port INT(10),
        Channel_no VARCHAR(255),
        Online_status VARCHAR(255),
        SN VARCHAR(255),
        Operation VARCHAR(255)
    );
    """

    try:
        # Execute the SQL command to create the Device_info table
        cursor.execute(create_table_sql)
        conn.commit()
        print(f"Device_info table created successfully in {customer_db_name}!")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        cursor.close()
        conn.close()

# Function to insert device data into the Device_info table
import mysql.connector  # Ensure you have this import at the top

def insert_device_data(customer_db_name, name, ip_or_domain_name, device_type, device_model, port, channel_no, online_status, sn, operation):
    print("Starting device insertion...")
    conn = get_customer_db_connection(customer_db_name)  # Make sure this function returns a valid connection
    cursor = conn.cursor()
    
    # Print the device data being inserted
    print(name, ip_or_domain_name, device_type, device_model, port, channel_no, online_status, sn, operation)
    
    try:
        # Execute the insert statement
        cursor.execute("""
            INSERT INTO Device_info (Name, IP_or_Domain_Name, Device_type, Device_model, Port, Channel_no, Online_status, SN, Operation)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (name, ip_or_domain_name, device_type, device_model, port, channel_no, online_status, sn, operation))
        
        # Commit the changes to the database
        conn.commit()
        print("Device data inserted successfully!")
    
    except mysql.connector.Error as err:
        print(f"Error inserting device data: {err}")
    
    finally:
        cursor.close()  # Close the cursor
        conn.close()    # Close the connection

# Function to retrieve all device data from the Device_info table
def get_all_devices(customer_db_name):
    conn = get_customer_db_connection(customer_db_name)
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM Device_info")
        devices = cursor.fetchall()
        return devices
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return []
    finally:
        cursor.close()
        conn.close()






# Function to create the Log table in the customer database
def create_log_table(customer_db_name):
    conn = get_customer_db_connection(customer_db_name)
    cursor = conn.cursor()

    # SQL statement to create the Log table
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS Log (
        No INT AUTO_INCREMENT PRIMARY KEY,
        Time TIME,
        Date DATE,
        User_name VARCHAR(255),
        Event_type VARCHAR(255),
        Device_name VARCHAR(255),
        Channel_name VARCHAR(255),
        Remarks VARCHAR(255)
    );
    """

    try:
        # Execute the SQL command to create the Log table
        cursor.execute(create_table_sql)
        conn.commit()
        print(f"Log table created successfully in {customer_db_name}!")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        cursor.close()
        conn.close()

# Function to insert log data into the Log table
def insert_log_data(customer_db_name, user_name, event_type, device_name, channel_name, remarks):
    conn = get_customer_db_connection(customer_db_name)
    cursor = conn.cursor()

    # Get the current date and time
    current_time = datetime.now().time()
    current_date = datetime.now().date()

    try:
        cursor.execute("""
            INSERT INTO Log (Time, Date, User_name, Event_type, Device_name, Channel_name, Remarks)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (current_time, current_date, user_name, event_type, device_name, channel_name, remarks))
        
        conn.commit()
        print("Log data inserted successfully!")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        cursor.close()
        conn.close()

# Function to retrieve all log data from the Log table
def get_all_logs(customer_db_name):
    conn = get_customer_db_connection(customer_db_name)
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM Log")
        logs = cursor.fetchall()
        return logs
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return []
    finally:
        cursor.close()
        conn.close()







# Function to create the Event table in the customer database
def create_event_table(customer_db_name):
    conn = get_customer_db_connection(customer_db_name)
    
    cursor = conn.cursor()

    # SQL statement to create the Event table with serial_no as AUTO_INCREMENT
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS Event (
        serial_no INT AUTO_INCREMENT PRIMARY KEY,
        Occur_time TIME,
        Occur_date DATE,
        Event_type VARCHAR(255),
        Device_name VARCHAR(255),
        Camera_location_description VARCHAR(255),
        Handling_time TIME,
        Handling_status VARCHAR(255),
        Operation VARCHAR(255)
    );
    """

    try:
        # Execute the SQL command to create the Event table
        cursor.execute(create_table_sql)
        conn.commit()
        print(f"Event table created successfully in {customer_db_name}!")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        cursor.close()
        conn.close()

# Function to insert event data into the Event table
def insert_event_data(customer_db_name, occur_time, occur_date, event_type, device_name,
                      camera_location_description, handling_time, handling_status, operation):
    print("Event insert data...!!!!!!")
    conn = get_customer_db_connection(customer_db_name)
    
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO Event (Occur_time, Occur_date, Event_type, Device_name,
                               Camera_location_description, Handling_time, Handling_status, Operation)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (occur_time, occur_date, event_type, device_name, camera_location_description,
              handling_time, handling_status, operation))

        conn.commit()
        print("Event data inserted successfully!")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        cursor.close()
        conn.close()


# Function to retrieve all event data from the Event table
def get_all_events(customer_db_name):
    print("get all Events data...!!!!!!")
    conn = get_customer_db_connection(customer_db_name)
    
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM Event")
        events = cursor.fetchall()
        return events
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return []
    finally:
        cursor.close()
        conn.close()

# Function to search for a specific event by serial_no
def get_event_by_serial_no(customer_db_name, serial_no):
    print("get all Event  data by serial no...!!!!!!")
    conn = get_customer_db_connection(customer_db_name)
    if conn is None:
        return None
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM Event WHERE serial_no = %s", (serial_no,))
        event = cursor.fetchone()
        if event:
            return event
        else:
            print(f"No event found with serial_no: {serial_no}")
            return None
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None
    finally:
        cursor.close()
        conn.close()

# Function to update event data by serial_no
def update_event_by_serial_no(customer_db_name, serial_no, occur_time, occur_date, event_type, device_name,
                               camera_location_description, handling_time, handling_status, operation):
    print("Event update data...!!!!!!")
    conn = get_customer_db_connection(customer_db_name)
    
    cursor = conn.cursor()

    try:
        cursor.execute("""
            UPDATE Event
            SET Occur_time = %s, Occur_date = %s, Event_type = %s, Device_name = %s,
                Camera_location_description = %s, Handling_time = %s, Handling_status = %s, Operation = %s
            WHERE serial_no = %s
        """, (occur_time, occur_date, event_type, device_name, camera_location_description,
              handling_time, handling_status, operation, serial_no))

        conn.commit()
        print(f"Event with serial_no {serial_no} updated successfully!")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        cursor.close()
        conn.close()





# Function to retrieve camera_id, ip_address, and port_number from the Cameras_info table
def get_all_camera(customer_db_name):
    conn = get_customer_db_connection(customer_db_name)
    cursor = conn.cursor(dictionary=True)

    try:
        # SQL query to fetch camera_id, ip_address, and port_number
        cursor.execute("SELECT camera_id, ip_address, port_number FROM Cameras_info")
        cameras = cursor.fetchall()
        result = {}
        for camera in cameras:
            # Add each camera_id as the key and its port and ip_address as the value in a list
            result["cam"+str(camera['camera_id'])] = [ camera['ip_address'],camera['port_number']]

        return result
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return []
    finally:
        cursor.close()
        conn.close()




def fetch_onvif_link_by_camera_id(customer_db_name, camera_id):
    
    try:
        # Establish a connection to the customer's database
        conn = get_customer_db_connection(customer_db_name)
        cursor = conn.cursor(dictionary=True)

        # Query to fetch ONVIF RTSP link
        query = """
            SELECT onvif_rtsp_settings 
            FROM Cameras_info 
            WHERE camera_id = %s;
        """
        cursor.execute(query, (camera_id,))
        result = cursor.fetchone()

        if result:
            return result['onvif_rtsp_settings']
        else:
            return f"No ONVIF link found for camera_id {camera_id}."
    except Error as e:
        return f"Error while executing query: {e}"
    finally:
        # Ensure the cursor and connection are closed
        if cursor:
            cursor.close()
        if conn:
            conn.close()
