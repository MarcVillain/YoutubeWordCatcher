import logging

_logger = logging.getLogger("ywc")


def setup(verbose):
    # Set logging level
    log_level = logging.DEBUG if verbose else logging.INFO
    _logger.setLevel(log_level)

    # Enable logging in stdout
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(log_level)
    _logger.addHandler(stream_handler)


def info(*args, **kwargs):
    _logger.info(*args, **kwargs)


def error(*args, **kwargs):
    _logger.error(*args, **kwargs)


def debug(*args, **kwargs):
    _logger.debug(*args, **kwargs)
