"""
Structured logging for the new architecture
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict, Optional
import uuid


class StructuredLogger:
    """
    Structured JSON logger with correlation ID tracking
    """

    def __init__(self, service_name: str):
        self.service_name = service_name
        self.logger = logging.getLogger(service_name)
        self.setup_handlers()

    def setup_handlers(self):
        """Configure JSON logging"""
        handler = logging.StreamHandler()
        formatter = logging.Formatter("%(message)s")
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def log_event(
        self,
        event: str,
        severity: str = "info",
        correlation_id: Optional[str] = None,
        user_id: Optional[str] = None,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        duration_ms: Optional[float] = None,
        error_code: Optional[str] = None,
        message: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None,
    ):
        """
        Log a structured event

        Args:
            event: Event name
            severity: 'info', 'warning', 'error', 'debug'
            correlation_id: Request correlation ID
            user_id: Acting user ID
            entity_type: Type of entity (protocol, execution, etc.)
            entity_id: ID of entity
            duration_ms: Duration in milliseconds
            error_code: Error code if applicable
            message: Human-readable message
            extra: Additional context as dict
        """
        if correlation_id is None:
            correlation_id = str(uuid.uuid4())

        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "service": self.service_name,
            "event": event,
            "severity": severity,
            "correlation_id": correlation_id,
        }

        if user_id:
            log_entry["user_id"] = user_id
        if entity_type:
            log_entry["entity_type"] = entity_type
        if entity_id:
            log_entry["entity_id"] = entity_id
        if duration_ms is not None:
            log_entry["duration_ms"] = round(duration_ms, 2)
        if error_code:
            log_entry["error_code"] = error_code
        if message:
            log_entry["message"] = message
        if extra:
            log_entry.update(extra)

        log_method = getattr(self.logger, severity, self.logger.info)
        log_method(json.dumps(log_entry))

        return correlation_id

    def info(self, event: str, **kwargs):
        """Log info event"""
        return self.log_event(event, severity="info", **kwargs)

    def warning(self, event: str, **kwargs):
        """Log warning event"""
        return self.log_event(event, severity="warning", **kwargs)

    def error(self, event: str, **kwargs):
        """Log error event"""
        return self.log_event(event, severity="error", **kwargs)

    def debug(self, event: str, **kwargs):
        """Log debug event"""
        return self.log_event(event, severity="debug", **kwargs)


# Global logger instance
logger = StructuredLogger("moove-backend")
