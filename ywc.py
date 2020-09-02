import argparse
import sys
import textwrap

from commands import chart
from commands import catch


class CommandsHandler:
    def __init__(self):
        parser = argparse.ArgumentParser(
            description="Extract clips where a word is pronounced in the videos of a youtube channel.",
            usage=textwrap.dedent(
                """\
                ywc [-h] [-v] <command> [options]
                
                The most commonly used ymc commands are:
                   catch   extract the clips
                   chart   generate statistics charts
                """
            ),
        )
        parser.add_argument(
            "-v",
            "--verbose",
            action="store_true",
            help="set logging level to DEBUG",
        )
        parser.add_argument("command", help="subcommand to run")

        args = parser.parse_args(sys.argv[1:2])
        if not hasattr(self, args.command):
            print(
                f"ywc: '{args.command}' is not a ywc command. See 'ywc --help'."
            )
            exit(1)

        getattr(self, args.command)()

    def catch(self):
        parser = argparse.ArgumentParser(
            description="Extract the video clips where a word is pronounced."
        )
        parser.add_argument("channel", help="name of the channel")
        parser.add_argument("word", help="word to extract")
        args = parser.parse_args(sys.argv[2:])
        catch.run(args)

    def chart(self):
        parser = argparse.ArgumentParser(
            description="Generate statistics charts."
        )
        parser.add_argument(
            "-t",
            "--type",
            default=chart.types[0],
            choices=chart.types,
            help="type of chart to generate",
        )
        args = parser.parse_args(sys.argv[2:])
        chart.run(args)


if __name__ == "__main__":
    CommandsHandler()
