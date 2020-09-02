"""
Extract clips of youtube videos where a word is pronounced
"""

import argparse
import os

from moviepy.video.io.VideoFileClip import VideoFileClip

from utils import youtube, config, io, logger, subtitles
from utils.helpers import str_to_sec


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


def _write_saved_data(conf, path, func):
    full_path = os.path.join(conf.data_folder, f"{path}.yaml")
    data = func()
    io.dump_yaml(full_path, data)
    return data


def _read_saved_data(conf, path, func, write=True):
    if not conf.do_output_data:
        return None

    full_path = os.path.join(conf.data_folder, f"{path}.yaml")
    data = io.load_yaml(full_path)
    if data or not write:
        return data

    return _write_saved_data(conf, path, func)


def _extract_video_data(conf, video_id):
    # Download subtitles
    with youtube.download(video_id, conf.download_folder, video=False) as dl:
        data = {
            "id": video_id,
            "subtitles_file": dl["subtitles_file"],
            "video_file": dl["video_file"],
        }

        if not dl["subtitles_file"]["exists"]:
            logger.error("No subtitles found")
            return data

        # Extract data
        subtitles_data = subtitles.extract_data(dl["subtitles_file"]["path"], conf.word_to_extract)

        return {
            **data,
            **subtitles_data,
        }


def _extract_video_clips(conf, video_id, video_data):
    # Check if there is something to extract
    if len(video_data.get("timestamps", [])) == 0:
        return []

    # Download video
    with youtube.download(video_id, conf.download_folder, subtitles=False) as dl:
        clips = []

        if not dl["video_file"]["path"]:
            logger.error("No video found")
            return clips

        video_clip = VideoFileClip(dl["video_file"]["path"])
        try:
            for i, (start, _, end) in enumerate(video_data.get("timestamps", [])):
                # Get absolute start and end
                video_start = str_to_sec(start) + conf.start_delay
                video_end = str_to_sec(end) + conf.end_delay
                # Prevent clip from being too long
                if video_end - video_start > conf.max_length:
                    video_end = video_start + conf.max_length
                # Extract clip
                subclip = video_clip.subclip(video_start, video_end)

                # Create destination
                subclip_file_path = os.path.join(conf.output_folder, "clips", video_id, f"{i}.mp4")
                os.makedirs(os.path.dirname(subclip_file_path), exist_ok=True)

                # Save clip
                subclip.write_videofile(subclip_file_path)
                clips.append(subclip_file_path)
        finally:
            video_clip.close()

        return clips


def run(args):
    conf = config.read(args.config, "catch", CatchConfig)

    channel_id = _read_saved_data(conf, "channel_id", lambda: youtube.get_channel_id(conf.api_key, conf.channel_name))
    videos = _read_saved_data(conf, "videos", lambda: youtube.get_videos(conf.api_key, channel_id))

    for i in range(len(videos)):
        video_id = videos[i]["id"]["videoId"]

        video_saved_data_path = os.path.join("videos", video_id)
        video_data = _read_saved_data(conf, video_saved_data_path, lambda: None, write=False)

        if video_data is None:
            video_data = _extract_video_data(conf, video_id)
            _write_saved_data(conf, video_saved_data_path, lambda: video_data)

        if video_data.get("clips", None) is None:
            video_data["clips"] = _extract_video_clips(conf, video_id, video_data)
            _write_saved_data(conf, video_saved_data_path, lambda: video_data)

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
