import json
from google import genai
from google.genai import types
from app.core.config import settings
from app.schemas.learner_profile import LearnerProfileSchema
from app.schemas.search_plan import SearchPlan

client = genai.Client(api_key=settings.GEMINI_API_KEY)

class SearchPlanGenerator:
    @staticmethod
    def generate_plan(profile: LearnerProfileSchema) -> SearchPlan:
        prompt = f"""
        Given the following learner profile, generate a structured search plan to find the best educational resources.
        
        Subject: {profile.subject}
        Goal: {profile.goal}
        Current Level: {profile.current_level}
        Deadline (days): {profile.deadline_days}
        Known Topics: {', '.join(profile.known_topics) if profile.known_topics else 'None'}
        Weak Topics: {', '.join(profile.weak_topics) if profile.weak_topics else 'None'}
        Preferred Formats: {[f.value for f in profile.preferred_formats]}
        Wants Projects: {profile.wants_projects}
        Wants Interview Prep: {profile.wants_interview_prep}
        
        Generate exactly 3 to 10 specific search queries (e.g., YouTube search strings) that would yield high-quality, relevant tutorials, lectures, or articles.
        Identify 3 to 30 required conceptual keywords.
        """
        
        completion = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction="You are an expert curriculum designer. Output the search plan adhering strictly to the JSON schema constraints.",
                response_mime_type="application/json",
                response_schema=SearchPlan,
                temperature=0.2
            )
        )
        
        if hasattr(completion, 'parsed') and completion.parsed:
            return completion.parsed
            
        plan_data = json.loads(completion.text)
        return SearchPlan(**plan_data)
