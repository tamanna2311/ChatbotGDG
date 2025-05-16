"""
File Name: cleaner.py
Purpose: Cleans the raw data fetched by the scraper and loads it into the database.
Why it exists: Web scraped data is often messy. We might get null difficulties, weird characters 
in titles, or empty tags. We must format it uniformly before it goes into our SQL database.
What it imports: src.database.insert_problem
Which files use it: run_pipeline.py
Inputs: List of raw dictionaries from scraper.
Outputs: None directly, but it inserts clean rows into the SQLite DB.
Role in pipeline: Step 3. Data Cleaning and Loading (ETL).
"""

# ==========================================
# BUILT-IN PYTHON LIBRARIES
# ==========================================
from typing import List, Dict, Any # Type hinting structures to declare exactly what data types to expect.

# ==========================================
# OUR CUSTOM PROJECT FILES (Modules we wrote)
# ==========================================
# src.database: We import 'insert_problem', our custom helper to safely write logic into the DB.
from src.database import insert_problem

def clean_and_load(raw_data: List[Dict[str, Any]]) -> None:
    """
    Iterates over the raw scraped data, applies cleaning rules, and saves to the database.
    
    What it does:
    1. Removes any problems missing critical fields (like contest_id or name).
    2. Fills missing difficulties with a default value (e.g., 0) or drops them.
       (Here we choose to keep them but assign None, which SQLite handles as NULL).
    3. Trims whitespace and normalizes text properties.
    4. Calls insert_problem() for each valid entry.
    
    Why it exists: "Garbage in, garbage out". If we index messy data, our 
    recommendations and summaries will be terrible.
    
    What inputs it expects: The list of dicts returned by scraper.scrape_problems().
    
    What it returns: None.
    
    Where it is used: In run_pipeline.py right after scraping.
    """
    valid_count = 0
    passed_count = 0
    
    for raw_prob in raw_data:
        # Rule 1: Must have an ID and a Name
        if not raw_prob.get('contest_id') or not raw_prob.get('problem_index'):
            passed_count += 1
            continue
            
        name = raw_prob.get('name', '').strip()
        if not name:
            passed_count += 1
            continue
            
        # Rule 2: Clean tags
        tags = raw_prob.get('tags', [])
        # Only keep non-empty strings and lowercase them
        clean_tags = [t.strip().lower() for t in tags if isinstance(t, str) and t.strip()]
        
        # Build the clean dictionary
        clean_prob = {
            'contest_id': raw_prob['contest_id'],
            'problem_index': str(raw_prob['problem_index']).strip(),
            'name': name,
            'difficulty': raw_prob.get('difficulty'), # Can be integer or None
            'url': raw_prob.get('url', f"https://codeforces.com/problemset/problem/{raw_prob['contest_id']}/{raw_prob['problem_index']}"),
            'statement_summary': raw_prob.get('statement_summary', '').strip(),
            'tags': clean_tags
        }
        
        # Insert into database using our database helper
        insert_problem(clean_prob)
        valid_count += 1
        
    print(f"Cleaning complete. Inserted {valid_count} clean problems. Dropped {passed_count} malformed rows.")

if __name__ == "__main__":
    # Small test
    test_data = [
        {"contest_id": 9999, "problem_index": "Z", "name": "  Ugly Text  ", "tags": [" MATH ", ""], "difficulty": None}
    ]
    clean_and_load(test_data)
