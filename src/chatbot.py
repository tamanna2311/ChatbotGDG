"""
File Name: chatbot.py
Purpose: Provides a command-line interface (CLI) for users to interact with the assistant.
Why it exists: While an API is great for production, a CLI chatbot is the simplest 
and fastest way to demonstrate the project working locally during an interview.
What it imports: src.rag_pipeline.RAGPipeline
Which files use it: run_pipeline.py (if the user chooses CLI mode).
Inputs: Raw text input from standard input (keyboard).
Outputs: Printed text to standard output (screen).
Role in pipeline: The User Interface.
"""

# ==========================================
# BUILT-IN PYTHON LIBRARIES
# ==========================================
import sys # Standard library used here specifically to call sys.exit() if the models fail to load, stopping the program safely.

# ==========================================
# OUR CUSTOM PROJECT FILES (Modules we wrote)
# ==========================================
# src.rag_pipeline: We import the 'Brain' of our system that connects queries to the Recommender and Hint engines.
from src.rag_pipeline import RAGPipeline

# src.recommender: We import the mathematical Search Engine. We initialize it here so the ML models load into RAM.
from src.recommender import Recommender

def start_chat():
    """
    Initializes the models and runs an infinite loop asking the user for input.
    
    [TUTORIAL] WHAT IT DOES:
    This is entirely a "frontend" file. 
    1. It boots up the `Recommender` (which loads the math arrays from disk).
    2. It hands that recommender over to the `RAGPipeline` (the brain).
    3. It starts a `while True:` loop inside your terminal, taking your typed input (`input()`)
       and passing it to the brain.
       
    [TUTORIAL] WHY IT EXISTS:
    Before we build a full React.js website or FastAPI server, we need a way to test that our 
    Machine Learning logic successfully works locally. A CLI (Command Line Interface) is the easiest way.
    """
    print("Loading AI Models... Please wait (this make take a few seconds).")
    try:
        recommender = Recommender()
        rag = RAGPipeline(recommender)
    except Exception as e:
        print(f"Failed to load models. Have you run the scraper and indexer yet? Error: {e}")
        sys.exit(1)
        
    print("\n" + "="*50)
    print("Welcome to Codeforces Assistant Chatbot!")
    print("Type 'quit', 'exit', or 'q' to leave.")
    print("Example Queries:")
    print(" - 'Suggest 3 problems about greedy algorithms'")
    print(" - 'Hint for 1900A'")
    print(" - 'Summarize 1500A'")
    print("="*50 + "\n")
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break
                
            if not user_input:
                continue
                
            print("Bot: Thinking...")
            response = rag.process_query(user_input)
            print(f"\nBot:\n{response}\n")
            
        except KeyboardInterrupt:
            # Handle Ctrl+C gracefully
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    start_chat()
