import os

from moviepy.video.io.VideoFileClip import VideoFileClip
from regex import regex

from utils import logger, youtube, subtitles
from utils.convert import str_to_sec

"""
Video data
"""


def _extract_timestamps(video_id, content, word_to_extract):
    logger.info(f"Extract timestamps where the word {word_to_extract} is pronounced", prefix=f"{video_id} >> ")

    pattern = r"<(\d{2}:\d{2}:\d{2}.\d{3})>([^<]+)<(\d{2}:\d{2}:\d{2}.\d{3})>"
    res = [
        (start, word.strip(), end)
        for start, word, end in regex.findall(pattern, content, overlapped=True)
        if regex.match(word_to_extract, word.strip())
    ]
    logger.debug(f"Extracted {len(res)} words")
    return res


def _extract_time(video_id, content):
    logger.info("Extract time of the video", prefix=f"{video_id} >> ")

    # This is an approximation of the video length based on the last timestamp
    # TODO: Find a way to get the real video length
    #       without having to download the video clip
    pattern = r"\d{2}:\d{2}:\d{2}.\d{3}"
    res = [match for match in regex.findall(pattern, content, overlapped=True)][-1]
    logger.debug(f"Extracted time of {res}")
    return res


def video_data(conf, video_id):
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
        with open(dl["subtitles_file"]["path"], "r") as f:
            content = subtitles.clean_vtt(f)
            return {
                **data,
                "timestamps": _extract_timestamps(video_id, content, conf.word_to_extract),
                "time": _extract_time(video_id, content),
            }


"""
Video clips
"""


def video_clips(conf, video_id, video_data):
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
            for i, (start, word, end) in enumerate(timestamps):
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
                subclip_video_file_subpath = os.path.join("clips", video_id, f"{clip_pos}_{word}.mp4")
                subclip_video_file_path = os.path.join(conf.output_folder, subclip_video_file_subpath)
                subclip_audio_file_path = subclip_video_file_path.replace(".mp4", ".mp3")
                os.makedirs(os.path.dirname(subclip_video_file_path), exist_ok=True)

                # Save clip
                if os.path.exists(subclip_video_file_path) and not os.path.exists(subclip_audio_file_path):
                    logger.info(f"Use existing video clip '{subclip_video_file_subpath}'")
                else:
                    logger.info(f"Save video clip '{subclip_video_file_subpath}'")
                    subclip.write_videofile(
                        subclip_video_file_path,
                        temp_audiofile=subclip_audio_file_path,
                        bitrate="20000k",
                        audio_bitrate="2000k",
                        threads=conf.max_video_write_thread_workers,
                    )

                clips.append(subclip_video_file_path)
        finally:
            video_clip.close()

        return clips
