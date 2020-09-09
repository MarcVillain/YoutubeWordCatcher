import os

from commands.catch import extract, saved_data
from utils import logger


def video(conf, videos, i):
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
    video_data = saved_data.read(conf, video_saved_data_path, lambda: None, write=False)

    if conf.do_override_video_data or video_data is None:
        video_data = extract.video_data(conf, video_id)
        if video_data is None:
            logger.info("Unable to load video data", prefix=conf.logger_prefix)
            return
        saved_data.write(conf, video_saved_data_path, lambda: video_data)

    timestamps_count = len(video_data.get("timestamps", []))
    logger.debug(f"Loaded {timestamps_count} timestamps", prefix=conf.logger_prefix)

    if conf.do_generate_clips and (conf.do_override_clips or video_data.get("clips", None) is None):
        clips = extract.video_clips(conf, video_id, video_data)
        if clips is not None:
            video_data["clips"] = clips
        saved_data.write(conf, video_saved_data_path, lambda: video_data)

    clips_len = len(video_data.get("clips", []))
    if clips_len == 0:
        logger.info("No clips to load", prefix=conf.logger_prefix)
    else:
        logger.info(f"Loaded {clips_len} clips", prefix=conf.logger_prefix)

    videos[i]["data"] = video_data
