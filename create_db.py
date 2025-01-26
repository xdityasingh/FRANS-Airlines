import sqlite3

def create_database():
    # Connect to the SQLite database (it will be created if it doesn't exist)
    conn = sqlite3.connect('system_database.db')  # SQLite will create the file if it doesn't exist
    cursor = conn.cursor()

    # Read and execute the SQL script to create tables and insert sample data
    with open('create_database.sql', 'r') as file:
        sql_script = file.read()
        cursor.executescript(sql_script)  # Execute the SQL script to create tables

    conn.commit()  # Commit changes to the database
    conn.close()   # Close the connection

# Run the function to create the database and tables
create_database()
