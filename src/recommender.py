"""
File Name: recommender.py
Purpose: Contains logic to recommend problems based on mathematical similarity.
Why it exists: The user requested a "similarity-based search and recommendations" feature.
Instead of building a massive Neural Network, we use Cosine Similarity on our pre-computed embeddings.
What it imports:
- pandas (to load our cached dataframe)
- joblib (to load our cached matrices)
- sklearn.metrics.pairwise.cosine_similarity (the core math algorithm)
Which files use it: api/main.py, src/chatbot.py, run_pipeline.py (for testing)
Inputs: A query string or target problem ID, number of recommendations to return (k).
Outputs: A list of dictionaries representing recommended problems.
Role in pipeline: This is the primary feature of our application. 
"""

# ==========================================
# BUILT-IN PYTHON LIBRARIES
# ==========================================
import os                                  # Standard library for resolving computer file paths.
from typing import List, Dict, Any         # Purely for type hinting our Python code to make reading and debugging easier.

# ==========================================
# EXTERNAL LIBRARIES (Installed via pip)
# ==========================================
import pandas as pd                        # Data science library used to efficiently hold our problem database in RAM.
import joblib                              # Used to instantly load our massively pre-calculated mathematical .pkl files from disk.
from sklearn.metrics.pairwise import cosine_similarity # The core math calculation that measures the distance/angle between two mathematical Vectors.
from sentence_transformers import SentenceTransformer  # Used here to encode the LIVE user query into a vector so we can measure it.

# ==========================================
# OUR CUSTOM PROJECT FILES (Modules we wrote)
# ==========================================
# src.config: Our central authority for paths and model names.
from src.config import PROCESSED_DATA_DIR, EMBEDDING_MODEL_NAME

class Recommender:
    """
    A class to encapsulate our recommendation logic.
    
    [TUTORIAL] WHY A CLASS?
    If we just used loose functions, Python would have to re-read the massive 80MB files 
    from the hard drive every time we wanted a recommendation. By tying it to a `class`, 
    we load the files exactly ONCE during `__init__`, save them inside `self`, and reuse 
    them instantly for all future questions.
    """
    def __init__(self):
        # Load the dataframe containing all problem metadata
        self.df_path = os.path.join(PROCESSED_DATA_DIR, "problems_df.pkl")
        self.tfidf_matrix_path = os.path.join(PROCESSED_DATA_DIR, "tfidf_matrix.pkl")
        self.embeddings_matrix_path = os.path.join(PROCESSED_DATA_DIR, "embeddings_matrix.pkl")
        
        # We explicitly assume these files exist. If not, the indexer hasn't run.
        if not os.path.exists(self.df_path):
             raise FileNotFoundError("Dataframe not found. Run indexer.py first.")
             
        self.df = pd.read_pickle(self.df_path)
        
        # Load matrices
        self.tfidf_matrix = joblib.load(self.tfidf_matrix_path)
        self.st_matrix = joblib.load(self.embeddings_matrix_path)
        
        # Load the SentenceTransformer model strictly for ENCODING the live user query.
        # We do not use it to encode all 15k problems again here.
        self.st_model = SentenceTransformer(EMBEDDING_MODEL_NAME)

    def recommend_by_similarity(self, query_text: str, top_k: int = 5, use_transformer: bool = True) -> List[Dict[str, Any]]:
        """
        Takes a raw text string representing what you want to learn, converts it to a mathematical vector, 
        and finds the closest matching problems in the database.
        
        [TUTORIAL] WHAT IT DOES:
        1. Encodes the query: Turns the English sentence into an array of floats using our Transformer.
        2. Computes Cosine Similarity: Mathematically calculates the distance between your query and all 15k problems.
        3. Sorts and slices: Picks the `top_k` problems with the highest similarity percentages.
        
        [TUTORIAL] WHY IT EXISTS:
        This is the "Retrieval" (R) step of our RAG pipeline. It handles both direct search bar queries 
        ("I want DP problems about water") and fetches context for our hint generator.
        """
        if use_transformer:
            # 1. Encode user query into a dense mathematical vector of shape (1, 384)
            query_vector = self.st_model.encode([query_text])
            # 2. Compare it to our pre-calculated matrix (N, 384) 
            # Cosine similarity measures the angle between vectors. 1.0 means identical direction (meaning).
            similarities = cosine_similarity(query_vector, self.st_matrix)[0]
        else:
            # For TF-IDF, we would need to load the TF-IDF model to transform the query.
            # For simplicity in this student project, we only implement the Transformer route for direct queries,
            # but we COULD load the joblib tfidf_model here and call .transform([query_text]).
            pass
            
        # 3. Get indices of the highest `top_k` similarities
        # argsort() sorts ascending, so we take the last `top_k` and reverse them [::-1]
        top_indices = similarities.argsort()[-top_k:][::-1]
        
        # 4. Fetch the actual problem data using the indices
        recommendations = []
        for idx in top_indices:
            row = self.df.iloc[idx]
            # Convert pandas Series to a native Python dictionary
            prob_dict = {
                "id": int(row['id']),
                "name": row['name'],
                "contest_id": int(row['contest_id']),
                "problem_index": row['problem_index'],
                "difficulty": int(row['difficulty']) if pd.notnull(row['difficulty']) else None,
                "tags": row['tags'],
                "url": row['url'],
                "similarity_score": float(similarities[idx])
            }
            recommendations.append(prob_dict)
            
        return recommendations


if __name__ == "__main__":
    # Test block
    print("Loading recommender...")
    try:
        rec = Recommender()
        print("Testing semantic search: 'dynamic programming on trees'")
        results = rec.recommend_by_similarity("dynamic programming on trees", top_k=2)
        for r in results:
             print(f"[{r['similarity_score']:.2f}] {r['name']} ({r['tags']})")
    except Exception as e:
        print("Make sure to run indexer.py first!")
        print(f"Error: {e}")
