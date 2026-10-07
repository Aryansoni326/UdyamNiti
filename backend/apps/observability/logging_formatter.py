"""
Structured JSON Log Formatter with Sensitive Data Redaction.
Outputs standard machine-parseable JSON logs containing:
- timestamp (ISO-8601 UTC)
- level (INFO, WARNING, ERROR, etc.)
- logger (module name)
- trace_id (propagated from active request context)
- message (redacted for passwords, secrets, and raw file bytes)
- execution context (filename, lineno, funcName)
- optional structured metadata
"""
import json
import logging
import re
from datetime import datetime
from typing import Any, Dict
from .context import get_current_trace_id, get_current_user_id


class StructuredJSONFormatter(logging.Formatter):
    """
    Format log records as structured single-line JSON with automatic secret masking.
    """

    SENSITIVE_KEY_PATTERNS = [
        re.compile(r'(?i)(password|secret|token|api_key|authorization|bearer|auth|file_bytes|raw_content|cookie)')
    ]

    MASK_VALUE = "[REDACTED]"

    def format(self, record: logging.LogRecord) -> str:
        # 1. Base log structure
        log_obj: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": self._sanitize_message(record.getMessage()),
            "trace_id": getattr(record, 'trace_id', None) or get_current_trace_id(),
            "module": record.module,
            "func_name": record.funcName,
            "line_no": record.lineno,
        }

        # 2. Add user context if present
        user_id = get_current_user_id()
        if user_id:
            log_obj["user_id"] = user_id

        # 3. Add exception info if present
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)

        # 4. Attach any extra dictionary attributes passed to logger
        for key, val in record.__dict__.items():
            if key not in (
                'args', 'asctime', 'created', 'exc_info', 'exc_text', 'filename',
                'funcName', 'id', 'levelname', 'levelno', 'lineno', 'module',
                'msecs', 'message', 'msg', 'name', 'pathname', 'process',
                'processName', 'relativeCreated', 'stack_info', 'thread', 'threadName'
            ):
                if isinstance(val, (str, int, float, bool, list, dict)) or val is None:
                    log_obj[key] = self._sanitize_value(key, val)

        return json.dumps(log_obj, ensure_ascii=False)

    def _sanitize_message(self, message: str) -> str:
        """Masks authorization headers and inline secrets within log messages."""
        if not isinstance(message, str):
            return str(message)
        # Mask Bearer tokens
        sanitized = re.sub(r'(?i)(bearer\s+)[a-zA-Z0-9_\-\.]{10,}', r'\1[REDACTED_TOKEN]', message)
        # Mask inline passwords
        sanitized = re.sub(r'(?i)(password[\'"\s:=]+)[^\s,}\'"]+', r'\1[REDACTED_PASSWORD]', sanitized)
        # Mask API keys
        sanitized = re.sub(r'(?i)(api[_-]?key[\'"\s:=]+)[^\s,}\'"]+', r'\1[REDACTED_KEY]', sanitized)
        # Truncate any overly long messages to prevent log flooding
        if len(sanitized) > 2000:
            sanitized = sanitized[:2000] + "... [TRUNCATED_OVERSIZED_LOG]"
        return sanitized

    def _sanitize_value(self, key: str, value: Any) -> Any:
        """Recursively redacts dictionary values with sensitive keys."""
        if any(p.search(key) for p in self.SENSITIVE_KEY_PATTERNS):
            return self.MASK_VALUE

        if isinstance(value, dict):
            return {k: self._sanitize_value(k, v) for k, v in value.items()}
        elif isinstance(value, list):
            return [self._sanitize_value(key, item) for item in value]
        elif isinstance(value, str) and len(value) > 1000:
            return value[:1000] + "... [TRUNCATED]"
        return value
