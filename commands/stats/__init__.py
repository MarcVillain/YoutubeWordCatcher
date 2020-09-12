"""
Generate statistics on the video's data.
"""
import argparse
import re

from commands.stats.config import StatsConfig
from utils import config, saved_data, logger, clips


def run(args):
    # Load configuration
    conf = config.read(args.config, "stats", StatsConfig)
    conf.logger_prefix = "> "

    # Load videos and their data
    logger.info("Load video's data")
    videos = saved_data.read_videos(conf)

    # Compute statistics
    logger.info("Compute statistics")
    number_of_videos = len(videos)
    number_of_words = 0
    wte_per_video = {}

    words = {}
    for video, (_, word, _), pos, counter in clips.list_for(videos, var="timestamps"):
        video_id = video["id"]["videoId"]
        number_of_words += 1

        words[word] = words.get(word, 0) + 1

        if re.match(conf.word_to_extract, word):
            wte_per_video[video_id] = wte_per_video.get(video_id, 0) + 1

    average_wte_per_video = 0 if number_of_words == 0 else sum(wte_per_video.values()) / number_of_words

    # Sort from high amount to low amount
    words_sorted = sorted([(amount, word) for word, amount in words.items()], reverse=True)
    words_first_10 = ", ".join([f"{word} ({amount} times)" for amount, word in words_sorted[:10]])

    number_of_wte = 0
    position_of_wte = ""
    for i, (amount, word) in enumerate(words_sorted):
        if re.match(conf.word_to_extract, word):
            number_of_wte += amount

            if position_of_wte == "":
                position_of_wte = str(i + 1)
            else:
                position_of_wte += f", {str(i + 1)}"

    # Display statistics
    logger.info(f"{'=' * 21} Statistics {'=' * 21}")
    logger.info(f"Number of videos: {number_of_videos}")
    logger.info(f"Number of words: {number_of_words}")
    logger.info(f"First 10 words: {words_first_10}")
    logger.info(f"Amount: {number_of_wte}", prefix=f"{conf.word_to_extract} >> ")
    logger.info(f"Position: {position_of_wte}", prefix=f"{conf.word_to_extract} >> ")
    logger.info(f"Average per video: {average_wte_per_video}", prefix=f"{conf.word_to_extract} >> ")


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
