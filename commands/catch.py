"""
Extract clips of youtube videos where a word is pronounced
"""
import argparse
import os
import uuid
from collections import deque
from concurrent.futures.thread import ThreadPoolExecutor
from copy import deepcopy

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
        self.max_length = float(kwargs.get("max_length", 1.5))
        # Shift of the start timestamp of a clip (in seconds)
        self.start_shift = float(kwargs.get("start_shift", -0.25))
        # Shift of the end timestamp of a clip (in seconds)
        self.end_shift = float(kwargs.get("end_shift", 0.75))

        """
        Switches
        """
        # Should the program data be outputted?
        self.do_output_data = bool(kwargs.get("do_output_data", True))
        # Should the text overlay be applied?
        self.do_text_overlay = bool(kwargs.get("do_text_overlay", True))
        # Should the downloaded files be deleted?
        self.do_cleanup_downloads = bool(kwargs.get("do_cleanup_downloads", True))
        # Should the video datas be computed even if they already exists?
        self.do_override_video_data = bool(kwargs.get("do_override_video_data", False))
        # Should the clips be generated even if they already exists?
        self.do_override_clips = bool(kwargs.get("do_override_clips", False))
        # Should the clips be generated?
        self.do_generate_clips = bool(kwargs.get("do_generate_clips", True))
        # Should the final video be generated?
        self.do_generate_final_video = bool(kwargs.get("do_generate_final_video", True))
        # Should the videos list data be updated?
        self.do_update_video_data = bool(kwargs.get("do_update_video_data", False))

        """
        Filters
        """
        # Only work with these video ids
        self.filter_videos_ids = kwargs.get("filter_videos_ids", [])
        # Ignore these video ids
        self.filter_out_videos_ids = kwargs.get("filter_out_videos_ids", [])

        """
        Thresholds
        """
        # Maximum amount of videos to download, cut and compose
        self.max_videos_amount = int(kwargs.get("max_videos_amount", 100000))
        # Maximum amount of threads to use when retrieving video data and cutting clips
        self.max_data_thread_workers = int(kwargs.get("max_data_thread_workers", 1))


def _write_saved_data(conf, path, func):
    full_path = os.path.join(conf.data_folder, f"{path}.yaml")
    data = func()

    if not conf.do_output_data:
        return data

    logger.info(f"Dump value of '{path}'", prefix=conf.logger_prefix)
    io.dump_yaml(full_path, data)
    return data


def read_saved_data(conf, path, func, write=True, update=False):
    full_path = os.path.join(conf.data_folder, f"{path}.yaml")

    if not update and os.path.exists(full_path):
        logger.info(f"Load value of '{path}'", prefix=conf.logger_prefix)
        return io.load_yaml(full_path)

    if not write:
        return func()

    return _write_saved_data(conf, path, func)


def _extract_video_data(conf, video_id):
    logger.info("Extract video data", prefix=conf.logger_prefix)
    # Download subtitles
    with youtube.download(video_id, conf.download_folder, video=False, cleanup=conf.do_cleanup_downloads) as dl:
        if dl is None:
            logger.error("Unable to download subtitles", prefix=conf.logger_prefix)
            return None

        data = {
            "id": video_id,
            "subtitles_file": dl["subtitles_file"],
            "video_file": dl["video_file"],
        }

        if not dl["subtitles_file"]["exists"]:
            logger.error("No subtitles found", prefix=conf.logger_prefix)
            return data

        # Extract data
        subtitles_data = subtitles.extract_data(video_id, dl["subtitles_file"]["path"], conf.word_to_extract)

        return {
            **data,
            **subtitles_data,
        }


def _extract_video_clips(conf, video_id, video_data):
    logger.info("Extract video clips", prefix=conf.logger_prefix)

    # Check if there is something to extract
    if len(video_data.get("timestamps", [])) == 0:
        logger.info("No timestamps to extract", prefix=conf.logger_prefix)
        return []

    # Download video
    with youtube.download(video_id, conf.download_folder, subtitles=False, cleanup=conf.do_cleanup_downloads) as dl:
        clips = []

        if dl is None:
            logger.error("Unable to download video", prefix=conf.logger_prefix)
            return None

        if not dl["video_file"]["exists"]:
            logger.error("No video file found")
            return clips

        video_clip = VideoFileClip(dl["video_file"]["path"])
        try:
            timestamps = video_data.get("timestamps", [])
            for i, (start, _, end) in enumerate(timestamps):
                clip_pos = str(i + 1).rjust(len(str(len(timestamps))))
                logger.info(f"Extract video clip ({clip_pos}/{len(timestamps)})", prefix=conf.logger_prefix)

                # Get absolute start and end
                video_start = str_to_sec(start) + conf.start_shift
                video_end = str_to_sec(end) + conf.end_shift
                # Prevent clip from being too long
                if video_end - video_start > conf.max_length:
                    video_end = video_start + conf.max_length
                # Extract clip
                subclip = video_clip.subclip(video_start, video_end)

                # Create destination
                subclip_file_path = os.path.join(conf.output_folder, "clips", video_id, f"{clip_pos}.mp4")
                subclip_audio_file_path = subclip_file_path.replace(".mp4", ".mp3")
                os.makedirs(os.path.dirname(subclip_file_path), exist_ok=True)

                # Save clip
                subclip.write_videofile(subclip_file_path, temp_audiofile=subclip_audio_file_path)
                clips.append(subclip_file_path)
        finally:
            video_clip.close()

        return clips


def _process_video(conf, videos, i):
    video_id = videos[i]["id"]["videoId"]

    if len(conf.filter_videos_ids) > 0 and (video_id not in conf.filter_videos_ids):
        logger.info("Ignored", prefix=conf.logger_prefix)
        return
    if len(conf.filter_out_videos_ids) > 0 and (video_id in conf.filter_out_videos_ids):
        logger.info("Filtered out", prefix=conf.logger_prefix)
        return

    max_videos_amount = min(conf.max_videos_amount, len(videos))
    videos = videos[:max_videos_amount]

    pos_log = str(i + 1).rjust(len(str(max_videos_amount)))
    # This might be an abuse as the conf is not the context but it works
    conf.logger_prefix = f"({pos_log}/{max_videos_amount}) {video_id} >> "

    logger.info("Retrieve video data", prefix=conf.logger_prefix)
    video_saved_data_path = os.path.join("videos", video_id)
    video_data = read_saved_data(conf, video_saved_data_path, lambda: None, write=False)

    if conf.do_override_video_data or video_data is None:
        video_data = _extract_video_data(conf, video_id)
        if video_data is None:
            logger.info("Unable to load video data", prefix=conf.logger_prefix)
            return
        _write_saved_data(conf, video_saved_data_path, lambda: video_data)

    if conf.do_generate_clips and (conf.do_override_clips or video_data.get("clips", None) is None):
        clips = _extract_video_clips(conf, video_id, video_data)
        if clips is not None:
            video_data["clips"] = clips
        _write_saved_data(conf, video_saved_data_path, lambda: video_data)

    clips_len = len(video_data.get("clips", []))
    if clips_len == 0:
        logger.info("No clips to load", prefix=conf.logger_prefix)
    else:
        logger.info(f"Loaded {clips_len} clips", prefix=conf.logger_prefix)

    videos[i]["data"] = video_data


def _clip_list(conf, videos):
    counter = 0

    for video in videos:
        video_id = video["id"]["videoId"]
        if len(conf.filter_videos_ids) > 0 and (video_id not in conf.filter_videos_ids):
            continue
        if len(conf.filter_out_videos_ids) > 0 and (video_id in conf.filter_out_videos_ids):
            continue

        if len(video["data"].get("clips", [])) > 0:
            for i, clip in enumerate(video["data"]["clips"]):
                counter += 1
                yield video, clip, i + 1, counter


def _build_final_video(conf, videos):
    logger.info("Build final clip")

    # TODO: Check if final file already exists

    # Ensure build folder exists
    os.makedirs(conf.build_folder, exist_ok=True)

    # Define some useful variables
    max_videos_amount = min(conf.max_videos_amount, len(videos))
    videos = videos[:max_videos_amount]

    threshold = 61
    total = sum(1 for _ in _clip_list(conf, videos))

    if total == 0:
        logger.info("No clips to build")
        return

    video_clips_queue = deque([clip_info for clip_info in _clip_list(conf, videos)])
    temp_clips_queue = deque([])

    temp_clips_files_counter = 1

    # While there are clips to concatenate
    while len(video_clips_queue) > 0 or len(temp_clips_queue) > 2:
        # TODO: Preload [temp_clips_files_counter] file if it exists

        video_clips = []
        do_concatenate_videos_clips = len(video_clips_queue) > 0

        if do_concatenate_videos_clips:
            # Create the group of videos to be concatenated
            clips_group = []
            while len(video_clips_queue) > 0 and len(clips_group) < threshold:
                clips_group.append(video_clips_queue.popleft())

            for video, clip, pos, counter in clips_group:
                # Build video clip
                video_id = video["id"]["videoId"]
                clips_count_log = str(len(video["data"]["clips"]))
                counter_log = str(counter).rjust(len(str(total)))
                logger.info(
                    f"Build clip (video {video_id}: {pos}/{clips_count_log}) (global: {counter_log}/{total})",
                )
                video_clip = VideoFileClip(clip)
                if conf.do_text_overlay:
                    video_clip = editor.add_info_overlay(video_clip, video, pos, counter, total)

                # Add video clip to list
                video_clips.append(video_clip)
        else:
            # Create the group of temporary clips videos to be concatenated
            clips_group = []
            while len(temp_clips_queue) > 0 and len(clips_group) < threshold:
                temp_clip = temp_clips_queue.popleft()
                # Prevent clips de-ordering
                if temp_clip is None:
                    if len(clips_group) == 1:
                        # Nothing to change or build really, just push pack the video file
                        temp_clips_queue.append(clips_group[0])
                        clips_group = []
                    # Ensure we are marking the build loop to prevent de-ordering
                    temp_clips_queue.append(None)
                    break
                clips_group.append(temp_clip)

            # Add video clips to list
            video_clips = [VideoFileClip(clip) for clip in clips_group]

        if len(video_clips) > 0:
            logger.info("Concatenate clips into a temporary clip")
            temp_clip = concatenate_videoclips(video_clips, method="compose")

            logger.info(f"Save temporary clip {temp_clips_files_counter}")
            temp_clip_file_path = os.path.join(conf.build_folder, f"t{threshold}_c{temp_clips_files_counter}.mp4")
            temp_clip_audio_file_path = temp_clip_file_path.replace(".mp4", ".mp3")
            temp_clip.write_videofile(temp_clip_file_path, temp_audiofile=temp_clip_audio_file_path)
            temp_clips_files_counter += 1

            # Add temporary clip to list
            temp_clips_queue.append(temp_clip_file_path)

            # Ensure we are marking the build loop to prevent de-ordering
            if do_concatenate_videos_clips and len(video_clips_queue) == 0:
                temp_clips_queue.append(None)

            # Close videos clips file descriptors
            for video_clip in video_clips:
                video_clip.close()

            # Cleanup temporary clips
            # (remove clips that got concatenated into another clip and are no longer needed)
            if not do_concatenate_videos_clips:
                for video_clip in video_clips:
                    try:
                        logger.info(f"Remove temporary clip '{os.path.basename(video_clip.filename)}'")
                        os.remove(video_clip.filename)
                    except OSError as e:
                        logger.error(f"Unable to remove clip: {e}")

    # Move final clip to desired result location
    last_temp_clip_file_path = temp_clips_queue[0] or temp_clips_queue[1]
    final_clip_file_path = os.path.join(conf.build_folder, f"{conf.channel_name}_{conf.word_to_extract}.mp4")
    try:
        os.rename(last_temp_clip_file_path, final_clip_file_path)
    except OSError as e:
        logger.error(f"Unable to rename temporary clip: {e}")


def run(args):
    conf = config.read(args.config, "catch", Config)

    # This might be an abuse as the conf is not the context but it works
    conf.logger_prefix = "> "

    logger.info("Retrieve channel id")
    channel_id = read_saved_data(conf, "channel_id", lambda: youtube.get_channel_id(conf.api_key, conf.channel_name))
    logger.info("Retrieve list of videos")
    videos = read_saved_data(
        conf, "videos", lambda: youtube.get_videos(conf.api_key, channel_id), update=conf.do_update_video_data
    )

    max_videos_amount = min(conf.max_videos_amount, len(videos))

    if conf.max_data_thread_workers <= 1:
        for i in range(max_videos_amount):
            _process_video(conf, videos, i)
    else:
        with ThreadPoolExecutor(max_workers=conf.max_data_thread_workers) as pool:
            for i in range(max_videos_amount):
                # We need to copy the configuration to edit the logging prefix
                # locally to a thread to be able to use it
                pool.submit(_process_video, deepcopy(conf), videos, i)

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
