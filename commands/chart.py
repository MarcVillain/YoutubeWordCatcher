"""
Generate statistical charts on the extracted timestamps
"""

import argparse

types = ["amount", "average"]


def run(args):
    pass


def parse(args):
    parser = argparse.ArgumentParser(
        description=__doc__
    )
    parser.add_argument(
        "-t",
        "--type",
        default=types[0],
        choices=types,
        help="type of chart to generate",
    )
    return parser.parse_args(args)
