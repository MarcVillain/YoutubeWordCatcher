"""
Extract clips of youtube videos where a word is pronounced
"""

import argparse
import os

from utils import youtube, config, io, logger, subtitles


class CatchConfig:
    def __init__(self, **kwargs):
        self.channel_name = kwargs.get("channel_name", "")
        self.word_to_extract = kwargs.get("word_to_extract", "")

        self.api_key = kwargs.get("api_key", "")

        self.output_folder = kwargs.get("output_folder", "")
        self.do_output_data = kwargs.get("do_output_data", True)
        self.data_folder = kwargs.get("data_folder", os.path.join(self.output_folder, "data"))
        self.download_folder = kwargs.get("download_folder", os.path.join(self.output_folder, "download"))

        self.max_length = kwargs.get("max_length", 1.5)
        self.start_delay = kwargs.get("start_delay", -0.25)
        self.end_delay = kwargs.get("end_delay", 0.75)


def _set_saved_data(conf, path, func):
    path = f"{path}.yaml"
    full_path = os.path.join(conf.data_folder, path)
    data = func()
    io.dump_yaml(full_path, data)
    return data


def _get_saved_data(conf, path, func):
    path = f"{path}.yaml"
    if not conf.do_output_data:
        return None

    full_path = os.path.join(conf.data_folder, path)
    data = io.load_yaml(full_path)
    if data:
        return data

    return _set_saved_data(conf, path, func)


def _extract_video_data(conf, video_id):
    data = {}

    # Download subtitles
    with youtube.download(video_id, conf.download_folder, video=False) as (subtitles_file_path, _):
        if not subtitles_file_path:
            logger.error("No subtitles found")
            return data

        data = subtitles.extract_data(subtitles_file_path, conf.word_to_extract)

    return data


def run(args):
    conf = config.read(args.config, "catch", CatchConfig)
    channel_id = _get_saved_data(conf, "channel_id", lambda: youtube.get_channel_id(conf.api_key, conf.channel_name))
    videos = _get_saved_data(conf, "videos", lambda: youtube.get_videos(conf.api_key, channel_id))
    for i in range(len(videos)):
        # Extract video data (time, timestamps, ...)
        if videos[i].get("data", None) is None:
            videos[i]["data"] = _extract_video_data(conf, videos[i]["id"]["videoId"])
            _set_saved_data(conf, "videos", lambda: videos)

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
