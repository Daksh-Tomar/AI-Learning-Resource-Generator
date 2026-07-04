import os
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from openai import OpenAI
from ..database import get_db
from ..schemas import ChatRequest, ChatResponse, LearnerProfileSchema
from ..models import Conversation

router = APIRouter(prefix="/api/chat", tags=["chat"])

# Initialize OpenAI Client (Make sure OPENAI_API_KEY is loaded via dotenv in main or database)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
You are LearnLens AI, an intelligent academic counselor and learning path generator.
Your goal is to conduct a short, adaptive interview to understand the user's learning goals, current level, constraints, and preferences.
Do NOT simply ask all questions at once. Ask one or two focused questions at a time based on what they just said.
Try to gather:
- What they are preparing for
- Their current knowledge level
- Their target level or deadline
- Their preferred learning format (video, text, mix)
- Topics they already know vs weak topics

Keep your responses conversational, concise, and encouraging.
If you believe you have enough information, you can mention that you are ready to generate a profile.
"""

@router.post("/message", response_model=ChatResponse)
def send_message(request: ChatRequest, db: Session = Depends(get_db)):
    # Reconstruct history for OpenAI
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for msg in request.history:
        messages.append({"role": msg.role, "content": msg.content})
    
    # Append the latest user message
    messages.append({"role": "user", "content": request.message})

    # Call OpenAI
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.7,
        max_tokens=300
    )
    
    ai_reply = response.choices[0].message.content

    # Save to db (optional/simplified for MVP)
    # Ideally, we would fetch or create the Conversation by session_id
    
    return ChatResponse(session_id=request.session_id, message=ai_reply)

@router.post("/profile/extract", response_model=LearnerProfileSchema)
def extract_profile(request: ChatRequest):
    # Reconstruct history to extract profile
    messages = [{"role": "system", "content": "You are a data extraction agent. Extract the user's learning profile from the conversation history."}]
    for msg in request.history:
        messages.append({"role": msg.role, "content": msg.content})
    messages.append({"role": "user", "content": request.message})
    
    # Use structured output parsing (new in OpenAI SDK)
    completion = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=messages,
        response_format=LearnerProfileSchema
    )
    
    profile = completion.choices[0].message.parsed
    return profile
