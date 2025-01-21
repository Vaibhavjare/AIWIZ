import mysql.connector
import os
from flask import jsonify
from mysql.connector import Error
import sys





from mysql.connector import pooling

dbconfig = {
    "database": "super_admin_db",
    "user": "root",
    "password": "Indra#123",
    "host": "localhost"
}

pool = pooling.MySQLConnectionPool(pool_name="mypool", pool_size=5, **dbconfig)

def get_super_db_connection():
    conn = pool.get_connection()
    if conn.is_connected():
        print("Database connection established successfully")
    else:
        print("Failed to connect to database")
    return conn



# Function to create the TempUser and OTP tables
def create_tempuser_and_otp_tables():
    try:
        db = get_super_db_connection()
        cursor = db.cursor()
        
        # Create TempUser table if it doesn't exist
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS TempUser (
            Customer_id INT AUTO_INCREMENT PRIMARY KEY,
            full_name VARCHAR(100) NOT NULL,
            username VARCHAR(50) UNIQUE NOT NULL,
            email VARCHAR(100)  UNIQUE NULL,
            password_hash VARCHAR(255) NOT NULL,
            contact_number VARCHAR(20),
            address VARCHAR(255),
            database_name VARCHAR(255), 
            sn VARCHAR(12),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            otp VARCHAR(6) NOT NULL
        )
        ''')

        # Create OTP table if it doesn't exist
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS OTP (
            id INT AUTO_INCREMENT PRIMARY KEY,
            email VARCHAR(100) UNIQUE NULL,
            otp VARCHAR(6) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        # Commit changes and close the connection
        db.commit()
        cursor.close()
        db.close()

        print("Tables TempUser and OTP created successfully")

    except mysql.connector.Error as err:
        print(f"Error: {err}")




# Function to insert a new TempUser
def insert_tempuser(full_name,username, email, password_hash, contact_number, address,customer_db_name,sn, otp):
    try:
        db = get_super_db_connection()
        cursor = db.cursor()

        print("\n enter in temp user ")
        print(full_name,username, email, password_hash, contact_number, address,customer_db_name,sn, otp)

        cursor.execute("SELECT email FROM TempUser WHERE email = %s", (email,))
        result = cursor.fetchone()

        if result:
            # If the email already exists, update the OTP
            cursor.execute("UPDATE TempUser SET otp = %s WHERE email = %s", (otp, email))
            print("update")
        else:
            # If the email doesn't exist, insert a new OTP record in temp user
            
            query = '''
            INSERT INTO TempUser (full_name,username, email, password_hash, contact_number, address,database_name,sn, otp)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s,%s)
            '''
            cursor.execute(query, (full_name,username, email, password_hash, contact_number, address,customer_db_name,sn, otp))
            print("done")

        db.commit()
        cursor.close()
        db.close()

        print("TempUser inserted successfully")

    except mysql.connector.Error as err:
        print(f"Error: {err}")


# Function to retrieve all TempUsers
def retrieve_tempusers(email,otp):
    print("\n fetch in temp user ")
    try:
        db = get_super_db_connection()
        cursor = db.cursor()


        if not all([email, otp]):
            return jsonify({"error": "Email and OTP are required"}), 400

        cursor.execute("SELECT * FROM tempuser WHERE email = %s AND otp = %s;", (email, otp))
        temp_user = cursor.fetchone()
        print(f"Retrieved TempUser record: {temp_user}")
        db.commit()
        return temp_user

    except mysql.connector.Error as err:
        print(f"Error: {err}")



def insert_otp(email, otp):
    connection = get_super_db_connection() # Replace with your DB connection function
    cursor = connection.cursor()
    print("hiiiiii")
    # Check if the email already exists in the OTP table
    print("otp inserted",email,otp)
    cursor.execute("SELECT email FROM otp WHERE email = %s", (email,))
    result = cursor.fetchone()
    
    if result:
        # If the email already exists, update the OTP
        cursor.execute("UPDATE otp SET otp = %s WHERE email = %s", (otp, email))
    else:
        # If the email doesn't exist, insert a new OTP record
        cursor.execute("INSERT INTO otp (email, otp) VALUES (%s, %s)", (email, otp))
    
    connection.commit()
    cursor.close()
    connection.close()


# Function to retrieve OTP by email
def retrieve_otp_by_email(email,otp):
    print("\n fetch in otp ")
    try:
        db = get_super_db_connection()
        cursor = db.cursor()

        query = "SELECT * FROM OTP WHERE email = %s AND otp=%s"
        cursor.execute(query, (email,otp))
        result = cursor.fetchone()

        if result:
            print(result)
            db.commit()
            return result
            
        else:
            print("No OTP found for the email")

        cursor.close()
        db.close()

    except mysql.connector.Error as err:
        print(f"Error: {err}")


def get__email_and_otp(email, otp):
    print("\n fetch in temp user  ")
    print("data = ",email,otp)
    try:
        conn = get_super_db_connection()  # Added parentheses
        cursor = conn.cursor()

        query = "SELECT * FROM TempUser WHERE email = %s AND otp = %s"
        cursor.execute(query, (email, otp))
        temp_user = cursor.fetchone()

        cursor.close()
        conn.close()
        print(temp_user)
        if temp_user:
            print("hi:",temp_user)
            return temp_user
        else:
            print("TempUser not found or OTP does not match")
            return None

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None





# Function to delete a user from the TempUser table by email
def delete_temp_user(email):
    print("\n fetch in delete temp user ")
    try:
        # Establishing the connection
        conn = get_super_db_connection()
        cursor = conn.cursor()

        # Deleting from TempUser table
        cursor.execute("DELETE FROM TempUser WHERE email = %s", (email,))
        
        # Commit the transaction
        conn.commit()

        # Close the cursor and connection
        cursor.close()
        conn.close()

        print(f"User with email {email} successfully deleted from TempUser table.")

    except mysql.connector.Error as err:
        print(f"Error: {err}")



# Function to delete a record from the OTP table by email
def delete_otp(email):
    print("\n fetch in delete otpr ")
    try:
        # Establishing the connection
        conn = get_super_db_connection()
        cursor = conn.cursor()

        # Deleting from OTP table
        cursor.execute("DELETE FROM OTP WHERE email = %s", (email,))
        
        # Commit the transaction
        conn.commit()

        # Close the cursor and connection
        cursor.close()
        conn.close()

        print(f"OTP with email {email} successfully deleted from OTP table.")

    except mysql.connector.Error as err:
        print(f"Error: {err}")


def update_otp_in_both_tables(email, new_otp):
    conn = get_super_db_connection()  # Assuming this function connects to your DB
    cursor = conn.cursor()

    print("enter upadte otp and TempUser function")

    try:
        # Log the update process
        print(f"Updating OTP in both otp and TempUser tables for email: {email}")

        # Perform the OTP update in the `otp` table
        cursor.execute("""
            UPDATE otp
            SET otp = %s
            WHERE email = %s
        """, (new_otp, email))

        # Perform the OTP update in the `temp_user` table
        cursor.execute("""
            UPDATE TempUser
            SET otp = %s
            WHERE email = %s
        """, (new_otp, email))

        # Commit the transaction to save the changes
        conn.commit()

        # Check if any rows were affected in both tables
        if cursor.rowcount == 0:
            print(f"No record found with email: {email}")
            return {"message": "No record found with the given email"}

        print("OTP updated successfully in both tables!")
        return {"message": "OTP updated successfully in both tables"}
    
    except mysql.connector.Error as err:
        # Log any errors that occur
        print(f"Error updating OTP: {err}")
        return {"error": str(err)}, 500
    
    finally:
        cursor.close()
        conn.close()





# Function to create the Customer table in the super admin database
def create_customer_table():
    conn = get_super_db_connection()
    cursor = conn.cursor()

    # SQL statement to create the Customer table
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS Customer (
        Customer_id INT AUTO_INCREMENT PRIMARY KEY,
        full_name VARCHAR(100) NOT NULL,
        username VARCHAR(50) UNIQUE NOT NULL,
        email VARCHAR(100) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        contact_number VARCHAR(20),
        address VARCHAR(255),
        database_name VARCHAR(255), 
        sn VARCHAR(12),
        registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """

    try:
        # Execute the SQL command to create the table
        cursor.execute(create_table_sql)
        conn.commit()
        print("Customer table created successfully!")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        cursor.close()
        conn.close()



# Super Admin Functions

# Function to get all customers from the super admin database
def get_customers():
    print("\n enter in fetching user  by name ")
    conn = get_super_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM Customer")
        customers = cursor.fetchall()
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify(customers)




def update_customer_password(email, new_password_hash):
    conn = get_super_db_connection()  
    cursor = conn.cursor()
    print("\n enter in update password fun")
    try:
        # Log the update process
        print(f"Updating password for customer with email: {email}")

        # Perform the password update
        cursor.execute("""
            UPDATE Customer
            SET password_hash = %s
            WHERE email = %s
        """, (new_password_hash, email))

        # Commit the transaction to save the changes
        conn.commit()

        # Check if any rows were affected (i.e., if the email exists)
        if cursor.rowcount == 0:
            print(f"No customer found with email: {email}")
            return {"message": "No customer found with the given email"}
        
        print("Password updated successfully!")
        return {"message": "Password updated successfully"}
    
    except mysql.connector.Error as err:
        
        print(f"Error updating password: {err}")
        return {"error": str(err)}, 500
    
    finally:
        cursor.close()
        conn.close()



import mysql.connector

def get_sn_from_database_name(customer_db_name):
    try:
        # Establishing the connection
        conn = get_super_db_connection()  
        cursor = conn.cursor()
        
        # Query to fetch the SN based on customer_db_name from the Customer table
        query = "SELECT sn FROM Customer WHERE database_name = %s"
        cursor.execute(query, (customer_db_name,))
        
        result = cursor.fetchone()  # Fetch the first result
        
        if result:
            sn = result[0]  # Access the SN value, which is the first column in the result tuple
            print(sn)  # Debugging line
            return sn
        else:
            print(f"SN not found for customer_db_name: {customer_db_name}")
            return None
        
    except mysql.connector.Error as err:
        print(f"Error while fetching SN: {err}")
        return None
    finally:
        if conn.is_connected():  # Ensure that the connection is closed
            cursor.close()
            conn.close()









def get_customer_by_email(email):
    print("\nFetching customer by email:", email)
    try:
        conn = get_super_db_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM Customer WHERE email = %s"
        cursor.execute(query, (email,))
        existing_customer = cursor.fetchone()

        cursor.close()
        conn.close()

        if existing_customer:
            return existing_customer  # This should return the full row, including the password hash
        else:
            print("Customer not found")
            return None

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None





def get_customer_by_sn(sn):
    print("\nFetching customer by sn:", sn)
    try:
        conn = get_super_db_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM Customer WHERE sn = %s"
        cursor.execute(query, (sn,))
        existing_customer = cursor.fetchone()

        cursor.close()
        conn.close()

        if existing_customer:
            return existing_customer  # This should return the full row, including the password hash
        else:
            print("Customer not found by sn")
            return None

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

# def get_customer_by_email(email):
#     print("\nFetching customer by email:", email)
#     try:
#         conn = get_super_db_connection()
#         cursor = conn.cursor(dictionary=True)

#         query = "SELECT * FROM Customer WHERE email = %s"
#         cursor.execute(query, (email,))

#         customer = cursor.fetchone()
#         print("Customer fetched:", customer)

#         cursor.close()
#         conn.close()
#         # Return customer details if found
#         if customer:
#             return customer
#         else:
#             print("Customer not found")
#             return None

       

    # except mysql.connector.Error as err:
    #     print(f"Error fetching customer by email: {err}")
    #     return None

# def get_customer_by_email(email):
#     conn = None
#     cursor = None
#     try:
#         conn = get_super_db_connection()  # Get your database connection
#         cursor = conn.cursor(dictionary=True)  # Use a dictionary cursor for better readability
        
#         # Prepare the query
#         query = "SELECT * FROM Customer WHERE email = %s"
        
#         # Execute the query with the email as a parameter
#         cursor.execute(query, (email,))
        
#         # Fetch the result
#         customer = cursor.fetchone()
        
#         # Return the fetched customer, or None if no customer is found
#         return customer
    
#     except mysql.connector.Error as err:
#         print(f"Error: {err}")
#         return None
    
#     finally:
#         if cursor:
#             cursor.close()  # Ensure cursor is closed
# #         if conn:
#             conn.close()    # Ensure connection is closed

    


def insert_customer(full_name, username, email, password_hash, contact_number, address, customer_db_name, sn):
    
    # Generate database name from email
    print("\nInserting customer and creating a new database")
    
    conn = get_super_db_connection()  # Your function to get DB connection
    cursor = conn.cursor()

    try:
        # Log the insert query for debugging
        print(f"Inserting customer: {full_name}, {username}, {email}, {contact_number}, {address}, {customer_db_name}, {sn}")
        
        # Insert customer into super admin database
        cursor.execute("""
            INSERT INTO Customer (full_name, username, email, password_hash, contact_number, address, database_name, sn)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (full_name, username, email, password_hash, contact_number, address, customer_db_name, sn))
        
        # Log success of insertion
        print("Customer inserted successfully!")
        
        # Create customer-specific database
        print(f"Creating database: {customer_db_name}")
        cursor.execute(f"CREATE DATABASE {customer_db_name}")
        
        conn.commit()  # Commit the transaction after all operations
        print(f"Database {customer_db_name} created successfully!")
    
    except mysql.connector.Error as err:
        # Log detailed error
        print(f"Error inserting customer or creating database: {err}")
        return jsonify({"error": str(err)}), 500
    
    finally:
        cursor.close()
        conn.close()

    return {"message": "Customer created and database initialized", "db_name": customer_db_name}








def get_customers_by_sn(sn):
    print("\nFetching user by SN:", sn)
    conn = get_super_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # SQL query to fetch username and database_name by sn
        cursor.execute("SELECT username, database_name FROM Customer WHERE sn = %s", (sn,))
        # Fetching the result
        customer = cursor.fetchone()
        print(customer)
        customer_db_name = customer['database_name']

        if customer:
            # If the customer is found, return the 
            from Database.customer_db import get_all_camera
            data =get_all_camera(customer_db_name)

            return data

    except mysql.connector.Error as err:
        # Handling any SQL or connection errors
        return 500

    finally:
        # Closing the cursor and connection
        cursor.close()
        conn.close()


def get_onvif_by_device_camid(sn, camera_id):
    print("Fetching ONVIF link...")

    try:
        # Establish the connection to the super database
        conn = get_super_db_connection()
        cursor = conn.cursor(dictionary=True)
        camera_id = int(camera_id.replace('cam', ''))

        # Fetch customer details based on SN
        cursor.execute("SELECT username, database_name FROM Customer WHERE sn = %s", (sn,))
        customer = cursor.fetchone()

        if not customer:
            return {"error": f"No customer found for serial number {sn}"}

        # Extract the customer database name
        customer_db_name = customer.get('database_name')
        print(f"customer_db_name: {customer_db_name}")

        if not customer_db_name:
            return {"error": f"Customer database name not found for SN {sn}"}

        # Import the function to fetch ONVIF link and call it inside try block
        from Database.customer_db import fetch_onvif_link_by_camera_id

        onvif_data = fetch_onvif_link_by_camera_id(customer_db_name, camera_id)

        if not onvif_data:
            return {"error": f"No ONVIF link found for camera_id {camera_id} in database {customer_db_name}"}

        return {"onvif_link": onvif_data}

    except Exception as e:
        return {"error": f"An unexpected error occurred: {str(e)}"}

    finally:
        # Cleanup resources
        if cursor:
            try:
                cursor.close()
            except Exception as cursor_error:
                print(f"Error closing cursor: {cursor_error}")
        if conn:
            try:
                conn.close()
            except Exception as conn_error:
                print(f"Error closing connection: {conn_error}")



def generate_rtsp_and_update(sn, camera_id, external_port):
    
    # Establish a connection to the super database
    conn = get_super_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Convert camera_id to an integer (removing 'cam' prefix)
        camera_id = int(camera_id.replace('cam', ''))
        
        # Fetch customer info from the super database
        cursor.execute("SELECT username, database_name FROM Customer WHERE sn = %s", (sn,))
        customer = cursor.fetchone()
        if not customer:
            return {"error": f"No customer found for serial number {sn}"}
        
        customer_db_name = customer.get('database_name')
        # print(f"Customer database name: {customer_db_name}")  # Debug log

        # Fetch camera info from the customer's database
        from Database.customer_db import get_camera_info_by_id
        res = get_camera_info_by_id(customer_db_name, camera_id)
        if not res:
            return {"error": f"No camera found with ID {camera_id} in database {customer_db_name}"}
        
        # Extract camera details for RTSP URL generation
        username = res[3]
        password = res[4]
        onvif_rtsp = res[5]

        # Generate RTSP URL
        rtsp_url = f"rtsp://{username}:{password}@127.0.0.1:{external_port}{onvif_rtsp}"
        print(f"Generated RTSP URL: {rtsp_url}")  # Debug log

        # Update external_port and rtsp_URL in the database
        from Database.customer_db import update_camera_info_rtsp
        update_response = update_camera_info_rtsp(customer_db_name, camera_id, external_port, rtsp_url)
        # print(update_response)  # Log update response

        return {"message": "RTSP URL generated and database updated successfully", "rtsp_url": rtsp_url}

    except Exception as e:
        print(f"Error: {e}")  # Log unexpected errors
        return {"error": str(e)}

    finally:
        cursor.close()
        conn.close()

    
