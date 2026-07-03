import os
import sys
from dotenv import load_dotenv

load_dotenv()
from fastapi import FastAPI
from pydantic import BaseModel

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ml_layer.relevance_ranker import rank_resources
from backend.plan_constructor import construct_plan
from backend.explanation_layer import generate_explanation

app = FastAPI(title="Learning Path API")

class PlanRequest(BaseModel):
    topic: str
    goal: str
    available_hours_per_week: float
    num_weeks: int
    skill_level: str

@app.post("/generate-plan")
def generate_learning_plan(req: PlanRequest):
    print(f"Received request for {req.topic}: '{req.goal}'")
    
    # 1. Rank resources using ML layer
    ranked = rank_resources(req.goal, top_k=20)
    
    if not ranked:
        return {"error": "No resources available for this topic or model not loaded."}
        
    # 2. Construct the plan
    plan_json = construct_plan(
        ranked_resources=ranked,
        available_hours_per_week=req.available_hours_per_week,
        num_weeks=req.num_weeks,
        start_difficulty=req.skill_level.lower()
    )
    
    # 3. Explain the plan via LLM
    explanation = generate_explanation(plan_json, req.goal)
    
    return {
        "plan_data": plan_json,
        "explanation": explanation
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
