"""
File Name: indexer.py
Purpose: Creates and saves mathematical representations (vectors/embeddings) of our problems.
Why it exists: Computers can't "understand" text directly. To find "similar" problems or 
to search by meaning, we must convert the text (name + tags + summary) into numbers.
What it imports: 
- pandas (to load data easily)
- scikit-learn's TfidfVectorizer (for keyword-based mathematical representation)
- sentence-transformers (for deep-learning based contextual representation, our CodeBERT stand-in)
- joblib (to save our models to disk)
Which files use it: run_pipeline.py (to build indexes), recommender.py and rag_pipeline.py (to load them)
Inputs: None directly, reads from Database.
Outputs: Writes .pkl (pickle) files containing trained models and matrices to the data/processed directory.
Role in pipeline: Step 4. Converts cleaned DB data into AI-ready matrices.

Interview specific explanation:
We use two different approaches to indexing, to demonstrate breadth of knowledge:
1. TF-IDF: Purely statistical. Counts word frequencies. Fast, great for finding problems with identical tags.
2. Sentence-Transformers (all-MiniLM-L6-v2): A proxy for CodeBERT. It understands *context*. 
   Even if two problems don't share exact words, it knows they are conceptually similar.
   We explicitly state in our README that this is a lightweight substitute for a massive CodeBERT model.
"""

# ==========================================
# BUILT-IN PYTHON LIBRARIES
# ==========================================
import os      # Standard library to safely handle file saving paths across different operating systems.

# ==========================================
# EXTERNAL LIBRARIES (Installed via pip)
# ==========================================
from sklearn.feature_extraction.text import TfidfVectorizer # A mathematical library used to count word frequencies and find obvious keyword matches.
from sentence_transformers import SentenceTransformer       # A deep-learning library used here as our 'CodeBERT stand-in' to understand semantic meaning (context).
import joblib                                               # A utility library used to save our heavy mathematical matrices directly to the hard drive as .pkl files.

# ==========================================
# OUR CUSTOM PROJECT FILES (Modules we wrote)
# ==========================================
# src.database: We import our data access helper to retrieve all currently cleaned problems.
from src.database import get_all_problems_as_dataframe

# src.config: We pull configuration rules for where to save the files and which Transformer to use.
from src.config import EMBEDDING_MODEL_NAME, PROCESSED_DATA_DIR

def create_indexes() -> None:
    """
    Reads all problems, builds TF-IDF and Transformer embeddings, and saves them to disk.
    
    [TUTORIAL] WHAT IT DOES:
    This is the core of the Machine Learning pipeline. 
    1. It reads the SQLite text data.
    2. It passes that text through two different math engines (TF-IDF and SentenceTransformers) to convert English into Vectors.
    3. It saves those matrices as `.pkl` files to the hard drive.
    
    [TUTORIAL] WHY IT EXISTS:
    Calculating vectors for 15,000 problems takes time (minutes or hours depending on hardware). 
    We do NOT want to do this every time a user asks a question. By calculating the vectors *offline* 
    and saving them directly to disk, the `chatbot` and `api` can instantly load the pre-computed 
    results in milliseconds. Data Science is all about caching heavy computations!
    """
    print("Fetching data for indexing...")
    df = get_all_problems_as_dataframe()
    
    if df.empty:
        print("No data found in database. Cannot create index.")
        return
        
    # 1. Prepare the text corpus
    # If a problem lacks tags, replace the NaN with empty string
    df['tags'] = df['tags'].fillna('')
    df['statement_summary'] = df['statement_summary'].fillna('')
    
    # We create a new column 'combined_text' which represents the whole "document" we want to index
    # Example: "Going Home brute force, math Find four elements"
    df['combined_text'] = df['name'] + " " + df['tags'] + " " + df['statement_summary']
    
    corpus = df['combined_text'].tolist()
    
    # 2. Build TF-IDF Index (Keyword matching)
    print("Building TF-IDF Index...")
    # TfidfVectorizer converts text to a matrix of TF-IDF features. 
    # stop_words='english' removes common words like "the", "and".
    tfidf_model = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf_model.fit_transform(corpus)
    
    # Check if directory exists
    os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)
    
    # Joblib allows us to save Python objects efficiently.
    joblib.dump(tfidf_model, os.path.join(PROCESSED_DATA_DIR, "tfidf_model.pkl"))
    joblib.dump(tfidf_matrix, os.path.join(PROCESSED_DATA_DIR, "tfidf_matrix.pkl"))
    
    # 3. Build Sentence Transformer Index (Semantic / Meaning matching)
    # This represents the CodeBERT/RAG logic.
    print(f"Building Transformer Embeddings using {EMBEDDING_MODEL_NAME}...")
    st_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    
    # encode() converts the list of strings into a 2D numpy array of floats 
    # (e.g., 384 dimensions for all-MiniLM-L6-v2)
    embeddings_matrix = st_model.encode(corpus, show_progress_bar=True)
    
    # Save the dense embeddings matrix. 
    # We don't need to save the model itself via joblib because sentence_transformers 
    # automatically caches the model weights. We just save the computed answers (the matrix).
    joblib.dump(embeddings_matrix, os.path.join(PROCESSED_DATA_DIR, "embeddings_matrix.pkl"))
    
    # Save the dataframe itself so our API can easily look up by row index
    df.to_pickle(os.path.join(PROCESSED_DATA_DIR, "problems_df.pkl"))
    
    print("Indexing Complete! Files saved to data/processed.")

if __name__ == "__main__":
    create_indexes()
