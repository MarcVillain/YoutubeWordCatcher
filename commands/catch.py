"""
Extract clips of youtube videos where a word is pronounced
"""

import argparse


def run(args):
    # Get channel id
    # Get channel video list
    # Extract timestamps
    # Extract clips
    # Build final video
    pass


def parse(args):
    parser = argparse.ArgumentParser(
        description=__doc__
    )
    parser.add_argument("channel", help="name of the channel")
    parser.add_argument("word", help="word to extract")
    return parser.parse_args(args)
