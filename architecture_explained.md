# Architecture Explained (For Beginners)

If you are a student or preparing for an interview, this document explains *exactly* how data travels from the internet through our codebase and out to the user.

## The Broad Picture
The system works in two distinct phases:
1. **Offline Phase (Data Engineering):** We gather data, clean it, save it, and index it into mathematical shapes.
2. **Online Phase (The Chatbot):** A user asks a question, and we instantly find the best answers from our pre-computed math indexes.

---

## The Flow of Data: Step-By-Step

### Phase 1: Offline Data Preparation 
*(Triggered by `python run_pipeline.py --scrape --index`)*

1. **`run_pipeline.py` starts.** 
   - *Why?* This is the orchestrator. Without it, you'd have to run 5 separate Python scripts manually in the right order.

2. **The Database is Created (`db/init_db.py`).**
   - `run_pipeline.py` calls `initialize_database()`.
   - *Why?* We need a secure bucket to drop our web data into. It reads `schema.sql` to make sure the bucket has the exact structure (columns) we want.

3. **Scraping the Web (`src/scraper.py`).**
   - `run_pipeline.py` calls `scrape_problems()`.
   - The scraper acts like a fake web browser. It uses `requests` to ask Codeforces for its HTML source. Then it uses `BeautifulSoup` to find specific tags (like reading a book looking for bold words). 
   - It outputs a raw `List` of Python dictionaries.

4. **Cleaning Data (`src/cleaner.py`).**
   - `run_pipeline.py` passes the raw list into `clean_and_load()`.
   - *Why?* The internet is messy. Tags might be empty strings, or difficulty numbers might be missing. If we put trash in the database, our AI models will output trash.
   - For every clean problem, the cleaner calls `insert_problem()` (from `src/database.py`).

5. **Saving to SQLite (`src/database.py`).**
   - `insert_problem()` takes the clean dict and writes pure SQL (e.g., `INSERT INTO problems...`).
   - Data is now persistently saved in `data/processed/codeforces.db`.

6. **Building AI Indexes (`src/indexer.py`).**
   - *Why?* A chatbot can't read a SQL database very quickly to find "things similar to XYZ".
   - `indexer.py` extracts all problems from the DB. 
   - It mathematically translates English text ("Dynamic Programming") into arrays of numbers (vectors) using `sentence-transformers` and `scikit-learn` TF-IDF. 
   - It saves these mathematical shapes as `.pkl` files on the hard drive using `joblib`.

---

### Phase 2: Online Chatbot
*(Triggered by `python run_pipeline.py --chat`)*

1. **Starting the Chatbot (`src/chatbot.py`).**
   - `chatbot.py` prints a welcome prompt and waits for you to type something.
   
2. **Loading the Brain (`src/recommender.py`).**
   - The moment the chatbot starts, it creates a `Recommender()` object.
   - *Why?* Remember those `.pkl` math files we built in Phase 1? The Recommender loads them into RAM once. This takes a few seconds, but ensures all future answers are millisecond-fast.

3. **Connecting RAG (`src/rag_pipeline.py`).**
   - `chatbot.py` creates a `RAGPipeline(recommender)`. 
   - Now the RAG object has access to the mathematical models.
   
4. **User Asks a Question.**
   - You type: *"Suggest some greedy problems."*
   - `chatbot.py` takes that raw string and passes it manually to `RagPipeline.process_query()`.
   
5. **Intent Parsing.**
   - `rag_pipeline.py` looks at your string. Does it have the word "hint"? No. Does it have "summarize"? No. So it decides you must be looking for recommendations.

6. **Semantic Search / Retrieval.**
   - `rag_pipeline.py` calls `recommender.recommend_by_similarity("Suggest some greedy problems.")`.
   - `recommender.py` pushes your string through the Transformer model, turning your sentence into a new Math Vector.
   - It measures the distance (Cosine Similarity) between your vector and all 15,000 problem vectors stored in RAM.
   - It returns the closest matches (e.g., the top 3).

7. **Generation & Output.**
   - `rag_pipeline.py` receives the top 3 matches and formats them nicely into text.
   - `chatbot.py` prints that text to your screen.

---

## Deep Dive: How the specific modules work

### How does Retrieval work?
Retrieval is the act of finding the *right* data out of a huge dataset. Standard databases use exact word matches (keyword search). Our recommender uses **Semantic Retrieval**. Because we trained a transformer model on the text, the vector for "dynamic programming cache" and the vector for "memoization array" will be very close together in mathematical space, even though they share almost zero actual alphabet letters.

### How does "Similarity Search" actually work under the hood?
Imagine a 2D graph with X and Y axes. A problem about "Apples" is at coordinate (1, 1). A problem about "Oranges" is at (1, 2). A problem about "Bicycles" is at (8, 9). 
Cosine similarity draws a line from the origin (0,0) to those coordinates, and measures the angle between the lines. Apples and Oranges will have a very small angle between them (they are highly similar). Apples and Bicycles will be 90 degrees apart (zero similarity). Our AI models do this, but instead of 2D space, they use 384-dimensional space to capture deep meaning.

### How does Hint Generation work (`src/hint_engine.py`)?
In a Multi-Million dollar project, a problem's extracted context is passed to an LLM like GPT-4, and GPT-4 is instructed: "Write a hint for this context without giving away the answer."
For our simplified student project, `hint_engine.py` looks at the fetched context (Specifically, the tags). If it sees the tag `dp`, it selects from a list of predefined, high-quality educational suggestions about state tracking and subproblems. It mimics the behavior of an LLM generation step quickly, cheaply, and safely.
