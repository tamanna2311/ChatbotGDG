"""
File Name: config.py
Purpose: Stores central configuration variables, file paths, and constants.
Why it exists: Hardcoding paths in multiple files leads to bugs and makes code hard to maintain. 
Centralizing them here ensures that if a folder moves, we only change one line of code.
What it imports: os (to build absolute paths reliably regardless of where the script is run from)
Which files use it: scraper.py, cleaner.py, database.py, indexer.py, api/main.py, run_pipeline.py
Inputs: None.
Outputs: Configuration variables (constants like DB_PATH).
Role in pipeline: Acts as the truth source for all file paths and hyper-parameters.
"""

# ==========================================
# BUILT-IN PYTHON LIBRARIES
# ==========================================
import os # Standard library used to dynamically figure out folder structures and map absolute file paths.

# 1. Base Directory Calculation
# __file__ is the current file path (src/config.py). 
# dirname gets the folder (src). dirname again gets the root folder (CodeforcesAssistant).
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 2. Data Directories
# We define specific folders for raw, processed, and cached data to keep things organized.
DATA_DIR = os.path.join(BASE_DIR, "data")
RAW_DATA_DIR = os.path.join(DATA_DIR, "raw")
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, "processed")
CACHE_DIR = os.path.join(DATA_DIR, "cache")

# 3. Database Configuration
# The single SQLite file that stores all our scraped information.
DB_PATH = os.path.join(PROCESSED_DATA_DIR, "codeforces.db")
SCHEMA_PATH = os.path.join(BASE_DIR, "db", "schema.sql")

# 4. Scraper Configuration
# For this student project, scraping all 15k problems takes hours and might get IP blocked.
# So we limit compilation to a small, respectable number of pages.
# Codeforces has ~100 problems per page.
MAX_PAGES_TO_SCRAPE = 2 

# Time to sleep between page requests to be polite to Codeforces servers.
SLEEP_TIME_SEC = 2.0

# 5. Embedding Model / RAG Configuration
# We use a lightweight open-source Sentence Transformer model.
# "all-MiniLM-L6-v2" is widely used for student projects because it's fast, small (~80MB),
# and generates highly capable semantic embeddings (vectors).
# It acts as our simplified stand-in for full-scale CodeBERT.
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

# 6. API Configuration
# Port and Host for FastAPI server.
API_HOST = "0.0.0.0"
API_PORT = 8000
