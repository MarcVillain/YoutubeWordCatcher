import os
import re

import yaml

import config
from logger import Logger


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


def data_file(log_msg, filename, override=False):
    def decorate(func):
        def call(*args, **kwargs):
            Logger.info(log_msg)

            # Pre
            filedir = os.path.join(config.build_dir, "data_save")
            filepath = os.path.join(filedir, f"{filename}.yaml")

            if override:
                try:
                    os.remove(filepath)
                except OSError:
                    pass

            if os.path.exists(filepath):
                with open(filepath, "r+") as file:
                    data = yaml.load(file) or None

                if data is not None:
                    Logger.info("Use saved value")
                    return data
            else:
                os.makedirs(filedir, exist_ok=True)
                with open(filepath, "w"):
                    pass

            # Run
            new_data = func(*args, **kwargs)

            # Post
            with open(filepath, "w+") as file:
                file.write(yaml.dump(new_data))

            # Return
            return new_data

        return call

    return decorate


