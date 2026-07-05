import os
import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from google import genai
from google.genai import types, errors
from database import get_db
from schemas import ChatRequest, ChatResponse, LearnerProfileSchema
from models import Conversation

router = APIRouter(prefix="/api/chat", tags=["chat"])

# Initialize Gemini Client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

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
    # Reconstruct history for Gemini
    contents = []
    for msg in request.history:
        role = 'model' if msg.role == 'ai' else 'user'
        contents.append(types.Content(role=role, parts=[types.Part.from_text(text=msg.content)]))
    
    # Append the latest user message
    contents.append(types.Content(role="user", parts=[types.Part.from_text(text=request.message)]))

    try:
        # Call Gemini
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.7,
                max_output_tokens=300
            )
        )
        ai_reply = response.text
    except errors.APIError as e:
        if e.code == 429:
            raise HTTPException(status_code=429, detail="Gemini API Quota Exceeded. Please check your billing details.")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # Save to db (optional/simplified for MVP)
    # Ideally, we would fetch or create the Conversation by session_id
    
    return ChatResponse(session_id=request.session_id, message=ai_reply)

@router.post("/profile/extract", response_model=LearnerProfileSchema)
def extract_profile(request: ChatRequest):
    # Reconstruct history for Gemini
    contents = []
    for msg in request.history:
        role = 'model' if msg.role == 'ai' else 'user'
        contents.append(types.Content(role=role, parts=[types.Part.from_text(text=msg.content)]))
    contents.append(types.Content(role="user", parts=[types.Part.from_text(text=request.message)]))
    
    try:
        # Use structured output
        completion = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction="You are a data extraction agent. Extract the user's learning profile from the conversation history.",
                response_mime_type="application/json",
                response_schema=LearnerProfileSchema,
                temperature=0.1
            )
        )
        
        # In case google-genai sdk supports .parsed
        if hasattr(completion, 'parsed') and completion.parsed:
            return completion.parsed
            
        profile_data = json.loads(completion.text)
        profile = LearnerProfileSchema(**profile_data)
        return profile
    except errors.APIError as e:
        if e.code == 429:
            raise HTTPException(status_code=429, detail="Gemini API Quota Exceeded. Please check your billing details.")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
