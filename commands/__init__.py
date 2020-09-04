import argparse
import importlib
import math
import pkgutil
import sys

from utils import logger


def parse():
    # Extract commands
    module_names = [module.name for module in pkgutil.iter_modules(["commands"])]
    commands = {}
    for module_name in module_names:
        module = importlib.import_module(f"commands.{module_name}")
        if module.__doc__ is not None:
            commands[module_name] = {
                "description": module.__doc__.strip().lower(),
                "func_parse": module.__getattribute__("parse"),
                "func_run": module.__getattribute__("run"),
            }

    # Build usage and description string
    usage = "ywc [-h] [-v] <command> [options]"
    description = (
        "Extract every clip of a Youtube channel's videos where a specific word is\n"
        "pronounced and build a big video out of it.\n\n"
        "available commands:"
    )
    command_max_len = 4 * math.ceil(len(max(commands.keys(), key=len)) / 4)
    for command_name, command in commands.items():
        command_name = command_name.ljust(command_max_len)
        command_desc = command["description"]
        description += f"\n    {command_name}{command_desc}"

    # Build parser
    parser = argparse.ArgumentParser(
        usage=usage, description=description, formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="set logging level to DEBUG",
    )
    parser.add_argument("command", help="command to run")

    # Parse arguments
    first_not_option_arg_pos = len(sys.argv)
    for i, arg in enumerate(sys.argv[1:]):
        if arg[0] != "-":
            first_not_option_arg_pos = i + 2
            break

    args = parser.parse_args(sys.argv[1:first_not_option_arg_pos])
    if args.command not in commands:
        print(f"ywc: '{args.command}' is not a ywc command. See 'ywc --help'.")
        exit(1)

    # Set logging level
    logger.setup(args.verbose)

    # Dispatch command call
    cmd_args = commands[args.command]["func_parse"](
        f"{sys.argv[0]} {args.command}", sys.argv[first_not_option_arg_pos:]
    )
    commands[args.command]["func_run"](cmd_args)
