# API Endpoints

## Health
- `GET /api/health`: Basic liveness probe.
- `GET /api/health/ready`: Deep health check verifying database connectivity.

## Chat
- `POST /api/chat/message`: Sends a message to the Gemini interview agent and returns the response. Maintains conversational context.

## Profiles
- `POST /api/profiles/extract`: Analyzes conversation history and uses Gemini Structured Outputs to extract and save a `LearnerProfileSchema`.

## Search Planning
- `POST /api/search-plan/generate`: Takes a `profile_id`, retrieves the profile from the database, and uses Gemini to generate a structured `SearchPlan`.
