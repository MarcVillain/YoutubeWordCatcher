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


def info(msg, prefix="> ", *args, **kwargs):
    _logger.info(prefix + msg, *args, **kwargs)


def error(msg, prefix="> ", *args, **kwargs):
    _logger.error(prefix + msg, *args, **kwargs)


def debug(msg, prefix="> ", *args, **kwargs):
    _logger.debug(prefix + msg, *args, **kwargs)
