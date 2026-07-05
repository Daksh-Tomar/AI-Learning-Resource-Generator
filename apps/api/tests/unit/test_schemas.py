import pytest
from app.schemas.learner_profile import LearnerProfileSchema, SkillLevel, LearningFormat

def test_learner_profile_validation():
    # Valid profile
    profile = LearnerProfileSchema(
        subject="Python",
        goal="Learn back-end",
        current_level=SkillLevel.beginner,
        deadline_days=30,
        daily_hours=2.0,
        known_topics=["variables", "loops"],
        weak_topics=["classes", "decorators"]
    )
    assert profile.subject == "Python"
    assert profile.total_available_hours == 60.0

def test_learner_profile_overlap_validation():
    # Overlapping topics should fail
    with pytest.raises(ValueError):
        LearnerProfileSchema(
            subject="Python",
            goal="Learn back-end",
            current_level=SkillLevel.beginner,
            deadline_days=30,
            daily_hours=2.0,
            known_topics=["variables", "loops", "classes"],
            weak_topics=["classes", "decorators"] # "classes" overlaps
        )
