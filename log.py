from loguru import logger
import sys

def exclude_log_levels(record):
    excluded_levels = ["DEBUG", "TRACE"]  # List of log levels to exclude
    return record["level"].name not in excluded_levels

logger.remove()  # Remove the default output
logger.add(
    "app.log",
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
    rotation="1 week",  
    retention="2 weeks",
    compression="zip",  
    serialize=True,  
    backtrace=True,
    filter=exclude_log_levels,
)

logger.add(
    sys.stdout,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
    level="INFO",
    colorize=True,
)