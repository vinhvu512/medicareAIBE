# token_context.py

from contextvars import ContextVar

# Define a Context Variable for the current token
current_token: ContextVar[str] = ContextVar('current_token', default=None)
