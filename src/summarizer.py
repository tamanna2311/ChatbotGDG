"""
File Name: summarizer.py
Purpose: Generates a concise editorial-style summary of a problem.
Why it exists: Often a user doesn't want to read a 4-page problem statement; 
they just want the mathematical/algorithmic "core idea" extracted.
What it imports: None.
Which files use it: rag_pipeline.py, chatbot.py
Inputs: Problem dict (name, tags, raw statement).
Outputs: A short string summary.
Role in pipeline: Supporting utility for text generation.

Simplification Note:
True summaries require LLMs. For this realistic student project, we use a template-based
generator that simulates what an LLM would extract based on the problem's metadata. 
In a real production system, this function would make a call to the OpenAI API or 
a local Llama-3 model.
"""

def generate_summary(problem_name: str, tags: str, statement_summary: str) -> str:
    """
    Creates a brief "Editorial Style" overview of a problem.
    
    What it does: 
    It strings together the problem's title, its algorithmic categorized tags, and 
    adds standard competitive programming phrasing to simulate an Editorial.
    
    Why it exists: To provide the "Summary" feature requested in the resume project requirements.
    
    What it returns: A formatted string summarizing the problem.
    """
    
    tags_display = tags if tags else "General Implementation"
    
    summary = (
        f"**Editorial Summary for {problem_name}**\n"
        f"Core Topic: {tags_display}\n"
        f"Abstract: {statement_summary}\n\n"
        "Likely approach: Identify the constraints, map the problem to the standard algorithms "
        f"associated with [{tags_display}], and build a time-efficient solution."
    )
    
    return summary
