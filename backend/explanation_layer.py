import os
import json
from dotenv import load_dotenv

load_dotenv()

# Fallback in case openai is not installed or key is missing
try:
    from openai import OpenAI
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
except:
    client = None

def generate_explanation(plan_json: list, user_goal: str) -> str:
    """
    Takes the structured plan and explains it using an LLM.
    If no LLM API key is available, returns a simple formatted string based on the data.
    """
    if client and os.environ.get("OPENAI_API_KEY"):
        prompt = f"""
        You are an AI learning path recommender. I have used an ML pipeline to score and rank resources for a user's goal: '{user_goal}'.
        Here is the JSON plan with actual ML-derived scores (relevance, quality, difficulty):
        
        {json.dumps(plan_json, indent=2)}
        
        Please format this plan into a human-readable response. 
        Explain *why* each resource was chosen using the provided scores (e.g., mention the quality score or relevance). 
        Do not invent new facts. Your job is just to format the data into a friendly explanation with pros/cons based on the difficulty and type.
        """
        
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "system", "content": "You are a helpful AI tutor."},
                          {"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"LLM API Error: {e}")
            pass
            
    # Fallback formatting if no LLM is available
    explanation = f"### Your Personalized Plan for: {user_goal}\n\n"
    explanation += "*(Note: This is a fallback formatted explanation since no LLM API key was provided.)*\n\n"
    
    for week in plan_json:
        explanation += f"#### Week {week['week']} (Total: {week['total_hours']} hours)\n"
        for res in week['resources']:
            explanation += f"- **[{res['title']}]({res['url']})** ({res['type']})\n"
            explanation += f"  - **Why?** Relevance score of {res['relevance_score']}. Quality score: {res.get('quality_score', 'N/A')}.\n"
            explanation += f"  - **Level:** {res['difficulty']} | **Time:** {res['estimated_hours']} hrs\n"
        explanation += "\n"
        
    return explanation
