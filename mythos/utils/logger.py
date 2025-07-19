import logging
import sys


class ColoredFormatter(logging.Formatter):
    """
    Custom formatter that adds color coding to log messages.
    """
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green  
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
        'RESET': '\033[0m'       # Reset to default
    }
    
    def format(self, record):
        """
        Format the log record with appropriate colors.
        
        Args:
            record: The log record to format.
            
        Returns:
            str: The formatted and colored log message.
        """
        # Get the original formatted message
        formatted_message = super().format(record)
        
        # Get color for this log level
        level_color = self.COLORS.get(record.levelname, '')
        reset_color = self.COLORS['RESET']
        
        # Apply color to the entire message
        return f"{level_color}{formatted_message}{reset_color}"


def get_logger(name: str) -> logging.Logger:
    """
    Configures and returns a logger with the specified name and color coding.
    
    Args:
        name (str): The name of the logger.
    
    Returns:
        logging.Logger: Configured logger instance with color support.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:
        # Console handler for output to stdout
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)

        # Colored formatter for log messages
        formatter = ColoredFormatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)

        logger.addHandler(console_handler)

    return logger 