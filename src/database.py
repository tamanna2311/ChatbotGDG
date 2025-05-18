"""
File Name: database.py
Purpose: Provides reusable helper functions to interact with the SQLite DB.
Why it exists: We don't want to copy-paste raw SQL queries and connection boilerplate 
(like conn = sqlite3.connect(), conn.cursor()) everywhere. We use these helper functions instead.
What it imports: sqlite3, pandas, src.config
Which files use it: cleaner.py (for inserting processed data), indexer.py (for reading data).
Inputs: Varies by function (DataFrames, dicts, queries).
Outputs: Varies by function (Insert success, DataFrames).
Role in pipeline: Central data access layer (DAO / Repository pattern).
"""

# ==========================================
# BUILT-IN PYTHON LIBRARIES
# ==========================================
import sqlite3 # The core engine that lets python talk directly to the .db file.
from typing import List, Dict, Any # Used purely for Type Hinting to make the code easier to read.

# ==========================================
# EXTERNAL LIBRARIES (Installed via pip)
# ==========================================
import pandas as pd # A powerful data manipulation library; used here to convert SQL tables into structured DataFrames.

# ==========================================
# OUR CUSTOM PROJECT FILES (Modules we wrote)
# ==========================================
# src.config: We pull the absolute path of the database so we always connect to the right one.
from src.config import DB_PATH

def get_connection() -> sqlite3.Connection:
    """
    Creates and returns a connection to the SQLite database.
    
    Why it exists: Used internally by other functions here to grab a connection quickly.
    What it returns: An open sqlite3.Connection object.
    Where it is used: In insert_problem(), fetch_all_problems(), etc.
    """
    return sqlite3.connect(DB_PATH)

def insert_problem(problem_data: Dict[str, Any]) -> None:
    """
    Inserts a single clean problem into the database, including its tags.
    
    [TUTORIAL] WHAT IT DOES:
    This function acts as our single Gateway into the database. 
    1. It takes a python Dictionary (representing one problem).
    2. Uses SQL "INSERT OR IGNORE" so that if we scrape the same problem twice, the pipeline doesn't crash.
    3. It iterates over the problem's 'tags' (which could be many), inserts them into a `tags` table, 
       and links them together in a `problem_tags` junction table.
       
    [TUTORIAL] CROSS-REFERENCE:
    This prevents `cleaner.py` from having to write massive SQL strings itself.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # We use INSERT OR IGNORE to prevent crashing if we run the scraper twice 
        # and try to insert a problem that is already there.
        cursor.execute('''
            INSERT OR IGNORE INTO problems 
            (contest_id, problem_index, name, difficulty, url, statement_summary)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            problem_data['contest_id'],
            problem_data['problem_index'],
            problem_data['name'],
            problem_data['difficulty'],
            problem_data['url'],
            problem_data['statement_summary']
        ))
        
        # After insertion, we need the database's internal ID for this problem.
        # If it was just inserted, lastrowid works. If it was IGNORED (already exists),
        # we have to fetch it explicitly.
        cursor.execute('''
            SELECT id FROM problems 
            WHERE contest_id = ? AND problem_index = ?
        ''', (problem_data['contest_id'], problem_data['problem_index']))
        
        problem_row = cursor.fetchone()
        if not problem_row:
            raise Exception("Failed to retrieve problem ID.")
        problem_id = problem_row[0]
        
        # Now handle tags
        for tag in problem_data.get('tags', []):
            tag = tag.strip().lower()
            if not tag:
                continue
                
            # Insert the tag if it's new
            cursor.execute('INSERT OR IGNORE INTO tags (name) VALUES (?)', (tag,))
            
            # Fetch the tag ID (whether we just inserted it or it already existed)
            cursor.execute('SELECT id FROM tags WHERE name = ?', (tag,))
            tag_id = cursor.fetchone()[0]
            
            # Link them together
            cursor.execute('''
                INSERT OR IGNORE INTO problem_tags (problem_id, tag_id)
                VALUES (?, ?)
            ''', (problem_id, tag_id))
            
        conn.commit()
    except Exception as e:
        print(f"Error inserting problem {problem_data['name']}: {e}")
        conn.rollback() # Undo any partial changes to prevent database corruption
    finally:
        conn.close()

def get_all_problems_as_dataframe() -> pd.DataFrame:
    """
    Retrieves all problems from the database and returns them as a Pandas DataFrame.
    
    [TUTORIAL] WHAT IT DOES:
    SQL is great for storage, but Machine Learning tools (like Scikit-Learn) don't speak SQL. 
    By returning a `pandas` DataFrame, we load the database into a row/column matrix in RAM that 
    the AI models can easily process.
    
    [TUTORIAL] HOW IT DOES IT:
    We use advanced SQL (JOIN and GROUP_CONCAT) to take the messy web of problems and tags 
    and squash them perfectly into a single flat row per problem.
    """
    conn = get_connection()
    # We use a SQL JOIN to combine problems, problem_tags, and tags tables.
    # GROUP_CONCAT puts all the tags into a single comma-separated string, 
    # making it very easy to work with in Pandas.
    query = '''
    SELECT 
        p.id, p.contest_id, p.problem_index, p.name, p.difficulty, p.url, p.statement_summary,
        GROUP_CONCAT(t.name, ', ') as tags
    FROM problems p
    LEFT JOIN problem_tags pt ON p.id = pt.problem_id
    LEFT JOIN tags t ON pt.tag_id = t.id
    GROUP BY p.id
    '''
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df
