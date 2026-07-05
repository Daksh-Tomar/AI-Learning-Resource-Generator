import json
from google import genai
from google.genai import types, errors
from app.core.config import settings
from app.schemas.learner_profile import LearnerProfileSchema
from app.schemas.chat import ChatMessage
from typing import List

client = genai.Client(api_key=settings.GEMINI_API_KEY)

class ProfileGenerator:
    @staticmethod
    def extract_profile(history: List[ChatMessage], latest_message: str) -> LearnerProfileSchema:
        contents = []
        for msg in history:
            role = 'model' if msg.role == 'ai' else 'user'
            contents.append(types.Content(role=role, parts=[types.Part.from_text(text=msg.content)]))
        contents.append(types.Content(role="user", parts=[types.Part.from_text(text=latest_message)]))
        
        completion = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction="You are a data extraction agent. Extract the user's learning profile from the conversation history. Infer reasonable defaults where necessary based on context.",
                response_mime_type="application/json",
                response_schema=LearnerProfileSchema,
                temperature=0.1
            )
        )
        
        if hasattr(completion, 'parsed') and completion.parsed:
            return completion.parsed
            
        profile_data = json.loads(completion.text)
        return LearnerProfileSchema(**profile_data)
