import logging
import uuid
import time
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("learnlens")

def setup_logging(log_level: str = "INFO"):
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    logger.addHandler(handler)
    
    # Prevent duplicate logs if setup is called multiple times
    logger.propagate = False

class RequestContextLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id
        
        start_time = time.time()
        
        # We don't log the full request body to avoid logging secrets, 
        # but we log the path and method.
        logger.info(f"Request started: {request.method} {request.url.path} [req_id={request_id}]")
        
        try:
            response = await call_next(request)
            process_time_ms = (time.time() - start_time) * 1000
            response.headers["X-Request-ID"] = request_id
            logger.info(
                f"Request completed: {request.method} {request.url.path} "
                f"- Status: {response.status_code} "
                f"- Duration: {process_time_ms:.2f}ms [req_id={request_id}]"
            )
            return response
        except Exception as e:
            process_time_ms = (time.time() - start_time) * 1000
            logger.error(
                f"Request failed: {request.method} {request.url.path} "
                f"- Error: {str(e)} "
                f"- Duration: {process_time_ms:.2f}ms [req_id={request_id}]",
                exc_info=True
            )
            raise
