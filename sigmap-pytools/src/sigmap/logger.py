import logging


class ColorFormatter(logging.Formatter):
    """
    Custom logging formatter that adds ANSI color codes to log messages.
    
    Provides color-coded output for different log levels to improve readability
    in terminal-based logging.
    """
    COLORS = {
        logging.DEBUG: "\033[37m",   # White
        logging.INFO: "\033[32m",    # Green
        logging.WARNING: "\033[33m", # Yellow
        logging.ERROR: "\033[31m",   # Red
        logging.CRITICAL: "\033[41m" # Red background
    }
    RESET = "\033[0m"

    def format(self, record):
        """
        Format log record with color coding.

        Parameters
        ----------
        record : logging.LogRecord
            Log record to format

        Returns
        -------
        str
            Formatted log message with ANSI color codes
        """
        color = self.COLORS.get(record.levelno, self.RESET)
        message = super().format(record)
        return f"{color}{message}{self.RESET}"

handler = logging.StreamHandler()
formatter = ColorFormatter("[%(asctime)s] %(levelname)s:%(name)s: %(message)s", "%H:%M:%S")
handler.setFormatter(formatter)

logging.basicConfig(level=logging.DEBUG, handlers=[handler])
