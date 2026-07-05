import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.core.database import SessionLocal
from app.models.learner_profile import LearnerProfileModel
from app.schemas.learner_profile import SkillLevel, LearningFormat
import uuid

def seed():
    db = SessionLocal()
    try:
        # Sample Profile 1
        profile1 = LearnerProfileModel(
            id=uuid.uuid4(),
            subject="Machine Learning",
            goal="Become an AI Engineer",
            current_level=SkillLevel.beginner.value,
            target_level=SkillLevel.intermediate.value,
            deadline_days=180,
            daily_hours=2.0,
            known_topics=["python", "linear algebra"],
            weak_topics=["calculus", "neural networks"],
            preferred_formats=[LearningFormat.video.value, LearningFormat.project_based.value],
            wants_projects=True
        )
        
        # Sample Profile 2
        profile2 = LearnerProfileModel(
            id=uuid.uuid4(),
            subject="Dynamic Programming",
            goal="Ace technical interviews",
            current_level=SkillLevel.intermediate.value,
            deadline_days=30,
            daily_hours=4.0,
            known_topics=["arrays", "hash maps"],
            weak_topics=["memoization", "recursion"],
            preferred_formats=[LearningFormat.written.value],
            wants_interview_prep=True
        )

        db.add(profile1)
        db.add(profile2)
        db.commit()
        print("Database seeded with sample learner profiles.")
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed()
