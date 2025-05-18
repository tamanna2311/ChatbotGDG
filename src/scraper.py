"""
File Name: scraper.py
Purpose: Fetches data (problems, tags, ratings) directly from the Codeforces website.
Why it exists: Without this, we have no data. We need to scrape the live web to build our knowledge base.
What it imports: 
- requests (to download HTML pages)
- BeautifulSoup (to parse HTML tags and extract text)
- time (to sleep, preventing us from getting banned)
- json (for fallback data saving)
Which files use it: run_pipeline.py
Inputs: Number of pages to scrape (from config).
Outputs: A list of dictionaries containing raw scraped problem data.
Role in pipeline: Step 2. Data Acquisition.

Interview specific explanation: 
We chose `requests` + `BeautifulSoup` because Codeforces Problemset pages are generally static HTML 
and do not require heavy JavaScript rendering. This approach is much faster and uses fewer resources 
than `Selenium`. However, if Codeforces activates high-level Cloudflare protection, a Selenium driver
must be used. For simplicity and stability in this student project, we use `requests` and provide
a synthesized "fallback" dataset if parsing fails.
"""

# ==========================================
# BUILT-IN PYTHON LIBRARIES
# ==========================================
import time    # A standard library used here to purposefully slow down our web scraping requests so we don't accidentally DDoS the server.
import json    # A standard library to save our downloaded data into raw .json text files.
import os      # A standard library to handle directory paths properly across Mac, Windows, and Linux.

# ==========================================
# EXTERNAL LIBRARIES (Installed via pip)
# ==========================================
import requests             # The engine that makes HTTP requests to fetch the actual HTML code of website pages.
from bs4 import BeautifulSoup # The parsing module that sifts through the raw HTML looking for specific tags (like reading a book looking for bold words).

# ==========================================
# OUR CUSTOM PROJECT FILES (Modules we wrote)
# ==========================================
# src.config: We import specific scraping parameters safely from our config file.
from src.config import MAX_PAGES_TO_SCRAPE, SLEEP_TIME_SEC, RAW_DATA_DIR

def scrape_problems(pages: int = MAX_PAGES_TO_SCRAPE) -> list:
    """
    Visits the Codeforces problemset page and extracts problem metadata into Python dictionaries.
    
    [TUTORIAL] WHAT IT DOES:
    Web scraping is the act of writing a script that pretends to be a human browsing the web.
    We point our script at 'codeforces.com/problemset', download the raw HTML text, and slice 
    it up to find exactly what we need (the problem names, difficulties, and topics).
    
    [TUTORIAL] WHY IT EXISTS:
    If we don't have data, we can't do Machine Learning or AI. Because Codeforces has over 
    15,000 problems, it's impossible to copy-paste them by hand. This script automates Data Acquisition.
    
    [TUTORIAL] OUTPUT EXAMPLE:
    It returns a list of dictionaries like this:
    [{'contest_id': 1500, 'problem_index': 'A', 'name': 'Title', 'tags': ['math'], 'diff': 800}]
    
    [TUTORIAL] ASSUMPTIONS & SIMPLIFICATIONS:
    - Websites change their HTML layouts perfectly. If Codeforces changes a `<table>` to a `<div>`, this scraper will break. That is the nature of scraping.
    - We are only scraping "metadata". To build a true massive RAG system, we would click into every single problem and scrape the 3-page problem statement too.
    """
    all_raw_problems = []
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    try:
        # We loop through multiple pages based on our configuration constant
        for page_num in range(1, pages + 1):
            url = f"https://codeforces.com/problemset/page/{page_num}"
            print(f"Scraping {url}...")
            
            # [TUTORIAL] DOWNLOADING THE PAGE
            # requests.get() reaches out to Codeforces. response.text contains the raw HTML code.
            response = requests.get(url, headers=headers)
            response.raise_for_status() # If the website returns a 404 (Not Found) or 500 (Server Error), crash loudly.
            
            # [TUTORIAL] PARSING THE HTML
            # We hand the raw text to BeautifulSoup. It turns a giant string into an easily navigable structure.
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # [TUTORIAL] FINDING THE RIGHT TABLE
            # We inspect the webpage (F12) to see that all problems are stored in a <table class="problems">.
            table = soup.find('table', {'class': 'problems'})
            if not table:
                print("Could not find the problems table. Layout might have changed.")
                break
                
            # Iterate over rows in the table. Skip the first row (headers).
            rows = table.find_all('tr')[1:]
            
            for row in rows:
                cols = row.find_all('td')
                if len(cols) < 4:
                    continue
                    
                # 1. Extract IDs from the first column
                # The text usually looks like " 1500 \n A "
                id_text = cols[0].text.strip().split()
                if len(id_text) < 1:
                    continue
                # Example: "1500A" -> we treat it as literal string for index, 
                # but let's try to extract cleanly. Codeforces link is /problemset/problem/1500/A
                a_tag = cols[0].find('a')
                if not a_tag:
                    continue
                    
                href_parts = a_tag['href'].strip('/').split('/')
                # href is like "problemset/problem/1932/F"
                if len(href_parts) >= 4:
                    contest_id = int(href_parts[-2])
                    problem_index = href_parts[-1]
                else:
                    continue

                # 2. Extract Name and Tags from the second column
                # E.g., <div> <a href="...">Problem Name</a> </div> <div> <a href="...">math</a> </div>
                name_div = cols[1].find('div', style='float: left;')
                if not name_div:
                     name_div = cols[1].find('div')
                
                name = name_div.find('a').text.strip() if name_div and name_div.find('a') else "Unknown"
                
                tags_divs = cols[1].find_all('a', class_='notice')
                tags = [tag.text.strip() for tag in tags_divs]
                
                # 3. Extract difficulty rating from the fourth column (index 3)
                rating_span = cols[3].find('span', title='Difficulty')
                difficulty = None
                if rating_span:
                    try:
                        difficulty = int(rating_span.text.strip())
                    except ValueError:
                        difficulty = None
                        
                # Create a raw problem dict
                prob = {
                    'contest_id': contest_id,
                    'problem_index': problem_index,
                    'name': name,
                    'tags': tags,
                    'difficulty': difficulty,
                    'url': f"https://codeforces.com/problemset/problem/{contest_id}/{problem_index}",
                    # We create a simulated 'statement_summary'. In a true massive scrape, 
                    # we would do another request here using Selenium or requests.
                    'statement_summary': f"A competitive programming problem about {', '.join(tags) if tags else 'algorithms'}."
                }
                
                all_raw_problems.append(prob)
                
            # Sleep to avoid DDOSing Codeforces
            time.sleep(SLEEP_TIME_SEC)
            
    except Exception as e:
        print(f"Scraping encountered an error: {e}")
        print("Falling back to simulated dataset.")
        # We return the fallback set so the project can still build and be demoed.
        return get_fallback_data()

    print(f"Successfully scraped {len(all_raw_problems)} problems.")
    
    # Save the raw data so we don't have to keep scraping during debugging
    with open(os.path.join(RAW_DATA_DIR, "raw_scraped.json"), "w") as f:
        json.dump(all_raw_problems, f, indent=4)
        
    return all_raw_problems

def get_fallback_data() -> list:
    """
    Returns a small hand-written dataset if scraping fails due to network or IP blocks.
    
    [TUTORIAL] WHY IT EXISTS:
    Websites like Codeforces use Cloudflare to block scrapers. If we are running this project 
    in an interview or without internet, we STILL need data so the pipeline doesn't crash.
    This acts as our offline safety net.
    """
    return [
        {
            "contest_id": 1900, "problem_index": "A", "name": "Cover in Water",
            "tags": ["greedy", "implementation", "strings"], "difficulty": 800,
            "url": "https://codeforces.com/problemset/problem/1900/A",
            "statement_summary": "Find the minimum number of actions to fill empty cells with water."
        },
        {
            "contest_id": 1899, "problem_index": "B", "name": "2D Traveling",
            "tags": ["graphs", "shortest paths", "math"], "difficulty": 1200,
            "url": "https://codeforces.com/problemset/problem/1899/B",
            "statement_summary": "Calculate the shortest path between cities with major cities having free travel."
        },
        {
            "contest_id": 1901, "problem_index": "C", "name": "Add, Divide and Floor",
            "tags": ["math", "greedy"], "difficulty": 1400,
            "url": "https://codeforces.com/problemset/problem/1901/C",
            "statement_summary": "Make all array elements equal by repeatedly adding X and dividing by 2."
        },
        {
            "contest_id": 1500, "problem_index": "A", "name": "Going Home",
            "tags": ["brute force", "math", "hashing"], "difficulty": 1700,
            "url": "https://codeforces.com/problemset/problem/1500/A",
            "statement_summary": "Find four distinct elements such that x + y = z + w."
        }
    ]

if __name__ == '__main__':
    data = scrape_problems(1)
    print("Test Scraped Data:", data[:2])
