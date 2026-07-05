# Application Architecture

## Layers
The application follows a standard layered architecture:

- **Core (`app/core/`)**: Cross-cutting concerns like Configuration, Logging, Database Session setup, and Exceptions.
- **API (`app/api/`)**: FastAPI routers handling HTTP requests, input validation (via Schemas), and delegating to Services.
- **Models (`app/models/`)**: SQLAlchemy declarative models mapping to PostgreSQL tables.
- **Schemas (`app/schemas/`)**: Pydantic models for request/response validation and internal data transfer.
- **Services (`app/services/`)**: Business logic (e.g., generating search plans, calculating scores, communicating with Gemini).
- **Repositories (`app/repositories/`)**: Data access layer encapsulating SQLAlchemy queries.

## Data Flow
1. Client sends request to `/api/routes`.
2. Router validates payload against `app/schemas`.
3. Router delegates task to `app/services`.
4. Service performs logic (e.g., calls Gemini) and interacts with `app/repositories`.
5. Repository queries/mutates PostgreSQL via `app/models`.
6. Results flow back to Router and are serialized as JSON.
