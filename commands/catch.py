"""
Extract clips of youtube videos where a word is pronounced
"""

import argparse
import os
import uuid

from moviepy.video.compositing.concatenate import concatenate_videoclips
from moviepy.video.io.VideoFileClip import VideoFileClip

from utils import youtube, config, io, logger, subtitles, editor
from utils.convert import str_to_sec


class Config:
    def __init__(self, **kwargs):
        """
        Initialize the configuration.
        :param kwargs: dictionary of key value to set
        """

        """
        General
        """
        # Name of the channel to extract the videos from
        self.channel_name = kwargs.get("channel_name", "")
        # Word to extract from the channel videos
        self.word_to_extract = kwargs.get("word_to_extract", "")

        """
        Youtube
        """
        # Your Youtube API key (https://developers.google.com/youtube/registering_an_application)
        self.api_key = kwargs.get("api_key", "")

        """
        Folders
        """
        # The folder where everything will be extracted
        self.output_folder = kwargs.get("output_folder", "")
        # The sub-folder used for persistent data storage (timestamps, lists, ...)
        self.data_folder = kwargs.get("data_folder", os.path.join(self.output_folder, "data"))
        # The sub-folder used for downloading files
        self.download_folder = kwargs.get("download_folder", os.path.join(self.output_folder, "download"))
        # The sub-folder used for the final video build
        self.build_folder = kwargs.get("build_folder", os.path.join(self.output_folder, "build"))

        """
        Clips settings
        """
        # Maximum length of a clip (in seconds)
        self.max_length = kwargs.get("max_length", 1.5)
        # Shift of the start timestamp of a clip (in seconds)
        self.start_shift = kwargs.get("start_shift", -0.25)
        # Shift of the end timestamp of a clip (in seconds)
        self.end_shift = kwargs.get("end_shift", 0.75)

        """
        Switches
        """
        # Should the program data be outputted?
        self.do_output_data = kwargs.get("do_output_data", True)
        # Should the text overlay be applied?
        self.do_text_overlay = kwargs.get("do_text_overlay", True)
        # Should the downloaded files be deleted?
        self.do_cleanup_downloads = kwargs.get("do_cleanup_downloads", True)
        # Should the video datas be computed even if they already exists?
        self.do_override_video_data = kwargs.get("do_override_video_data", False)
        # Should the clips be generated even if they already exists?
        self.do_override_clips = kwargs.get("do_override_clips", False)
        # Should the clips be generated?
        self.do_generate_clips = kwargs.get("do_generate_clips", True)
        # Should the final video be generated?
        self.do_generate_final_video = kwargs.get("do_generate_final_video", True)
        # Should the videos list data be updated?
        self.do_update_video_data = kwargs.get("do_update_video_data", False)

        """
        Filters
        """
        # Only work with these video ids
        self.filter_videos_ids = kwargs.get("filter_videos_ids", [])

        """
        Thresholds
        """
        # Maximum amount of videos to download, cut and compose
        self.max_videos_amount = kwargs.get("max_videos_amount", 100000)


def _write_saved_data(conf, path, func):
    full_path = os.path.join(conf.data_folder, f"{path}.yaml")
    data = func()

    if not conf.do_output_data:
        return data

    io.dump_yaml(full_path, data)
    return data


def read_saved_data(conf, path, func, write=True, update=False):
    full_path = os.path.join(conf.data_folder, f"{path}.yaml")

    if not update and os.path.exists(full_path):
        logger.info("Load saved value")
        return io.load_yaml(full_path)

    if not write:
        return func()

    return _write_saved_data(conf, path, func)


def _extract_video_data(conf, video_id):
    logger.info("Extract video data")
    # Download subtitles
    with youtube.download(video_id, conf.download_folder, video=False, cleanup=conf.do_cleanup_downloads) as dl:
        if dl is None:
            logger.error("Unable to download subtitles")
            return None

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
        logger.info("No timestamps to extract")
        return []

    # Download video
    with youtube.download(video_id, conf.download_folder, subtitles=False, cleanup=conf.do_cleanup_downloads) as dl:
        clips = []

        if dl is None:
            logger.error("Unable to download video")
            return None

        if not dl["video_file"]["exists"]:
            logger.error("No video file found")
            return clips

        video_clip = VideoFileClip(dl["video_file"]["path"])
        try:
            timestamps = video_data.get("timestamps", [])
            for i, (start, _, end) in enumerate(timestamps):
                clip_pos = str(i + 1).rjust(len(str(len(timestamps))))
                logger.info(f"Extract video clip ({clip_pos}/{len(timestamps)})")

                # Get absolute start and end
                video_start = str_to_sec(start) + conf.start_shift
                video_end = str_to_sec(end) + conf.end_shift
                # Prevent clip from being too long
                if video_end - video_start > conf.max_length:
                    video_end = video_start + conf.max_length
                # Extract clip
                subclip = video_clip.subclip(video_start, video_end)

                # Create destination
                subclip_file_path = os.path.join(conf.output_folder, "clips", video_id, f"{i}.mp4")
                subclip_audio_file_path = subclip_file_path.replace(".mp4", ".mp3")
                os.makedirs(os.path.dirname(subclip_file_path), exist_ok=True)

                # Save clip
                subclip.write_videofile(subclip_file_path, temp_audiofile=subclip_audio_file_path)
                clips.append(subclip_file_path)
        finally:
            video_clip.close()

        return clips


def _clip_list(conf, videos):
    max_videos_amount = min(conf.max_videos_amount, len(videos))
    for video in videos[:max_videos_amount]:
        video_id = video["id"]["videoId"]
        if len(conf.filter_videos_ids) > 0 and (video_id not in conf.filter_videos_ids):
            continue

        if len(video["data"]["clips"]) > 0:
            for pos, clip in enumerate(video["data"]["clips"]):
                yield video, clip, pos


def _build_final_video(conf, videos):
    video_clips = []
    total = sum(1 for _ in _clip_list(conf, videos))

    for counter, (video, clip, pos) in enumerate(_clip_list(conf, videos)):
        video_id = video["id"]["videoId"]
        pos_log = str(pos + 1)
        clips_count_log = str(len(video["data"]["clips"]))
        counter_log = str(counter + 1).rjust(len(str(total)))
        logger.info(f"Build final clip (video {video_id}: {pos_log}/{clips_count_log}) (global: {counter_log}/{total})")

        video_clip = VideoFileClip(clip)
        if conf.do_text_overlay:
            video_clip = editor.add_info_overlay(video_clip, video, pos, counter, total)
        video_clips.append(video_clip)

    if len(video_clips) == 0:
        logger.info(f"No clips to concatenate for final video")
        return

    logger.info(f"Concatenate all clips for final video")
    final_clip = concatenate_videoclips(video_clips, method="compose")
    final_clip_file_path = os.path.join(
        conf.output_folder, f"{conf.channel_name}_{conf.word_to_extract}_{str(uuid.uuid4())[:6]}.mp4"
    )
    final_clip_audio_file_path = final_clip_file_path.replace(".mp4", ".mp3")
    final_clip.write_videofile(final_clip_file_path, temp_audiofile=final_clip_audio_file_path)


def run(args):
    conf = config.read(args.config, "catch", Config)

    logger.prefix = "> "

    logger.info("Retrieve channel id")
    channel_id = read_saved_data(conf, "channel_id", lambda: youtube.get_channel_id(conf.api_key, conf.channel_name))
    logger.info("Retrieve list of videos")
    videos = read_saved_data(
        conf, "videos", lambda: youtube.get_videos(conf.api_key, channel_id), update=conf.do_update_video_data
    )

    pos = 1
    videos_len = min(conf.max_videos_amount, len(videos))
    videos_len_log = videos_len if len(conf.filter_videos_ids) == 0 else len(conf.filter_videos_ids)
    for i in range(videos_len):
        video_id = videos[i]["id"]["videoId"]

        if len(conf.filter_videos_ids) > 0 and (video_id not in conf.filter_videos_ids):
            continue

        pos_log = str(pos).rjust(len(str(videos_len_log)))
        logger.prefix = f"({pos_log}/{videos_len_log}) {video_id} >> "

        logger.info("Retrieve video data")
        video_saved_data_path = os.path.join("videos", video_id)
        video_data = read_saved_data(conf, video_saved_data_path, lambda: None, write=False)

        if conf.do_override_video_data or video_data is None:
            video_data = _extract_video_data(conf, video_id)
            if video_data is None:
                logger.info("Unable to load video data")
                continue
            _write_saved_data(conf, video_saved_data_path, lambda: video_data)

        if conf.do_generate_clips and (conf.do_override_clips or video_data.get("clips", None) is None):
            clips = _extract_video_clips(conf, video_id, video_data)
            if clips is not None:
                video_data["clips"] = clips
            _write_saved_data(conf, video_saved_data_path, lambda: video_data)

        clips_len = len(video_data.get("clips", []))
        if clips_len == 0:
            logger.info("No clips to load")
        else:
            logger.info(f"Loaded {clips_len} clips")

        videos[i]["data"] = video_data
        pos += 1

    logger.prefix = "> "

    if conf.do_generate_final_video:
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
