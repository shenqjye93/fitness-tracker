import json
import sqlite3
from typing import Dict, Any
import os
from pathlib import Path

def get_project_paths():
    """
    Get the paths for the project files relative to this script.
    """
    # Get the app directory (parent of the migration directory)
    app_dir = Path(__file__).parent.parent

    # Define paths relative to app directory
    json_path = app_dir / 'data' / 'data.json'
    db_path = app_dir / 'data' / 'health_metrics.sqlite'

    return json_path, db_path

def delete_tables(cursor: sqlite3.Cursor) -> None:
    table_name = 'users'
    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}';")
    if cursor.fetchone():
        print(f"Table '{table_name}' exists. Deleting...")
        cursor.execute(f"DROP TABLE {table_name};")
        conn.commit()
    else:
        print(f"Table '{table_name}' does not exist.")
        

def create_tables(cursor: sqlite3.Cursor) -> None:
    """
    Create separate tables for different categories of data.
    """

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users_info (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL                         
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS health_metrics (
        id INTEGER PRIMARY KEY,
        category TEXT,
        type TEXT,
        systolic INTEGER,
        diasystolic INTEGER,
        pulse INTEGER,
        level INTERGER                           
    )
    """)

    # Create exercise metrics table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS exercise_metrics (
        id INTEGER PRIMARY KEY,
        category TEXT,
        name TEXT,
        type TEXT,
        weight REAL
    )
    """)

    cursor.execute("ALTER TABLE exercise_metrics ADD COLUMN user_id INTEGER REFERENCES users_info(id);")
    cursor.execute("ALTER TABLE health_metrics ADD COLUMN user_id INTEGER REFERENCES users_info(id);")


def insert_data(cursor: sqlite3.Cursor, data: Dict[str, Any]) -> None:
    """
    Insert data into appropriate tables based on category.
    
    Args:
        cursor: SQLite cursor object
        data: Dictionary of health metrics data
    """
    # Prepare statements for each table
    bp_insert = """
    INSERT INTO health_metrics (id,  category, type, systolic, diasystolic, pulse, level)
    VALUES (?, ?, ?, ?, ?, ?, NULL)
    """
    
    glucose_insert = """
    INSERT INTO health_metrics (id,  category, type, systolic, diasystolic, pulse, level)
    VALUES (?, ?, ?, NULL, NULL, NULL, ?)
    """
    
    exercise_insert = """
    INSERT INTO exercise_metrics (id,  category, name, type, weight)
    VALUES (?, ?, ?, ?, ?)
    """
    
    # Process each record
    for key, record in data.items():
        if record['category'] == 'metric' and record['type'] == 'glucose':
            cursor.execute(glucose_insert, (
                record['id'],
                record['category'],
                record['type'],
                record['level']
            ))
        elif record['category'] == 'metric' and record['type'] == 'bp':
            cursor.execute(bp_insert, (
                record['id'],
                record['category'],
                record['type'],
                record['level']['systolic'],
                record['level']['diasystolic'],
                record['level']['pulse']
            ))
        elif record['category'] == 'exercise':
            cursor.execute(exercise_insert, (
                record['id'],
                record['category'],
                record['name'],
                record['type'],
                record['weight']
            ))

def json_to_sqlite(json_file_path: str, db_file_path: str) -> None:
    """
    Main function to transfer JSON data to SQLite database.
    
    Args:
        json_file_path: Path to the JSON file
        db_file_path: Path to the SQLite database file
    """
    # Ensure data directory exists
    os.makedirs(os.path.dirname(db_file_path), exist_ok=True)

    # Read JSON data
    with open(json_file_path, 'r') as file:
        json_data = json.load(file)
    
    # Connect to SQLite database
    with sqlite3.connect(db_file_path) as conn:
        cursor = conn.cursor()
        
        # Create the tables
        create_tables(cursor)
        
        # Insert the data
        insert_data(cursor, json_data)

        delete_tables(cursor)
        
        # Commit the changes
        conn.commit()
  

if __name__ == "__main__":
    # Get project paths
    json_file_path, db_file_path = get_project_paths()

    try:
        json_to_sqlite(json_file_path, db_file_path)
        print("Data successfully transferred to SQLite database!")
        
        # Optional: Print sample queries to verify the data
        with sqlite3.connect(db_file_path) as conn:
            cursor = conn.cursor()
            print("\nSample bp readings:")
            cursor.execute("SELECT * FROM health_metrics WHERE type = ? LIMIT 3", ('bp',))
            print(cursor.fetchall())

            cursor = conn.cursor()
            print("\nSample glucose readings:")
            cursor.execute("SELECT * FROM health_metrics WHERE type = ? LIMIT 3", ('glucose',))
            print(cursor.fetchall())
            
            print("\nSample exercise records:")
            cursor.execute("SELECT * FROM exercise_metrics LIMIT 3")
            print(cursor.fetchall())
            
    except Exception as e:
        print(f"Error: {str(e)}")