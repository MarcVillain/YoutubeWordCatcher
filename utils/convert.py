import re


def str_to_sec(timestamp):
    """
    format: HH:mm:ss.xxx
    """
    parts = re.split("[:.]", timestamp)
    return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2]) + (float(parts[3]) / 1000)


def sec_to_str(sec):
    """
    format: HH:mm:ss.xxx
    """
    hours = int(sec / 3600)
    sec %= 3600
    minutes = int(sec / 60)
    sec %= 60
    secs = int(sec / 1)
    sec %= 1
    millisecs = secs
    return f"{hours}:{minutes}:{secs}.{millisecs}"
