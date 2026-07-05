import os
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from google import genai
from google.genai import types, errors
from app.core.database import get_db
from app.core.config import settings
from app.schemas.chat import ChatRequest, ChatResponse
import logging

router = APIRouter(prefix="/api/chat", tags=["chat"])
logger = logging.getLogger("learnlens.api")
client = genai.Client(api_key=settings.GEMINI_API_KEY)

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
    logger.info(f"Received chat message for session {request.session_id}")
    contents = []
    for msg in request.history:
        role = 'model' if msg.role == 'ai' else 'user'
        contents.append(types.Content(role=role, parts=[types.Part.from_text(text=msg.content)]))
    
    contents.append(types.Content(role="user", parts=[types.Part.from_text(text=request.message)]))

    try:
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
        logger.error(f"Gemini API Error: {str(e)}")
        if e.code == 429:
            raise HTTPException(status_code=429, detail="Gemini API Quota Exceeded. Please check your billing details.")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.exception("Unexpected error in chat endpoint")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
    return ChatResponse(session_id=request.session_id, message=ai_reply)
