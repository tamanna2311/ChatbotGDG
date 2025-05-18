"""
File Name: main.py
Purpose: Defines a RESTful API using FastAPI.
Why it exists: If we ever want to build a React or Vue.js frontend, or allow 
other developers to use our application, a CLI isn't enough. We need an API 
that communicates over standard HTTP protocols.
What it imports: 
- fastapi (to create the server)
- src.rag_pipeline, src.recommender (our core logic)
- api.schemas (for data validation)
Which files use it: run_pipeline.py (if the user chooses API mode).
Inputs: HTTP Requests (GET, POST).
Outputs: JSON Responses.
Role in pipeline: The Web Interface.
"""

# ==========================================
# BUILT-IN PYTHON LIBRARIES
# ==========================================
import os              # Standard library to safely handle file paths across operating systems.
from typing import List # Type hinting for Python dictionaries and arrays.

# ==========================================
# EXTERNAL LIBRARIES (Installed via pip)
# ==========================================
from fastapi import FastAPI, HTTPException # The Web Framework logic, and a helper to return clean HTTP 500/404 errors.

# ==========================================
# OUR CUSTOM PROJECT FILES (Modules we wrote)
# ==========================================
# api.schemas: We import the Strict Pydantic validators we defined so external users can't crash the server with bad JSON.
from api.schemas import ChatRequest, ChatResponse, RecommendationRequest, ProblemSchema

# src.recommender: We import our massive mathematical matrices.
from src.recommender import Recommender

# src.rag_pipeline: We import the logic loop that connects user input to the Recommender and Summarization tool.
from src.rag_pipeline import RAGPipeline

app = FastAPI(
    title="Codeforces Assistant API",
    description="An API for semantic search, recommendation, and hints for Codeforces problems.",
    version="1.0.0"
)

# We use global variables to hold our heavy models. 
# They are initialized the first time someone makes a request (lazy loading) 
# or on startup, so we don't crash standard imports.
RECOMMENDER = None
RAG = None

@app.on_event("startup")
async def startup_event():
    """
    [TUTORIAL] WHAT IT DOES:
    This block of code runs ONE TIME right when you type `uvicorn api.main:app` or `python run_pipeline.py --api`.
    
    [TUTORIAL] WHY IT EXISTS:
    We must load the `Recommender` (which reads 80MB of matrices from the hard drive into RAM) right at the start. 
    If we loaded the Recommender inside one of the routes (like `/chat`), your API would hang for 3 seconds EVERY time 
    a user sent a message! By doing it on "startup", the API routes become lightning fast (0.01 seconds).
    """
    global RECOMMENDER, RAG
    print("API Starting up... Loading models.")
    try:
        RECOMMENDER = Recommender()
        RAG = RAGPipeline(RECOMMENDER)
        print("Models loaded successfully.")
    except Exception as e:
        print(f"Warning: Models failed to load. Have you run the indexer? Error: {e}")

@app.get("/")
def read_root():
    """
    A simple health check endpoint.
    """
    return {"message": "Welcome to the Codeforces Assistant API. Visit /docs for documentation."}

@app.post("/chat", response_model=ChatResponse)
def handle_chat(request: ChatRequest):
    """
    The main Chat endpoint.
    
    [TUTORIAL] HOW IT WORKS:
    1. A frontend application sends an HTTP POST request to `http://localhost:8000/chat`.
    2. Inside the request is a JSON Body: `{"query": "Summarize 1500A"}`.
    3. `request: ChatRequest` automatically validates that JSON using Pydantic.
    4. We pass `request.query` to our Python RAG engine.
    5. We wrap the generated string back into a Pydantic `ChatResponse` and return it as JSON to the frontend.
    """
    if RAG is None:
        raise HTTPException(status_code=500, detail="Models are not loaded.")
        
    try:
        response_text = RAG.process_query(request.query)
        return ChatResponse(response=response_text)
    except Exception as e:
         raise HTTPException(status_code=500, detail=str(e))

@app.post("/recommend", response_model=List[ProblemSchema])
def get_recommendations(request: RecommendationRequest):
    """
    A standalone Retrieval endpoint.
    
    [TUTORIAL] WHY HAVE TWO ENDPOINTS?
    While `/chat` is an all-in-one "Brain" that returns English paragraphs, sometimes a frontend developer 
    just wants to build a standard "Search Results" page. This endpoint skips the Generative (G) step of RAG 
    and just returns a clean JSON array of the top K closest problem arrays.
    """
    if RECOMMENDER is None:
        raise HTTPException(status_code=500, detail="Models are not loaded.")
        
    try:
        recs = RECOMMENDER.recommend_by_similarity(request.query, top_k=request.top_k)
        return recs
    except Exception as e:
         raise HTTPException(status_code=500, detail=str(e))
