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
    Combines problem properties into an "Editorial-style" summary paragraph.
    
    [TUTORIAL] WHAT IT DOES:
    It acts as an automated news reporter. It takes raw metadata (like difficulty 1500, tags [math, greedy]) 
    and translates them into a single, cohesive, human-readable english paragraph.
    
    [TUTORIAL] WHY IT EXISTS:
    Humans prefer reading paragraphs over looking at JSON dictionaries. This serves as the 
    'Generation' component of the RAG pipeline when the user asks 'Summarize what 1500A is about.'
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
