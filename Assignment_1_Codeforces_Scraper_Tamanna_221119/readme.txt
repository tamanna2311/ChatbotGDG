This is the folder structure of the scraper implemented using bs4, it is designed to repeatedly ask for codeforces URLs to be extracted.
├── problems&editorials_scraper.py                  # Python script for scraping
├── debug_page_source.html      # Debug file to save page source for troubleshooting
├── problems/                   # Directory to store scraped problems
│   ├── {problem_id}/           # Subfolder for each problem ID
│   │   ├── {problem_letter}.txt   # Problem statement as text
│   │   ├── {problem_letter}.json  # Metadata in JSON format
├── editorials/                 # Directory to store scraped editorials
│   ├── {entry_id}.txt          # Editorial content as text
│   ├── {entry_id}.json         # Metadata in JSON format