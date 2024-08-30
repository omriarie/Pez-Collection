import sqlite3

def create_database():
    # Connect to the SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect('pez_collection.db')
    cursor = conn.cursor()

    # Create the PEZ collection table with updated columns
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS pez_collection (
        id TEXT PRIMARY KEY,
        full_name TEXT,
        series TEXT,
        pup_name TEXT,
        year_of_manufacture INTEGER,
        country_of_manufacture TEXT,
        patent TEXT,
        leg TEXT,  -- "with", "without", "thin"
        leg_color TEXT,  -- Only applicable if leg is "with" or "thin"
        image BLOB
    )
    ''')

    # Save changes and close connection
    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_database()
