from fastapi import Request, FastAPI
from fastapi.responses import JSONResponse
import uuid

class BaseAPIException(Exception):
    def __init__(self, message: str, code: str = "INTERNAL_ERROR", status_code: int = 500):
        self.message = message
        self.code = code
        self.status_code = status_code

class ProfileNotFoundError(BaseAPIException):
    def __init__(self, message: str = "Learner profile could not be found."):
        super().__init__(message=message, code="PROFILE_NOT_FOUND", status_code=404)

class ConversationNotFoundError(BaseAPIException):
    def __init__(self, message: str = "Conversation could not be found."):
        super().__init__(message=message, code="CONVERSATION_NOT_FOUND", status_code=404)

class SearchPlanGenerationError(BaseAPIException):
    def __init__(self, message: str = "Failed to generate search plan."):
        super().__init__(message=message, code="SEARCH_PLAN_GENERATION_ERROR", status_code=500)

class InvalidProfileStateError(BaseAPIException):
    def __init__(self, message: str = "Invalid profile state."):
        super().__init__(message=message, code="INVALID_PROFILE_STATE", status_code=400)

class ExternalProviderError(BaseAPIException):
    def __init__(self, message: str = "External provider failed."):
        super().__init__(message=message, code="EXTERNAL_PROVIDER_ERROR", status_code=502)

class ConfigurationError(BaseAPIException):
    def __init__(self, message: str = "Service configuration error."):
        super().__init__(message=message, code="CONFIGURATION_ERROR", status_code=500)

def setup_exception_handlers(app: FastAPI):
    @app.exception_handler(BaseAPIException)
    async def custom_exception_handler(request: Request, exc: BaseAPIException):
        request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "request_id": request_id
                }
            }
        )
    
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
        # In production, we'd log the traceback here instead of returning it
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "An unexpected error occurred.",
                    "request_id": request_id
                }
            }
        )
