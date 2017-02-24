
import logging
import types
import textwrap

LOG_WIDTH = 80


def log_textWithIndent(self, text):
    tempTextwrap = textwrap.wrap(text, LOG_WIDTH, subsequent_indent='(cont) ')
    for i in tempTextwrap: self.info(i)


def log_newline(self, how_many_lines=1):
    # Switch handler, output a blank line
    self.removeHandler(self.console_handler)
    self.addHandler(self.blank_handler)
    for i in range(how_many_lines):
        self.info('')

    # Switch back
    self.removeHandler(self.blank_handler)
    self.addHandler(self.console_handler)


def create_logger(name):
    # Create a handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(logging.Formatter(fmt="%(name)s %(levelname)s [%(asctime)s]\t: %(message)s"))

    # Create a "blank line" handler
    blank_handler = logging.StreamHandler()
    blank_handler.setLevel(logging.DEBUG)
    blank_handler.setFormatter(logging.Formatter(fmt=''))

    # Create a logger, with the previously-defined handler
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(console_handler)

    # Save some data and add a method to logger object
    logger.console_handler = console_handler
    logger.blank_handler = blank_handler
    logger.newline = types.MethodType(log_newline, logger)

    return logger
