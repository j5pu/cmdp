"""Color Logger Package."""
__all__ = ("ColorLogger",)

import logging
from typing import ClassVar


class ColorLogger(logging.Formatter):
    """Color logger class."""
    black = "\x1b[30m"
    blue = "\x1b[34m"
    cyan = "\x1b[36m"
    green = "\x1b[32m"
    grey = "\x1b[38;21m"
    magenta = "\x1b[35m"
    red = "\x1b[31;21m"
    red_bold = "\x1b[31;1m"
    reset = "\x1b[0m"
    white = "\x1b[37m"
    yellow = "\x1b[33;21m"
    fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"
    vertical = f"{red}|{reset} "
    FORMATS: ClassVar[dict[int, str]] = {
        logging.DEBUG: grey + fmt + reset,
        logging.INFO: f"{cyan}%(levelname)8s{reset} {vertical}"
                      f"{cyan}%(name)s{reset} {vertical}"
                      f"{cyan}%(filename)s{reset}:{cyan}%(lineno)d{reset} {vertical}"
                      f"{green}%(extra)s{reset} {vertical}"
                      f"{cyan}%(message)s{reset}",
        logging.WARNING: f"{yellow}%(levelname)8s{reset} {vertical}"
                         f"{yellow}%(name)s{reset} {vertical}"
                         f"{yellow}%(filename)s{reset}:{yellow}%(lineno)d{reset} {vertical}"
                         f"{green}%(repo)s{reset} {vertical}"
                         f"{yellow}%(message)s{reset}",
        logging.ERROR: red + fmt + reset,
        logging.CRITICAL: red_bold + fmt + reset,
    }

    def format(self, record: logging.LogRecord):  # noqa: A003
        """Format log."""
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        if "extra" not in record.__dict__:
            record.__dict__["extra"] = ""
        return formatter.format(record)

    @classmethod
    def logger(cls, name: str = __name__) -> logging.Logger:
        """Get logger.

        Examples:
            >>> from nodeps import ColorLogger
            >>> from nodeps import NODEPS_PROJECT_NAME
            >>>
            >>> lo = ColorLogger.logger(NODEPS_PROJECT_NAME)
            >>> lo.info("hola", extra=dict(extra="bapy"))
            >>> lo.info("hola")

        Args:
            name: logger name

        Returns:
            logging.Logger
        """
        l = logging.getLogger(name)
        l.propagate = False
        l.setLevel(logging.DEBUG)
        if l.handlers:
            l.handlers[0].setLevel(logging.DEBUG)
            l.handlers[0].setFormatter(cls())
        else:
            handler = logging.StreamHandler()
            handler.setLevel(logging.DEBUG)
            handler.setFormatter(cls())
            l.addHandler(handler)
        return l

