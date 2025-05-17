"""
File Name: run_pipeline.py
Purpose: The main entry point to run the entire project.
Why it exists: It's bad practice to require a user to run 5 different python scripts in a 
specific order (`python src/config.py`, then `python db/init_db.py`, etc.). 
This script orchestrates the pipeline: it initializes the DB, scrapes the web, cleans the data, 
builds the AI indexes, and then starts either the API or the Chatbot.
What it imports: Almost everything from the `src` folder.
Which files use it: The user runs this directly via `python run_pipeline.py`.
Inputs: Command line arguments.
Outputs: Controls the flow of the application.
Role in pipeline: The Orchestrator / Director.
"""

# ==========================================
# BUILT-IN PYTHON LIBRARIES
# ==========================================
import argparse # A standard Python library used to read arguments typed in the terminal. Ex: 'python run_pipeline.py --scrape'.
import sys      # A standard Python library for system-level operations, used here to cleanly stop the program via sys.exit().
import os       # A standard Python library to build reliable file paths and create folders regardless of operating system.

# ==========================================
# EXTERNAL LIBRARIES (Installed via pip)
# ==========================================
import uvicorn  # A fast web server engine. FastAPI defines the routes, but Uvicorn is the actual background server serving the data.

# ==========================================
# OUR CUSTOM PROJECT FILES (Modules we wrote)
# ==========================================
# src.config: We import our global constants here to ensure file paths are centrally managed.
from src.config import DB_PATH, SCHEMA_PATH, API_HOST, API_PORT

# db.init_db: We import the logic that creates empty SQLite tables safely.
from db.init_db import initialize_database

# src.scraper: We import the code that visits Codeforces.com, downloads the HTML, and extracts raw problem metadata.
from src.scraper import scrape_problems

# src.cleaner: We import the logic that takes raw scraper data, normalizes string problems, and writes exactly to SQLite.
from src.cleaner import clean_and_load

# src.indexer: We import the AI mathematical engine. This transforms the raw text problems into TF-IDF and Transformer matrices.
from src.indexer import create_indexes

# src.chatbot: We import the file holding the conversational loop logic for the Command Line Interface (CLI).
from src.chatbot import start_chat

def main():
    """
    Parses command line arguments and acts as the switchboard directing traffic to the right parts of the project.
    
    TUTORIAL EXPLANATION:
    When you build a software pipeline, you don't want to force the end-user to know exactly which file 
    to run, or what order to run them in. By writing a 'main()' orchestrator, we give the user a single 
    command interface. We use `argparse` to create "flags" (like --scrape). If a user types the flag, 
    we execute that exact block of code.
    """
    
    # 1. Setup the Argument Parser
    # This creates the help menu and tells Python to look out for specific words typed in the terminal.
    parser = argparse.ArgumentParser(description="Codeforces Assistant RAG Pipeline")
    
    # 2. Define our Flags
    # action='store_true' means if the user types '--scrape', the variable `args.scrape` becomes True. 
    # If they don't type it, it defaults to False.
    parser.add_argument('--scrape', action='store_true', help="Run the scraper and clean the data to Database.")
    parser.add_argument('--index', action='store_true', help="Rebuild the TF-IDF and Transformer embeddings.")
    parser.add_argument('--chat', action='store_true', help="Start the interactive CLI chatbot.")
    parser.add_argument('--api', action='store_true', help="Start the FastAPI server.")
    
    # 3. Parse the Flags
    # This actually reads the terminal input and populates the `args` object.
    args = parser.parse_args()
    
    # 4. Handle Empty Input
    # If the user just types `python run_pipeline.py` without any flags, we print the instructions and safely exit the script (sys.exit).
    if not (args.scrape or args.index or args.chat or args.api):
        parser.print_help()
        print("\n[TUTORIAL] Try running: python run_pipeline.py --scrape --index --chat")
        sys.exit(0)

    # ==========================================
    # PHASE 1: DATA ACQUISITION & CLEANING
    # ==========================================
    # Triggered by: python run_pipeline.py --scrape
    if args.scrape:
        print("\n=== Phase 1: Database Setup and Scraping ===")
        # Always make sure the directories (like data/processed) exist before we try to create a file inside them.
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        
        # Initialize empty tables in the SQLite database
        initialize_database(DB_PATH, SCHEMA_PATH)
        
        # Fetch the raw HTML strings from Codeforces and extract dicts
        raw_data = scrape_problems()
        
        # Clean the messy raw data and insert it securely into SQLite
        clean_and_load(raw_data)
        
    # ==========================================
    # PHASE 2: MATHEMATICAL INDEXING (THE "AI" PART)
    # ==========================================
    # Triggered by: python run_pipeline.py --index
    if args.index:
        print("\n=== Phase 2: Building AI Indexes ===")
        # This function pulls all problems from SQLite, converts their text into math Vectors, 
        # and saves those vectors as .pkl files to the hard drive so they can be loaded instantly later.
        create_indexes()
        
    # ==========================================
    # PHASE 3A: THE COMMAND LINE CHATBOT
    # ==========================================
    # Triggered by: python run_pipeline.py --chat
    if args.chat:
        print("\n=== Phase 3: Launching CLI Chatbot ===")
        # NOTE: If the DB doesn't exist and indexer hasn't run, this will crash.
        # That's why the README instructs users to run with --scrape and --index FIRST before running --chat.
        start_chat()
        
    # ==========================================
    # PHASE 3B: THE WEB API
    # ==========================================
    # Triggered by: python run_pipeline.py --api
    if args.api:
        print("\n=== Phase 3: Launching API Server ===")
        # uvicorn is the server that natively runs FastAPI applications.
        # It binds our python logic to network ports so web browsers can communicate with it.
        uvicorn.run("api.main:app", host=API_HOST, port=API_PORT, reload=True)

# STANDARD PYTHON PRACTICE:
# This ensures that `main()` is only called if we run the script directly from the terminal.
# If another python file tried to `import run_pipeline`, this block prevents it from accidentally running immediately.
if __name__ == "__main__":
    main()
