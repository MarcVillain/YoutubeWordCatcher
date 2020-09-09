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
from utils.convert import str_to_bool


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
        Words chart options
        """
        # If set, all words are black except for the given ones. Else, give random color to every word.
        self.words_chart_words_color = dict(ast.literal_eval(kwargs.get("words_chart_words_color", "{}")))
        # Maximum number of words to display on the chart (only get n first)
        self.words_chart_max_words_display_count = int(kwargs.get("words_chart_max_words_display_count", 500))

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
        # Should an output file be created?
        self.do_output_file = str_to_bool(kwargs.get("do_output_file", "False"))
        # Should the chart be displayed on screen?
        self.do_display_chart = str_to_bool(kwargs.get("do_display_chart", "True"))

        """
        Filters
        """
        # Only work with these video ids
        self.filter_videos_ids = kwargs.get("filter_videos_ids", [])
        # Only work with these video titles
        self.filter_videos_titles = kwargs.get("filter_videos_titles", [])

        """
        Thresholds
        """
        # Maximum amount of videos to download, cut and compose
        self.max_videos_amount = int(kwargs.get("max_videos_amount", 100000))
        # Above the specified 'n' spacing, make the tags appear every so often
        # example: 40 elements with a space of 20 will have a tag appear every one in two.
        self.tag_spacing = int(kwargs.get("tag_spacing", 20))


def run(args):
    # Load configuration
    conf = config.read(args.config, "chart", Config)
    conf.logger_prefix = "> "

    # Load videos and their data
    videos = read_saved_data(conf, "videos", lambda: [], write=False)
    max_videos_amount = min(conf.max_videos_amount, len(videos))
    for i in range(max_videos_amount):
        video_id = videos[i]["id"]["videoId"]
        video_saved_data_path = os.path.join("videos", video_id)

        pos_log = str(i + 1).rjust(len(str(max_videos_amount)))
        conf.logger_prefix = f"({pos_log}/{max_videos_amount}) {video_id} >> "

        logger.info("Read saved video data", prefix=conf.logger_prefix)
        video_data = read_saved_data(conf, video_saved_data_path, lambda: {}, write=False)
        videos[i]["data"] = video_data

    # Apply video filters
    if len(conf.filter_videos_ids) > 0:
        videos = [video for video in videos if video["id"]["videoId"] in conf.filter_videos_ids]
    if len(conf.filter_videos_titles) > 0:
        videos = [video for video in videos if video["snippet"]["title"] in conf.filter_videos_titles]
        conf.title_colors = [(title, color) for title, color in conf.title_colors if title in conf.filter_videos_titles]

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
