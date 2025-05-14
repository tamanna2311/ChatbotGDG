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

from src.rag_pipeline import RAGPipeline
from src.recommender import Recommender
import sys

def start_chat():
    """
    Initializes the models and starts an infinite loop to accept user text.
    
    What it does:
    1. Loads the Recommender (which takes a few seconds to load the matrices).
    2. Instantiates the RAG Pipeline.
    3. Prints a welcome message.
    4. Loops continuously, passing user input to `rag.process_query()`.
    
    Why it exists: To provide an interactive experience simulating the "Chatbot" requirement.
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
