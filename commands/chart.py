"""
Generate statistical charts on the extracted timestamps
"""

import argparse
import ast
import importlib
import math
import os
import pkgutil

from commands.catch import read_saved_data
from utils import config, logger


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
        Options
        """
        # Dictionary of title keys associated with color values
        # example: {"[TAG]": "red"}
        self.title_colors = dict(ast.literal_eval(kwargs.get("title_colors", "{}")))

        """
        Folders
        """
        # The folder where everything was extracted
        self.output_folder = kwargs.get("output_folder", "")
        # The sub-folder used for persistent data storage (timestamps, lists, ...)
        self.data_folder = kwargs.get("data_folder", os.path.join(self.output_folder, "data"))
        # The sub-folder used to save charts
        self.charts_folder = kwargs.get("charts_folder", os.path.join(self.output_folder, "charts"))

        """
        Switches
        """
        self.do_output_file = bool(kwargs.get("do_output_file", False))
        self.do_display_chart = bool(kwargs.get("do_display_chart", True))

        """
        Filters
        """
        # Only work with these video ids
        self.filter_videos_ids = list(kwargs.get("filter_videos_ids", []))
        # Only work with these video titles
        self.filter_videos_titles = list(kwargs.get("filter_videos_titles", []))

        """
        Thresholds
        """
        # Above the specified 'n' spacing, make the tags appear every so often
        # example: 40 elements with a space of 20 will have a tag appear every one in two.
        self.tag_spacing = int(kwargs.get("tag_spacing", 20))


def run(args):
    # Load configuration
    conf = config.read(args.config, "chart", Config)

    # Load videos and their data
    videos = read_saved_data(conf, "videos", lambda: [], write=False)
    videos_len = len(videos)
    for i in range(videos_len):
        video_id = videos[i]["id"]["videoId"]
        video_saved_data_path = os.path.join("videos", video_id)

        pos_log = str(i + 1).rjust(len(str(videos_len)))
        logger.prefix = f"({pos_log}/{videos_len}) {video_id} >> "

        logger.info("Retrieve video data")
        video_data = read_saved_data(conf, video_saved_data_path, lambda: {}, write=False)
        videos[i]["data"] = video_data

    # Apply video filters
    if len(conf.filter_videos_ids) > 0:
        videos = [video for video in videos if video["id"]["videoId"] in conf.filter_videos_ids]
    if len(conf.filter_videos_titles) > 0:
        videos = [video for video in videos if video["snippet"]["title"] in conf.filter_videos_titles]
        conf.title_colors = [(title, color) for title, color in conf.title_colors if title in conf.filter_videos_titles]

    logger.prefix = "> "

    # Run compute() function in the proper module
    module = importlib.import_module(f"commands.charts.{args.type}")
    module.__getattribute__("compute")(conf, videos)


def parse(prog, args):
    chart_types = [module.name for module in pkgutil.iter_modules([os.path.join("commands", "charts")])]

    # Build description string
    description = f"{__doc__}\n\navailable types:"
    type_max_len = 4 * math.ceil(len(max(chart_types, key=len)) / 4)
    for chart_type in chart_types:
        module = importlib.import_module(f"commands.charts.{chart_type}")
        type_name = chart_type.ljust(type_max_len)
        type_desc = module.__doc__.strip().lower()
        description += f"\n    {type_name}{type_desc}"

    # Parse arguments
    parser = argparse.ArgumentParser(prog=prog, description=description, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument(
        "-c",
        "--config",
        metavar="FILE",
        default="config.ini",
        help="ini configuration file",
    )
    parser.add_argument(
        "-t",
        "--type",
        default="average",
        metavar="NAME",
        choices=chart_types,
        help="type of chart to generate",
    )
    return parser.parse_args(args)
