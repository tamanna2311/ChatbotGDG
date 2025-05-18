"""
File Name: schemas.py
Purpose: Defines the data validation structures for our FastAPI endpoints.
Why it exists: Pydantic schemas ensure that any data sent to our API is correctly 
typed (e.g., query must be a string). If someone sends invalid JSON, FastAPI automatically 
rejects it with a helpful error, protecting our backend code from crashing.
What it imports: pydantic.BaseModel
Which files use it: api/main.py
Inputs: None (these are class definitions).
Outputs: None.
Role in pipeline: Data validation layer for the API.
"""

# ==========================================
# BUILT-IN PYTHON LIBRARIES
# ==========================================
from typing import List, Optional # Type hinting libraries. Optional means a variable can be None without crashing.

# ==========================================
# EXTERNAL LIBRARIES (Installed via pip)
# ==========================================
from pydantic import BaseModel    # The core engine behind FastAPI validation. It ensures incoming JSON strictly matches our classes.

class ChatRequest(BaseModel):
    """
    Schema for the main chatbot endpoint.
    
    [TUTORIAL] WHAT IT DOES:
    Whenever someone sends data over the internet to our API, we cannot trust them. They might 
    send an array instead of a string, or an empty JSON. This `Pydantic BaseModel` acts like a 
    security bouncer. It guarantees that the incoming request MUST be a JSON object containing 
    exactly one key named "query", and its value MUST be a string. If they send anything else, 
    FastAPI automatically blocks them with a "422 Unprocessable Entity" error.
    """
    query: str

class ChatResponse(BaseModel):
    """
    Schema for what the chatbot returns.
    """
    response: str
    
class RecommendationRequest(BaseModel):
    """
    Schema for a direct recommendation request (skipping the string parsing).
    """
    query: str
    top_k: Optional[int] = 5
    
class ProblemSchema(BaseModel):
    """
    Schema representing a Codeforces problem in our API outputs.
    """
    id: int
    name: str
    contest_id: int
    problem_index: str
    difficulty: Optional[int]
    tags: str
    url: str
    similarity_score: float
