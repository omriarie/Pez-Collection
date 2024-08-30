# import sqlite3
#
# def create_database():
#     # Connect to the SQLite database (or create it if it doesn't exist)
#     conn = sqlite3.connect('pez_collection.db')
#     cursor = conn.cursor()
    # Create the PEZ collection table with updated columns
    # cursor.execute('''
    # CREATE TABLE IF NOT EXISTS pez_collection (
    #     id TEXT PRIMARY KEY,
    #     full_name TEXT,
    #     series TEXT,
    #     pup_name TEXT,
    #     year_of_manufacture INTEGER,
    #     country_of_manufacture TEXT,
    #     patent TEXT,
    #     leg TEXT,  -- "with", "without", "thin"
    #     leg_color TEXT,  -- Only applicable if leg is "with" or "thin"
    #     image BLOB
    # )
    # ''')
    #
    # # Save changes and close connection
    # conn.commit()
    # conn.close()
#
# if __name__ == "__main__":
#     create_database()

import sqlite3

# Function to connect to the SQLite database
def get_db_connection():
    conn = sqlite3.connect('pez_collection.db')  # Use your database name here
    return conn

# Create the 'id_tracker' table and insert the initial value of 25
def initialize_id_tracker():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create the 'id_tracker' table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS id_tracker (
            last_id INTEGER
        )
    ''')

    # Insert the initial value of 25 for 'last_id'
    cursor.execute("INSERT INTO id_tracker (last_id) VALUES (25)")

    # Commit the changes and close the connection
    conn.commit()
    conn.close()
    print("Database table created and initialized with last_id = 25.")

# Run the function to initialize the 'id_tracker' table
initialize_id_tracker()



