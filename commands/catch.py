"""
Extract clips of youtube videos where a word is pronounced
"""

import argparse
import os
import uuid

from moviepy.video.compositing.concatenate import concatenate_videoclips
from moviepy.video.io.VideoFileClip import VideoFileClip

from utils import youtube, config, io, logger, subtitles, editor
from utils.helpers import str_to_sec


class CatchConfig:
    def __init__(self, **kwargs):
        # General
        self.channel_name = kwargs.get("channel_name", "")
        self.word_to_extract = kwargs.get("word_to_extract", "")

        # Youtube
        self.api_key = kwargs.get("api_key", "")

        # Folders
        self.output_folder = kwargs.get("output_folder", "")
        self.data_folder = kwargs.get("data_folder", os.path.join(self.output_folder, "data"))
        self.download_folder = kwargs.get("download_folder", os.path.join(self.output_folder, "download"))
        self.build_folder = kwargs.get("build_folder", os.path.join(self.output_folder, "build"))

        # Clips settings
        self.max_length = kwargs.get("max_length", 1.5)
        self.start_delay = kwargs.get("start_delay", -0.25)
        self.end_delay = kwargs.get("end_delay", 0.75)

        # Switches
        self.do_output_data = kwargs.get("do_output_data", True)
        self.do_text_overlay = kwargs.get("do_text_overlay", True)


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
    if data:
        logger.info("Use saved value")
        return data
    if not write:
        return data

    return _write_saved_data(conf, path, func)


def _extract_video_data(conf, video_id):
    logger.info("Extract video data")
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
    logger.info("Extract video clips")

    # Check if there is something to extract
    if len(video_data.get("timestamps", [])) == 0:
        return []

    # Download video
    with youtube.download(video_id, conf.download_folder, subtitles=False) as dl:
        clips = []

        if not dl["video_file"]["exists"]:
            logger.error("No video file found")
            return clips

        video_clip = VideoFileClip(dl["video_file"]["path"])
        try:
            timestamps = video_data.get("timestamps", [])
            for i, (start, _, end) in enumerate(timestamps):
                clip_pos = str(i + 1).rjust(len(str(timestamps)))
                logger.info(f"Extract video clip ({clip_pos}/{len(timestamps)})")

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


def _clip_list(videos):
    # REMOVE ME: [:50]
    for video in videos[:50]:
        if len(video["data"]["clips"]) > 0:
            for pos, clip in enumerate(video["data"]["clips"]):
                yield video, clip, pos


def _build_final_video(conf, videos):
    video_clips = []
    total = sum(1 for _ in _clip_list(videos))

    for counter, (video, clip, pos) in enumerate(_clip_list(videos)):
        video_id = video["id"]["videoId"]
        pos_log = str(pos + 1)
        clips_count_log = str(len(video["data"]["clips"]))
        counter_log = str(counter + 1).rjust(len(str(total)))
        logger.info(f"Build final clip (video {video_id}: {pos_log}/{clips_count_log}) (global: {counter_log}/{total})")

        video_clip = VideoFileClip(clip)
        if conf.do_text_overlay:
            video_clip = editor.add_info_overlay(video_clip, video, pos, counter, total)
        video_clips.append(video_clip)

    logger.info(f"Concatenate all clips for final video")
    final_clip = concatenate_videoclips(video_clips, method="compose")
    final_clip_file_path = os.path.join(
        conf.output_folder, f"{conf.channel_name}_{conf.word_to_extract}_{str(uuid.uuid4())[:6]}.mp4"
    )
    final_clip.write_videofile(final_clip_file_path)


def run(args):
    conf = config.read(args.config, "catch", CatchConfig)

    logger.prefix = "> "

    channel_id = _read_saved_data(conf, "channel_id", lambda: youtube.get_channel_id(conf.api_key, conf.channel_name))
    videos = _read_saved_data(conf, "videos", lambda: youtube.get_videos(conf.api_key, channel_id))

    videos_len = len(videos)
    for i in range(videos_len):
        video_id = videos[i]["id"]["videoId"]

        pos_log = str(i + 1).rjust(len(str(videos_len)))
        logger.prefix = f"({pos_log}/{videos_len}) {video_id} >> "

        logger.info("Retrieve video data")
        video_saved_data_path = os.path.join("videos", video_id)
        video_data = _read_saved_data(conf, video_saved_data_path, lambda: None, write=False)

        if video_data is None:
            video_data = _extract_video_data(conf, video_id)
            _write_saved_data(conf, video_saved_data_path, lambda: video_data)

        if video_data.get("clips", None) is None:
            video_data["clips"] = _extract_video_clips(conf, video_id, video_data)
            _write_saved_data(conf, video_saved_data_path, lambda: video_data)

        videos[i]["data"] = video_data

        # REMOVE ME: next two lines
        if i == 50:
            break

    logger.prefix = "> "

    _build_final_video(conf, videos)


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
