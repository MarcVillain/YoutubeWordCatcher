"""
Generate statistical charts on the extracted timestamps
"""

import argparse
import importlib
import math
import os
import pkgutil

from commands.chart.config import ChartConfig
from utils import config, logger, saved_data


def run(args):
    # Load configuration
    conf = config.read(args.config, "chart", ChartConfig)
    conf.logger_prefix = "> "

    # Load videos and their data
    videos = saved_data.read_videos(conf)

    # Apply video filters
    if len(conf.filter_videos_ids) > 0:
        videos = [video for video in videos if video["id"]["videoId"] in conf.filter_videos_ids]
    if len(conf.filter_videos_titles) > 0:
        videos = [video for video in videos if video["snippet"]["title"] in conf.filter_videos_titles]
        conf.title_colors = [(title, color) for title, color in conf.title_colors if title in conf.filter_videos_titles]

    # Run compute() function in the proper module
    module = importlib.import_module(f"commands.chart.charts.{args.type}")
    module.__getattribute__("compute")(conf, videos)


def parse(prog, args):
    chart_types = [module.name for module in pkgutil.iter_modules([os.path.join("commands", "chart", "charts")])]

    # Build description string
    description = f"{__doc__}\n\navailable types:"
    type_max_len = 4 * math.ceil(len(max(chart_types, key=len)) / 4)
    for chart_type in chart_types:
        module = importlib.import_module(f"commands.chart.charts.{chart_type}")
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
