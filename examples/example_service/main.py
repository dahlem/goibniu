"""Example FastAPI service for testing API extraction.

This simple service provides a health check endpoint that demonstrates
the API extraction capabilities of Goibniu. Used in integration tests.
"""

__authors__ = ["Dominik Dahlem"]
__status__ = "Development"

from fastapi import FastAPI

app = FastAPI()


@app.get('/ping')
def ping():
    """Health check endpoint.

    Returns:
        dict: Simple pong response

    Example:
        >>> response = ping()
        >>> response['message']
        'pong'

    """
    return {'message': 'pong'}
