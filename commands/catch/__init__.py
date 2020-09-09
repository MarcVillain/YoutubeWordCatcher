"""
Extract clips of youtube videos where a word is pronounced
"""
import argparse
from concurrent.futures.thread import ThreadPoolExecutor
from copy import deepcopy

from commands.catch import saved_data, process, build
from commands.catch.config import CatchConfig
from utils import config, logger, youtube


def run(args):
    conf = config.read(args.config, "catch", CatchConfig)

    # This might be an abuse as the conf is not the context but it works
    conf.logger_prefix = "> "

    logger.info("Retrieve channel id")
    channel_id = saved_data.read(conf, "channel_id", lambda: youtube.get_channel_id(conf.api_key, conf.channel_name))
    logger.info("Retrieve list of videos")
    videos = saved_data.read(
        conf, "videos", lambda: youtube.get_videos(conf.api_key, channel_id), update=conf.do_update_video_data
    )

    max_videos_amount = min(conf.max_videos_amount, len(videos))

    if conf.max_data_thread_workers <= 1:
        for i in range(max_videos_amount):
            process.video(conf, videos, i)
    else:
        with ThreadPoolExecutor(max_workers=conf.max_data_thread_workers) as pool:
            for i in range(max_videos_amount):
                # We need to copy the configuration to edit the logging prefix
                # locally to a thread to be able to use it
                pool.submit(process.video, deepcopy(conf), videos, i)

    if conf.do_generate_final_video:
        video_file_path = build.final_video(conf, videos)
        if video_file_path is not None:
            logger.info(f"Final video: {video_file_path}", prefix=">>> ")


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
