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

from pydantic import BaseModel
from typing import List, Optional

class ChatRequest(BaseModel):
    """
    Schema for the main chatbot endpoint.
    A user will POST a JSON like: {"query": "Give me a hint for 1500A"}
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
