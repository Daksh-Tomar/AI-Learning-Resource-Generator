class ProviderError(Exception):
    """Base class for all provider-related errors."""
    pass

class ProviderTimeoutError(ProviderError):
    pass

class ProviderServerError(ProviderError):
    pass

class InvalidApiKeyError(ProviderError):
    pass

class QuotaExceededError(ProviderError):
    pass

class ResourceNotFoundError(ProviderError):
    pass

class TranscriptUnavailableError(ProviderError):
    pass

class CommentsDisabledError(ProviderError):
    pass
