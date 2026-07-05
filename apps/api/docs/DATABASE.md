# Database Design

## PostgreSQL & Alembic
- The database is PostgreSQL.
- `pgvector` extension is enabled for future semantic search on `transcript_chunks`.
- All tables use `UUID` for primary keys.
- Timestamps (`created_at`, `updated_at`) are timezone-aware.

## Schema Overview
- `users`: Standard user accounts.
- `conversations` / `messages`: Chat history for the interview phase.
- `learner_profiles`: Structured goals, constraints, and preferences extracted from chat.
- `search_sessions` / `search_plans`: Generated search strategies based on profiles.
- `resources`: Metadata for educational content (e.g., YouTube videos).
- `resource_metrics`: Engagement stats (views, likes).
- `transcripts` / `transcript_chunks`: Chunked text with `pgvector` embeddings.
- `recommendations`: Final ranked suggestions presented to the user.

## Migration Commands
- Generate migration: `alembic revision --autogenerate -m "Migration message"`
- Upgrade database: `alembic upgrade head`
- Downgrade database: `alembic downgrade -1`
