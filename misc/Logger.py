import logging
import inspect
import sys

class Logger:
    _logger_instance = None
    _ui_logger_instance = None
    _ui_terminal = None

    @staticmethod
    def _initialize_logger():
        """Initializes the logger with multiple handlers."""
        logger = logging.getLogger("Logger")
        logger.setLevel(logging.DEBUG)

        # Avoid adding handlers multiple times
        if not logger.hasHandlers():
            # Console handler (built-in terminal)
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.DEBUG)
            console_formatter = logging.Formatter('%(asctime)s - [%(levelname)s] %(message)s', datefmt='%H:%M:%S')
            console_handler.setFormatter(console_formatter)
            logger.addHandler(console_handler)

        return logger

    @staticmethod
    def _initialize_ui_logger():
        """Initializes the UI logger with custom handler."""
        ui_logger = logging.getLogger("UILogger")
        ui_logger.setLevel(logging.DEBUG)

        # Avoid adding handlers multiple times
        if not ui_logger.hasHandlers():
            # Custom UI handler
            ui_handler = UIHandler()
            ui_handler.setLevel(logging.DEBUG)
            ui_formatter = logging.Formatter('%(asctime)s - [%(levelname)s] %(message)s', datefmt='%H:%M:%S')
            ui_handler.setFormatter(ui_formatter)
            ui_logger.addHandler(ui_handler)

        return ui_logger

    @classmethod
    def get_logger(cls):
        """Returns the singleton logger instance for terminal."""
        if cls._logger_instance is None:
            cls._logger_instance = cls._initialize_logger()
        return cls._logger_instance

    @classmethod
    def get_ui_logger(cls):
        """Returns the singleton logger instance for UI."""
        if cls._ui_logger_instance is None:
            cls._ui_logger_instance = cls._initialize_ui_logger()
        return cls._ui_logger_instance

    @staticmethod
    def _get_caller_info():
        """Fetches the caller's file and line number."""
        frame = inspect.stack()[2]
        filename = frame.filename.split("/")[-1]  # Extract file name
        line_number = frame.lineno
        return f"{filename}:{line_number}"

    @staticmethod
    def console(message, source=None, level="info"):
        """Logs a message to the built-in terminal."""
        logger = Logger.get_logger()
        caller_info = Logger._get_caller_info()
        source_info = source if source else caller_info
        log_function = getattr(logger, level.lower(), logger.info)
        log_function(f"{source_info} - {message}")

    @staticmethod
    def ui(message, source=None, level="info"):
        """Logs a message to the custom UI."""
        ui_logger = Logger.get_ui_logger()
        caller_info = Logger._get_caller_info()
        source_info = source if source else caller_info
        log_function = getattr(ui_logger, level.lower(), ui_logger.info)
        log_function(f"{source_info} - {message}", extra={'to_ui': True})


class UIHandler(logging.Handler):
    """Custom handler to simulate logging to a UI."""
    def emit(self, record):
        msg = self.format(record)
        # Only emit to the UI if `to_ui` is set to True
        if getattr(record, 'to_ui', False):
            if Logger._ui_terminal:
                Logger._ui_terminal.display(msg)
            else:
                print(f"UI NOT CONNECTED: {msg}")
