"""
File Name: init_db.py
Purpose: Initializes the SQLite database based on the schema.sql file.
Why it exists: We need a programmatic way to create our database tables automatically before the scraper runs.
What it imports: 
- sqlite3 (for DB connection)
- os (for path handling)
Which files use it: run_pipeline.py calls this before scraping.
Inputs: None directly from command line, but relies on paths defined in the file.
Outputs: A new SQLite database file (.db) with empty tables. If the db already exists, it applies schema.sql (using IF NOT EXISTS).
Role in pipeline: Step 1. Prepares the storage layer so incoming scraped data has a place to go.
"""

# ==========================================
# BUILT-IN PYTHON LIBRARIES
# ==========================================
import sqlite3 # Standard library for interacting directly with SQLite databases via SQL commands.
import os      # Standard library used to construct reliable file paths across different operating systems.

def initialize_database(db_path: str, schema_path: str) -> None:
    """
    Reads the schema from `schema_path` and executes it on the database at `db_path`.
    
    What it does:
    1. Connects to (and potentially creates) the SQLite database.
    2. Reads the schema.sql file containing table definitions.
    3. Executes the SQL script to create tables.
    
    Why it exists: To ensure our relational database has the exact structure we need
    for later data insertion and retrieval.
    
    What inputs it expects: 
    - db_path: A string path where the .db file should be stored.
    - schema_path: A string path to the schema.sql file.
    
    What it returns: None.
    
    Where it is used: In the main execution script (`run_pipeline.py`).
    
    Assumptions/Simplifications:
    - Assumes the parent directories for db_path already exist.
    - Assumes schema.sql is safe and correct.
    """
    # ==========================================
    # [TUTORIAL] 1. ESTABLISH DATABASE CONNECTION
    # ==========================================
    # We chose SQLite because it's lightweight, entirely file-based, and perfect for student projects.
    # It requires no separate server running in the background. 
    # If the file at `db_path` does not exist, SQLite will automatically create it for you here.
    print(f"Connecting to database at {db_path}...")
    connection = sqlite3.connect(db_path)
    
    # A 'cursor' is a temporary workspace in your computer's memory that allows you to execute SQL commands line by line.
    cursor = connection.cursor()
    
    # ==========================================
    # [TUTORIAL] 2. READ THE SCHEMA TEMPLATE
    # ==========================================
    # Rather than putting massive multi-line SQL strings inside our Python code, we keep SQL in a separate `.sql` file.
    # This is a standard industry practice because it keeps python files clean and allows SQL editors to format the schema file properly.
    print(f"Reading schema from {schema_path}...")
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema_script = f.read()
        
    # ==========================================
    # [TUTORIAL] 3. EXECUTE THE SQL SCRIPT
    # ==========================================
    # Standard cursor.execute() only runs ONE sql statement at a time.
    # cursor.executescript() is a special method that allows executing a massive string containing multiple semicolons.
    print("Executing schema...")
    cursor.executescript(schema_script)
    
    # ==========================================
    # [TUTORIAL] 4. COMMIT AND CLOSE
    # ==========================================
    # In databases, writing a command doesn't actually save it to the hard drive yet (in case you make a mistake and want to rollback).
    # 'commit()' tells the database: "I am finished, lock these changes into the hard drive permanently."
    connection.commit()
    
    # We close the connection to free up system resources.
    connection.close()
    print("Database initialized successfully!")

if __name__ == "__main__":
    # For independent testing of this module
    # Define absolute or relative paths based on script location
    base_dir = os.path.dirname(os.path.dirname(__file__))
    db_file_path = os.path.join(base_dir, "data", "processed", "codeforces.db")
    sql_file_path = os.path.join(base_dir, "db", "schema.sql")
    
    initialize_database(db_file_path, sql_file_path)
