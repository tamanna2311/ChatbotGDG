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

from fastapi import FastAPI, HTTPException
from typing import List
import os

from api.schemas import ChatRequest, ChatResponse, RecommendationRequest, ProblemSchema
from src.recommender import Recommender
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
    Runs automatically when the FastAPI server starts.
    We load the machine learning models here so they are ready in memory.
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
    The main RAG Chat endpoint. Pass in a string, get a string back.
    Example body: {"query": "Summarize 1500A"}
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
    A more traditional endpoint. Pass in a string, get a JSON array of problem objects in return.
    Useful for populating a strict UI structure rather than a chat window.
    """
    if RECOMMENDER is None:
        raise HTTPException(status_code=500, detail="Models are not loaded.")
        
    try:
        recs = RECOMMENDER.recommend_by_similarity(request.query, top_k=request.top_k)
        return recs
    except Exception as e:
         raise HTTPException(status_code=500, detail=str(e))
