"""
Logging configuration for Windows-MCP server using structlog.
Logs server lifecycle events and tool invocations to the logs folder.
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from functools import wraps
from typing import Callable, Any

import structlog


def setup_logging(log_dir: str = "logs") -> structlog.BoundLogger:
    """
    Configure structlog to output JSON logs to a file in the logs directory.

    Args:
        log_dir: Directory path for log files (relative to project root)

    Returns:
        Configured structlog logger instance
    """
    # Ensure logs directory exists
    log_path = Path(__file__).parent.parent / log_dir
    log_path.mkdir(exist_ok=True)

    # Create log filename with timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d")
    log_file = log_path / f"mcp-server-{timestamp}.log"

    # Configure standard logging for file output
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.INFO)

    # Configure console handler for development
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(logging.WARNING)

    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.handlers = []
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    # Configure structlog
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Create formatter for file output
    formatter = structlog.stdlib.ProcessorFormatter(
        processor=structlog.processors.JSONRenderer(ensure_ascii=False),
        foreign_pre_chain=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
        ],
    )
    file_handler.setFormatter(formatter)

    # Console uses key-value format for readability
    console_formatter = structlog.stdlib.ProcessorFormatter(
        processor=structlog.dev.ConsoleRenderer(colors=False),
        foreign_pre_chain=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
        ],
    )
    console_handler.setFormatter(console_formatter)

    return structlog.get_logger("windows-mcp")


# Global logger instance
logger: structlog.BoundLogger = None


def get_logger() -> structlog.BoundLogger:
    """Get the configured logger instance, initializing if necessary."""
    global logger
    if logger is None:
        logger = setup_logging()
    return logger


def log_tool_call(func: Callable) -> Callable:
    """
    Decorator to log MCP tool invocations.

    Logs tool name, parameters, and result status.
    """

    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        log = get_logger()
        tool_name = func.__name__

        # Log tool invocation
        log.info(
            "tool_invoked",
            tool_name=tool_name,
            parameters=_serialize_params(kwargs)
            if kwargs
            else _serialize_params_from_args(func, args),
        )

        try:
            result = func(*args, **kwargs)
            log.info(
                "tool_completed",
                tool_name=tool_name,
                status="success",
            )
            return result
        except Exception as e:
            log.error(
                "tool_failed",
                tool_name=tool_name,
                status="error",
                error_type=type(e).__name__,
                error_message=str(e),
            )
            raise

    return wrapper


def _serialize_params(params: dict) -> dict:
    """Serialize parameters for logging, handling non-serializable types."""
    result = {}
    for key, value in params.items():
        if isinstance(value, (str, int, float, bool, type(None))):
            result[key] = value
        elif isinstance(value, (list, tuple)):
            result[key] = list(value)
        elif isinstance(value, dict):
            result[key] = _serialize_params(value)
        else:
            result[key] = str(value)
    return result


def _serialize_params_from_args(func: Callable, args: tuple) -> dict:
    """Convert positional args to named params for logging."""
    import inspect

    sig = inspect.signature(func)
    params = list(sig.parameters.keys())
    result = {}
    for i, arg in enumerate(args):
        if i < len(params):
            param_name = params[i]
            if isinstance(arg, (str, int, float, bool, type(None))):
                result[param_name] = arg
            elif isinstance(arg, (list, tuple)):
                result[param_name] = list(arg)
            else:
                result[param_name] = str(arg)
    return result
