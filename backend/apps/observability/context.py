"""
Context variable storage for distributed request trace IDs and context metadata.
Allows any function, logger, or database query to access the active trace ID
without passing request objects through every layer of the call stack.
"""
import uuid
from contextvars import ContextVar
from typing import Optional

_trace_id_ctx: ContextVar[Optional[str]] = ContextVar('udyamniti_trace_id', default=None)
_user_id_ctx: ContextVar[Optional[str]] = ContextVar('udyamniti_user_id', default=None)


def get_current_trace_id() -> str:
    """Returns the active request trace ID or generates an ephemeral one."""
    val = _trace_id_ctx.get()
    if not val:
        val = f"trc_{uuid.uuid4().hex[:12]}"
        _trace_id_ctx.set(val)
    return val


def set_current_trace_id(trace_id: str) -> None:
    """Sets the active request trace ID for this execution context."""
    _trace_id_ctx.set(trace_id)


def clear_current_trace_id() -> None:
    """Clears the trace ID context."""
    _trace_id_ctx.set(None)


def get_current_user_id() -> Optional[str]:
    return _user_id_ctx.get()


def set_current_user_id(user_id: Optional[str]) -> None:
    _user_id_ctx.set(user_id)
