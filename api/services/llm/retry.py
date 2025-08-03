from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from google.api_core.exceptions import ResourceExhausted, ServiceUnavailable, InternalServerError

retry_strategy = retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(
        multiplier=1, 
        min=4, 
        max=50
    ),
    retry=retry_if_exception_type((ResourceExhausted, ServiceUnavailable, InternalServerError)),
    reraise=True
)

def is_retryable_error(e):
    return isinstance(e, (ResourceExhausted, ServiceUnavailable, InternalServerError))