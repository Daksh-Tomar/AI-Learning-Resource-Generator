# Phase 0 MVP Scope

## Included in Phase 0 Foundation
- Modular FastAPI Architecture (Core, API, Models, Schemas, Services, Repositories).
- Pydantic v2 schemas for strict data validation (LearnerProfile, SearchPlan).
- Comprehensive SQLAlchemy models using UUIDs and timestamps.
- Alembic migration environment configured and initial migration script created.
- Centralized configuration management using `pydantic-settings`.
- Robust error handling and structured logging middleware.
- Test suite with Pytest covering validation and normalization.
- Database seeding script for local development.

## Excluded from Phase 0 (For Future Phases)
- Full YouTube/External API integration.
- Text embedding generation and semantic similarity search.
- Recommendation algorithms and ranking models.
- Redis caching layer.
- LangGraph and Multi-Agent setups.
- Real-time video transcription.
