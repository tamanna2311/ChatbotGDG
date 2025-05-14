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

import argparse
import sys
import os
import uvicorn

from src.config import DB_PATH, SCHEMA_PATH, API_HOST, API_PORT
from db.init_db import initialize_database
from src.scraper import scrape_problems
from src.cleaner import clean_and_load
from src.indexer import create_indexes
from src.chatbot import start_chat

def main():
    """
    Parses command line arguments and runs the appropriate parts of the pipeline.
    """
    parser = argparse.ArgumentParser(description="Codeforces Assistant RAG Pipeline")
    
    # We add flags so the user can choose what parts of the pipeline to run.
    parser.add_argument('--scrape', action='store_true', help="Run the scraper and clean the data to Database.")
    parser.add_argument('--index', action='store_true', help="Rebuild the TF-IDF and Transformer embeddings.")
    parser.add_argument('--chat', action='store_true', help="Start the interactive CLI chatbot.")
    parser.add_argument('--api', action='store_true', help="Start the FastAPI server.")
    
    args = parser.parse_args()
    
    # If the user didn't specify any arguments, print help and exit.
    if not (args.scrape or args.index or args.chat or args.api):
        parser.print_help()
        print("\nTry running: python run_pipeline.py --scrape --index --chat")
        sys.exit(0)

    # Step 1 & 2 & 3: Scrape locally, clean, and insert to Database
    if args.scrape:
        print("\n=== Phase 1: Database Setup and Scraping ===")
        # Always make sure DB is initialized before we insert
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        initialize_database(DB_PATH, SCHEMA_PATH)
        
        # Scrape and load
        raw_data = scrape_problems()
        clean_and_load(raw_data)
        
    # Step 4: Indexing
    if args.index:
        print("\n=== Phase 2: Building AI Indexes ===")
        create_indexes()
        
    # Step 5A: Launch Chatbot
    if args.chat:
        print("\n=== Phase 3: Launching CLI Chatbot ===")
        # Note: If the DB doesn't exist and indexer hasn't run, this will crash.
        # That's why the README instructs users to run with --scrape and --index first.
        start_chat()
        
    # Step 5B: Launch API
    if args.api:
        print("\n=== Phase 3: Launching API Server ===")
        # uvicorn is the server that natively runs FastAPI applications.
        uvicorn.run("api.main:app", host=API_HOST, port=API_PORT, reload=True)

if __name__ == "__main__":
    main()
