"""
File Name: rag_pipeline.py
Purpose: Connects the Recommender (Retrieval) and the Hint/Summary engines (Generation).
Why it exists: RAG stands for Retrieval-Augmented Generation. This orchestrates that process.
It retrieves similar problems, and then generates an answer based on both the user's query 
and those specific retrieved context problems.
What it imports: 
- src.recommender.Recommender
- src.hint_engine.generate_hint
- src.summarizer.generate_summary
Which files use it: chatbot.py, api/main.py
Inputs: User messages (e.g., "Give me a hint for 1500A" or "I want DP problems").
Outputs: A generated string response.
Role in pipeline: The "Brain" of the chatbot.
"""

# ==========================================
# OUR CUSTOM PROJECT FILES (Modules we wrote)
# ==========================================
# src.recommender: We import our mathematical search engine logic to handle the "Retrieval" (R) step of RAG.
from src.recommender import Recommender

# src.hint_engine: We import our logic rule system that handles safe, non-spoiling hint "Generation" (G/Augmentation).
from src.hint_engine import generate_hint

# src.summarizer: We import our automated template generator that builds Editorial summaries.
from src.summarizer import generate_summary

class RAGPipeline:
    def __init__(self, recommender: Recommender):
        """
        We pass the Recommender in rather than instantiating it here so we don't 
        accidentally load the 80MB models multiple times in memory.
        """
        self.recommender = recommender
        self.df = self.recommender.df
        
    def _find_problem_by_id_string(self, id_str: str) -> dict:
        """
        Utility to find a problem like "1500A" in the pandas DataFrame.
        """
        # separate numbers from letters
        import re
        match = re.match(r'(\d+)([a-zA-Z]+)', id_str.strip())
        if not match:
             return None
             
        c_id = int(match.group(1))
        p_idx = match.group(2).upper()
        
        # Searching the pandas dataframe
        res = self.df[(self.df['contest_id'] == c_id) & (self.df['problem_index'] == p_idx)]
        if res.empty:
            return None
        return res.iloc[0].to_dict()

    def process_query(self, query: str) -> str:
        """
        The main handler for user string queries.
        
        What it does:
        1. Parses the intent of the user (e.g., are they asking for a summary, a hint, or similar problems?).
        2. RETRIEVAL STEP: Fetches the requested problem or similar problems from the Recommender.
        3. GENERATION STEP: Passes that retrieved data into the HintEngine or Summarizer.
        
        Why it exists: To provide a single, clean API for the frontend/chatbot.
        """
        q_lower = query.lower()
        
        # Intent 1: Give a Hint
        if "hint" in q_lower:
            # Try to extract the problem name like "1500A"
            words = query.split()
            problem = None
            for w in words:
                problem = self._find_problem_by_id_string(w)
                if problem:
                    break
                    
            if problem:
                return generate_hint(tags=problem['tags'], difficulty=problem['difficulty'], problem_name=problem['name'])
            else:
                return "I couldn't identify the problem ID in your request. Please ask like: 'Give me a hint for 1500A'."

        # Intent 2: Summarize
        elif "summarize" in q_lower or "summary" in q_lower:
             # Similar extraction logic
             words = query.split()
             problem = None
             for w in words:
                 problem = self._find_problem_by_id_string(w)
                 if problem:
                     break
             if problem:
                 return generate_summary(problem['name'], problem['tags'], problem['statement_summary'])
             else:
                 return "I couldn't identify the problem ID. Try 'Summarize 1500A'."
                 
        # Intent 3: Recommend / Semantic Search
        # Example query: "Suggest 5 DP problems about water"
        else:
            # We treat the entire user query as semantic input to our Sentence-Transformer.
            # RETRIEVAL:
            recs = self.recommender.recommend_by_similarity(query, top_k=3)
            
            # GENERATION (in this case, just formatting the output)
            if not recs:
                return "I couldn't find any recommendations for that."
                
            response = [f"Here are my top recommendations based on your query '{query}':"]
            for r in recs:
                url = f"https://codeforces.com/problemset/problem/{r['contest_id']}/{r['problem_index']}"
                diff = r['difficulty'] if r['difficulty'] else "N/A"
                response.append(f"- **{r['name']}** (Rating: {diff}) | Tags: {r['tags']} | Match: {r['similarity_score']:.2f}\n  Link: {url}")
                
            return "\n\n".join(response)
