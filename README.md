# Codeforces Scraper + Chatbot (Educational Project)

## 1. Project Overview
This project is an end-to-end Machine Learning and Software Engineering pipeline designed to help Competitive Programmers improve their problem discovery and learning workflow. It scrapes live data from Codeforces, structures it into a SQLite database, indexes the text using NLP techniques (TF-IDF and Sentence Transformers), and provides a chatbot interface capable of giving contextual hints and recommendations.

## 2. Problem Statement
Codeforces contains over 15,000 algorithmic problems. When a beginner asks "How do I get better at Dynamic Programming?", they are usually given a massive, unorganized list of problems. Furthermore, if they get stuck on a problem, reading the official "Editorial" often spoils the entire solution immediately, ruining the learning experience.

## 3. Why Competitive Programming Problem Discovery is Hard
- **Metadata is sparse**: Tags are often too broad (e.g., "math" can mean anything from basic addition to complex combinatorics).
- **Difficulty is subjective**: A 1500-rated graph problem might "feel" completely different from a 1500-rated greedy problem.
- **Search lacks context**: Traditional search bars only look for exact mathematical keyword matches, ignoring the *intent* of the problem.

## 4. Why Scraping and Structuring is Useful
By extracting raw web HTML into a structured SQLite database, we transform a disorganized website into a queryable knowledge graph. We can filter problems precisely (e.g., "Find all `dp` problems where difficulty is exactly `1400`"). 

## 5. Why Similarity-Based Recommendation is Useful
Sometimes a user solves a problem they loved and wants to practice another one *exactly like it*. By using **Cosine Similarity**, we measure the exact mathematical distance between the algorithmic concepts of two problems. This means we can recommend problems that share the same underlying structure, even if they use different story wrappers (e.g., apples vs. watermelons).

## 6. What RAG Means (In Simple Language)
**RAG** stands for **Retrieval-Augmented Generation**. 
Think of a standard Chatbot (like ChatGPT) as a student taking a test with only their memorized knowledge. RAG is like giving that student an "open book" test. 
1. **Retrieval**: When you ask a question, the system first searches an internal database (our Codeforces SQLite DB) to find the exact, factual information relevant to your question.
2. **Augmented Generation**: The system then looks at the information it just retrieved, and generates a custom answer based *strictly* on those facts.

In our project, we fetch similar problems or requested metadata (Retrieval) and use it to format localized hints and summaries without hallucinating.

## 7. Project Architecture
Our project follows an ETL pipeline + RAG Chatbot structure:
1. **Scraping (Extract)**: Fetch HTML from Codeforces using `requests` and `BeautifulSoup`.
2. **Cleaning (Transform)**: Standardize text, drop missing values, and handle edge cases.
3. **Database (Load)**: Store data reliably in SQLite.
4. **Indexing**: Run `scikit-learn` and `sentence-transformers` over the database to build mathematical vectors.
5. **Chatbot API**: Use `FastAPI` or CLI to accept user queries, map them to vectors, perform similarity comparisons, and generate hints.

## 8. Folder Structure
```text
CodeforcesAssistant/
├── data/
│   ├── raw/                 # Where raw JSON scraper dumps go
│   ├── processed/           # Our clean SQLite DB and mathematical matrices (.pkl)
├── db/
│   ├── schema.sql           # SQL logic for setting up tables
│   ├── init_db.py           # Script to initialize empty tables
├── src/
│   ├── config.py            # Global variables and file paths
│   ├── scraper.py           # Hits Codeforces.com and extracts data
│   ├── cleaner.py           # Cleans raw text and drops bad data
│   ├── database.py          # Helper functions to query SQLite easily (DAO)
│   ├── indexer.py           # Builds TF-IDF and Transformer models
│   ├── recommender.py       # Math logic for finding "similar" problems
│   ├── rag_pipeline.py      # Connects user queries to retrieval & generation
│   ├── hint_engine.py       # Safely generates non-spoiler hints
│   ├── summarizer.py        # Generates short editorial overviews
│   ├── chatbot.py           # Command-Line User Interface
├── api/
│   ├── main.py              # FastAPI Web Backend
│   ├── schemas.py           # Pydantic data validation
├── tests/                   # Automated unit testing
├── run_pipeline.py          # The main script to run everything
├── requirements.txt         # Dependencies
├── README.md                # This file
└── architecture_explained.md# Detailed technical teardown
```

## 9. Database Design
We use SQLite because it requires no background server setup, meaning it's highly portable.
Our tables:
- `problems`: id, contest_id, problem_index, name, difficulty, url, statement_summary
- `tags`: id, name
- `problem_tags`: problem_id, tag_id (A junction table to allow a problem to have many tags, and a tag to have many problems).

## 10. Step-by-Step Execution Guide
1. **Install Dependencies**:
   `pip install -r requirements.txt`
2. **Scrape and Build DB**:
   `python run_pipeline.py --scrape`
3. **Build the Machine Learning Indexes**:
   `python run_pipeline.py --index`
4. **Chat via Terminal**:
   `python run_pipeline.py --chat`
5. **(Optional) Run Web API**:
   `python run_pipeline.py --api`
   Then visit `http://localhost:8000/docs` in your browser.

## 11. Example Chatbot Queries
- "I need 3 graph and dfs problems."
- "Hint for 1500A"
- "Summarize 1899B"

## 12. Example API Requests
**Endpoint**: `POST /chat`
**Body**:
```json
{
  "query": "give me a hint for 1500A"
}
```
**Response**:
```json
{
  "response": "[HINT generated by HintEngine]: This involves Dynamic Programming. Ask yourself: what is the 'state' you need to keep track of at step 'i'?"
}
```

## 13. Limitations and Simplifications
- **No live Selenium Scraping**: Codeforces heavily throttles scraping. To ensure this project is simple and testable locally during interviews without getting IP banned, we scrape a very small portion of Codeforces using static HTTP requests, and include an offline fallback dataset.
- **Heuristic Hints**: True GPT-4 based hint generation requires an expensive paid API key. We are substituting this with a rule-based `hint_engine.py` that relies on tag heuristics to simulate the RAG Generation step.
- **CodeBERT Stand-in**: Training or running Microsoft's actual CodeBERT is computationally heavy. We use `sentence-transformers` (`all-MiniLM-L6-v2`) which captures incredible semantic relationships in text natively on a CPU in seconds.

## 14. Future Improvements
- Integrate OpenAI / Gemini API locally for true autonomous Hint Generation.
- Create a React frontend for the Chatbot.
- Perform batch background scraping using Celery.

## 15. Interview Explanation Section
**How to explain this in an interview:**
"I built an end-to-end NLP pipeline to help students learn algorithms. I scraped Codeforces using Requests/BS4, parsed the semi-structured HTML into a normalized SQLite database, and used SentenceTransformers to embed the problem metadata. Finally, I built a Retrieval-Augmented Generation approach via FastAPI so users could ask semantic questions and receive context-aware, non-spoiling hints rather than just blind text matches."

**Why BS4 over Selenium?** BS4 is memory-efficient and fast for static HTML. I only jump to Selenium if JavaScript rendering or CloudFlare bypass is strictly necessary.
**Why SQLite?** It avoids the overhead of running a local Postgres Docker container, making the project highly portable while still demonstrating knowledge of foreign keys and relational normalization.
**Why Cosine Similarity?** It calculates the difference in angles between two high-dimensional vectors, seamlessly scoring semantic closeness from 0.0 to 1.0.
