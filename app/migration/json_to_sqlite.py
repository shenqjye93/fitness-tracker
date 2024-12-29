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
    print(f'app_dir: {app_dir}')

    # Define paths relative to app directory
    json_path = app_dir / 'data' / 'data.json'
    db_path = app_dir / 'data' / 'health_metrics.sqlite'

    return json_path, db_path

def create_tables(cursor: sqlite3.Cursor) -> None:
    """
    Create separate tables for different categories of data.
    """

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bp_metrics (
        id INTEGER PRIMARY KEY,
        timestamp INTEGER,
        category TEXT,
        type TEXT,
        systolic INTEGER,
        diasystolic INTEGER,
        pulse INTEGER                 
    )
    """)
    # Create glucose metrics table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS glucose_metrics (
        id INTEGER PRIMARY KEY,
        timestamp INTEGER,
        category TEXT,
        type TEXT,
        level INTEGER
    )
    """)
    
    # Create exercise metrics table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS exercise_metrics (
        id INTEGER PRIMARY KEY,
        timestamp INTEGER,
        category TEXT,
        name TEXT,
        type TEXT,
        weight REAL
    )
    """)

def insert_data(cursor: sqlite3.Cursor, data: Dict[str, Any]) -> None:
    """
    Insert data into appropriate tables based on category.
    
    Args:
        cursor: SQLite cursor object
        data: Dictionary of health metrics data
    """
    # Prepare statements for each table
    bp_insert = """
    INSERT INTO bp_metrics (id, timestamp, category, type, systolic, diasystolic, pulse)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    
    glucose_insert = """
    INSERT INTO glucose_metrics (id, timestamp, category, type, level)
    VALUES (?, ?, ?, ?, ?)
    """
    
    exercise_insert = """
    INSERT INTO exercise_metrics (id, timestamp, category, name, type, weight)
    VALUES (?, ?, ?, ?, ?, ?)
    """
    
    # Process each record
    for timestamp, record in data.items():
        if record['category'] == 'metric' and record['type'] == 'glucose':
            cursor.execute(glucose_insert, (
                record['id'],
                int(timestamp),
                record['category'],
                record['type'],
                record['level']
            ))
        elif record['category'] == 'metric' and record['type'] == 'bp':
            cursor.execute(bp_insert, (
                record['id'],
                int(timestamp),
                record['category'],
                record['type'],
                record['level']['systolic'],
                record['level']['diasystolic'],
                record['level']['pulse']
            ))
        elif record['category'] == 'exercise':
            cursor.execute(exercise_insert, (
                record['id'],
                int(timestamp),
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
        
        # Commit the changes
        conn.commit()

if __name__ == "__main__":
    # Get project paths
    json_file_path, db_file_path = get_project_paths()
    print(json_file_path)
    print(db_file_path)

    try:
        json_to_sqlite(json_file_path, db_file_path)
        print("Data successfully transferred to SQLite database!")
        
        # Optional: Print sample queries to verify the data
        with sqlite3.connect(db_file_path) as conn:
            cursor = conn.cursor()
            print("\nSample bp readings:")
            cursor.execute("SELECT * FROM bp_metrics LIMIT 3")
            print(cursor.fetchall())

            cursor = conn.cursor()
            print("\nSample glucose readings:")
            cursor.execute("SELECT * FROM glucose_metrics LIMIT 3")
            print(cursor.fetchall())
            
            print("\nSample exercise records:")
            cursor.execute("SELECT * FROM exercise_metrics LIMIT 3")
            print(cursor.fetchall())
            
    except Exception as e:
        print(f"Error: {str(e)}")