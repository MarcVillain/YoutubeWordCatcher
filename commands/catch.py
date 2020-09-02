"""
Extract clips of youtube videos where a word is pronounced
"""

import argparse
import os

from utils import youtube, config, io


class CatchConfig:
    def __init__(self, **kwargs):
        self.channel_name = kwargs.get("channel_name", "")
        self.word_to_extract = kwargs.get("word_to_extract", "")

        self.api_key = kwargs.get("api_key", "")

        self.output_folder = kwargs.get("output_folder", "")
        self.do_output_data = kwargs.get("do_output_data", True)
        self.data_folder = kwargs.get("data_folder", os.path.join(self.output_folder, "data"))

        self.max_length = kwargs.get("max_length", 1.5)
        self.start_delay = kwargs.get("start_delay", -0.25)
        self.end_delay = kwargs.get("end_delay", 0.75)


def get_saved_data(conf, path, func):
    path = f"{path}.yaml"
    if not conf.do_output_data:
        return None

    full_path = os.path.join(conf.data_folder, path)
    data = io.load_yaml(full_path)
    if data:
        return data

    new_data = func()
    io.dump_yaml(full_path, new_data)

    return new_data


def run(args):
    conf = config.read(args.config, "catch", CatchConfig)
    channel_id = get_saved_data(conf, "channel_id", lambda: youtube.get_channel_id(conf.api_key, conf.channel_name))
    videos = get_saved_data(conf, "videos", lambda: youtube.get_videos(conf.api_key, channel_id))
    # Get channel video list
    # Extract timestamps
    # Extract clips
    # Build final video
    pass


def parse(prog, args):
    parser = argparse.ArgumentParser(prog=prog, description=__doc__)
    parser.add_argument(
        "-c",
        "--config",
        metavar="FILE",
        default="config.ini",
        help="ini configuration file",
    )
    return parser.parse_args(args)
