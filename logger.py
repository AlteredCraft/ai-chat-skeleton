"""
Logging module with support for different log levels.
Log level can be configured via LOG_LEVEL environment variable.
"""
import os
import sys
from datetime import datetime
from enum import IntEnum


class LogLevel(IntEnum):
    """Log level enumeration."""
    DEBUG = 0
    INFO = 1
    WARN = 2
    ERROR = 3


class Logger:
    """Simple logger with support for different log levels."""

    def __init__(self, name: str = "app"):
        self.name = name
        self._level = self._get_log_level_from_env()

    def _get_log_level_from_env(self) -> LogLevel:
        """Get log level from LOG_LEVEL environment variable."""
        level_str = os.getenv("LOG_LEVEL", "INFO").upper()
        level_map = {
            "DEBUG": LogLevel.DEBUG,
            "INFO": LogLevel.INFO,
            "WARN": LogLevel.WARN,
            "WARNING": LogLevel.WARN,
            "ERROR": LogLevel.ERROR,
        }
        return level_map.get(level_str, LogLevel.INFO)

    def _log(self, level: LogLevel, level_name: str, message: str, **kwargs):
        """Internal logging method."""
        if level < self._level:
            return

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] [{level_name}] [{self.name}] {message}"

        # Add any additional key-value pairs
        if kwargs:
            extras = " ".join(f"{k}={v}" for k, v in kwargs.items())
            log_message += f" | {extras}"

        # Error and warn go to stderr, info and debug go to stdout
        output = sys.stderr if level >= LogLevel.WARN else sys.stdout
        print(log_message, file=output)

    def debug(self, message: str, **kwargs):
        """Log debug message."""
        self._log(LogLevel.DEBUG, "DEBUG", message, **kwargs)

    def info(self, message: str, **kwargs):
        """Log info message."""
        self._log(LogLevel.INFO, "INFO", message, **kwargs)

    def warn(self, message: str, **kwargs):
        """Log warning message."""
        self._log(LogLevel.WARN, "WARN", message, **kwargs)

    def warning(self, message: str, **kwargs):
        """Alias for warn."""
        self.warn(message, **kwargs)

    def error(self, message: str, **kwargs):
        """Log error message."""
        self._log(LogLevel.ERROR, "ERROR", message, **kwargs)

    def set_level(self, level: LogLevel | str):
        """Set the log level."""
        if isinstance(level, str):
            level_map = {
                "DEBUG": LogLevel.DEBUG,
                "INFO": LogLevel.INFO,
                "WARN": LogLevel.WARN,
                "WARNING": LogLevel.WARN,
                "ERROR": LogLevel.ERROR,
            }
            level = level_map.get(level.upper(), LogLevel.INFO)
        self._level = level

    def get_level(self) -> LogLevel:
        """Get current log level."""
        return self._level


# Create a default logger instance
logger = Logger()
